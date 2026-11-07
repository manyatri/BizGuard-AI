"""
Simulation API — inject failure scenarios and reset the simulation state.

GET  /api/v1/simulation/scenarios             — list all available scenarios
POST /api/v1/simulation/inject-scenario       — inject any named scenario
POST /api/v1/simulation/inject-bug            — alias: black_kurti_size_mismatch
POST /api/v1/simulation/reset                 — reset all simulation state
GET  /api/v1/simulation/status                — current simulation state
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.simulation_service import SimulationService
from app.services.failure_simulator import FailureSimulator

router = APIRouter(prefix="/simulation", tags=["Simulation"])

# Human-readable metadata for every scenario
_SCENARIO_META = {
    "black_kurti_size_mismatch": {
        "label": "Black Kurti Size Mismatch",
        "category": "BUSINESS",
        "description": (
            "Customer orders Black Kurti Size M. Payment succeeds, but inventory "
            "reserves Size L instead. Order stalls at STALLED_INCONSISTENT."
        ),
        "severity": "CRITICAL",
        "affected_rule": "RULE_VARIANT_INVENTORY_MISMATCH",
    },
    "inventory_api_timeout": {
        "label": "Inventory API Timeout",
        "category": "TECHNICAL",
        "description": (
            "Payment captured but inventory reservation call times out. "
            "Order stuck at PAYMENT_CAPTURED with no stock held."
        ),
        "severity": "HIGH",
        "affected_rule": "RULE_PAYMENT_WITHOUT_INVENTORY",
    },
    "payment_sync_failure": {
        "label": "Payment Sync Failure",
        "category": "TECHNICAL",
        "description": (
            "Payment gateway accepted charge but webhook delivery failed. "
            "Order stays PENDING, payment shows INITIATED forever."
        ),
        "severity": "HIGH",
        "affected_rule": "RULE_PAYMENT_SYNC_FAILURE",
    },
    "invoice_generation_failure": {
        "label": "Invoice Generation Failure",
        "category": "TECHNICAL",
        "description": (
            "Invoice microservice OOM-crashed after inventory was allocated. "
            "Order is INVENTORY_ALLOCATED with no invoice record."
        ),
        "severity": "MEDIUM",
        "affected_rule": "RULE_INVENTORY_ALLOCATED_NO_INVOICE",
    },
    "wrong_color_inventory": {
        "label": "Wrong Color Inventory Reserved",
        "category": "BUSINESS",
        "description": (
            "Customer ordered Black Kurti but stock was reserved on a different "
            "color variant (e.g. White). Order variant_id is correct; reservation is not."
        ),
        "severity": "CRITICAL",
        "affected_rule": "RULE_COLOR_INVENTORY_MISMATCH",
    },
    "negative_inventory": {
        "label": "Negative Inventory",
        "category": "BUSINESS",
        "description": (
            "quantity_reserved exceeds quantity_on_hand for a variant, "
            "creating a negative available stock situation."
        ),
        "severity": "CRITICAL",
        "affected_rule": "RULE_NEGATIVE_INVENTORY",
    },
    "duplicate_payment": {
        "label": "Duplicate Payment",
        "category": "BUSINESS",
        "description": (
            "Two CAPTURED payment records exist for the same order. "
            "Customer has been charged twice."
        ),
        "severity": "CRITICAL",
        "affected_rule": "RULE_DUPLICATE_PAYMENT",
    },
    "incorrect_invoice_amount": {
        "label": "Incorrect Invoice Amount",
        "category": "BUSINESS",
        "description": (
            "Invoice total_amount is 30% lower than order total_amount. "
            "Tax and revenue reporting will be wrong."
        ),
        "severity": "HIGH",
        "affected_rule": "RULE_INVOICE_AMOUNT_MISMATCH",
    },
    "shipped_without_payment": {
        "label": "Shipped Without Payment",
        "category": "BUSINESS",
        "description": (
            "Order status set to SHIPPED but no CAPTURED payment record exists. "
            "Revenue was never collected."
        ),
        "severity": "CRITICAL",
        "affected_rule": "RULE_SHIPPED_WITHOUT_PAYMENT",
    },
    "out_of_stock_sale": {
        "label": "Out-of-Stock Sale",
        "category": "BUSINESS",
        "description": (
            "An order was accepted for a variant that has zero on-hand stock. "
            "The product should have been blocked from checkout."
        ),
        "severity": "HIGH",
        "affected_rule": "RULE_OUT_OF_STOCK_SOLD",
    },
    "refund_not_synced": {
        "label": "Refund Not Synchronized",
        "category": "WORKFLOW",
        "description": (
            "Return is APPROVED but the payment record was never updated to REFUNDED. "
            "Customer is owed money that hasn't been returned."
        ),
        "severity": "HIGH",
        "affected_rule": "RULE_REFUND_NOT_SYNCED",
    },
}


class InjectScenarioRequest(BaseModel):
    scenario: str
    notes: Optional[str] = None


@router.get("/scenarios")
async def list_scenarios():
    """Returns all available failure scenarios with metadata."""
    return {
        "total": len(_SCENARIO_META),
        "scenarios": [
            {"key": key, **meta}
            for key, meta in _SCENARIO_META.items()
        ],
    }


@router.post("/inject-scenario")
async def inject_scenario(body: InjectScenarioRequest, db: Session = Depends(get_db)):
    """
    Injects any named failure scenario into the database.
    Produces real broken state — not just a notification.
    """
    if body.scenario not in _SCENARIO_META:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown scenario '{body.scenario}'. "
                   f"Available: {list(_SCENARIO_META.keys())}",
        )
    try:
        result = FailureSimulator.inject_scenario(db, body.scenario)
        meta = _SCENARIO_META[body.scenario]
        return {
            "injected": True,
            "scenario_key": body.scenario,
            "scenario_label": meta["label"],
            "category": meta["category"],
            "severity": meta["severity"],
            "affected_rule": meta["affected_rule"],
            "result": result,
        }
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Injection failed: {e}")


@router.post("/inject-bug")
async def inject_bug(db: Session = Depends(get_db)):
    """
    Injects the classic Black Kurti Size Mismatch scenario (backward-compatible alias).
    Creates a real order for Size M but reserves inventory on Size L.
    """
    try:
        result = SimulationService.inject_black_kurti_bug(db)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/reset")
async def reset_simulation(db: Session = Depends(get_db)):
    """
    Resets all simulation state: deletes incidents, stalled orders,
    clears all inventory reservations.
    """
    result = SimulationService.reset_simulation(db)
    return result


@router.get("/status")
async def simulation_status(db: Session = Depends(get_db)):
    """Returns current simulation state."""
    return SimulationService.get_status(db)
