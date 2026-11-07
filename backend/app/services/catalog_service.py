from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from typing import List, Optional
from app.models.catalog import Category, Product, ProductVariant, Inventory

class CatalogService:
    @staticmethod
    def get_categories(db: Session) -> List[Category]:
        stmt = select(Category).options(
            selectinload(Category.products).selectinload(Product.variants).selectinload(ProductVariant.inventory)
        )
        return list(db.scalars(stmt).all())

    @staticmethod
    def get_products(db: Session, category_slug: Optional[str] = None) -> List[Product]:
        stmt = select(Product).options(
            selectinload(Product.variants).selectinload(ProductVariant.inventory),
            selectinload(Product.category)
        )
        if category_slug:
            stmt = stmt.join(Product.category).where(Category.slug == category_slug)
        return list(db.scalars(stmt).all())

    @staticmethod
    def get_product_by_id(db: Session, product_id: str) -> Optional[Product]:
        stmt = select(Product).where(Product.id == product_id).options(
            selectinload(Product.variants).selectinload(ProductVariant.inventory),
            selectinload(Product.category)
        )
        return db.scalars(stmt).first()

    @staticmethod
    def get_variant_by_id(db: Session, variant_id: str) -> Optional[ProductVariant]:
        stmt = select(ProductVariant).where(ProductVariant.id == variant_id).options(
            selectinload(ProductVariant.inventory),
            selectinload(ProductVariant.product)
        )
        return db.scalars(stmt).first()

    @staticmethod
    def get_variant_by_sku(db: Session, sku: str) -> Optional[ProductVariant]:
        stmt = select(ProductVariant).where(ProductVariant.sku == sku).options(
            selectinload(ProductVariant.inventory),
            selectinload(ProductVariant.product)
        )
        return db.scalars(stmt).first()
