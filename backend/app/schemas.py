# backend/app/schemas.py
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
from datetime import datetime

class ProductoBase(BaseModel):
    id_product_type: Optional[int] = None
    id_unit_measurement: Optional[int] = None
    code: Optional[int] = Field(None,description="Código interno (entero)")
    cname: str = Field(..., max_length=255)
    description: Optional[str] = None
    photo: Optional[str] = Field(None, max_length=512)  # puede ser URL Firebase
    unit_cost: Optional[float] = None
    add_user: Optional[int] = None
    mod_user: Optional[int] = None

class ProductoCreate(ProductoBase):
    pass  # todos los campos opcionales arriba; code y cname requeridos

class ProductoUpdate(BaseModel):
    id_product_type: Optional[int] = None
    id_unit_measurement: Optional[int] = None
    code: Optional[int] = None
    cname: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    photo: Optional[str] = Field(None, max_length=512)
    unit_cost: Optional[float] = None
    add_user: Optional[int] = None
    mod_user: Optional[int] = None

class ProductoOut(ProductoBase):
    id_product: int
    add_date: datetime
    mod_date: datetime

    class Config:
        from_attributes = True

# ========== WAREHOUSES ==========
class WarehouseBase(BaseModel):
    code: Optional[int] = Field(None, description="Código numérico interno")
    cname: str = Field(..., min_length=1, max_length=255, description="Nombre del almacén")
    description: Optional[str] = None
    add_user: Optional[int] = None
    mod_user: Optional[int] = None

class WarehouseCreate(WarehouseBase):
    pass

class WarehouseUpdate(BaseModel):
    code: Optional[int] = None
    cname: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    mod_user: Optional[int] = None

class WarehouseOut(WarehouseBase):
    id_warehouse: int
    add_date: datetime
    mod_date: datetime

    class Config:
        from_attributes = True

# ========== KITS ==========
# ---------- KITS ----------
from typing import List  # si no lo tienes ya

class KitBase(BaseModel):
    code: Optional[int] = Field(None, description="Código del kit")
    cname: str = Field(..., max_length=255, description="Nombre del kit")
    description: Optional[str] = Field(None, max_length=255)
    photo: Optional[str] = Field(None, max_length=512)
    add_user: Optional[int] = None
    mod_user: Optional[int] = None

class KitCreate(KitBase):
    pass

class KitUpdate(BaseModel):
    code: Optional[int] = None
    cname: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=255)
    photo: Optional[str] = Field(None, max_length=512)
    mod_user: Optional[int] = None

class KitOut(KitBase):
    id_kit: int
    add_date: datetime
    mod_date: datetime
    class Config:
        from_attributes = True

# ---------- KIT COMPOSITION ----------
class KitCompositionBase(BaseModel):
    id_product: int
    quantaty: int = Field(..., ge=1)
    add_user: Optional[int] = None  # Solo add_user, no mod_user

class KitCompositionUpdate(BaseModel):
    quantaty: Optional[int] = Field(None, ge=1)
    mod_user: Optional[int] = None

class KitCompositionOut(BaseModel):
    id_kit_composition: int
    id_kit: int
    id_product: int
    quantaty: int
    add_date: datetime
    mod_date: datetime
    # Datos denormalizados para el frontend (opcionales)
    product_code: Optional[int] = None
    product_name: Optional[str] = None

    class Config:
        from_attributes = True

# ========== TRANSACTIONS ==========
class TransactionBase(BaseModel):
    id_product: int
    id_warehouse: int
    type_transaction: int = Field(..., description="0=entrada, 1=salida")
    id_planification_expense_request: Optional[int] = None
    id_kit: Optional[int] = None
    quantaty_kit: Optional[int] = None
    quantaty_products: int
    description: Optional[str] = None
    expiration_date: Optional[datetime] = None
    add_user: Optional[int] = None
    mod_user: Optional[int] = None

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    id_product: Optional[int] = None
    id_warehouse: Optional[int] = None
    type_transaction: Optional[int] = None
    id_planification_expense_request: Optional[int] = None
    id_kit: Optional[int] = None
    quantaty_kit: Optional[int] = None
    quantaty_products: Optional[int] = None
    description: Optional[str] = None
    expiration_date: Optional[datetime] = None
    mod_user: Optional[int] = None

class TransactionOut(TransactionBase):
    id_product_transaction: int
    add_date: datetime
    mod_date: datetime
    # Campos denormalizados (nombres para mostrar en el frontend)
    product_name: Optional[str] = None
    warehouse_name: Optional[str] = None
    kit_name: Optional[str] = None

    class Config:
        from_attributes = True