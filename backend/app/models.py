# backend/app/models.py
from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime, ForeignKey, text
)
from sqlalchemy.orm import relationship
from .database import Base

# Nota: uso DateTime para add_date/mod_date con CURRENT_TIMESTAMP
# (si quieres estrictamente DATE, lo cambiamos a Date + CURRENT_DATE)

class TabProductos(Base):
    __tablename__ = "tab_productos"

    id_product = Column(Integer, primary_key=True, autoincrement=True, index=True)
    id_product_type = Column(Integer, nullable=True)
    id_unit_measurement = Column(Integer, nullable=True)
    code = Column(Integer, nullable=False, unique=True, index=True)
    cname = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    photo = Column(String(512), nullable=True)  # link Firebase u otro
    unit_cost = Column(Float, nullable=True)
    add_user = Column(Integer, nullable=True)
    add_date = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    mod_user = Column(Integer, nullable=True)
    mod_date = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), nullable=False)

    # Relaciones útiles
    product_transactions = relationship("TabProductTransaction", back_populates="product")
    kit_compositions = relationship("TabKitComposition", back_populates="product")


class TabWarehouse(Base):
    __tablename__ = "tab_warehouse"

    id_warehouse = Column(Integer, primary_key=True, autoincrement=True, index=True)
    code = Column(Integer, nullable=False, unique=True, index=True)
    cname = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    add_user = Column(Integer, nullable=True)
    add_date = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    mod_user = Column(Integer, nullable=True)
    mod_date = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), nullable=False)

    product_transactions = relationship("TabProductTransaction", back_populates="warehouse")


class TabKit(Base):
    __tablename__ = "tab_kit"

    id_kit = Column(Integer, primary_key=True, autoincrement=True, index=True)
    code = Column(Integer, nullable=False, unique=True, index=True)
    cname = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    photo = Column(String(512), nullable=True)
    add_user = Column(Integer, nullable=True)
    add_date = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    mod_user = Column(Integer, nullable=True)
    mod_date = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), nullable=False)

    compositions = relationship("TabKitComposition", back_populates="kit")
    product_transactions = relationship("TabProductTransaction", back_populates="kit")


class TabKitComposition(Base):
    __tablename__ = "tab_kit_composition"

    id_kit_composition = Column(Integer, primary_key=True, autoincrement=True, index=True)
    id_kit = Column(Integer, ForeignKey("tab_kit.id_kit"), nullable=False)
    id_product = Column(Integer, ForeignKey("tab_productos.id_product"), nullable=False)
    quantaty = Column(Integer, nullable=False)

    add_user = Column(Integer, nullable=True)
    add_date = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    mod_user = Column(Integer, nullable=True)
    mod_date = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), nullable=False)

    kit = relationship("TabKit", back_populates="compositions")
    product = relationship("TabProductos", back_populates="kit_compositions")


class TabProductTransaction(Base):
    __tablename__ = "tab_product_transaction"

    id_product_transaction = Column(Integer, primary_key=True, autoincrement=True, index=True)
    id_product = Column(Integer, ForeignKey("tab_productos.id_product"), nullable=False)
    id_warehouse = Column(Integer, ForeignKey("tab_warehouse.id_warehouse"), nullable=False)
    type_transaction = Column(Integer, nullable=False)  # 0=suma, 1=resta
    id_planification_expense_request = Column(Integer, nullable=True)
    id_kit = Column(Integer, ForeignKey("tab_kit.id_kit"), nullable=True)
    quantaty_kit = Column(Integer, nullable=True)
    quantaty_products = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    expiration_date = Column(DateTime, nullable=True)  # sólo para entradas

    add_user = Column(Integer, nullable=True)
    add_date = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    mod_user = Column(Integer, nullable=True)
    mod_date = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), nullable=False)

    product = relationship("TabProductos", back_populates="product_transactions")
    warehouse = relationship("TabWarehouse", back_populates="product_transactions")
    kit = relationship("TabKit", back_populates="product_transactions")
