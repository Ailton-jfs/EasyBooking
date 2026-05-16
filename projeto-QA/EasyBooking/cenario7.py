# =========================================
# CENÁRIO 7 — SQL INJECTION
# =========================================

import sqlite3

# banco em memória
conexao = sqlite3.connect(":memory:")
cursor = conexao.cursor()

cursor.execute("""
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY,
    nome TEXT
)
""")

cursor.execute("INSERT INTO usuarios (nome) VALUES (?)", ("joao",))
cursor.execute("INSERT INTO usuarios (nome) VALUES (?)", ("maria",))

conexao.commit()

def buscar_usuario(nome):

    # query parametrizada
    query = "SELECT * FROM usuarios WHERE nome = ?"

    cursor.execute(query, (nome,))

    resultado = cursor.fetchall()

    return resultado


print(buscar_usuario("joao"))

# tentativa de SQL Injection
print(buscar_usuario("' OR '1'='1"))

