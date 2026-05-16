# CENÁRIO 2 — CONTROLE DE ACESSO


usuarios = {
    "admin": {"role": "admin"},
    "joao": {"role": "user"},
    "visitante": {"role": "guest"}
}

def acessar_dados(usuario):

    if usuario not in usuarios:
        return "Usuário não encontrado"

    if usuarios[usuario]["role"] != "admin":
        return "Acesso negado"

    return "Dados confidenciais acessados"


print(acessar_dados("admin"))
print(acessar_dados("joao"))
print(acessar_dados("visitante"))