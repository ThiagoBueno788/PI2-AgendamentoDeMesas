import os
import psycopg2
from flask import Flask

# Cria a aplicação Flask
app = Flask(__name__)

# Pega a variável de ambiente do Render (URL do banco)
DATABASE_URL = os.environ.get("DATABASE_URL")

@app.route("/")
def home():
    try:
        # Testa conexão com o banco
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("SELECT version();")
        versao = cur.fetchone()
        cur.close()
        conn.close()
        return f"<h1>Conexão OK!</h1><p>PostgreSQL versão: {versao}</p>"
    except Exception as e:
        return f"<h1>Erro na conexão com o banco</h1><p>{e}</p>"

# Só roda isso em modo local (no Render o gunicorn cuida do server)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
