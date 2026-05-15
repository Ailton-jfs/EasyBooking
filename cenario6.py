# CENÁRIO 6 — PAINEL ADMIN

usuarios = {
    "admin": {"role": "admin"},
    "joao": {"role": "user"}
}

def acessar_painel_admin(usuario):

    if usuario not in usuarios:
        return "Usuário inválido"

    if usuarios[usuario]["role"] != "admin":
        return "Acesso negado"

    return "Acesso ao painel administrativo liberado"


print(acessar_painel_admin("admin"))
print(acessar_painel_admin("joao"))