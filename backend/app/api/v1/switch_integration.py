"""
Switch Integration Router — monitors Switch bus status.
"""
from fastapi import APIRouter
from app.services.switch_client import switch_client

router = APIRouter(prefix="/switch", tags=["Switch Integration"])


@router.get("/status")
async def get_switch_status():
    """
    Returns the real connection status to the Switch agent bus.
    Never fakes connection status.
    """
    return switch_client.get_status()
