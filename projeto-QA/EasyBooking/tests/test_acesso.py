# CENÁRIOS 2 e 6 — CONTROLE DE ACESSO E PAINEL ADMIN
import pytest
from app.db import get_connection, init_db
from app.auth import registrar, acessar_painel_admin


@pytest.fixture
def conn():
    c = get_connection()
    init_db(c)
    registrar(c, "admin", "Admin123", role="admin")
    registrar(c, "joao", "Joao123", role="user")
    registrar(c, "visitante", "Visit123", role="guest")
    return c


def test_admin_acessa_painel(conn):
    assert acessar_painel_admin(conn, "admin") == "Acesso ao painel administrativo liberado"


def test_user_nao_acessa_painel(conn):
    assert acessar_painel_admin(conn, "joao") == "Acesso negado"


def test_guest_nao_acessa_painel(conn):
    assert acessar_painel_admin(conn, "visitante") == "Acesso negado"


def test_usuario_invalido_nao_acessa(conn):
    assert acessar_painel_admin(conn, "inexistente") == "Usuário inválido"
