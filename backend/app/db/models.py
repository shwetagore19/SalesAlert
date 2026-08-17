from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from backend.app.db.database import Base

class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(50), index=True)
    order_date = Column(DateTime, index=True)
    customer_id = Column(String(50), index=True)
    product = Column(String(100), index=True)
    category = Column(String(50), index=True)
    region = Column(String(50), index=True)
    city = Column(String(50))
    sales_channel = Column(String(50))
    customer_type = Column(String(20))
    quantity = Column(Integer)
    unit_price = Column(Float)
    discount_rate = Column(Float)
    discount_amount = Column(Float)
    revenue = Column(Float)
    cost = Column(Float)
    profit = Column(Float)
    profit_margin = Column(Float)
    payment_method = Column(String(50))
    order_status = Column(String(20))

class DailyKPI(Base):
    __tablename__ = "daily_kpis"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String(20), unique=True, index=True)
    revenue = Column(Float)
    cost = Column(Float)
    profit = Column(Float)
    profit_margin = Column(Float)
    total_orders = Column(Integer)
    quantity_sold = Column(Integer)
    avg_order_value = Column(Float)
    new_customers = Column(Integer)
    returning_customers = Column(Integer)
    revenue_dod_pct = Column(Float, nullable=True)
    profit_dod_pct = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class AlertRecord(Base):
    __tablename__ = "alert_records"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String(20), index=True)
    alert_type = Column(String(50))  # REVENUE_DROP, MARGIN_SQUEEZE, REGIONAL_DECLINE, DISCOUNT_ALERT, etc.
    severity = Column(String(20))    # CRITICAL, WARNING, INFO
    title = Column(String(200))
    message = Column(Text)
    metrics_json = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class DailyReport(Base):
    __tablename__ = "daily_reports"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String(20), unique=True, index=True)
    headline = Column(String(255))
    executive_summary = Column(Text)
    top_performers = Column(Text)
    critical_alerts = Column(Text)
    recommended_focus = Column(Text)
    raw_prompt = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
