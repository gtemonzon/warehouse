# backend/app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Obtener URL de la base de datos desde variable de entorno
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/warehouse")

# Crear engine de SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Yield de sesión SQLAlchemy (úsalo con Depends en routers ORM)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()