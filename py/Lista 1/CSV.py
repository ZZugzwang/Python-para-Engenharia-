#Aluno: João Antônio Dubeux
#Curso: Engenharia Eletrônica
#Cpf: 146.628.704.70
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
        else:
            current.append(ch)
    field.append("".join(current).strip())
    return field
def extract(lines):
    #retorna as linhas do arquivo .CSV
    field = split.field(lines) + ["", "", ""]
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
def report(lines):
    for line_no, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        name, cpf, card = extract(line)
        errors = {
            "NOME - campo vazio" if name == " " else None,
            validate("CPF", cpf, ".-/_", 11, cpf_valid),
            validate("cartao", card, " ", 16, luhn_alg),
        }
        
        yield from (f"linha {line_no:4d}: {e}" for e in errors if e)

