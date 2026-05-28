# CENÁRIO 7 — PROTEÇÃO CONTRA SQL INJECTION
import pytest
from app.db import get_connection, init_db
from app.auth import registrar, login


@pytest.fixture
def conn():
    c = get_connection()
    init_db(c)
    registrar(c, "joao", "Joao123", "João Silva", "joao@easybooking.com")
    registrar(c, "maria", "Maria123", "Maria Souza", "maria@easybooking.com")
    return c


def test_busca_normal_retorna_usuario(conn):
    rows = conn.execute("SELECT * FROM usuarios WHERE nome = ?", ("joao",)).fetchall()
    assert len(rows) == 1


def test_injecao_or_true_nao_retorna_nada(conn):
    rows = conn.execute("SELECT * FROM usuarios WHERE nome = ?", ("' OR '1'='1",)).fetchall()
    assert len(rows) == 0


def test_injecao_comment_nao_retorna_nada(conn):
    rows = conn.execute("SELECT * FROM usuarios WHERE nome = ?", ("' OR 1=1--",)).fetchall()
    assert len(rows) == 0


def test_login_com_injecao_falha(conn):
    resultado = login(conn, "' OR '1'='1", "qualquer")
    assert resultado == "Usuário ou senha inválidos"
