#Aluno: João Antônio Dubeux
#Curso: Engenharia Eletrônica
#lista 1 : algoritimo leitura CSV

# ---------------------------------------------------------------------------
# VISÃO GERAL
# O programa lê um arquivo CSV (nome, CPF, cartão de crédito), valida cada
# linha e imprime um relatório com os erros encontrados. Também gera um
# relatório em HTML. Nenhuma biblioteca (nem a standard library) é importada:
# tudo é feito com as construções da própria linguagem.
#
# POR QUE USAR list comprehensions, geradores, enumerate, zip, etc.?
# Em C, o equivalente seria um for com índice, vetores auxiliares alocados
# manualmente, variáveis acumuladoras e vários if. Em Python:
#  - o código diz O QUE queremos  e não COMO
#    controlar índices, o que reduz erros (off-by-one, estouro de
#    vetor, esquecer de inicializar um acumulador);
#  - não há alocação/liberação de memória nem tamanho fixo de vetor: as
#    listas crescem sozinhas e o lixo é coletado automaticamente;
#  - geradores (yield) produzem os resultados sob demanda, um de cada vez,
#    sem montar um vetor gigante na memória (em C seria preciso um buffer
#    ou uma função com ponteiros e estado externo).
# ---------------------------------------------------------------------------
#A ideia de criar um relatorio opcional html foi uma ideia extra pra facilitar a visualização de casos teste 
# Conjunto de caracteres aceitos como dígito. Usamos esta string em vez de
# str.isdigit() porque isdigit() aceita dígitos de outros alfabetos (por
# exemplo "４", de largura total) que o int() converteria sem reclamar, o que
# seria uma brecha para entradas maliciosas.
DIGITS = "0123456789"

def split(line):
    #separa as linhas do arquivo csv em partes
    # Divide uma linha CSV em campos, respeitando aspas: uma vírgula dentro de
    # aspas ("Silva, Maria") faz parte do campo e NÃO é separador.
    # field   -> lista de campos já prontos
    # current -> lista de caracteres do campo que está sendo lido agora
    # quotes  -> True enquanto estivermos dentro de um trecho entre aspas
    field, current, quotes= [], [], False
    # rstrip remove só o fim de linha (\r\n), preservando o resto do conteúdo
    for ch in line.rstrip("\r\n"):
        if ch == '"':
            # aspas apenas "ligam/desligam" o modo aspas e não entram no campo
            quotes = not quotes
        elif ch == "," and not quotes:
            # vírgula fora de aspas: fecha o campo atual.
            # "".join(lista) monta a string de uma vez (mais eficiente e mais
            # simples do que concatenar caractere a caractere como em C).
            # strip() tira espaços nas pontas do campo.
            field.append("".join(current).strip())
            current = []
        else:
            current.append(ch)
    # o último campo não termina em vírgula, então é fechado aqui
    field.append("".join(current).strip())
    return field

def extract(lines):
    #retorna as linhas do arquivo .CSV
    # Garante SEMPRE exatamente 3 campos (nome, cpf, cartão).
    # Somando ["", "", ""] à lista, uma linha com campos faltando fica
    # preenchida com strings vazias (e será reportada como "campo vazio");
    # o fatiamento [:3] descarta campos extras. Assim não há IndexError
    field = split(lines) + ["", "", ""]
    return field[:3]

def cpf_valid(digits):
    # Valida os dois dígitos verificadores do CPF.
    # 'digits' é uma lista com 11 caracteres numéricos.
    # List comprehension: converte cada caractere em inteiro numa única linha
    nums = [int(c) for c in digits]
    # Rejeita CPFs com todos os dígitos iguais (111.111.111-11 etc.).
    # Eles passam na conta matemática, mas não são CPFs válidos.
    # set() elimina repetidos: se sobrou só 1 valor, todos eram iguais.
    if len(set(nums)) == 1:
        return False
    def check_cpf(base):
        # Calcula um dígito verificador a partir dos dígitos de 'base'.
        # Os pesos vão de len(base)+1 até 2 (10..2 para o 1º dígito,
        # 11..2 para o 2º), gerados por range com passo -1.
        # zip emparelha cada dígito com o seu peso, sem usar índice, e a
        # expressão geradora dentro do sum() soma os produtos sem criar
        # uma lista intermediária.
        total = sum(j * k for j, k in zip(base, range(len(base) + 1, 1, -1)))
        # (total*10 % 11) % 10 é a regra oficial: resto 10 vira dígito 0.
        return (total * 10 % 11) % 10
    # 1º dígito usa os 9 primeiros; 2º dígito usa os 10 primeiros
    # (os 9 iniciais + o 1º dígito verificador). Fatiar (nums[:9]) evita
    # laços com índices.
    return check_cpf(nums[:9]) == nums[9] and check_cpf(nums[:10]) == nums[10]

