from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from db import engine

app = FastAPI(title="Warehouse API", version="0.1.0")

@app.get("/health")
def health():
    with engine.connect() as conn:
        r = conn.execute(text("SELECT 1")).scalar()
    return {"ok": True, "db": bool(r)}

class ReceiveIn(BaseModel):
    user_id: int
    product_id: int
    warehouse_id: int
    quantity: int
    planification_expense_request_id: int | None = None
    note: str | None = None

@app.post("/transactions/receive")
def receive(in_data: ReceiveIn):
    if in_data.quantity <= 0:
        raise HTTPException(status_code=400, detail="quantity must be > 0")
    sql = text("""CALL sp_receive_product(:user_id,:product_id,:warehouse_id,:quantity,:plan_req,:note)""")
    with engine.begin() as conn:
        conn.execute(sql, {
            "user_id": in_data.user_id,
            "product_id": in_data.product_id,
            "warehouse_id": in_data.warehouse_id,
            "quantity": in_data.quantity,
            "plan_req": in_data.planification_expense_request_id,
            "note": in_data.note
        })
    return {"status": "ok"}

class IssueIn(BaseModel):
    user_id: int
    product_id: int
    warehouse_id: int
    quantity: int
    planification_expense_request_id: int | None = None
    note: str | None = None

@app.post("/transactions/issue")
def issue(in_data: IssueIn):
    if in_data.quantity <= 0:
        raise HTTPException(status_code=400, detail="quantity must be > 0")
    sql = text("""CALL sp_issue_product(:user_id,:product_id,:warehouse_id,:quantity,:plan_req,:note)""")
    with engine.begin() as conn:
        conn.execute(sql, {
            "user_id": in_data.user_id,
            "product_id": in_data.product_id,
            "warehouse_id": in_data.warehouse_id,
            "quantity": in_data.quantity,
            "plan_req": in_data.planification_expense_request_id,
            "note": in_data.note
        })
    return {"status": "ok"}

class IssueKitIn(BaseModel):
    user_id: int
    kit_id: int
    warehouse_id: int
    kit_quantity: int
    planification_expense_request_id: int | None = None
    note: str | None = None

@app.post("/transactions/issue-kit")
def issue_kit(in_data: IssueKitIn):
    if in_data.kit_quantity <= 0:
        raise HTTPException(status_code=400, detail="kit_quantity must be > 0")
    sql = text("""CALL sp_issue_kit(:user_id,:kit_id,:warehouse_id,:kit_quantity,:plan_req,:note)""")
    with engine.begin() as conn:
        conn.execute(sql, {
            "user_id": in_data.user_id,
            "kit_id": in_data.kit_id,
            "warehouse_id": in_data.warehouse_id,
            "kit_quantity": in_data.kit_quantity,
            "plan_req": in_data.planification_expense_request_id,
            "note": in_data.note
        })
    return {"status": "ok"}

@app.get("/stock")
def stock():
    sql = text("""SELECT p.id AS product_id, p.sku, p.name, w.id AS warehouse_id, w.code AS warehouse, COALESCE(s.qty_on_hand,0) AS qty_on_hand
                 FROM vw_current_stock s
                 JOIN tab_product p ON p.id = s.product_id
                 JOIN tab_warehouse w ON w.id = s.warehouse_id
                 ORDER BY p.name, w.code""")
    with engine.connect() as conn:
        rows = conn.execute(sql).mappings().all()
    return {"items": [dict(r) for r in rows]}

@app.get("/ledger/{product_id}")
def ledger(product_id: int):
    sql = text("""SELECT * FROM vw_product_ledger WHERE product_id = :pid ORDER BY performed_at DESC, id DESC""")
    with engine.connect() as conn:
        rows = conn.execute(sql, {"pid": product_id}).mappings().all()
    return {"items": [dict(r) for r in rows]}
