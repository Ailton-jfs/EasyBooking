import sqlite3


def get_connection(db_path=":memory:"):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn):
    # migração: se a tabela antiga não tem a coluna 'servico', recria
    try:
        conn.execute("SELECT servico FROM agendamentos LIMIT 1")
    except sqlite3.OperationalError:
        conn.execute("DROP TABLE IF EXISTS agendamentos")
        conn.commit()

    conn.executescript("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE NOT NULL,
            nome_completo TEXT NOT NULL DEFAULT '',
            email TEXT UNIQUE NOT NULL DEFAULT '',
            senha_hash BLOB NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            tentativas INTEGER NOT NULL DEFAULT 0,
            bloqueado INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS agendamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL,
            data TEXT NOT NULL,
            hora TEXT NOT NULL,
            servico TEXT NOT NULL,
            observacoes TEXT DEFAULT '',
            status TEXT NOT NULL DEFAULT 'ativo',
            criado_em TEXT DEFAULT (datetime('now', 'localtime'))
        );
    """)
    conn.commit()

    columns = [row[1] for row in conn.execute("PRAGMA table_info(usuarios)").fetchall()]
    if "nome_completo" not in columns:
        conn.execute("ALTER TABLE usuarios ADD COLUMN nome_completo TEXT NOT NULL DEFAULT ''")
    if "email" not in columns:
        conn.execute("ALTER TABLE usuarios ADD COLUMN email TEXT NOT NULL DEFAULT ''")
    conn.commit()
