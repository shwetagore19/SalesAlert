from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.db.database import get_db
from backend.app.db.models import Sale
from backend.app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api", tags=["Sales & Products"])

@router.get("/sales")
def get_sales_list(
    limit: int = Query(50, ge=1, le=500),
    category: str = Query(None),
    region: str = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Sale)
    if category:
        query = query.filter(Sale.category == category)
    if region:
        query = query.filter(Sale.region == region)
        
    sales = query.order_by(Sale.order_date.desc()).limit(limit).all()
    return {"count": len(sales), "sales": sales}

@router.get("/products/performance")
def get_products_performance(date: str = Query(None), db: Session = Depends(get_db)):
    return AnalyticsService.get_product_performance(db, date)

@router.get("/regions/performance")
def get_regions_performance(date: str = Query(None), db: Session = Depends(get_db)):
    return AnalyticsService.get_regional_performance(db, date)
