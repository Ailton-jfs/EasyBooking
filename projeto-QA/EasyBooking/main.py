import sys
sys.stdout.reconfigure(encoding="utf-8")

from app.db import get_connection, init_db
from app import auth, agendamentos

DB_PATH = "easybooking.db"


def menu_principal():
    print("\n=== EasyBooking ===")
    print("1. Login")
    print("2. Registrar")
    print("0. Sair")
    return input("Escolha: ").strip()


def menu_usuario(nome, role):
    print(f"\n=== Menu ({nome}) ===")
    print("1. Criar agendamento")
    print("2. Ver meus agendamentos")
    print("3. Cancelar agendamento")
    if role == "admin":
        print("4. Painel admin — ver todos os agendamentos")
    print("0. Logout")
    return input("Escolha: ").strip()


def main():
    conn = get_connection(DB_PATH)
    init_db(conn)

    # cria admin padrão na primeira execução
    auth.registrar(conn, "admin", "Admin123", "Administrador", "admin@easybooking.com", role="admin")

    usuario_logado = None
    role_logado = None

    while True:
        if not usuario_logado:
            opcao = menu_principal()

            if opcao == "0":
                print("Até logo!")
                break

            elif opcao == "1":
                nome = input("Usuário: ").strip()
                senha = input("Senha: ").strip()
                resultado = auth.login(conn, nome, senha)
                print(resultado)
                if resultado == "Login realizado com sucesso":
                    row = conn.execute(
                        "SELECT role FROM usuarios WHERE nome = ?", (nome,)
                    ).fetchone()
                    usuario_logado = nome
                    role_logado = row["role"]

            elif opcao == "2":
                nome = input("Usuário: ").strip()
                nome_completo = input("Nome completo: ").strip()
                email = input("E-mail: ").strip()
                senha = input("Senha: ").strip()
                if auth.registrar(conn, nome, senha, nome_completo, email):
                    print("Usuário registrado com sucesso!")
                else:
                    print("Erro: nome de usuário já existe.")

        else:
            opcao = menu_usuario(usuario_logado, role_logado)

            if opcao == "0":
                usuario_logado = None
                role_logado = None
                print("Logout realizado.")

            elif opcao == "1":
                horario = input("Horário (AAAA-MM-DD HH:MM): ").strip()
                print(agendamentos.criar(conn, usuario_logado, horario))

            elif opcao == "2":
                lista = agendamentos.listar(conn, usuario_logado)
                if not lista:
                    print("Nenhum agendamento ativo.")
                for ag in lista:
                    print(f"  [{ag['id']}] {ag['horario']}")

            elif opcao == "3":
                ag_id = input("ID do agendamento: ").strip()
                if ag_id.isdigit():
                    print(agendamentos.cancelar(conn, int(ag_id), usuario_logado))
                else:
                    print("ID inválido.")

            elif opcao == "4" and role_logado == "admin":
                print(auth.acessar_painel_admin(conn, usuario_logado))
                todos = agendamentos.listar(conn)
                if not todos:
                    print("Nenhum agendamento ativo no sistema.")
                for ag in todos:
                    print(f"  [{ag['id']}] {ag['usuario']} — {ag['horario']}")


if __name__ == "__main__":
    main()
