# backend/reset_data.py
from app.database import engine

# Orden importante: primero las tablas hijas (con foreign keys)
queries = [
    "SET FOREIGN_KEY_CHECKS = 0",  # Desactivar verificación temporal
    "TRUNCATE TABLE tab_product_transaction",
    "TRUNCATE TABLE tab_kit_composition",
    "TRUNCATE TABLE tab_kit",
    "TRUNCATE TABLE tab_warehouse",
    "TRUNCATE TABLE tab_products",
    "SET FOREIGN_KEY_CHECKS = 1",  # Reactivar verificación
]

with engine.connect() as conn:
    for q in queries:
        print(f"Ejecutando: {q}")
        conn.execute(q)
        conn.commit()
    print("✓ Todas las tablas han sido vaciadas")