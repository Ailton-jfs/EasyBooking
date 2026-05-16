from datetime import datetime, date

FORMATO_DATA = "%Y-%m-%d"

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


def criar(conn, usuario, data_str, hora, servico, observacoes=""):
    if not all([usuario, data_str, hora, servico]):
        return "Erro: dados incompletos"

    try:
        data = datetime.strptime(data_str, FORMATO_DATA).date()
    except ValueError:
        return "Erro: data inválida"

    if data < date.today():
        return "Erro: não é possível agendar em datas passadas"

    if hora not in HORARIOS:
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
