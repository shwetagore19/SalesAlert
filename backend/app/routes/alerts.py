from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.db.database import get_db
from backend.app.services.alert_service import AlertService

router = APIRouter(prefix="/api/alerts", tags=["Business Alerts"])

@router.get("")
def get_alerts(date: str = Query(None, description="Target date YYYY-MM-DD"), db: Session = Depends(get_db)):
    alerts = AlertService.evaluate_daily_alerts(db, date)
    return {"count": len(alerts), "alerts": alerts}
