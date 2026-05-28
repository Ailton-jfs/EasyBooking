# CENÁRIO 1 — LOGIN SEGURO
import bcrypt
import pytest
from app.db import get_connection, init_db
from app.auth import registrar, login
from server import validar_senha_erro


@pytest.fixture
def conn():
    c = get_connection()
    init_db(c)
    registrar(c, "admin", "SenhaForte123", "Admin Completo", "admin@easybooking.com", role="admin")
    registrar(c, "joao", "OutraSenha456", "João Silva", "joao@easybooking.com")
    return c


def test_login_correto(conn):
    assert login(conn, "admin", "SenhaForte123") == "Login realizado com sucesso"


def test_login_senha_errada(conn):
    assert login(conn, "admin", "senhaerrada") == "Usuário ou senha inválidos"


def test_login_usuario_inexistente(conn):
    assert login(conn, "fantasma", "qualquer") == "Usuário ou senha inválidos"


def test_registro_email_duplicado(conn):
    resultado = registrar(
        conn,
        "maria",
        "SenhaNova123!",
        "Maria Souza",
        "joao@easybooking.com",
    )
    assert resultado == "email"


def test_bloqueio_apos_3_tentativas(conn):
    login(conn, "joao", "errado")
    login(conn, "joao", "errado")
    login(conn, "joao", "errado")
    assert login(conn, "joao", "OutraSenha456") == "Conta bloqueada temporariamente"


def test_senha_armazenada_como_hash(conn):
    row = conn.execute("SELECT senha_hash FROM usuarios WHERE nome = 'admin'").fetchone()
    assert row["senha_hash"] != b"SenhaForte123"
    assert bcrypt.checkpw(b"SenhaForte123", row["senha_hash"])


def test_senha_rejeita_sequencia_numerica_ou_alfabetica():
    assert validar_senha_erro("Abc!1234") == "A senha não pode conter sequências como 1234 ou abcd."
    assert validar_senha_erro("Abc!9876") == "A senha não pode conter sequências como 1234 ou abcd."
    assert validar_senha_erro("Abc1!abcd") == "A senha não pode conter sequências como 1234 ou abcd."
    assert validar_senha_erro("Abc1!dcba") == "A senha não pode conter sequências como 1234 ou abcd."
    assert validar_senha_erro("QwE!1357") is None
