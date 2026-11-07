from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any
from datetime import datetime

class OrderItemCreate(BaseModel):
    variant_id: str
    quantity: int = Field(default=1, gt=0)

class CheckoutRequest(BaseModel):
    customer_name: str
    customer_email: str
    customer_phone: Optional[str] = None
    shipping_address: Optional[dict] = None
    items: List[OrderItemCreate]
    payment_gateway: str = "Razorpay Mock"

class OrderItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    variant_id: str
    product_title: str
    ordered_size: str
    ordered_color: str
    quantity: int
    unit_price: float
    subtotal: float

class PaymentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    order_id: str
    payment_gateway: str
    transaction_reference: str
    amount: float
    currency: str
    status: str
    idempotency_key: str
    captured_at: Optional[datetime] = None

class InvoiceItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    sku: str
    description: str
    size: str
    color: str
    quantity: int
    unit_price: float

class InvoiceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    order_id: str
    invoice_number: str
    tax_amount: float
    total_amount: float
    status: str
    created_at: datetime
    items: List[InvoiceItemRead] = []

class OrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    order_number: str
    customer_name: str
    customer_email: str
    customer_phone: Optional[str] = None
    shipping_address: Optional[Any] = None
    total_amount: float
    status: str
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemRead] = []
    payments: List[PaymentRead] = []
    invoices: List[InvoiceRead] = []
