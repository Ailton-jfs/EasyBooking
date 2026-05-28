import bcrypt

MAX_TENTATIVAS = 3


def registrar(conn, nome, senha, nome_completo, email, role="user"):
    if conn.execute("SELECT 1 FROM usuarios WHERE nome = ?", (nome,)).fetchone():
        return "nome"
    if email and conn.execute("SELECT 1 FROM usuarios WHERE email = ?", (email,)).fetchone():
        return "email"

    senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt())
    try:
        conn.execute(
            "INSERT INTO usuarios (nome, nome_completo, email, senha_hash, role) VALUES (?, ?, ?, ?, ?)",
            (nome, nome_completo, email, senha_hash, role),
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


def obter_usuario(conn, nome):
    return conn.execute(
        "SELECT nome, nome_completo, email, role FROM usuarios WHERE nome = ?", (nome,)
    ).fetchone()


def atualizar_usuario(conn, nome, nome_completo, email, senha=None):
    existing = conn.execute(
        "SELECT nome FROM usuarios WHERE email = ? AND nome != ?", (email, nome)
    ).fetchone()
    if existing:
        return "email"

    if senha:
        senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt())
        conn.execute(
            "UPDATE usuarios SET nome_completo = ?, email = ?, senha_hash = ? WHERE nome = ?",
            (nome_completo, email, senha_hash, nome),
        )
    else:
        conn.execute(
            "UPDATE usuarios SET nome_completo = ?, email = ? WHERE nome = ?",
            (nome_completo, email, nome),
        )
    conn.commit()
    return True
