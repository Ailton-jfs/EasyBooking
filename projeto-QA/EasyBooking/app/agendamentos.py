from datetime import datetime, date

FORMATO_DATA = "%Y-%m-%d"

HORARIO_MINIMO = "08:00"
HORARIO_MAXIMO = "17:00"

SERVICOS = [
    "Consulta Médica",
    "Reunião de Negócios",
    "Atendimento ao Cliente",
    "Avaliação Técnica",
    "Outros",
]

HORARIOS = [
    "08:00", "09:00", "10:00", "11:00",
    "13:00", "14:00", "15:00", "16:00", "17:00",
]


def validar_hora(hora_str):
    try:
        hora = datetime.strptime(hora_str, "%H:%M").time()
    except ValueError:
        return False

    inicio = datetime.strptime(HORARIO_MINIMO, "%H:%M").time()
    fim = datetime.strptime(HORARIO_MAXIMO, "%H:%M").time()
    return inicio <= hora <= fim


def criar(conn, usuario, data_str, hora, servico, observacoes=""):
    if not all([usuario, data_str, hora, servico]):
        return "Erro: dados incompletos"

    try:
        data = datetime.strptime(data_str, FORMATO_DATA).date()
    except ValueError:
        return "Erro: data inválida"

    if data < date.today():
        return "Erro: não é possível agendar em datas passadas"

    if hora not in HORARIOS and not validar_hora(hora):
        return "Erro: horário inválido"

    if servico not in SERVICOS:
        return "Erro: serviço inválido"

    ocupado = conn.execute(
        "SELECT id FROM agendamentos WHERE data = ? AND hora = ? AND status = 'ativo'",
        (data_str, hora),
    ).fetchone()

    if ocupado:
        return "Erro: horário já ocupado"

    conn.execute(
        "INSERT INTO agendamentos (usuario, data, hora, servico, observacoes) VALUES (?, ?, ?, ?, ?)",
        (usuario, data_str, hora, servico, observacoes),
    )
    conn.commit()
    return f"Agendamento confirmado: {servico} em {data_str} às {hora}"


def cancelar(conn, agendamento_id, usuario):
    row = conn.execute(
        "SELECT * FROM agendamentos WHERE id = ? AND usuario = ?",
        (agendamento_id, usuario),
    ).fetchone()

    if not row:
        return "Erro: agendamento não encontrado"

    if row["status"] == "cancelado":
        return "Erro: agendamento já cancelado"

    conn.execute(
        "UPDATE agendamentos SET status = 'cancelado' WHERE id = ?",
        (agendamento_id,),
    )
    conn.commit()
    return "Agendamento cancelado com sucesso"


def listar(conn, usuario=None):
    if usuario:
        rows = conn.execute(
            "SELECT * FROM agendamentos WHERE usuario = ? AND status = 'ativo' ORDER BY data, hora",
            (usuario,),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM agendamentos WHERE status = 'ativo' ORDER BY data, hora"
        ).fetchall()
    return [dict(r) for r in rows]


def historico(conn, usuario):
    rows = conn.execute(
        "SELECT * FROM agendamentos WHERE usuario = ? ORDER BY data DESC, hora DESC",
        (usuario,),
    ).fetchall()
    return [dict(r) for r in rows]


def slots_ocupados(conn, data_str):
    rows = conn.execute(
        "SELECT hora FROM agendamentos WHERE data = ? AND status = 'ativo'",
        (data_str,),
    ).fetchall()
    return [r["hora"] for r in rows]


def horarios_disponiveis(conn, data_str):
    ocupados = slots_ocupados(conn, data_str)
    return [hora for hora in HORARIOS if hora not in ocupados]


def proximo_horario_livre(conn, data_str):
    disponiveis = horarios_disponiveis(conn, data_str)
    return disponiveis[0] if disponiveis else None


def proximo_dia_com_slot(conn, start_date_str, days_window=30):
    """Procura o próximo dia (após start_date_str) dentro de `days_window`
    que tenha pelo menos um horário disponível. Retorna tupla
    (data_str, hora) ou None se não encontrar.
    """
    from datetime import timedelta
    try:
        start_date = datetime.strptime(start_date_str, FORMATO_DATA).date()
    except Exception:
        return None

    for i in range(1, days_window + 1):
        d = start_date + timedelta(days=i)
        d_str = d.strftime(FORMATO_DATA)
        disponiveis = horarios_disponiveis(conn, d_str)
        if disponiveis:
            return (d_str, disponiveis[0])
    return None
