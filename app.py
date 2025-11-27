from flask import Flask, render_template, request
import psycopg2
from dotenv import load_dotenv
import os

# Cargar variables del archivo .env
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

app = Flask(__name__)

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

@app.route("/", methods=["GET", "POST"])
def search():
    query = request.form.get("q", "").strip()
    results = []

    if query:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                like_pattern = f"%{query}%"

                cur.execute("""
                    SELECT codigo, nombre, precio
                    FROM productos
                    WHERE UPPER(nombre) LIKE UPPER(%s)
                       OR UPPER(codigo) LIKE UPPER(%s)
                    ORDER BY nombre
                """, (like_pattern, like_pattern))

                for codigo, nombre, precio in cur.fetchall():
                    results.append({
                        "codigo": codigo,
                        "nombre": nombre,
                        "precio": float(precio)
                    })
        finally:
            conn.close()

    return render_template("search.html", query=query, results=results)

if __name__ == "__main__":
    # host=0.0.0.0 para que otros dispositivos de la red puedan entrar
    app.run(host="0.0.0.0", port=5000, debug=True)
