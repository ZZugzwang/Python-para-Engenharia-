#Aluno: João Antônio Dubeux
#Curso: Engenharia Eletrônica
#lista 1 : algoritimo leitura CSV
DIGITS = "0123456789"
def split(line):
    #separa as linhas do arquivo csv em partes
    field, current, quotes= [], [], False
    for ch in line.rstrip("\r\n"):
        if ch == '"':
            quotes = not quotes
        elif ch == "," and not quotes:
            field.append("".join(current).strip())
            current = []
        else:
            current.append(ch)
    field.append("".join(current).strip())
    return field
def extract(lines):
    #retorna as linhas do arquivo .CSV
    field = split(lines) + ["", "", ""]
    return field[:3]
def cpf_valid(digits):
    nums = [int(c) for c in digits]
    if len(set(nums)) == 1:
        return False
    def check_cpf(base):
        total = sum(j * k for j, k in zip(base, range(len(base) + 1, 1, -1)))
        return (total * 10 % 11) % 10
    return check_cpf(nums[:9]) == nums[9] and check_cpf(nums[:10]) == nums[10]
def luhn_alg(digits):
    nums = [int(c) for c in reversed(digits)]
    total = sum(n if i % 2 == 0 else (n * 2 if n < 5 else n * 2 - 9)
                for i, n in enumerate(nums))
    return total % 10 == 0

def validate(label, value, separators, lenght, checker):
    if value == "":
        return f"{label} - campo vazio"
    if any(c not in DIGITS and c not in separators for c in value):
        return f"{label} - caractere invalido"
    digits = [c for c in value if c in DIGITS]
    if len(digits) != lenght:
        return f"{label} - quantidade incorreta de caracteres ({len(digits)} digitos)"
    if not checker(digits):
        return f"{label} - erro de verificação "
    return None

#NOVO: devolve (numero da linha, texto original, mensagem) para cada erro.
#A tela e o arquivo HTML usam esta mesma função.
def find_errors(lines):
    for line_no, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        name, cpf, card = extract(line)
        errors = (
            "NOME - campo vazio" if name == "" else None,
            validate("CPF", cpf, ".-/_", 11, cpf_valid),
            validate("cartao", card, " ", 16, luhn_alg),
        )
        yield from ((line_no, line.strip(), e) for e in errors if e)

def report(lines):
    yield from (f"linha {n:4d}: {e}" for n, _, e in find_errors(lines))

#NOVO: troca caracteres especiais do HTML (o CSV pode ter <script>, & etc.)
def esc(text):
    return (text.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;").replace('"', "&quot;"))

#NOVO: corta textos muito longos para nao estourar a tabela
def short(text, size=60):
    return text if len(text) <= size else text[:size] + "…"

#NOVO: monta e salva o relatorio em HTML (rows = lista de (linha, texto, mensagem))
def write_html(out_path, source, total_lines, rows):
    bad_lines = len({n for n, _, _ in rows})
    by_field = [(f, len([r for r in rows if r[2].startswith(f + " -")]))
                for f in ("NOME", "CPF", "cartao")]
    by_reason = [(m, len([r for r in rows if m in r[2]]))
                 for m in ("campo vazio", "caractere invalido",
                           "quantidade incorreta", "erro de verificação")]
    summary = "".join(f"<tr><td>{esc(k)}</td><td>{v}</td></tr>"
                      for k, v in by_field + by_reason)
    body = "".join(
        f"<tr><td>{n:4d}</td><td>{esc(e.split(' - ', 1)[0])}</td>"
        f"<td>{esc(e.split(' - ', 1)[1])}</td><td><code>{esc(short(text))}</code></td></tr>"
        for n, text, e in rows)
    html = f"""<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="utf-8">
<title>Relatório de validação</title>
<style>
body{{font-family:Arial,sans-serif;margin:2em;color:#222}}
table{{border-collapse:collapse;margin-bottom:2em}}
th,td{{border:1px solid #999;padding:6px 10px;text-align:left}}
th{{background:#e8e8e8}} code{{word-break:break-all}}
</style></head><body>
<h1>Relatório de validação</h1>
<p>Aluno: João Antônio Dubeux | Arquivo: <b>{esc(source)}</b><br>
Linhas lidas: {total_lines} | Linhas com erro: {bad_lines} | Total de erros: {len(rows)}</p>
<h2>Resumo</h2>
<table><tr><th>Categoria</th><th>Quantidade</th></tr>{summary}</table>
<h2>Erros encontrados</h2>
<table><tr><th>Linha</th><th>Campo</th><th>Motivo</th><th>Conteúdo da linha</th></tr>
{body}</table>
</body></html>"""
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

def main():
    path = input("Arquivo CSV: ").strip()
    try:
        with open(path, encoding="utf-8-sig") as f:
            lines = f.readlines()  #lista, para poder percorrer mais de uma vez
    except OSError as e:
        print(f"Não foi possivel abrir o arquivo: {e}")
        return
    errors = list(report(lines))
    print("\n".join(errors) if errors else "nenhum erro encontrado.")
    write_html("relatorio.html", path, len(lines), list(find_errors(lines)))
    print("\nRelatorio salvo em relatorio.html")

if __name__ == "__main__":
    main()