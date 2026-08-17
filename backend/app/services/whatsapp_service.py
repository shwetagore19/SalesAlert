import os
from sqlalchemy.orm import Session
from backend.app.services.analytics_service import AnalyticsService
from backend.app.services.llm_service import LLMService

class WhatsAppService:
    @classmethod
    def send_daily_whatsapp(cls, db: Session, target_date_str: str = None, recipient_phone: str = None) -> dict:
        kpis = AnalyticsService.get_daily_kpis(db, target_date_str)
        newspaper = LLMService.generate_daily_newspaper(db, target_date_str)

        date_str = kpis.get("date", "")
        rev = kpis.get("revenue", 0.0)
        prof = kpis.get("profit", 0.0)
        margin = kpis.get("profit_margin", 0.0)
        comps = kpis.get("comparisons", {})
        rev_dod = comps.get("revenue_dod_pct", 0.0)

        message_body = (
            f"📊 *DAILY BUSINESS REPORT ({date_str})*\n\n"
            f"• *Revenue*: Rs. {rev:,.2f} ({rev_dod:+.1f}% DoD)\n"
            f"• *Profit*: Rs. {prof:,.2f} ({margin:.1f}% Margin)\n"
            f"• *Orders*: {kpis.get('total_orders', 0)}\n\n"
            f"📰 *Headline*: {newspaper.get('headline')}\n\n"
            f"⚠️ *Alerts*:\n{newspaper.get('critical_alerts')}\n\n"
            f"🎯 *Action*: {newspaper.get('recommended_focus')}"
        )

        sid = os.getenv("WHATSAPP_ACCOUNT_SID")
        token = os.getenv("WHATSAPP_AUTH_TOKEN")
        from_num = os.getenv("WHATSAPP_FROM", "whatsapp:+14155238886")
        to_num = recipient_phone or os.getenv("MANAGER_PHONE", "whatsapp:+919876543210")

        if sid and token:
            try:
                from twilio.rest import Client
                client = Client(sid, token)
                msg = client.messages.create(body=message_body, from_=from_num, to=to_num)
                print(f"[WhatsAppService] WhatsApp sent via Twilio (SID: {msg.sid})")
                return {"status": "sent", "sid": msg.sid, "to": to_num}
            except Exception as e:
                print(f"[WhatsAppService] Error sending Twilio WhatsApp ({e})")
                return {"status": "error", "error": str(e), "message": message_body}
        else:
            print(f"[WhatsAppService] Twilio WhatsApp credentials not configured. Formatted daily WhatsApp payload for date {date_str}.")
            return {"status": "simulated", "message_payload": message_body}
