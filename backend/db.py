import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "warehouse_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "warehouse_pass")
DB_NAME = os.getenv("DB_NAME", "warehouse")
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=3600)
