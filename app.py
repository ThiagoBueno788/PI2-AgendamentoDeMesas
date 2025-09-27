import os
import psycopg2
from flask import Flask, render_template

app = Flask(__name__)

# URL do banco (vai vir das variáveis de ambiente no Render)
DATABASE_URL = os.environ.get("DATABASE_URL")

# Conectar ao Neon (com sslmode)
def get_connection():
    return psycopg2.connect(DATABASE_URL, sslmode="require")

@app.route("/")
def home():
    # Exemplo de query simples
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT NOW();")  # só para testar
        result = cur.fetchone()
        cur.close()
        conn.close()
        return render_template("index.html", data=result[0])
    except Exception as e:
        return f"Erro ao conectar ao banco: {e}"