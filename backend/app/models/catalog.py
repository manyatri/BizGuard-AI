import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Numeric, Integer, Boolean, DateTime, ForeignKey, Text, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
from app.core.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now)

    products: Mapped[List["Product"]] = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    category_id: Mapped[str] = mapped_column(String(36), ForeignKey("categories.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    base_sku: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    fabric: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    base_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now)

    category: Mapped["Category"] = relationship("Category", back_populates="products")
    variants: Mapped[List["ProductVariant"]] = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")

class ProductVariant(Base):
    __tablename__ = "product_variants"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id"), nullable=False)
    sku: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    size: Mapped[str] = mapped_column(String(20), nullable=False) # e.g. XS, S, M, L, XL, XXL, 28, 30, 32
    color: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. Jet Black, Sage Green, Champagne
    color_code: Mapped[Optional[str]] = mapped_column(String(7), nullable=True) # #111111
    price_adjustment: Mapped[float] = mapped_column(Numeric(10, 2), default=0.00)
    barcode: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now)

    product: Mapped["Product"] = relationship("Product", back_populates="variants")
    inventory: Mapped[Optional["Inventory"]] = relationship("Inventory", back_populates="variant", uselist=False, cascade="all, delete-orphan")
    order_items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="variant")

class Inventory(Base):
    __tablename__ = "inventories"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    variant_id: Mapped[str] = mapped_column(String(36), ForeignKey("product_variants.id"), unique=True, nullable=False)
    quantity_on_hand: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    quantity_reserved: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reorder_threshold: Mapped[int] = mapped_column(Integer, default=5)
    warehouse_bin: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False) # Optimistic locking token
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now)

    variant: Mapped["ProductVariant"] = relationship("ProductVariant", back_populates="inventory")

    @property
    def quantity_available(self) -> int:
        return max(0, self.quantity_on_hand - self.quantity_reserved)
