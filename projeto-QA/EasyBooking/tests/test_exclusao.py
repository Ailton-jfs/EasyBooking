# CENÁRIO 5 — EXCLUSÃO DE USUÁRIO
import pytest
from app.db import get_connection, init_db
from app.auth import registrar, excluir_usuario


@pytest.fixture
def conn():
    c = get_connection()
    init_db(c)
    registrar(c, "joao", "Joao123", "João Silva", "joao@easybooking.com")
    registrar(c, "maria", "Maria123", "Maria Silva", "maria@easybooking.com")
    registrar(c, "ana", "Ana123", "Ana Souza", "ana@easybooking.com")
    return c


def test_excluir_usuario_existente(conn):
    assert excluir_usuario(conn, "joao") is True


def test_usuario_excluido_nao_existe_mais(conn):
    excluir_usuario(conn, "joao")
    row = conn.execute("SELECT * FROM usuarios WHERE nome = 'joao'").fetchone()
    assert row is None


def test_excluir_usuario_inexistente(conn):
    assert excluir_usuario(conn, "fantasma") is False


def test_outros_usuarios_nao_sao_afetados(conn):
    excluir_usuario(conn, "joao")
    assert conn.execute("SELECT * FROM usuarios WHERE nome = 'maria'").fetchone() is not None
    assert conn.execute("SELECT * FROM usuarios WHERE nome = 'ana'").fetchone() is not None
