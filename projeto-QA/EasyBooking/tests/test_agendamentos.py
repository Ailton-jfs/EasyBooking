# CENÁRIO 3 — VALIDAÇÃO DE AGENDAMENTO
import pytest
from app.db import get_connection, init_db
from app.agendamentos import criar, cancelar, listar, SERVICOS, HORARIOS


@pytest.fixture
def conn():
    c = get_connection()
    init_db(c)
    criar(c, "joao", "2026-06-01", "10:00", "Consulta Médica")
    criar(c, "maria", "2026-06-01", "14:00", "Reunião de Negócios")
    return c


def test_agendamento_valido(conn):
    resultado = criar(conn, "ana", "2026-06-01", "16:00", "Atendimento ao Cliente")
    assert "confirmado" in resultado


def test_horario_ja_ocupado(conn):
    assert criar(conn, "pedro", "2026-06-01", "10:00", "Consulta Médica") == "Erro: horário já ocupado"


def test_dados_incompletos_sem_usuario(conn):
    assert criar(conn, "", "2026-06-01", "09:00", "Consulta Médica") == "Erro: dados incompletos"


def test_dados_incompletos_sem_data(conn):
    assert criar(conn, "carlos", "", "09:00", "Consulta Médica") == "Erro: dados incompletos"


def test_dados_incompletos_sem_servico(conn):
    assert criar(conn, "carlos", "2026-06-01", "09:00", "") == "Erro: dados incompletos"


def test_formato_data_invalido(conn):
    assert criar(conn, "carlos", "01/06/2026", "09:00", "Consulta Médica") == "Erro: data inválida"


def test_data_no_passado(conn):
    assert criar(conn, "lucas", "2020-01-01", "08:00", "Consulta Médica") == "Erro: não é possível agendar em datas passadas"


def test_horario_invalido(conn):
    assert criar(conn, "lucas", "2026-06-01", "07:30", "Consulta Médica") == "Erro: horário inválido"


def test_servico_invalido(conn):
    assert criar(conn, "lucas", "2026-06-01", "09:00", "Serviço Inventado") == "Erro: serviço inválido"


def test_cancelar_agendamento_existente(conn):
    ag_id = conn.execute("SELECT id FROM agendamentos WHERE usuario = 'joao'").fetchone()["id"]
    assert cancelar(conn, ag_id, "joao") == "Agendamento cancelado com sucesso"


def test_cancelar_agendamento_inexistente(conn):
    assert cancelar(conn, 9999, "joao") == "Erro: agendamento não encontrado"


def test_cancelar_ja_cancelado(conn):
    ag_id = conn.execute("SELECT id FROM agendamentos WHERE usuario = 'joao'").fetchone()["id"]
    cancelar(conn, ag_id, "joao")
    assert cancelar(conn, ag_id, "joao") == "Erro: agendamento já cancelado"


def test_listar_agendamentos_do_usuario(conn):
    lista = listar(conn, "joao")
    assert len(lista) == 1
    assert lista[0]["hora"] == "10:00"
    assert lista[0]["servico"] == "Consulta Médica"
