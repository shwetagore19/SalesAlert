from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.db.database import get_db
from backend.app.services.root_cause_service import RootCauseService
from backend.app.services.recommendation_service import RecommendationService
from backend.app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/intelligence", tags=["Sales Intelligence Engine"])

@router.get("/root-cause")
def get_root_cause_analysis(date: str = Query(None), db: Session = Depends(get_db)):
    """Answers: Why did sales/profit change today? Decomposes DoD deltas across dimensions."""
    analysis = RootCauseService.analyze_root_cause(db, date)
    return analysis

@router.get("/recommendations")
def get_action_recommendations(date: str = Query(None), db: Session = Depends(get_db)):
    """Answers: What action should the manager take next? Prioritized recommendations."""
    recs = RecommendationService.generate_recommendations(db, date)
    return {"recommendations": recs}

@router.get("/channels")
def get_channel_metrics(date: str = Query(None), db: Session = Depends(get_db)):
    """Sales Channel performance breakdown (Online vs Store vs B2B)."""
    channels = AnalyticsService.get_channel_performance(db, date)
    return {"channels": channels}

@router.get("/discount-impact")
def get_discount_impact_metrics(db: Session = Depends(get_db)):
    """Discount rate tiering and profit margin erosion impact."""
    impact = AnalyticsService.get_discount_impact(db)
    return impact
