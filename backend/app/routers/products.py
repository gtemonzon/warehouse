# backend/app/routers/products.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from ..database import get_db
from ..models import TabProductos, TabProductTransaction, TabWarehouse
from ..schemas import ProductoCreate, ProductoOut, ProductoUpdate

router = APIRouter(prefix="/products", tags=["products"])

@router.post("/", response_model=ProductoOut, status_code=201)
def create_product(payload: ProductoCreate, db: Session = Depends(get_db)):
    # code único
    if payload.code:
        exists = db.query(TabProductos).filter(TabProductos.code == payload.code).first()
        if exists:
            raise HTTPException(status_code=409, detail="El código ya existe")
    item = TabProductos(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.get("/", response_model=List[ProductoOut])
def list_products(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None, description="Buscar por code o cname"),
    skip: int = 0,
    limit: int = Query(50, le=200),
):
    query = db.query(TabProductos)
    if q:
        like = f"%{q}%"
        query = query.filter((TabProductos.code.like(like)) | (TabProductos.cname.like(like)))
    return query.order_by(TabProductos.id_product.desc()).offset(skip).limit(limit).all()

@router.get("/{id_product}", response_model=ProductoOut)
def get_product(id_product: int, db: Session = Depends(get_db)):
    item = db.get(TabProductos, id_product)
    if not item:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return item

@router.put("/{id_product}", response_model=ProductoOut)
def update_product(id_product: int, payload: ProductoUpdate, db: Session = Depends(get_db)):
    item = db.get(TabProductos, id_product)
    if not item:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    data = payload.model_dump(exclude_unset=True)
    # mantener unicidad de code si cambia
    if "code" in data and data["code"] is not None:
        clash = db.query(TabProductos).filter(
            TabProductos.code == data["code"],
            TabProductos.id_product != id_product
        ).first()
        if clash:
            raise HTTPException(status_code=409, detail="El código ya existe")
    for k, v in data.items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return item

@router.delete("/{id_product}", status_code=204)
def delete_product(id_product: int, db: Session = Depends(get_db)):
    item = db.get(TabProductos, id_product)
    if not item:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    db.delete(item)
    db.commit()
    return

@router.get("/inventory/summary", response_model=List[dict])
def get_inventory_summary(db: Session = Depends(get_db)):
    """
    Devuelve el stock de cada producto desagregado por bodega
    """
    # Calcular stock por producto y bodega
    query = db.query(
        TabProductTransaction.id_product,
        TabProductTransaction.id_warehouse,
        TabProductos.cname.label('product_name'),
        TabWarehouse.cname.label('warehouse_name'),
        func.sum(
            case(
                (TabProductTransaction.type_transaction == 0, TabProductTransaction.quantaty_products),
                else_=-TabProductTransaction.quantaty_products
            )
        ).label('stock')
    ).join(
        TabProductos, TabProductTransaction.id_product == TabProductos.id_product
    ).join(
        TabWarehouse, TabProductTransaction.id_warehouse == TabWarehouse.id_warehouse
    ).group_by(
        TabProductTransaction.id_product,
        TabProductTransaction.id_warehouse,
        TabProductos.cname,
        TabWarehouse.cname
    ).all()
    
    # Convertir a lista de diccionarios
    return [
        {
            "id_product": row.id_product,
            "id_warehouse": row.id_warehouse,
            "product_name": row.product_name,
            "warehouse_name": row.warehouse_name,
            "stock": row.stock or 0
        }
        for row in query
    ]