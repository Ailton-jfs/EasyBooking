# CENÁRIO 4 — DADOS DE SAÚDE


usuarios_autorizados = ["medico", "enfermeiro"]

def mostrar_exame(usuario, nome, glicose):

    if usuario not in usuarios_autorizados:
        return "Acesso negado"

    return f"Paciente: {nome}, Glicose: {glicose}"


print(mostrar_exame("medico", "Maria", 180))
print(mostrar_exame("visitante", "Maria", 180))