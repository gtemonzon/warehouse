from fastapi import APIRouter
from ..db import db_ping

router = APIRouter(prefix="/health", tags=["health"])

@router.get("")
def health():
    return {"ok": True}

@router.get("/db")
def health_db():
    db_ping()
    return {"db": "ok"}
