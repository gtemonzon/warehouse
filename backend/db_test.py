import mysql.connector
import os

def test_connection():
    try:
        # Usar las variables del .env (ajusta si hace falta)
        conn = mysql.connector.connect(
            host="127.0.0.1",
            port=3306,
            user="warehouse_user",
            password="12345678",
            database="warehouse"
        )

        cursor = conn.cursor()
        cursor.execute("SELECT DATABASE();")
        db_name = cursor.fetchone()
        print(f"✅ Conectado a la base de datos: {db_name[0]}")

        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        print("📦 Tablas disponibles:")
        for t in tables:
            print(f" - {t[0]}")

        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        print(f"❌ Error de conexión: {err}")

if __name__ == "__main__":
    test_connection()
