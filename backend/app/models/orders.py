import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Numeric, Integer, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional, Any
from app.core.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)

class Order(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    order_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    customer_name: Mapped[str] = mapped_column(String(150), nullable=False)
    customer_email: Mapped[str] = mapped_column(String(255), nullable=False)
    customer_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    shipping_address: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    total_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), 
        default="PENDING", 
        nullable=False, 
        index=True
    ) # PENDING, PAYMENT_CAPTURED, INVENTORY_ALLOCATED, INVOICED, SHIPPED, DELIVERED, STALLED_INCONSISTENT
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now)

    items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payments: Mapped[List["Payment"]] = relationship("Payment", back_populates="order")
    invoices: Mapped[List["Invoice"]] = relationship("Invoice", back_populates="order")
    shipments: Mapped[List["Shipment"]] = relationship("Shipment", back_populates="order")
    returns: Mapped[List["ReturnRecord"]] = relationship("ReturnRecord", back_populates="order")
    workflow_executions: Mapped[List["WorkflowExecution"]] = relationship("WorkflowExecution", back_populates="order")
    incidents: Mapped[List["Incident"]] = relationship("Incident", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    order_id: Mapped[str] = mapped_column(String(36), ForeignKey("orders.id"), nullable=False)
    variant_id: Mapped[str] = mapped_column(String(36), ForeignKey("product_variants.id"), nullable=False)
    product_title: Mapped[str] = mapped_column(String(255), nullable=False)
    ordered_size: Mapped[str] = mapped_column(String(20), nullable=False)
    ordered_color: Mapped[str] = mapped_column(String(50), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    subtotal: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    order: Mapped["Order"] = relationship("Order", back_populates="items")
    variant: Mapped["ProductVariant"] = relationship("ProductVariant", back_populates="order_items")

class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    order_id: Mapped[str] = mapped_column(String(36), ForeignKey("orders.id"), nullable=False)
    payment_gateway: Mapped[str] = mapped_column(String(50), default="Razorpay Mock") # Razorpay Mock, Stripe
    transaction_reference: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    status: Mapped[str] = mapped_column(String(50), default="INITIATED") # INITIATED, CAPTURED, FAILED, REFUNDED
    idempotency_key: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    captured_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    order: Mapped["Order"] = relationship("Order", back_populates="payments")

class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    order_id: Mapped[str] = mapped_column(String(36), ForeignKey("orders.id"), nullable=False)
    invoice_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    tax_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0.00)
    total_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="ISSUED") # ISSUED, VOIDED, CORRECTED
    pdf_storage_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now)

    order: Mapped["Order"] = relationship("Order", back_populates="invoices")
    items: Mapped[List["InvoiceItem"]] = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")

class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    invoice_id: Mapped[str] = mapped_column(String(36), ForeignKey("invoices.id"), nullable=False)
    variant_id: Mapped[str] = mapped_column(String(36), ForeignKey("product_variants.id"), nullable=False)
    sku: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    size: Mapped[str] = mapped_column(String(20), nullable=False)
    color: Mapped[str] = mapped_column(String(50), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="items")

class Shipment(Base):
    __tablename__ = "shipments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    order_id: Mapped[str] = mapped_column(String(36), ForeignKey("orders.id"), nullable=False)
    carrier: Mapped[str] = mapped_column(String(100), default="FashionLogistics Express")
    tracking_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="MANIFESTED") # MANIFESTED, PICKED_UP, IN_TRANSIT, DELIVERED, ON_HOLD
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now)

    order: Mapped["Order"] = relationship("Order", back_populates="shipments")

class ReturnRecord(Base):
    __tablename__ = "returns"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    order_id: Mapped[str] = mapped_column(String(36), ForeignKey("orders.id"), nullable=False)
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="REQUESTED") # REQUESTED, APPROVED, RECEIVED, RESTOCKED, REJECTED
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now)

    order: Mapped["Order"] = relationship("Order", back_populates="returns")
