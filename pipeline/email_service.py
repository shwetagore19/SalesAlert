"""
Stakeholder Email Service
Formats and delivers a daily executive business summary email using real KPI data.
"""

import smtplib
import os
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class EmailService:
    """Formats and sends the daily 8:00 AM stakeholder business summary email."""

    @staticmethod
    def _trend_arrow(pct: float) -> str:
        if pct > 0:
            return f"▲ +{pct:.1f}%"
        elif pct < 0:
            return f"▼ {pct:.1f}%"
        return "─ 0.0%"

    @staticmethod
    def _trend_color(pct: float, invert: bool = False) -> str:
        positive = pct > 0
        if invert:
            positive = not positive
        return "#15803d" if positive else "#b91c1c"

    @classmethod
    def build_html_report(
        cls,
        kpis: dict,
        alerts: list,
        root_cause: dict,
        recommendations: list,
        newspaper: dict = None,
    ) -> str:
        """Builds a bright, clean, mobile-responsive HTML email body from KPI data."""
        date_str = kpis.get("date", datetime.now().strftime("%Y-%m-%d"))
        comps = kpis.get("comparisons", {})

        # Extract LLM newspaper fields if available
        newspaper = newspaper or {}
        headline = newspaper.get("headline", "")
        executive_summary = newspaper.get("executive_summary", "")
        recommended_focus = newspaper.get("recommended_focus", "")

        # Use LLM executive summary or fall back to root-cause summary narrative
        summary_text = executive_summary or root_cause.get("summary_narrative", "Daily summary unavailable.")

        # ── Colour-coded KPI rows ──────────────────────────────────────────────
        def kpi_row(label: str, value: str, pct: float, invert=False, note="") -> str:
            arrow = cls._trend_arrow(pct)
            color = cls._trend_color(pct, invert)
            note_html = f"<span style='color:#64748b;font-size:10px;font-weight:normal;margin-left:8px;'>({note})</span>" if note else ""
            return f"""
            <tr style='border-bottom:1px solid #e2e8f0;'>
              <td style='padding:8px 12px;color:#334155;font-size:12px;'>{label}</td>
              <td style='padding:8px 12px;color:#0f172a;font-weight:700;font-size:12px;text-align:right;'>
                {value}{note_html}
              </td>
              <td style='padding:8px 12px;font-weight:700;font-size:12px;text-align:right;color:{color};'>{arrow}</td>
            </tr>"""

        revenue = kpis.get("revenue", 0)
        profit = kpis.get("profit", 0)
        margin = kpis.get("profit_margin", 0)
        orders = kpis.get("total_orders", 0)

        rev_dod = comps.get("revenue_dod_pct", 0)
        rev_wow = comps.get("revenue_wow_pct", 0)
        prof_dod = comps.get("profit_dod_pct", 0)
        orders_dod = comps.get("orders_dod_pct", 0)
        margin_diff = comps.get("margin_dod_diff", 0)

        kpi_rows = (
            kpi_row("💰 Daily Revenue", f"Rs. {revenue:,.2f}", rev_dod, note=f"WoW: {cls._trend_arrow(rev_wow)}")
            + kpi_row("📈 Net Profit", f"Rs. {profit:,.2f}", prof_dod)
            + kpi_row("📊 Profit Margin", f"{margin:.2f}%", margin_diff, note="Benchmark: >15.0%")
            + kpi_row("🛒 Total Orders", str(orders), orders_dod)
        )

        # ── Action Recommendations ──────────────────────────────────────────────
        recs_html = ""
        
        # Merge LLM recommended focus and rule-based recommendations
        combined_recs = []
        if recommended_focus:
            # Parse recommended focus line by line
            lines = [l.strip() for l in recommended_focus.split("\n") if l.strip()]
            for line in lines:
                # Remove leading numbers/bullets
                cleaned_line = line.lstrip("0123456789.-*• ")
                if cleaned_line:
                    combined_recs.append({
                        "area": "Operational Focus",
                        "priority": "HIGH",
                        "title": cleaned_line,
                        "description": "",
                        "expected_impact": "Improve target operational efficiency."
                    })
                    
        # Add rule-based ones
        for rec in recommendations[:3]:
            # Avoid duplicating titles
            if not any(r["title"].lower() in rec["title"].lower() for r in combined_recs):
                combined_recs.append(rec)

        if combined_recs:
            for i, rec in enumerate(combined_recs[:3], 1):
                is_high = rec.get("priority") == "HIGH"
                badge_bg = "#fef2f2" if is_high else "#fffbeb"
                badge_color = "#ef4444" if is_high else "#d97706"
                recs_html += f"""
                <div style='background:#f8fafc;border:1px solid #f1f5f9;border-radius:4px;padding:8px 12px;margin-bottom:4px;'>
                  <table width='100%' cellpadding='0' cellspacing='0'>
                    <tr>
                      <td style='font-size:11px;color:#0f172a;font-weight:600;'>{i}. {rec.get("title","")}</td>
                      <td style='text-align:right;width:80px;'>
                        <span style='background:{badge_bg};color:{badge_color};font-size:8px;font-weight:700;padding:1px 4px;border-radius:3px;border:1px solid {badge_color}22;'>{rec.get("priority","")}</span>
                      </td>
                    </tr>
                  </table>
                </div>"""
        else:
            recs_html = "<div style='color:#64748b;font-size:11px;'>No action items generated.</div>"

        # ── Full HTML Template ──────────────────────────────────────────────────
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Daily Sales Intelligence Report — {date_str}</title>
</head>
<body style='margin:0;padding:0;background:#f1f5f9;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;-webkit-font-smoothing:antialiased;'>
  <table width='100%' cellpadding='0' cellspacing='0' style='background:#f1f5f9;padding:16px 8px;'>
    <tr><td align='center'>
      <table width='560' cellpadding='0' cellspacing='0' style='max-width:560px;width:100%;background:#ffffff;border:1px solid #cbd5e1;border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,0.03);overflow:hidden;'>

        <!-- HEADER -->
        <tr><td style='background:#f8fafc;border-bottom:1px solid #cbd5e1;padding:16px 20px;'>
          <div style='color:#0284c7;font-size:10px;font-weight:700;letter-spacing:1px;text-transform:uppercase;'>
            🤖 AI Sales Intelligence
          </div>
          <h1 style='margin:4px 0 0 0;color:#0f172a;font-size:15px;font-weight:800;letter-spacing:-.1px;line-height:1.3;'>
            {headline or "Daily Business Summary"}
          </h1>
          <div style='color:#64748b;font-size:11px;margin-top:4px;'>
            📅 Date: <strong style='color:#334155;'>{date_str}</strong> &nbsp;|&nbsp; Generated at 08:00 AM IST
          </div>
        </td></tr>

        <!-- 1. KPI SCORECARD -->
        <tr><td style='padding:16px 20px 8px;'>
          <div style='color:#0284c7;font-weight:800;font-size:12px;letter-spacing:.3px;margin-bottom:8px;text-transform:uppercase;'>📊 KPI Scorecard</div>
          <table width='100%' cellpadding='0' cellspacing='0' style='border:1px solid #e2e8f0;border-radius:6px;border-collapse:collapse;overflow:hidden;'>
            <tr style='background:#f8fafc;border-bottom:1px solid #e2e8f0;'>
              <th style='padding:6px 12px;text-align:left;color:#475569;font-size:10px;font-weight:700;letter-spacing:.3px;text-transform:uppercase;'>Metric</th>
              <th style='padding:6px 12px;text-align:right;color:#475569;font-size:10px;font-weight:700;letter-spacing:.3px;text-transform:uppercase;'>Value</th>
              <th style='padding:6px 12px;text-align:right;color:#475569;font-size:10px;font-weight:700;letter-spacing:.3px;text-transform:uppercase;'>DoD Change</th>
            </tr>
            {kpi_rows}
          </table>
        </td></tr>

        <!-- 2. DAILY SALES SUMMARY -->
        <tr><td style='padding:8px 20px 8px;'>
          <div style='color:#0284c7;font-weight:800;font-size:12px;letter-spacing:.3px;margin-bottom:6px;text-transform:uppercase;'>📰 Daily Sale Summary</div>
          <div style='background:#f0f9ff;border:1px solid #bae6fd;border-left:3px solid #0284c7;border-radius:6px;padding:12px;color:#0369a1;font-size:12px;line-height:1.5;font-weight:500;'>
            {summary_text}
          </div>
        </td></tr>

        <!-- 3. MANAGER ACTION PLAN -->
        <tr><td style='padding:8px 20px 16px;'>
          <div style='color:#0284c7;font-weight:800;font-size:12px;letter-spacing:.3px;margin-bottom:8px;text-transform:uppercase;'>🎯 Recommended Actions</div>
          {recs_html}
        </td></tr>

        <!-- FOOTER -->
        <tr><td style='background:#f8fafc;border-top:1px solid #cbd5e1;padding:12px 20px;'>
          <div style='color:#64748b;font-size:10px;text-align:center;line-height:1.5;'>
            Generated automatically by <strong>AI Sales Intelligence Engine</strong>.<br>
            All KPI calculations are verified using records in <code>sales_intelligence.db</code>.<br>
            Please do not reply to this email.
          </div>
        </td></tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""
        return html

    @classmethod
    def send_email(
        cls,
        html_content: str,
        date_str: str,
        subject: str = None,
    ) -> dict:
        """
        Sends the HTML report via SMTP.
        Falls back to saving the HTML file locally if SMTP credentials are not configured.
        Returns {"sent": bool, "method": str, "detail": str}
        """
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        sender_email = os.getenv("SENDER_EMAIL", "")
        sender_password = os.getenv("SENDER_PASSWORD", "")
        recipient_emails_raw = os.getenv("STAKEHOLDER_EMAIL", "")
        recipients = [e.strip() for e in recipient_emails_raw.split(",") if e.strip()]

        if not subject:
            subject = f"📊 Daily Business Intelligence Report — {date_str}"

        # ── Save HTML locally (always backup) ───────────────────────────────────
        output_dir = Path("data/generated_daily_sales")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"daily_report_{date_str}.html"
        latest_path = output_dir / "latest_8am_business_summary.html"

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            with open(latest_path, "w", encoding="utf-8") as f:
                f.write(html_content)
        except Exception as e:
            logger.error(f"[EmailService] Failed to save local HTML backup: {e}")

        # ── Try SMTP Delivery ───────────────────────────────────────────────────
        if sender_email and sender_password and recipients:
            try:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"] = f"Sales Intelligence <{sender_email}>"
                msg["To"] = ", ".join(recipients)
                msg.attach(MIMEText(html_content, "html"))

                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.ehlo()
                    server.starttls()
                    server.login(sender_email, sender_password)
                    server.sendmail(sender_email, recipients, msg.as_string())

                logger.info(f"[EmailService] Email delivered to: {recipients}")
                return {"sent": True, "method": "smtp", "detail": f"Delivered to {recipients}"}

            except Exception as exc:
                logger.error(f"[EmailService] SMTP delivery failed: {exc}")
                # Fall through to file fallback

        msg = f"SMTP not configured or failed. Report saved to: {output_path}"
        logger.warning(f"[EmailService] {msg}")
        return {"sent": False, "method": "file_fallback", "detail": str(output_path)}

    @classmethod
    def send_daily_email(cls, db, target_date_str: str = None, recipient_email: str = None) -> dict:
        """
        Builds the daily HTML report (incorporating LLM newspaper insights) and sends it.
        """
        from pipeline.analytics_service import AnalyticsService
        from pipeline.alert_service import AlertService
        from pipeline.root_cause_service import RootCauseService
        from pipeline.recommendation_service import RecommendationService
        from pipeline.llm_service import LLMService

        kpis = AnalyticsService.get_daily_kpis(db, target_date_str)
        if not kpis or "date" not in kpis:
            return {"sent": False, "error": "No KPIs available for the target date"}

        date_str = kpis["date"]
        alerts = AlertService.evaluate_daily_alerts(db, date_str)
        root_cause = RootCauseService.analyze_root_cause(db, date_str)
        recommendations = RecommendationService.generate_recommendations(db, date_str)
        
        # Generate LLM daily insights
        newspaper = LLMService.generate_daily_newspaper(db, date_str)

        # Build HTML report
        html_report = cls.build_html_report(kpis, alerts, root_cause, recommendations, newspaper)
        
        # Override recipient if provided
        if recipient_email:
            os.environ["STAKEHOLDER_EMAIL"] = recipient_email

        res = cls.send_email(html_report, date_str)
        return res
