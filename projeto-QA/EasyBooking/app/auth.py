import bcrypt

MAX_TENTATIVAS = 3


def registrar(conn, nome, senha, role="user"):
    senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt())
    try:
        conn.execute(
            "INSERT INTO usuarios (nome, senha_hash, role) VALUES (?, ?, ?)",
            (nome, senha_hash, role),
        )
        conn.commit()
        return True
    except Exception:
        return False


def login(conn, nome, senha):
    row = conn.execute("SELECT * FROM usuarios WHERE nome = ?", (nome,)).fetchone()

    if not row:
        return "Usuário ou senha inválidos"

    if row["bloqueado"] or row["tentativas"] >= MAX_TENTATIVAS:
        return "Conta bloqueada temporariamente"

    if bcrypt.checkpw(senha.encode(), row["senha_hash"]):
        conn.execute("UPDATE usuarios SET tentativas = 0 WHERE nome = ?", (nome,))
        conn.commit()
        return "Login realizado com sucesso"

    conn.execute(
        "UPDATE usuarios SET tentativas = tentativas + 1 WHERE nome = ?", (nome,)
    )
    conn.commit()
    return "Usuário ou senha inválidos"


def acessar_painel_admin(conn, nome):
    row = conn.execute("SELECT role FROM usuarios WHERE nome = ?", (nome,)).fetchone()
    if not row:
        return "Usuário inválido"
    if row["role"] != "admin":
        return "Acesso negado"
    return "Acesso ao painel administrativo liberado"


def excluir_usuario(conn, nome):
    result = conn.execute("DELETE FROM usuarios WHERE nome = ?", (nome,))
    conn.commit()
    return result.rowcount > 0
