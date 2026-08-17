import os
import json
import httpx
from sqlalchemy.orm import Session
from pipeline.models import DailyReport
from pipeline.analytics_service import AnalyticsService
from pipeline.alert_service import AlertService

class LLMService:
    @classmethod
    def generate_daily_newspaper(cls, db: Session, target_date_str: str = None) -> dict:
        kpis = AnalyticsService.get_daily_kpis(db, target_date_str)
        if not kpis or "date" not in kpis:
            return {}

        date_str = kpis["date"]

        # Check existing report in DB
        existing = db.query(DailyReport).filter(DailyReport.date == date_str).first()
        if existing and not os.getenv("REGENERATE_REPORT"):
            return {
                "date": existing.date,
                "headline": existing.headline,
                "executive_summary": existing.executive_summary,
                "top_performers": existing.top_performers,
                "critical_alerts": existing.critical_alerts,
                "recommended_focus": existing.recommended_focus,
                "created_at": existing.created_at.strftime("%Y-%m-%d %H:%M:%S") if existing.created_at else ""
            }

        prod_perf = AnalyticsService.get_product_performance(db, date_str)
        reg_perf = AnalyticsService.get_regional_performance(db, date_str)
        alerts = AlertService.evaluate_daily_alerts(db, date_str)

        comps = kpis.get("comparisons", {})
        top_prod = prod_perf.get("top_products_by_revenue", [{}])[0].get("product", "N/A")
        top_reg = reg_perf.get("top_region", {}).get("region", "N/A")

        # Check provider and API keys
        llm_provider = os.getenv("LLM_PROVIDER", "fallback").lower()
        api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("GEMINI_API_KEY")
        report_data = None

        if llm_provider == "ollama":
            try:
                print(f"[LLMService] Attempting Ollama query...")
                report_data = cls._call_ollama_api(kpis, prod_perf, reg_perf, alerts)
            except Exception as e:
                print(f"[LLMService] Ollama query failed ({e}). Trying OpenAI API as backup if configured...")

        if not report_data and api_key:
            try:
                print(f"[LLMService] Attempting OpenAI API call...")
                report_data = cls._call_llm_api(api_key, kpis, prod_perf, reg_perf, alerts)
            except Exception as e:
                print(f"[LLMService] OpenAI API call failed ({e}). Falling back to rule-driven report synthesizer.")

        if not report_data:
            print("[LLMService] Using rule-driven report synthesizer.")
            report_data = cls._synthesize_fallback_report(kpis, prod_perf, reg_perf, alerts)

        # Save to DB
        if existing:
            db.delete(existing)
            db.commit()

        report_obj = DailyReport(
            date=date_str,
            headline=report_data["headline"],
            executive_summary=report_data["executive_summary"],
            top_performers=report_data["top_performers"],
            critical_alerts=report_data["critical_alerts"],
            recommended_focus=report_data["recommended_focus"]
        )
        db.add(report_obj)
        db.commit()

        return {
            "date": date_str,
            "headline": report_data["headline"],
            "executive_summary": report_data["executive_summary"],
            "top_performers": report_data["top_performers"],
            "critical_alerts": report_data["critical_alerts"],
            "recommended_focus": report_data["recommended_focus"],
            "created_at": report_obj.created_at.strftime("%Y-%m-%d %H:%M:%S") if report_obj.created_at else ""
        }

    @classmethod
    def _synthesize_fallback_report(cls, kpis: dict, prod_perf: dict, reg_perf: dict, alerts: list) -> dict:
        date_str = kpis.get("date", "")
        rev = kpis.get("revenue", 0.0)
        prof = kpis.get("profit", 0.0)
        margin = kpis.get("profit_margin", 0.0)
        orders = kpis.get("total_orders", 0)
        comps = kpis.get("comparisons", {})

        rev_dod = comps.get("revenue_dod_pct", 0.0)
        prof_dod = comps.get("profit_dod_pct", 0.0)

        # Headline
        rev_trend = "surges" if rev_dod > 5.0 else ("declines" if rev_dod < -5.0 else "remains steady")
        headline = f"Daily Business Newspaper: Revenue {rev_trend} to Rs. {rev:,.2f} ({rev_dod:+.1f}%)"

        # Executive Summary
        exec_summary = (
            f"On {date_str}, total business revenue reached Rs. {rev:,.2f} across {orders} completed orders. "
            f"Net profit stood at Rs. {prof:,.2f} representing a profit margin of {margin:.1f}%. "
            f"Compared to the previous period, revenue moved {rev_dod:+.1f}% and profit changed by {prof_dod:+.1f}%."
        )

        # Top Performers
        top_prods = prod_perf.get("top_products_by_revenue", [])
        top_prod_name = top_prods[0]["product"] if top_prods else "N/A"
        top_prod_rev = top_prods[0]["revenue"] if top_prods else 0.0

        top_reg = reg_perf.get("top_region", {})
        top_reg_name = top_reg.get("region", "N/A")
        top_reg_rev = top_reg.get("revenue", 0.0)

        top_performers = (
            f"Product Leader: {top_prod_name} generated the highest revenue today at Rs. {top_prod_rev:,.2f}. "
            f"Regional Leader: {top_reg_name} led across all territories with total sales of Rs. {top_reg_rev:,.2f}."
        )

        # Critical Alerts
        if alerts:
            alert_msgs = [f"- [{a['severity']}] {a['title']}: {a['message']}" for a in alerts]
            critical_alerts = "\n".join(alert_msgs)
        else:
            critical_alerts = "No critical business warnings detected today. Performance metrics meet operational thresholds."

        # Recommended Focus
        focus_items = []
        if rev_dod < 0:
            focus_items.append("Investigate drivers behind today's revenue decline and evaluate channel performance.")
        if comps.get("margin_dod_diff", 0.0) < -1.5:
            focus_items.append("Review discount rates across categories to prevent profit margin erosion.")
        declining_regs = reg_perf.get("declining_regions", [])
        if declining_regs:
            reg_names = ", ".join([r["region"] for r in declining_regs])
            focus_items.append(f"Conduct regional reviews for underperforming markets: {reg_names}.")
        if not focus_items:
            focus_items.append("Maintain current marketing push and monitor high-margin product inventory levels.")

        recommended_focus = "\n".join([f"{i+1}. {item}" for i, item in enumerate(focus_items)])

        return {
            "headline": headline,
            "executive_summary": exec_summary,
            "top_performers": top_performers,
            "critical_alerts": critical_alerts,
            "recommended_focus": recommended_focus
        }

    @classmethod
    def _call_llm_api(cls, api_key: str, kpis: dict, prod_perf: dict, reg_perf: dict, alerts: list) -> dict:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""
