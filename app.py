import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Pega a URL do banco do Render
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
    mesas = request.form.get("table")

    print("Recebido:", nome, telefone, data, horario, pessoas, mesas)  # debug

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Verifica se o cliente já existe
        cur.execute("SELECT id_cliente, reservas FROM cliente WHERE telefone = %s;", (telefone,))
        cliente = cur.fetchone()

        if cliente:
            # Atualiza contagem de reservas
            id_cliente, reservas = cliente
            cur.execute("UPDATE cliente SET reservas = %s WHERE id_cliente = %s;", (reservas + 1, id_cliente))
            # Atualiza também os últimos dados de reserva
            cur.execute("""
                UPDATE cliente 
                SET data = %s, horario = %s, pessoas = %s, mesas = %s 
                WHERE id_cliente = %s;
            """, (data, horario, pessoas, mesas, id_cliente))
        else:
            # Insere novo cliente
            cur.execute("""
                INSERT INTO cliente (nome, telefone, reservas, data, horario, pessoas, mesas)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
            """, (nome, telefone, 1, data, horario, pessoas, mesas))

        conn.commit()
        cur.close()
        conn.close()

        # Redireciona de volta para a página inicial
        return redirect(url_for("index"))
    except Exception as e:
        return f"<h1>Erro ao salvar agendamento:</h1><p>{e}</p>"

# Listagem de clientes
@app.route("/clientes")
def listar_clientes():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id_cliente, nome, telefone, reservas, data, horario, pessoas, mesas
            FROM cliente
            ORDER BY id_cliente DESC;
        """)
        clientes = cur.fetchall()
        cur.close()
        conn.close()
        return render_template("clientes.html", clientes=clientes)
    except Exception as e:
        return f"<h1>Erro ao buscar clientes:</h1><p>{e}</p>"

# Inicializa o app localmente
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
