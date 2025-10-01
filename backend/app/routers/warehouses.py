# backend/app/routers/warehouses.py
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import TabWarehouse
from ..schemas import WarehouseCreate, WarehouseOut, WarehouseUpdate

router = APIRouter(prefix="/warehouses", tags=["warehouses"])

@router.post("/", response_model=WarehouseOut, status_code=201)
def create_warehouse(payload: WarehouseCreate, db: Session = Depends(get_db)):
    # Validar código único si existe
    if payload.code:
        exists = db.query(TabWarehouse).filter(TabWarehouse.code == payload.code).first()
        if exists:
            raise HTTPException(status_code=409, detail="El código ya existe")
    
    # Crear warehouse
    item = TabWarehouse(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.get("/", response_model=List[WarehouseOut])
def list_warehouses(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None, description="Buscar por nombre"),
    skip: int = 0,
    limit: int = Query(50, le=200),
):
    query = db.query(TabWarehouse)
    if q:
        like = f"%{q}%"
        query = query.filter(TabWarehouse.cname.like(like))
    return query.order_by(TabWarehouse.id_warehouse.desc()).offset(skip).limit(limit).all()

@router.get("/{warehouse_id}", response_model=WarehouseOut)
def get_warehouse(warehouse_id: int, db: Session = Depends(get_db)):
    item = db.get(TabWarehouse, warehouse_id)
    if not item:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return item

@router.put("/{warehouse_id}", response_model=WarehouseOut)
def update_warehouse(warehouse_id: int, payload: WarehouseUpdate, db: Session = Depends(get_db)):
    item = db.get(TabWarehouse, warehouse_id)
    if not item:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    
    data = payload.model_dump(exclude_unset=True)
    
    # Validar código único si cambia
    if "code" in data and data["code"] is not None:
        clash = db.query(TabWarehouse).filter(
            TabWarehouse.code == data["code"],
            TabWarehouse.id_warehouse != warehouse_id
        ).first()
        if clash:
            raise HTTPException(status_code=409, detail="El código ya existe")
    
    for k, v in data.items():
        setattr(item, k, v)
    
    db.commit()
    db.refresh(item)
    return item

@router.delete("/{warehouse_id}", status_code=204)
def delete_warehouse(warehouse_id: int, db: Session = Depends(get_db)):
    item = db.get(TabWarehouse, warehouse_id)
    if not item:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    db.delete(item)
    db.commit()
    return None