def luhn_alg(digits):
    # Algoritmo de Luhn para o número do cartão de crédito.
    # reversed() percorre os dígitos da direita para a esquerda, que é a
    # ordem exigida pelo algoritmo, sem precisar calcular índices
    # decrescentes (len-1-i) como em C.
    nums = [int(c) for c in reversed(digits)]
    # enumerate fornece (posição, dígito) ao mesmo tempo, dispensando o
    # contador manual 'i++'.
    # Posições pares (0, 2, ...) entram como estão; nas ímpares o dígito é
    # dobrado e, se o resultado passar de 9, subtrai-se 9 (equivale a somar
    # os dois algarismos do resultado). Como n*2 > 9 só quando n >= 5:
    #   n < 5  -> n*2          n >= 5 -> n*2 - 9
    total = sum(n if i % 2 == 0 else (n * 2 if n < 5 else n * 2 - 9)
                for i, n in enumerate(nums))
    # o cartão é válido quando a soma é múltiplo de 10
    return total % 10 == 0

def validate(label, value, separators, lenght, checker):
    # Função genérica de validação, usada tanto para o CPF quanto para o cartão
    # (evita duplicar código). Parâmetros:
    #   label      -> nome do campo para a mensagem ("CPF" ou "cartao")
    #   value      -> texto lido do CSV
    #   separators -> caracteres de separação permitidos nesse campo
    #   lenght     -> quantidade exata de dígitos esperada (11 ou 16)
    #   checker    -> função que confere os dígitos verificadores
    # 'checker' é uma função passada como argumento (funções são objetos em
    # Python); em C seria preciso um ponteiro para função.
    # Retorna a mensagem de erro (str) ou None se o campo estiver correto.

    # 1º erro: campo vazio
    if value == "":
        return f"{label} - campo vazio"
    # 2º erro: qualquer caractere que não seja dígito nem separador permitido
    # (letras, emojis, tabs, dígitos de largura total...). any() para no
    # primeiro caractere ruim, sem varrer o resto à toa.
    if any(c not in DIGITS and c not in separators for c in value):
        return f"{label} - caractere invalido"
    # Extrai só os dígitos, descartando os separadores (filtro numa linha)
    digits = [c for c in value if c in DIGITS]
    # 3º erro: quantidade de dígitos diferente da esperada
    if len(digits) != lenght:
        return f"{label} - quantidade incorreta de caracteres ({len(digits)} digitos)"
    # 4º erro: dígitos verificadores não conferem
    if not checker(digits):
        return f"{label} - erro de verificação "
    return None

# devolve (numero da linha, texto original, mensagem) para cada erro.
#A tela e o arquivo HTML usam esta mesma função.
def find_errors(lines):
    # GERADOR: cada 'yield' entrega um erro por vez, assim que ele é achado,
    # sem montar antes uma lista com todos os erros (economiza memória e
    # permite que o chamador processe aos poucos).
    # enumerate(..., start=1) numera as linhas a partir de 1, como no editor
    # de texto, em vez de manter um contador manual.
    for line_no, line in enumerate(lines, start=1):
        # linhas em branco são ignoradas, mas a numeração continua correta
        if not line.strip():
            continue
        # desempacotamento: atribui os 3 campos às 3 variáveis de uma vez
        name, cpf, card = extract(line)
        # Tupla com o resultado de cada verificação (None = sem erro).
        # O nome só precisa ser não vazio; CPF e cartão passam por validate().
        # Como cada campo gera sua própria mensagem, uma linha com erro no
        # CPF E no cartão produz DOIS erros, como pede a lista.
        errors = (
            "NOME - campo vazio" if name == "" else None,
            validate("CPF", cpf, ".-/_", 11, cpf_valid),
            validate("cartao", card, " ", 16, luhn_alg),
        )
        # 'yield from' + expressão geradora: entrega apenas os erros que não
        # são None (o filtro 'if e' substitui um if/append dentro de um for).
        yield from ((line_no, line.strip(), e) for e in errors if e)

def report(lines):
    # Gera as linhas do relatório de tela, no formato "linha NNN: erro".
    # {n:4d} reserva 4 posições para o número da linha (alinhamento).
    # Também é um gerador: formata cada erro só quando for pedido.
    # O '_' ignora o texto original da linha, que aqui não é necessário.
    yield from (f"linha {n:4d}: {e}" for n, _, e in find_errors(lines))

