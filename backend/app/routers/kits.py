# backend/app/routers/kits.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import TabKit, TabKitComposition, TabProductos
from app.schemas import (
    KitCreate, KitUpdate, KitOut,
    KitCompositionBase, KitCompositionUpdate, KitCompositionOut
)

router = APIRouter(prefix="/kits", tags=["kits"])

# -------- Kits --------
@router.get("/", response_model=List[KitOut])  # ✅ Agregada barra
def list_kits(
    q: Optional[str] = Query(None, description="Buscar por nombre"),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    query = db.query(TabKit)
    if q:
        query = query.filter(TabKit.cname.like(f"%{q}%"))
    rows = query.order_by(TabKit.id_kit.desc()).offset(skip).limit(limit).all()
    return rows

@router.get("/{kit_id}", response_model=KitOut)
def get_kit(kit_id: int, db: Session = Depends(get_db)):
    obj = db.get(TabKit, kit_id)  # ✅ Corregido método deprecado
    if not obj:
        raise HTTPException(status_code=404, detail="Kit not found")
    return obj

@router.post("/", response_model=KitOut, status_code=201)  # ✅ Agregada barra
def create_kit(body: KitCreate, db: Session = Depends(get_db)):
    obj = TabKit(
        code=body.code,
        cname=body.cname,
        description=body.description,
        photo=body.photo,
        add_user=body.add_user,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.put("/{kit_id}", response_model=KitOut)
def update_kit(kit_id: int, body: KitUpdate, db: Session = Depends(get_db)):
    obj = db.get(TabKit, kit_id)  # ✅ Corregido método deprecado
    if not obj:
        raise HTTPException(status_code=404, detail="Kit not found")
    
    if body.code is not None:
        obj.code = body.code
    if body.cname is not None:
        obj.cname = body.cname
    if body.description is not None:
        obj.description = body.description
    if body.photo is not None:
        obj.photo = body.photo
    if body.mod_user is not None:
        obj.mod_user = body.mod_user
    
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{kit_id}", status_code=204)
def delete_kit(kit_id: int, db: Session = Depends(get_db)):
    obj = db.get(TabKit, kit_id)  # ✅ Corregido método deprecado
    if not obj:
        raise HTTPException(status_code=404, detail="Kit not found")
    db.delete(obj)
    db.commit()
    return None

# -------- Kit Composition --------
@router.get("/{kit_id}/composition", response_model=List[KitCompositionOut])
def list_composition(kit_id: int, db: Session = Depends(get_db)):
    q = (
        db.query(
            TabKitComposition.id_kit_composition,
            TabKitComposition.id_kit,
            TabKitComposition.id_product,
            TabKitComposition.quantaty,
            TabKitComposition.add_date,
            TabKitComposition.mod_date,
            TabProductos.code.label("product_code"),
            TabProductos.cname.label("product_name"),
        )
        .join(TabProductos, TabProductos.id_product == TabKitComposition.id_product)
        .filter(TabKitComposition.id_kit == kit_id)
        .order_by(TabKitComposition.id_kit_composition.desc())
    )
    rows = q.all()
    
    return [
        {
            "id_kit_composition": r.id_kit_composition,
            "id_kit": r.id_kit,
            "id_product": r.id_product,
            "quantaty": r.quantaty,
            "add_date": r.add_date,
            "mod_date": r.mod_date,
            "product_code": r.product_code,
            "product_name": r.product_name,
        }
        for r in rows
    ]

@router.post("/{kit_id}/composition", response_model=KitCompositionOut, status_code=201)
def add_composition(kit_id: int, body: KitCompositionBase, db: Session = Depends(get_db)):
    # Validar existencia del kit y el producto
    if not db.get(TabKit, kit_id):  # ✅ Corregido
        raise HTTPException(status_code=404, detail="Kit not found")
    if not db.get(TabProductos, body.id_product):  # ✅ Corregido
        raise HTTPException(status_code=404, detail="Product not found")
    
    obj = TabKitComposition(
        id_kit=kit_id,
        id_product=body.id_product,
        quantaty=body.quantaty,
        add_user=body.add_user,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    
    # Obtener datos del producto
    p = db.get(TabProductos, body.id_product)
    return {
        "id_kit_composition": obj.id_kit_composition,
        "id_kit": obj.id_kit,
        "id_product": obj.id_product,
        "quantaty": obj.quantaty,
        "add_date": obj.add_date,
        "mod_date": obj.mod_date,
        "product_code": p.code if p else None,
        "product_name": p.cname if p else None,
    }

@router.put("/{kit_id}/composition/{comp_id}", response_model=KitCompositionOut)
def update_composition(
    kit_id: int, comp_id: int, body: KitCompositionUpdate, db: Session = Depends(get_db)
):
    obj = db.get(TabKitComposition, comp_id)  # ✅ Corregido
    if not obj or obj.id_kit != kit_id:
        raise HTTPException(status_code=404, detail="Composition row not found")
    
    if body.quantaty is not None:
        obj.quantaty = body.quantaty
    if body.mod_user is not None:
        obj.mod_user = body.mod_user
    
    db.commit()
    db.refresh(obj)
    
    p = db.get(TabProductos, obj.id_product)
    return {
        "id_kit_composition": obj.id_kit_composition,
        "id_kit": obj.id_kit,
        "id_product": obj.id_product,
        "quantaty": obj.quantaty,
        "add_date": obj.add_date,
        "mod_date": obj.mod_date,
        "product_code": p.code if p else None,
        "product_name": p.cname if p else None,
    }

@router.delete("/{kit_id}/composition/{comp_id}", status_code=204)
def delete_composition(kit_id: int, comp_id: int, db: Session = Depends(get_db)):
    obj = db.get(TabKitComposition, comp_id)  # ✅ Corregido
    if not obj or obj.id_kit != kit_id:
        raise HTTPException(status_code=404, detail="Composition row not found")
    db.delete(obj)
    db.commit()
    return None