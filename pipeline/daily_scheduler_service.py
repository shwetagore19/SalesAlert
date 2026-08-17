"""
Daily Scheduler Service
Runs the complete 8:00 AM pipeline:
  Data Generation → Validation → DB Persistence → KPI Calculation →
  Alert Detection → Root-Cause Analysis → Recommendations → Email Delivery
"""

import logging
from datetime import datetime, timezone, timedelta
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

# IST = UTC+5:30 → 8:00 AM IST = 2:30 AM UTC
IST_OFFSET = timedelta(hours=5, minutes=30)

def run_daily_alert_workflow(target_date_str: str = None) -> dict:
    """
    Executes the complete 8-step Sales Intelligence pipeline.
    Returns a summary dict of the run results.
    """
    from pipeline.database import SessionLocal, init_db
    from pipeline.analytics_service import AnalyticsService
    from pipeline.alert_service import AlertService
    from pipeline.root_cause_service import RootCauseService
    from pipeline.recommendation_service import RecommendationService
    from pipeline.email_service import EmailService
    from pipeline.data_validation_service import DataValidationService
    from pipeline.models import Sale
    from sqlalchemy import inspect

    from pathlib import Path
    import pandas as pd

    init_db()
    db = SessionLocal()
    results = {"started_at": datetime.now().isoformat(), "steps": []}

    try:
        # ── STEP 1: Generate Synthetic Daily Transactions ─────────────────────
        logger.info("[DailyPipeline] Step 1: Generating synthetic daily transactions...")
        if target_date_str is None:
            # Determine the next date based on the last record in the database
            last_sale = db.query(Sale).order_by(Sale.order_date.desc()).first()
            if last_sale:
                last_dt = pd.to_datetime(last_sale.order_date)
                target_date_str = (last_dt + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
            else:
                target_date_str = datetime.now().strftime("%Y-%m-%d")

        logger.info(f"[DailyPipeline] Target date for generation: {target_date_str}")
        from pipeline.daily_data_generator import DailyDataGenerator
        generator = DailyDataGenerator()
        gen_result = generator.generate_day(target_date_str)
        # generate_day returns a dict with key "records"
        raw_records = gen_result.get("records", []) if isinstance(gen_result, dict) else []
        results["steps"].append({"step": "generate", "records_generated": len(raw_records)})
        logger.info(f"[DailyPipeline] Step 1 DONE: {len(raw_records)} records generated for {target_date_str}")

        # ── STEP 2: Validate & Clean ──────────────────────────────────────────
        logger.info("[DailyPipeline] Step 2: Validating & cleaning sales batch...")
        val_result = DataValidationService.validate_and_clean_sales_batch(raw_records or [])
        cleaned = val_result["valid_records"]
        results["steps"].append({
            "step": "validate",
            "total_input": val_result["total_input"],
            "valid": val_result["valid_count"],
            "dropped": val_result["dropped_count"]
        })
        logger.info(f"[DailyPipeline] Step 2 DONE: {val_result['valid_count']} valid / {val_result['dropped_count']} dropped")

        # ── STEP 3: Persist to Database ───────────────────────────────────────
        logger.info("[DailyPipeline] Step 3: Persisting to database...")
        model_cols = {c.key for c in inspect(Sale).mapper.column_attrs}
        new_sales = []
        for rec in cleaned:
            filtered = {k: v for k, v in rec.items() if k in model_cols}
            # Convert order_date string → Python datetime (SQLite requires datetime object)
            if "order_date" in filtered and isinstance(filtered["order_date"], str):
                filtered["order_date"] = pd.to_datetime(filtered["order_date"]).to_pydatetime()
            new_sales.append(Sale(**filtered))
        db.bulk_save_objects(new_sales)
        db.commit()
        results["steps"].append({"step": "persist", "records_saved": len(new_sales)})
        logger.info(f"[DailyPipeline] Step 3 DONE: {len(new_sales)} records saved to database for {target_date_str}")

        # ── STEP 4: Compute KPIs ───────────────────────────────────────────────
        logger.info("[DailyPipeline] Step 4: Computing KPIs...")
        kpis = AnalyticsService.get_daily_kpis(db, target_date_str)
        comps = kpis.get("comparisons", {})
        results["steps"].append({
            "step": "kpis",
            "revenue": kpis.get("revenue"),
            "profit": kpis.get("profit"),
            "margin_pct": kpis.get("profit_margin"),
            "orders": kpis.get("total_orders"),
            "rev_dod_pct": comps.get("revenue_dod_pct"),
        })
        logger.info(f"[DailyPipeline] Step 4 DONE: Revenue=Rs.{kpis.get('revenue', 0):,.2f} | Profit=Rs.{kpis.get('profit', 0):,.2f} | Margin={kpis.get('profit_margin', 0):.2f}%")

        # ── STEP 5: Detect Business Alerts ────────────────────────────────────
        logger.info("[DailyPipeline] Step 5: Detecting business anomalies and alerts...")
        alerts = AlertService.evaluate_daily_alerts(db, target_date_str)
        results["steps"].append({"step": "alerts", "count": len(alerts)})
        logger.info(f"[DailyPipeline] Step 5 DONE: {len(alerts)} active alerts")

        # ── STEP 6: Root-Cause Variance Decomposition ─────────────────────────
        logger.info("[DailyPipeline] Step 6: Running root-cause variance decomposition...")
        root_cause = RootCauseService.analyze_root_cause(db, target_date_str)
        results["steps"].append({"step": "root_cause", "narrative_available": bool(root_cause.get("summary_narrative"))})
        logger.info(f"[DailyPipeline] Step 6 DONE: {root_cause.get('summary_narrative', 'N/A')[:80]}...")

        # ── STEP 7: Generate Manager Recommendations ──────────────────────────
        logger.info("[DailyPipeline] Step 7: Generating manager action recommendations...")
        recommendations = RecommendationService.generate_recommendations(db, target_date_str)
        results["steps"].append({"step": "recommendations", "count": len(recommendations)})
        logger.info(f"[DailyPipeline] Step 7 DONE: {len(recommendations)} recommendations generated")

        # ── STEP 8: Generate Newspaper, Build HTML Report & Send Email ────────
        logger.info("[DailyPipeline] Step 8: Generating insights, building HTML report and delivering email...")
        delivery = EmailService.send_daily_email(db, target_date_str)
        results["steps"].append({"step": "email", **delivery})
        logger.info(f"[DailyPipeline] Step 8 DONE: {delivery}")

        results["status"] = "SUCCESS"
        results["date"] = target_date_str
        results["completed_at"] = datetime.now().isoformat()
        logger.info(f"[DailyPipeline] === 8-STEP PIPELINE COMPLETE for {target_date_str} ===")

    except Exception as exc:
        logger.error(f"[DailyPipeline] FATAL ERROR: {exc}", exc_info=True)
        results["status"] = "ERROR"
        results["error"] = str(exc)
    finally:
        db.close()

    return results


def start_scheduler(blocking: bool = True):
    """
    Starts the APScheduler cron job that fires at 08:00 AM IST every day.
    blocking=True  → keeps the process alive (for standalone runner)
    blocking=False → background scheduler (for embedding inside FastAPI)
    """
    SchedulerClass = BlockingScheduler if blocking else BackgroundScheduler
    scheduler = SchedulerClass(timezone="Asia/Kolkata")

    # Cron trigger: 8:00 AM IST every day
    scheduler.add_job(
        func=run_daily_alert_workflow,
        trigger=CronTrigger(hour=8, minute=0, timezone="Asia/Kolkata"),
        id="daily_8am_business_alert",
        name="Daily 8:00 AM Business Intelligence Report",
        replace_existing=True,
    )

    logger.info("[Scheduler] Daily 8:00 AM alert job registered (Asia/Kolkata timezone).")
    scheduler.start()
    return scheduler
