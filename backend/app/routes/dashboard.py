from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.db.database import get_db
from backend.app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/today")
def get_today_dashboard(date: str = Query(None, description="Optional target date YYYY-MM-DD"), db: Session = Depends(get_db)):
    kpis = AnalyticsService.get_daily_kpis(db, date)
    return kpis

@router.get("/trends")
def get_dashboard_trends(days: int = Query(30, description="Number of historical days"), db: Session = Depends(get_db)):
    trends = AnalyticsService.get_trend_series(db, days)
    return {"trends": trends}

@router.get("/metadata")
def get_dashboard_metadata(db: Session = Depends(get_db)):
    return AnalyticsService.get_data_source_metadata(db)

