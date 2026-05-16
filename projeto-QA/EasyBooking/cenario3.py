# CENÁRIO 3 — VALIDAÇÃO DE AGENDAMENTO

from datetime import datetime

agendamentos = [
    {"usuario": "joao", "horario": "2026-06-01 10:00"},
    {"usuario": "maria", "horario": "2026-06-01 14:00"},
]

def agendar(usuario, horario_str):
    if not usuario or not horario_str:
        return "Erro: dados incompletos"

    try:
        horario = datetime.strptime(horario_str, "%Y-%m-%d %H:%M")
    except ValueError:
        return "Erro: data ou hora inválida"

    if horario < datetime.now():
        return "Erro: não é possível agendar em datas passadas"

    for ag in agendamentos:
        if ag["horario"] == horario_str:
            return "Erro: horário já ocupado"

    agendamentos.append({"usuario": usuario, "horario": horario_str})
    return f"Agendamento confirmado para {usuario} às {horario_str}"


# agendamento válido
print(agendar("ana", "2026-06-01 16:00"))

# horário já ocupado
print(agendar("pedro", "2026-06-01 10:00"))

# dados incompletos
print(agendar("", "2026-06-01 09:00"))

# data inválida
print(agendar("carlos", "01/06/2026 09:00"))

# data no passado
print(agendar("lucas", "2020-01-01 08:00"))
