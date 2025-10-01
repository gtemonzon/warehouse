from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool
from .config import settings

engine: Engine = create_engine(
    settings.url,
    poolclass=QueuePool,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=5,
    future=True,
)

def db_ping() -> bool:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return True

def on_hand(product_id: int) -> int:
    """
    Intenta leer de la vista vw_inventory; si no existe, usa la función fn_on_hand.
    """
    with engine.connect() as conn:
        try:
            row = conn.execute(
                text("SELECT on_hand FROM vw_inventory WHERE id_product = :pid"),
                {"pid": product_id},
            ).first()
            if row and row[0] is not None:
                return int(row[0])
        except Exception:
            # Si la vista no existe, caemos a la función
            pass

        row = conn.execute(
            text("SELECT fn_on_hand(:pid) AS on_hand"),
            {"pid": product_id},
        ).first()
        return int(row[0] if row and row[0] is not None else 0)
