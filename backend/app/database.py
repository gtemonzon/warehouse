# backend/app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# === SQLAlchemy (para endpoints que usen ORM) ===
DATABASE_URL = "mysql+mysqlconnector://warehouse_user:12345678@127.0.0.1:3306/warehouse"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Yield de sesión SQLAlchemy (úsalo con Depends en routers ORM)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# === Conector directo MySQL (para routers que usan SQL crudo) ===
# Así mantenemos compatibilidad con products/warehouses/transactions actuales.
import mysql.connector

def get_connection():
    """Conexión directa mysql.connector (cierra con context manager)."""
    return mysql.connector.connect(
        host="127.0.0.1",
        user="warehouse_user",
        password="12345678",
        database="warehouse",
        port=3306,
        autocommit=False,
    )
