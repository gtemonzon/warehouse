from fastapi import APIRouter, HTTPException
from ..db import on_hand

router = APIRouter(prefix="/inventory", tags=["inventory"])

@router.get("/{product_id}")
def get_on_hand(product_id: int):
    try:
        qty = on_hand(product_id)
        return {"product_id": product_id, "on_hand": qty}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
