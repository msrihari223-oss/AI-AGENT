from fastapi import APIRouter
from backend.schemas.incident import DashboardStats
from backend.services.incident_service import incident_service

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_metrics():
    """Retrieve aggregate cybersecurity SOC metrics, severity distributions, and recent incidents"""
    return incident_service.get_dashboard_stats()
