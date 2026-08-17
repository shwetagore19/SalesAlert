import pandas as pd
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session
from backend.app.db.database import get_db, DATASET_PATH
from backend.app.db.models import Sale
from backend.app.services.llm_service import LLMService
from backend.app.services.email_service import EmailService
from backend.app.services.whatsapp_service import WhatsAppService
from backend.daily_data_generator import DailyDataGenerator

router = APIRouter(prefix="/api", tags=["Reports & Automation"])

@router.get("/reports/latest")
def get_latest_report(date: str = Query(None), db: Session = Depends(get_db)):
    report = LLMService.generate_daily_newspaper(db, date)
    return report

@router.post("/reports/email")
def trigger_email_report(payload: dict = Body(default={}), db: Session = Depends(get_db)):
    target_date = payload.get("date")
    recipient = payload.get("email")
    res = EmailService.send_daily_email(db, target_date, recipient)
    return res

@router.post("/reports/whatsapp")
def trigger_whatsapp_report(payload: dict = Body(default={}), db: Session = Depends(get_db)):
    target_date = payload.get("date")
    phone = payload.get("phone")
    res = WhatsAppService.send_daily_whatsapp(db, target_date, phone)
    return res

@router.post("/daily-update")
def trigger_daily_update(payload: dict = Body(default={}), db: Session = Depends(get_db)):
    """
    Simulate a new daily business update:
    1. Generate new transactions for target date
    2. Sync new records into PostgreSQL/SQLite database
    3. Evaluate KPIs & business alerts
    4. Generate LLM Daily Business Newspaper
    5. Trigger email & WhatsApp delivery
    """
    target_date_str = payload.get("date")
    orders_count = payload.get("orders_count")
    
    # 1. Run Generator
    generator = DailyDataGenerator()
    gen_result = generator.generate_day(target_date_str, orders_count)
    gen_records = gen_result["records"]
    new_date = gen_result["date"]
    
    # 2. Automated Data Validation & Cleaning Pipeline
    from backend.app.services.data_validation_service import DataValidationService
    val_result = DataValidationService.validate_and_clean_sales_batch(gen_records)
    valid_records = val_result["valid_records"]

    # 3. Insert validated records into DB session
    new_sales = []
    for r in valid_records:
        sale = Sale(
            order_id=r["order_id"],
            order_date=pd.to_datetime(r["order_date"]),
            customer_id=r["customer_id"],
            product=r["product"],
            category=r["category"],
            region=r["region"],
            city=r["city"],
            sales_channel=r["sales_channel"],
            customer_type=r["customer_type"],
            quantity=r["quantity"],
            unit_price=r["unit_price"],
            discount_rate=r["discount_rate"],
            discount_amount=r["discount_amount"],
            revenue=r["revenue"],
            cost=r["cost"],
            profit=r["profit"],
            profit_margin=r["profit_margin"],
            payment_method=r["payment_method"],
            order_status=r["order_status"]
        )
        new_sales.append(sale)
        
    db.bulk_save_objects(new_sales)
    db.commit()

    # 3. Generate Newspaper Report
    report = LLMService.generate_daily_newspaper(db, new_date)

    # 4. Trigger Email & WhatsApp
    email_res = EmailService.send_daily_email(db, new_date)
    wa_res = WhatsAppService.send_daily_whatsapp(db, new_date)

    return {
        "status": "success",
        "date": new_date,
        "orders_generated": len(gen_records),
        "total_revenue": gen_result["total_revenue"],
        "total_profit": gen_result["total_profit"],
        "report": report,
        "email_delivery": email_res,
        "whatsapp_delivery": wa_res
    }
