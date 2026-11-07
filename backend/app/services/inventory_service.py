from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException
from app.models.catalog import Inventory, ProductVariant
from typing import Optional

class InventoryService:
    @staticmethod
    def get_inventory_for_variant(db: Session, variant_id: str) -> Optional[Inventory]:
        return db.scalars(
            select(Inventory).where(Inventory.variant_id == variant_id)
        ).first()

    @staticmethod
    def check_availability(db: Session, variant_id: str, requested_qty: int = 1) -> bool:
        inventory = InventoryService.get_inventory_for_variant(db, variant_id)
        if not inventory:
            return False
        return inventory.quantity_available >= requested_qty

    @staticmethod
    def reserve_stock(db: Session, variant_id: str, qty: int = 1) -> Inventory:
        inventory = InventoryService.get_inventory_for_variant(db, variant_id)
        if not inventory:
            raise HTTPException(status_code=404, detail=f"Inventory for variant {variant_id} not found")
        
        if inventory.quantity_available < qty:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient inventory available for variant {variant_id}. Available: {inventory.quantity_available}, Requested: {qty}"
            )
        
        inventory.quantity_reserved += qty
        inventory.version += 1
        db.commit()
        db.refresh(inventory)
        return inventory

    @staticmethod
    def release_reservation(db: Session, variant_id: str, qty: int = 1) -> Inventory:
        inventory = InventoryService.get_inventory_for_variant(db, variant_id)
        if not inventory:
            raise HTTPException(status_code=404, detail=f"Inventory for variant {variant_id} not found")
        
        inventory.quantity_reserved = max(0, inventory.quantity_reserved - qty)
        inventory.version += 1
        db.commit()
        db.refresh(inventory)
        return inventory

    @staticmethod
    def execute_atomic_swap(
        db: Session, 
        incorrect_variant_id: str, 
        correct_variant_id: str, 
        qty: int = 1
    ) -> dict:
        """
        Executes an atomic compensating transaction:
        1. Decrements reserved stock on incorrect variant (+1 back to available)
        2. Increments reserved stock on correct variant (-1 available)
        """
        incorrect_inv = InventoryService.get_inventory_for_variant(db, incorrect_variant_id)
        correct_inv = InventoryService.get_inventory_for_variant(db, correct_variant_id)
        
        if not incorrect_inv or not correct_inv:
            raise HTTPException(status_code=404, detail="One or more inventory variant records missing")
        
        if correct_inv.quantity_available < qty:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot swap: correct variant {correct_variant_id} lacks available stock ({correct_inv.quantity_available} available)"
            )
        
        # Compensating step 1: Revert accidental deduction
        incorrect_inv.quantity_reserved = max(0, incorrect_inv.quantity_reserved - qty)
        incorrect_inv.version += 1

        # Compensating step 2: Legitimate deduction
        correct_inv.quantity_reserved += qty
        correct_inv.version += 1

        db.commit()
        db.refresh(incorrect_inv)
        db.refresh(correct_inv)

        return {
            "reverted_variant_id": incorrect_variant_id,
            "reverted_new_reserved": incorrect_inv.quantity_reserved,
            "allocated_variant_id": correct_variant_id,
            "allocated_new_reserved": correct_inv.quantity_reserved
        }
