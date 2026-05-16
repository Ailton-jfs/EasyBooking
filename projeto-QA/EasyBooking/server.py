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

app = Flask(__name__)
app.secret_key = "easybooking-secret-2026"

DB_PATH = "easybooking.db"


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
    auth.registrar(_conn, "admin", "Admin123", role="admin")
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
                "SELECT role FROM usuarios WHERE nome = ?", (nome,)
            ).fetchone()
            session["usuario"] = nome
            session["role"] = row["role"]
            return redirect(url_for("dashboard"))
        flash(resultado, "erro")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if "usuario" in session:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        senha = request.form.get("senha", "").strip()
        if not nome or not senha:
            flash("Preencha todos os campos.", "erro")
        elif len(senha) < 6:
            flash("A senha deve ter ao menos 6 caracteres.", "erro")
        elif auth.registrar(get_db(), nome, senha):
            flash("Conta criada! Faça login.", "sucesso")
            return redirect(url_for("login"))
        else:
            flash("Nome de usuário já existe.", "erro")
    return render_template("register.html")


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
    hoje = datetime.today().strftime("%Y-%m-%d")
    proximos = [a for a in ativos if a["data"] >= hoje]
    proximo = proximos[0] if proximos else None

    return render_template(
        "dashboard.html",
        active="dashboard",
        agendamentos=ativos,
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
    return jsonify({"ocupados": ocupados})


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
