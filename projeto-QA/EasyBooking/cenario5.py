# CENÁRIO 5 — EXCLUSÃO COMPLETA


usuarios = ["joao", "maria", "ana"]
backup = ["joao", "maria", "ana"]
logs = ["joao acessou sistema"]

def excluir_usuario(nome):

    if nome in usuarios:
        usuarios.remove(nome)

    if nome in backup:
        backup.remove(nome)

    logs_filtrados = []

    for log in logs:
        if nome not in log:
            logs_filtrados.append(log)

    return {
        "usuarios": usuarios,
        "backup": backup,
        "logs": logs_filtrados
    }


print(excluir_usuario("joao"))