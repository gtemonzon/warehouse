# backend/app/routers/transactions.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.get("/", response_model=List[schemas.TransactionOut])
def list_transactions(
    q: Optional[str] = Query(None, description="Buscar por descripción"),
    type_transaction: Optional[int] = Query(None, description="0 entrada, 1 salida"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    # Query con JOINs para traer nombres
    query = db.query(
        models.TabProductTransaction.id_product_transaction,
        models.TabProductTransaction.id_product,
        models.TabProductTransaction.id_warehouse,
        models.TabProductTransaction.type_transaction,
        models.TabProductTransaction.id_planification_expense_request,
        models.TabProductTransaction.id_kit,
        models.TabProductTransaction.quantaty_kit,
        models.TabProductTransaction.quantaty_products,
        models.TabProductTransaction.description,
        models.TabProductTransaction.expiration_date,
        models.TabProductTransaction.add_user,
        models.TabProductTransaction.add_date,
        models.TabProductTransaction.mod_user,
        models.TabProductTransaction.mod_date,
        models.TabProductos.cname.label("product_name"),
        models.TabWarehouse.cname.label("warehouse_name"),
        models.TabKit.cname.label("kit_name"),
    ).join(
        models.TabProductos,
        models.TabProductos.id_product == models.TabProductTransaction.id_product
    ).join(
        models.TabWarehouse,
        models.TabWarehouse.id_warehouse == models.TabProductTransaction.id_warehouse
    ).outerjoin(
        models.TabKit,
        models.TabKit.id_kit == models.TabProductTransaction.id_kit
    )
    
    # Filtros
    if q:
        query = query.filter(func.lower(models.TabProductTransaction.description).like(f"%{q.lower()}%"))
    if type_transaction in (0, 1):
        query = query.filter(models.TabProductTransaction.type_transaction == type_transaction)
    
    # Obtener resultados
    results = query.order_by(models.TabProductTransaction.id_product_transaction.desc()).offset(skip).limit(limit).all()
    
    # Mapear a diccionarios
    return [
        {
            "id_product_transaction": r.id_product_transaction,
            "id_product": r.id_product,
            "id_warehouse": r.id_warehouse,
            "type_transaction": r.type_transaction,
            "id_planification_expense_request": r.id_planification_expense_request,
            "id_kit": r.id_kit,
            "quantaty_kit": r.quantaty_kit,
            "quantaty_products": r.quantaty_products,
            "description": r.description,
            "expiration_date": r.expiration_date,
            "add_user": r.add_user,
            "add_date": r.add_date,
            "mod_user": r.mod_user,
            "mod_date": r.mod_date,
            "product_name": r.product_name,
            "warehouse_name": r.warehouse_name,
            "kit_name": r.kit_name,
        }
        for r in results
    ]

@router.get("/{tx_id}", response_model=schemas.TransactionOut)
def get_transaction(tx_id: int, db: Session = Depends(get_db)):
    result = db.query(
        models.TabProductTransaction.id_product_transaction,
        models.TabProductTransaction.id_product,
        models.TabProductTransaction.id_warehouse,
        models.TabProductTransaction.type_transaction,
        models.TabProductTransaction.id_planification_expense_request,
        models.TabProductTransaction.id_kit,
        models.TabProductTransaction.quantaty_kit,
        models.TabProductTransaction.quantaty_products,
        models.TabProductTransaction.description,
        models.TabProductTransaction.expiration_date,
        models.TabProductTransaction.add_user,
        models.TabProductTransaction.add_date,
        models.TabProductTransaction.mod_user,
        models.TabProductTransaction.mod_date,
        models.TabProductos.cname.label("product_name"),
        models.TabWarehouse.cname.label("warehouse_name"),
        models.TabKit.cname.label("kit_name"),
    ).join(
        models.TabProductos,
        models.TabProductos.id_product == models.TabProductTransaction.id_product
    ).join(
        models.TabWarehouse,
        models.TabWarehouse.id_warehouse == models.TabProductTransaction.id_warehouse
    ).outerjoin(
        models.TabKit,
        models.TabKit.id_kit == models.TabProductTransaction.id_kit
    ).filter(models.TabProductTransaction.id_product_transaction == tx_id).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return {
        "id_product_transaction": result.id_product_transaction,
        "id_product": result.id_product,
        "id_warehouse": result.id_warehouse,
        "type_transaction": result.type_transaction,
        "id_planification_expense_request": result.id_planification_expense_request,
        "id_kit": result.id_kit,
        "quantaty_kit": result.quantaty_kit,
        "quantaty_products": result.quantaty_products,
        "description": result.description,
        "expiration_date": result.expiration_date,
        "add_user": result.add_user,
        "add_date": result.add_date,
        "mod_user": result.mod_user,
        "mod_date": result.mod_date,
        "product_name": result.product_name,
        "warehouse_name": result.warehouse_name,
        "kit_name": result.kit_name,
    }

@router.post("/", response_model=schemas.TransactionOut, status_code=201)
def create_transaction(payload: schemas.TransactionCreate, db: Session = Depends(get_db)):
    if payload.type_transaction not in (0, 1):
        raise HTTPException(status_code=400, detail="type_transaction must be 0 (in) or 1 (out)")
    
    row = models.TabProductTransaction(
        id_product=payload.id_product,
        id_warehouse=payload.id_warehouse,
        type_transaction=payload.type_transaction,
        id_planification_expense_request=payload.id_planification_expense_request,
        id_kit=payload.id_kit,
        quantaty_kit=payload.quantaty_kit,
        quantaty_products=payload.quantaty_products,
        description=payload.description,
        expiration_date=payload.expiration_date,
        add_user=payload.add_user,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    
    # Retornar con nombres incluidos
    return get_transaction(row.id_product_transaction, db)

@router.put("/{tx_id}", response_model=schemas.TransactionOut)
def update_transaction(tx_id: int, payload: schemas.TransactionUpdate, db: Session = Depends(get_db)):
    row = db.get(models.TabProductTransaction, tx_id)
    if not row:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    data = payload.model_dump(exclude_unset=True)
    if "type_transaction" in data and data["type_transaction"] not in (0, 1):
        raise HTTPException(status_code=400, detail="type_transaction must be 0 (in) or 1 (out)")
    
    for k, v in data.items():
        setattr(row, k, v)
    
    db.commit()
    db.refresh(row)
    
    # Retornar con nombres incluidos
    return get_transaction(tx_id, db)

@router.delete("/{tx_id}", status_code=204)
def delete_transaction(tx_id: int, db: Session = Depends(get_db)):
    row = db.get(models.TabProductTransaction, tx_id)
    if not row:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(row)
    db.commit()

@router.get("/inventory/{warehouse_id}/{product_id}")
def get_inventory(warehouse_id: int, product_id: int, db: Session = Depends(get_db)):
    """
    Calcula las existencias actuales de un producto en un almacén
    sumando todas las entradas (type=0) y restando todas las salidas (type=1)
    """
    # Sumar entradas
    entradas = db.query(func.sum(models.TabProductTransaction.quantaty_products)).filter(
        models.TabProductTransaction.id_warehouse == warehouse_id,
        models.TabProductTransaction.id_product == product_id,
        models.TabProductTransaction.type_transaction == 0
    ).scalar() or 0
    
    # Sumar salidas
    salidas = db.query(func.sum(models.TabProductTransaction.quantaty_products)).filter(
        models.TabProductTransaction.id_warehouse == warehouse_id,
        models.TabProductTransaction.id_product == product_id,
        models.TabProductTransaction.type_transaction == 1
    ).scalar() or 0
    
    stock = entradas - salidas
    
    return {
        "id_warehouse": warehouse_id,
        "id_product": product_id,
        "stock": stock,
        "entradas": entradas,
        "salidas": salidas
    }