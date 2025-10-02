import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

# Página inicial (formulário)
@app.route("/")
def index():
    return render_template("index.html")

# Salvar agendamento no banco
@app.route("/agendar", methods=["POST"])
def agendar():
    nome = request.form.get("name")
    telefone = request.form.get("phone")
    data = request.form.get("date")
    horario = request.form.get("time")
    pessoas = request.form.get("people")
    mesa = request.form.get("table")

    print("Recebido:", nome, telefone)  # 👈 debug aqui

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # insere cliente (ou atualiza reservas)
        cur.execute("SELECT id_cliente, reservas FROM cliente WHERE telefone = %s;", (telefone,))
        cliente = cur.fetchone()

        if cliente:
            id_cliente, reservas = cliente
            cur.execute("UPDATE cliente SET reservas = %s WHERE id_cliente = %s;", (reservas + 1, id_cliente))
        else:
            cur.execute(
                "INSERT INTO cliente (nome, telefone, reservas) VALUES (%s, %s, %s);",
                (nome, telefone, 1)
            )

        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("index"))
    except Exception as e:
        return f"<h1>Erro ao salvar agendamento:</h1><p>{e}</p>"

# Listagem de clientes
@app.route("/clientes")
def listar_clientes():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id_cliente, nome, telefone, reservas FROM cliente ORDER BY reservas DESC;")
        clientes = cur.fetchall()
        cur.close()
        conn.close()
        return render_template("clientes.html", clientes=clientes)
    except Exception as e:
        return f"<h1>Erro ao buscar clientes:</h1><p>{e}</p>"
