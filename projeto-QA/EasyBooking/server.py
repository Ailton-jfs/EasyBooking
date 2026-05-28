import os
import re
import sys
sys.stdout.reconfigure(encoding="utf-8")

from datetime import datetime
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, g, flash, jsonify,
)
from app.db import get_connection, init_db
from app import auth, agendamentos
from app.agendamentos import SERVICOS, HORARIOS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(
    __name__,
    static_folder=os.path.join(BASE_DIR, "static"),
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_url_path="/static",
)
app.secret_key = "easybooking-secret-2026"

DB_PATH = "easybooking.db"

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validar_email(email):
    return bool(EMAIL_REGEX.match(email))


def validar_nome_completo(nome_completo):
    return bool(nome_completo and len(nome_completo.split()) >= 2)


def validar_senha(senha):
    return validar_senha_erro(senha) is None


def sequencia_crescente(valor):
    return all(ord(valor[i + 1]) == ord(valor[i]) + 1 for i in range(len(valor) - 1))


def sequencia_decrescente(valor):
    return all(ord(valor[i + 1]) == ord(valor[i]) - 1 for i in range(len(valor) - 1))


def senha_tem_sequencia(senha):
    for grupo in re.findall(r"\d+|[A-Za-z]+", senha):
        if len(grupo) < 3:
            continue
        valor = grupo.lower() if grupo.isalpha() else grupo
        if sequencia_crescente(valor) or sequencia_decrescente(valor):
            return True
    return False


def validar_senha_erro(senha):
    if len(senha) < 8:
        return "A senha deve ter ao menos 8 caracteres."
    if not re.search(r"[A-Z]", senha):
        return "A senha deve conter pelo menos uma letra maiúscula."
    if not re.search(r"[a-z]", senha):
        return "A senha deve conter pelo menos uma letra minúscula."
    if not re.search(r"\d", senha):
        return "A senha deve conter pelo menos um número."
    if senha_tem_sequencia(senha):
        return "A senha não pode conter sequências como 1234 ou abcd."
    if not re.search(r"[!@#$%^&*()_+\-=[\]{};':\"\\|,.<>/?]", senha):
        return "A senha deve conter pelo menos um símbolo especial."
    return None


def get_db():
    if "db" not in g:
        g.db = get_connection(DB_PATH)
    return g.db


@app.teardown_appcontext
def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