#NOVO: troca caracteres especiais do HTML (o CSV pode ter <script>, & etc.)
def esc(text):
    # Evita que conteúdo malicioso vindo do CSV (por exemplo uma tag <script>)
    # seja interpretado como HTML. O "&" precisa ser trocado PRIMEIRO, senão
    # os "&" criados pelas outras substituições seriam trocados de novo.
    return (text.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;").replace('"', "&quot;"))

#NOVO: corta textos muito longos para nao estourar a tabela
def short(text, size=60):
    # Expressão condicional: devolve o texto inteiro se for curto, ou os
    # primeiros 'size' caracteres seguidos de reticências se for longo.
    return text if len(text) <= size else text[:size] + "…"

#NOVO: monta e salva o relatorio em HTML (rows = lista de (linha, texto, mensagem))
def write_html(out_path, source, total_lines, rows):
    # Número de linhas DIFERENTES com erro: o conjunto (set comprehension)
    # elimina repetições, já que uma linha pode ter até 2 erros.
    bad_lines = len({n for n, _, _ in rows})
    # Contagem de erros por campo (NOME, CPF, cartao). A list comprehension
    # interna filtra os erros daquele campo e len() conta quantos são;
    # tudo numa expressão, sem contadores manuais nem vários if/else.
    by_field = [(f, len([r for r in rows if r[2].startswith(f + " -")]))
                for f in ("NOME", "CPF", "cartao")]
    # Contagem de erros por tipo de motivo, no mesmo estilo
    by_reason = [(m, len([r for r in rows if m in r[2]]))
                 for m in ("campo vazio", "caractere invalido",
                           "quantidade incorreta", "erro de verificação")]
    # Monta as linhas <tr> da tabela-resumo juntando os dois resultados.
    # "".join(...) concatena tudo de uma vez; esc() protege o HTML.
    summary = "".join(f"<tr><td>{esc(k)}</td><td>{v}</td></tr>"
                      for k, v in by_field + by_reason)
    # Monta as linhas da tabela de erros. e.split(' - ', 1) separa a mensagem
    # em [campo, motivo] (só no primeiro " - "). O texto original da linha é
    # encurtado por short() e escapado por esc() antes de ir para o HTML.
    body = "".join(
        f"<tr><td>{n:4d}</td><td>{esc(e.split(' - ', 1)[0])}</td>"
        f"<td>{esc(e.split(' - ', 1)[1])}</td><td><code>{esc(short(text))}</code></td></tr>"
        for n, text, e in rows)
    # Modelo da página (string com três aspas, que aceita várias linhas).
    # As chaves do CSS são duplicadas ({{ }}) para não serem confundidas
    # com os campos {variavel} do f-string.
    html = f"""<!DOCTYPE html>\r
<html lang="pt-BR"><head><meta charset="utf-8">\r
<title>Relatório de validação</title>\r
<style>\r
body{{font-family:Arial,sans-serif;margin:2em;color:#222}}\r
table{{border-collapse:collapse;margin-bottom:2em}}\r
th,td{{border:1px solid #999;padding:6px 10px;text-align:left}}\r
th{{background:#e8e8e8}} code{{word-break:break-all}}\r
</style></head><body>\r
<h1>Relatório de validação</h1>\r
<p>Aluno: João Antônio Dubeux | Arquivo: <b>{esc(source)}</b><br>\r
Linhas lidas: {total_lines} | Linhas com erro: {bad_lines} | Total de erros: {len(rows)}</p>\r
<h2>Resumo</h2>\r
<table><tr><th>Categoria</th><th>Quantidade</th></tr>{summary}</table>\r
<h2>Erros encontrados</h2>\r
<table><tr><th>Linha</th><th>Campo</th><th>Motivo</th><th>Conteúdo da linha</th></tr>\r
{body}</table>\r
</body></html>"""
    # 'with' garante que o arquivo seja fechado mesmo se ocorrer algum erro
    # (em C seria preciso lembrar do fclose em todos os caminhos).
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

def main():
    # Pede o nome do arquivo CSV ao usuário
    path = input("Arquivo CSV: ").strip()
    try:
        # utf-8-sig remove o BOM que o Excel costuma colocar no início do arquivo
        with open(path, encoding="utf-8-sig") as f:
            lines = f.readlines()  #lista, para poder percorrer mais de uma vez
    except OSError as e:
        # arquivo inexistente, sem permissão etc.: avisa e encerra sem quebrar
        print(f"Não foi possivel abrir o arquivo: {e}")
        return
    # list() consome o gerador report() e guarda os resultados para imprimir.
    # Isso é necessário porque um gerador só pode ser percorrido uma vez, e
    # 'lines' (uma lista) é reutilizada logo abaixo para o HTML.
    errors = list(report(lines))
    # Imprime um erro por linha; se a lista estiver vazia, avisa que não há erros
    print("\n".join(errors) if errors else "nenhum erro encontrado.")
    write_html("relatorio.html", path, len(lines), list(find_errors(lines)))
    print("\nRelatorio salvo em relatorio.html")

# Só executa main() quando o arquivo é rodado diretamente (e não quando é
# importado por outro programa, por exemplo nos testes)
if __name__ == "__main__":
    main()