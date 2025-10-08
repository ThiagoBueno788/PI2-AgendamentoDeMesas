import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# URL do banco do Render/Neon
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

# Página inicial (formulário)
@app.route("/")
def index():
    return render_template("index.html")

# Rota para salvar reserva
@app.route("/agendar", methods=["POST"])
def agendar():
    nome = request.form.get("name")
    telefone = request.form.get("phone")
    data = request.form.get("date")
    horario = request.form.get("time")
    pessoas = request.form.get("people")
    mesas = request.form.get("table")

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Verifica se o cliente já existe
        cur.execute("SELECT id_cliente FROM cliente WHERE telefone = %s;", (telefone,))
        cliente = cur.fetchone()

        if cliente:
            id_cliente = cliente[0]
        else:
            # Insere novo cliente
            cur.execute("INSERT INTO cliente (nome, telefone) VALUES (%s, %s) RETURNING id_cliente;", (nome, telefone))
            id_cliente = cur.fetchone()[0]

        # Insere a reserva vinculada ao cliente
        cur.execute("""
            INSERT INTO reserva (id_cliente, data, horario, pessoas, mesas)
            VALUES (%s, %s, %s, %s, %s);
        """, (id_cliente, data, horario, pessoas, mesas))

        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("index"))
    except Exception as e:
        return f"<h1>Erro ao salvar reserva:</h1><p>{e}</p>"

# Rota para listar clientes + reservas
@app.route("/clientes")
def listar_clientes():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT c.id_cliente, c.nome, c.telefone,
                   r.data, r.horario, r.pessoas, r.mesas
            FROM cliente c
            LEFT JOIN reserva r ON c.id_cliente = r.id_cliente
            ORDER BY r.data DESC NULLS LAST, r.horario DESC NULLS LAST;
        """)
        clientes = cur.fetchall()
        cur.close()
        conn.close()
        return render_template("clientes.html", clientes=clientes)
    except Exception as e:
        return f"<h1>Erro ao buscar clientes:</h1><p>{e}</p>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
