# CENÁRIO 1 — LOGIN SEGURO
import bcrypt
import pytest
from app.db import get_connection, init_db
from app.auth import registrar, login


@pytest.fixture
def conn():
    c = get_connection()
    init_db(c)
    registrar(c, "admin", "SenhaForte123", role="admin")
    registrar(c, "joao", "OutraSenha456")
    return c


def test_login_correto(conn):
    assert login(conn, "admin", "SenhaForte123") == "Login realizado com sucesso"


def test_login_senha_errada(conn):
    assert login(conn, "admin", "senhaerrada") == "Usuário ou senha inválidos"


def test_login_usuario_inexistente(conn):
    assert login(conn, "fantasma", "qualquer") == "Usuário ou senha inválidos"


def test_bloqueio_apos_3_tentativas(conn):
    login(conn, "joao", "errado")
    login(conn, "joao", "errado")
    login(conn, "joao", "errado")
    assert login(conn, "joao", "OutraSenha456") == "Conta bloqueada temporariamente"


def test_senha_armazenada_como_hash(conn):
    row = conn.execute("SELECT senha_hash FROM usuarios WHERE nome = 'admin'").fetchone()
    assert row["senha_hash"] != b"SenhaForte123"
    assert bcrypt.checkpw(b"SenhaForte123", row["senha_hash"])