@app.template_filter("data_br")
def data_br(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").strftime("%d/%m/%Y")
    except Exception:
        return value


@app.template_filter("dia_semana")
def dia_semana(value):
    dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
    try:
        d = datetime.strptime(value, "%Y-%m-%d")
        return dias[d.weekday()]
    except Exception:
        return ""


with app.app_context():
    _conn = get_connection(DB_PATH)
    init_db(_conn)
    auth.registrar(_conn, "admin", "Admin123", "Administrador", "admin@easybooking.com", role="admin")
    _conn.close()


@app.route("/")
def index():
    if "usuario" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if "usuario" in session:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        senha = request.form.get("senha", "").strip()
        resultado = auth.login(get_db(), nome, senha)
        if resultado == "Login realizado com sucesso":
            row = get_db().execute(
                "SELECT role, nome_completo, email FROM usuarios WHERE nome = ?", (nome,)
            ).fetchone()
            session["usuario"] = nome
            session["role"] = row["role"]
            session["nome_completo"] = row["nome_completo"] or nome
            session["email"] = row["email"]
            return redirect(url_for("dashboard"))
        flash(resultado, "erro")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if "usuario" in session:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        nome_completo = request.form.get("nome_completo", "").strip()
        email = request.form.get("email", "").strip()
        senha = request.form.get("senha", "").strip()
        confirm = request.form.get("confirm", "").strip()
        if not nome or not senha:
            flash("Preencha todos os campos.", "erro")
        elif not nome_completo or not email or not confirm:
            flash("Preencha todos os campos.", "erro")
        elif not validar_nome_completo(nome_completo):
            flash("Informe seu nome completo.", "erro")
        elif not validar_email(email):
            flash("Informe um e-mail válido.", "erro")
        elif senha != confirm:
            flash("As senhas não conferem.", "erro")
        else:
            erro_senha = validar_senha_erro(senha)
            if erro_senha:
                flash(erro_senha, "erro")
            else:
                resultado = auth.registrar(get_db(), nome, senha, nome_completo, email)
                if resultado == True:
                    flash("Conta criada! Faça login.", "sucesso")
                    return redirect(url_for("login"))
                elif resultado == "nome":
                    flash("Nome de usuário já existe.", "erro")
                elif resultado == "email":
                    flash("E-mail já cadastrado.", "erro")
                else:
                    flash("Erro ao criar conta.", "erro")

    return render_template("register.html")


@app.route("/perfil", methods=["GET", "POST"])
def perfil():
    if "usuario" not in session:
        return redirect(url_for("login"))

    usuario = session["usuario"]
    if request.method == "POST":
        nome_completo = request.form.get("nome_completo", "").strip()
        email = request.form.get("email", "").strip()
        senha = request.form.get("senha", "").strip()
        confirm = request.form.get("confirm", "").strip()

        if not nome_completo or not email:
            flash("Preencha nome completo e e-mail.", "erro")
        elif not validar_nome_completo(nome_completo):
            flash("Informe seu nome completo.", "erro")
        elif not validar_email(email):
            flash("Informe um e-mail válido.", "erro")
        elif senha or confirm:
            if senha != confirm:
                flash("As senhas não conferem.", "erro")
            else:
                erro_senha = validar_senha_erro(senha)
                if erro_senha:
                    flash(erro_senha, "erro")
                else:
                    resultado = auth.atualizar_usuario(
                        get_db(), usuario, nome_completo, email, senha
                    )
                    if resultado == True:
                        session["nome_completo"] = nome_completo
                        session["email"] = email
                        flash("Perfil atualizado.", "sucesso")
                        return redirect(url_for("perfil"))
                    elif resultado == "email":
                        flash("Outro usuário já está usando esse e-mail.", "erro")
                    else:
                        flash("Erro ao atualizar perfil.", "erro")
        else:
            resultado = auth.atualizar_usuario(
                get_db(), usuario, nome_completo, email
            )
            if resultado == True:
                session["nome_completo"] = nome_completo
                session["email"] = email
                flash("Perfil atualizado.", "sucesso")
                return redirect(url_for("perfil"))
            elif resultado == "email":
                flash("Outro usuário já está usando esse e-mail.", "erro")
            else:
                flash("Erro ao atualizar perfil.", "erro")

    user = auth.obter_usuario(get_db(), usuario)
    return render_template("perfil.html", active="perfil", user=user)


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "usuario" not in session:
        return redirect(url_for("login"))

    usuario = session["usuario"]

    if request.method == "POST":
        data_str = request.form.get("data", "").strip()
        hora = request.form.get("hora", "").strip()
        servico = request.form.get("servico", "").strip()
        obs = request.form.get("observacoes", "").strip()
        resultado = agendamentos.criar(get_db(), usuario, data_str, hora, servico, obs)
        categoria = "sucesso" if not resultado.startswith("Erro") else "erro"
        flash(resultado, categoria)
        return redirect(url_for("dashboard"))

    ativos = agendamentos.listar(get_db(), usuario)
    hist = agendamentos.historico(get_db(), usuario)
    historico = hist[:5]
    hoje = datetime.today().strftime("%Y-%m-%d")
    proximos = [a for a in ativos if a["data"] >= hoje]
    proximo = proximos[0] if proximos else None

    return render_template(
        "dashboard.html",
        active="dashboard",
        agendamentos=ativos,
        historico=historico,
        total_historico=len(hist),
        proximo=proximo,
        servicos=SERVICOS,
        horarios=HORARIOS,
        hoje=hoje,
    )


@app.route("/slots")
def slots():
    if "usuario" not in session:
        return jsonify({"erro": "não autorizado"}), 401
    data_str = request.args.get("data", "")
    ocupados = agendamentos.slots_ocupados(get_db(), data_str)
    proximo_hora = agendamentos.proximo_horario_livre(get_db(), data_str)
    proximo_data_hora = None
    if not proximo_hora:
        next_pair = agendamentos.proximo_dia_com_slot(get_db(), data_str)
        if next_pair:
            proximo_data_hora = {"data": next_pair[0], "hora": next_pair[1]}

    return jsonify({
        "ocupados": ocupados,
        "proximo": proximo_hora,
        "proximo_data": proximo_data_hora,
    })


@app.route("/cancelar/<int:ag_id>", methods=["POST"])
def cancelar(ag_id):
    if "usuario" not in session:
        return redirect(url_for("login"))
    resultado = agendamentos.cancelar(get_db(), ag_id, session["usuario"])
    categoria = "sucesso" if not resultado.startswith("Erro") else "erro"
    flash(resultado, categoria)
    return redirect(url_for("dashboard"))


@app.route("/admin")
def admin():
    if session.get("role") != "admin":
        flash("Acesso negado.", "erro")
        return redirect(url_for("dashboard"))

    todos = agendamentos.listar(get_db())
    usuarios = [
        dict(u)
        for u in get_db().execute("SELECT nome, role FROM usuarios ORDER BY role, nome").fetchall()
    ]
    servico_popular = get_db().execute("""
        SELECT servico, COUNT(*) as total
        FROM agendamentos WHERE status = 'ativo'
        GROUP BY servico ORDER BY total DESC LIMIT 1
    """).fetchone()

    total_usuarios = get_db().execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]

    return render_template(
        "admin.html",
        active="admin",
        agendamentos=todos,
        usuarios=usuarios,
        servico_popular=dict(servico_popular) if servico_popular else None,
        total_usuarios=total_usuarios,
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