You are an expert executive business analyst. Based strictly on the verified daily sales facts provided below, generate a JSON object with 5 fields:
1. headline (string)
2. executive_summary (string)
3. top_performers (string)
4. critical_alerts (string)
5. recommended_focus (string)

Verified Facts:
- Date: {kpis.get('date')}
- Revenue: Rs. {kpis.get('revenue'):,.2f} ({kpis.get('comparisons', {}).get('revenue_dod_pct', 0.0):+.1f}% DoD)
- Profit: Rs. {kpis.get('profit'):,.2f} ({kpis.get('comparisons', {}).get('profit_dod_pct', 0.0):+.1f}% DoD)
- Profit Margin: {kpis.get('profit_margin'):.1f}%
- Orders: {kpis.get('total_orders')}
- Top Product: {prod_perf.get('top_products_by_revenue', [{}])[0].get('product', 'N/A')}
- Top Region: {reg_perf.get('top_region', {}).get('region', 'N/A')}
- Detected Alerts: {json.dumps(alerts)}

Respond ONLY with valid JSON. Do not invent any numbers.
"""
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"},
            "temperature": 0.3
        }
        
        with httpx.Client(timeout=15.0) as client:
            resp = client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            res_json = resp.json()
            content = res_json["choices"][0]["message"]["content"]
            return json.loads(content)

    @classmethod
    def _call_ollama_api(cls, kpis: dict, prod_perf: dict, reg_perf: dict, alerts: list) -> dict:
        url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
        model = os.getenv("OLLAMA_MODEL", "llama3")
        
        prompt = f"""
You are an expert executive business analyst. Based strictly on the daily sales facts provided below, generate a JSON object with exactly 5 fields:
1. headline (string)
2. executive_summary (string)
3. top_performers (string)
4. critical_alerts (string)
5. recommended_focus (string)

Verified Facts:
- Date: {kpis.get('date')}
- Revenue: Rs. {kpis.get('revenue'):,.2f} ({kpis.get('comparisons', {}).get('revenue_dod_pct', 0.0):+.1f}% DoD)
- Profit: Rs. {kpis.get('profit'):,.2f} ({kpis.get('comparisons', {}).get('profit_dod_pct', 0.0):+.1f}% DoD)
- Profit Margin: {kpis.get('profit_margin'):.1f}%
- Orders: {kpis.get('total_orders')}
- Top Product: {prod_perf.get('top_products_by_revenue', [{}])[0].get('product', 'N/A')}
- Top Region: {reg_perf.get('top_region', {}).get('region', 'N/A')}
- Detected Alerts: {json.dumps(alerts)}

Respond ONLY with valid JSON. Do not invent any numbers.
"""
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a professional business analyst. You respond only with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            "stream": False,
            "format": "json"
        }
        
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
            res_json = resp.json()
            content = res_json["message"]["content"]
            return json.loads(content)
