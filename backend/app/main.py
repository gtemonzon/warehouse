from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from .config import settings
from .database import Base, engine
from .routers import health, products, warehouses, kits, transactions

# ---------- App ----------
app = FastAPI(title="Warehouse API", version="0.1.0")

# Crear tablas si no existen (no altera las existentes)
Base.metadata.create_all(bind=engine)

# ---------- CORS para Producción ----------
# Obtener orígenes desde variable de entorno o usar valor por defecto
# ---------- CORS para Producción ----------
import os

cors_origins_str = os.getenv("CORS_ORIGINS", "*")
if cors_origins_str == "*":
    origins = ["*"]
else:
    origins = [origin.strip() for origin in cors_origins_str.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Routers ----------
app.include_router(health.router)
app.include_router(products.router)
app.include_router(warehouses.router)
app.include_router(kits.router)
app.include_router(transactions.router)

# ---------- Root ----------
@app.get("/")
def root():
    return {"ok": True, "message": "Warehouse API running 🚀"}

# ---------- Health check adicional para servicios cloud ----------
@app.get("/ping")
def ping():
    return {"status": "healthy"}