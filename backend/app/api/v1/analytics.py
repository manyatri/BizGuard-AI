"""
Analytics API — live metrics from the database.
GET /api/v1/analytics/dashboard
GET /api/v1/analytics/incidents/timeline
GET /api/v1/analytics/inventory/health
GET /api/v1/analytics/workflows/stats
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard")
async def dashboard_metrics(db: Session = Depends(get_db)):
    """Returns all live KPIs for the BizGuard dashboard."""
    return AnalyticsService.get_dashboard_metrics(db)


@router.get("/incidents/timeline")
async def incident_timeline(
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    """Returns incidents grouped by day for the last N days."""
    return {
        "days": days,
        "timeline": AnalyticsService.get_incident_timeline(db, days),
    }


@router.get("/inventory/health")
async def inventory_health(db: Session = Depends(get_db)):
    """Returns per-variant inventory health status."""
    items = AnalyticsService.get_inventory_health(db)
    healthy = sum(1 for i in items if i["health_status"] == "HEALTHY")
    low = sum(1 for i in items if i["health_status"] == "LOW_STOCK")
    out = sum(1 for i in items if i["health_status"] == "OUT_OF_STOCK")
    return {
        "summary": {"healthy": healthy, "low_stock": low, "out_of_stock": out},
        "variants": items,
    }


@router.get("/workflows/stats")
async def workflow_stats(db: Session = Depends(get_db)):
    """Returns workflow execution statistics."""
    return AnalyticsService.get_workflow_stats(db)
