import os
import psycopg2
from flask import Flask, render_template

app = Flask(__name__)

# Pega a URL do banco das variáveis de ambiente (Render → Environment Variables)
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

@app.route("/")
def index():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT NOW();")
        data = cur.fetchone()
        cur.close()
        conn.close()
        # Renderiza o index.html e passa a data do banco
        return render_template("index.html", data=data[0])
    except Exception as e:
        # Mostra erro na tela se não conseguir conectar
        return f"<h1>Erro ao conectar ao banco:</h1><p>{e}</p>"