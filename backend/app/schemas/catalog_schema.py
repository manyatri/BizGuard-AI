from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime

class InventoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    variant_id: str
    quantity_on_hand: int
    quantity_reserved: int
    quantity_available: int
    reorder_threshold: int
    warehouse_bin: Optional[str] = None
    version: int
    updated_at: datetime

class VariantRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    product_id: str
    sku: str
    size: str
    color: str
    color_code: Optional[str] = None
    price_adjustment: float
    barcode: Optional[str] = None
    inventory: Optional[InventoryRead] = None

class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    category_id: str
    title: str
    base_sku: str
    description: Optional[str] = None
    fabric: Optional[str] = None
    base_price: float
    image_url: Optional[str] = None
    is_active: bool
    variants: List[VariantRead] = []

class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    slug: str
    products: List[ProductRead] = []
