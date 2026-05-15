# CENÁRIO 1 — LOGIN SEGURO

import bcrypt

users_db = {
    "admin": bcrypt.hashpw("SenhaForte123".encode(), bcrypt.gensalt()),
    "joao": bcrypt.hashpw("OutraSenha456".encode(), bcrypt.gensalt())
}

tentativas = {}

def login(usuario, senha):

    if tentativas.get(usuario, 0) >= 3:
        return "Conta bloqueada temporariamente"

    if usuario in users_db:
        senha_correta = users_db[usuario]

        if bcrypt.checkpw(senha.encode(), senha_correta):
            tentativas[usuario] = 0
            return "Login realizado com sucesso"

    tentativas[usuario] = tentativas.get(usuario, 0) + 1
    return "Usuário ou senha inválidos"


print(login("admin", "SenhaForte123"))
print(login("admin", "errado"))
print(login("admin", "errado"))
print(login("admin", "errado"))
print(login("admin", "SenhaForte123"))