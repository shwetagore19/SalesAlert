import json
from sqlalchemy.orm import Session
from pipeline.models import AlertRecord
from pipeline.analytics_service import AnalyticsService

class AlertService:
    @classmethod
    def evaluate_daily_alerts(cls, db: Session, target_date_str: str = None) -> list:
        kpis = AnalyticsService.get_daily_kpis(db, target_date_str)
        if not kpis or "date" not in kpis:
            return []

        date_str = kpis["date"]
        comps = kpis.get("comparisons", {})
        alerts = []

        # 1. Revenue Drop Alert
        rev_dod = comps.get("revenue_dod_pct", 0.0)
        if rev_dod < -10.0:
            alerts.append({
                "date": date_str,
                "alert_type": "REVENUE_DROP",
                "severity": "CRITICAL" if rev_dod < -20.0 else "WARNING",
                "title": f"Significant Revenue Decline ({rev_dod:.1f}%)",
                "message": f"Daily revenue decreased by {abs(rev_dod):.1f}% from Rs. {comps.get('prev_revenue', 0):,.2f} to Rs. {kpis.get('revenue', 0):,.2f}.",
                "metrics_json": json.dumps({"rev_dod_pct": rev_dod, "current_revenue": kpis.get("revenue"), "prev_revenue": comps.get("prev_revenue")})
            })

        # 2. Profit Margin Squeeze Warning
        margin_diff = comps.get("margin_dod_diff", 0.0)
        if rev_dod >= 0 and margin_diff < -2.0:
            alerts.append({
                "date": date_str,
                "alert_type": "MARGIN_SQUEEZE",
                "severity": "WARNING",
                "title": f"Profit Margin Squeeze ({margin_diff:.1f}% pts)",
                "message": f"Revenue grew by {rev_dod:.1f}%, but profit margin squeezed by {abs(margin_diff):.1f}% points due to increased discounting or higher product costs.",
                "metrics_json": json.dumps({"margin_diff": margin_diff, "current_margin": kpis.get("profit_margin"), "rev_dod_pct": rev_dod})
            })

        # 3. Regional Decline Alert
        reg_perf = AnalyticsService.get_regional_performance(db, date_str)
        declining_regions = reg_perf.get("declining_regions", [])
        for reg in declining_regions:
            if reg.get("growth_pct", 0.0) < -10.0:
                alerts.append({
                    "date": date_str,
                    "alert_type": "REGIONAL_DECLINE",
                    "severity": "WARNING",
                    "title": f"Regional Sales Drop in {reg['region']} ({reg['growth_pct']:.1f}%)",
                    "message": f"Sales in {reg['region']} dropped by {abs(reg['growth_pct']):.1f}% compared to yesterday.",
                    "metrics_json": json.dumps(reg)
                })

        # 4. Customer Acquisition Alert
        new_cust_dod = comps.get("new_cust_dod_pct", 0.0)
        if new_cust_dod < -15.0:
            alerts.append({
                "date": date_str,
                "alert_type": "CUSTOMER_ACQUISITION_DROP",
                "severity": "INFO",
                "title": f"New Customer Acquisition Drop ({new_cust_dod:.1f}%)",
                "message": f"New customer onboarding dropped by {abs(new_cust_dod):.1f}% today ({kpis.get('new_customers')} new customers vs previous period).",
                "metrics_json": json.dumps({"new_cust_dod_pct": new_cust_dod, "new_customers": kpis.get("new_customers")})
            })

        # Save alerts to DB
        saved_alerts = []
        for a in alerts:
            existing = db.query(AlertRecord).filter(
                AlertRecord.date == a["date"],
                AlertRecord.alert_type == a["alert_type"],
                AlertRecord.title == a["title"]
            ).first()
            if not existing:
                rec = AlertRecord(
                    date=a["date"],
                    alert_type=a["alert_type"],
                    severity=a["severity"],
                    title=a["title"],
                    message=a["message"],
                    metrics_json=a["metrics_json"]
                )
                db.add(rec)
                saved_alerts.append(rec)

        db.commit()

        # Query all alerts for target date
        all_today_records = db.query(AlertRecord).filter(AlertRecord.date == date_str).all()
        return [{
            "id": rec.id,
            "date": rec.date,
            "alert_type": rec.alert_type,
            "severity": rec.severity,
            "title": rec.title,
            "message": rec.message,
            "created_at": rec.created_at.strftime("%Y-%m-%d %H:%M:%S") if rec.created_at else ""
        } for rec in all_today_records]
