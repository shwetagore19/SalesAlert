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
        return "#16a34a" if positive else "#dc2626"

    @classmethod
    def build_html_report(
        cls,
        kpis: dict,
        alerts: list,
        root_cause: dict,
        recommendations: list,
    ) -> str:
        """Builds a mobile-responsive HTML email body from real, verified KPI data."""

        date_str = kpis.get("date", datetime.now().strftime("%Y-%m-%d"))
        comps = kpis.get("comparisons", {})

        # ── Colour-coded KPI rows ──────────────────────────────────────────────
        def kpi_row(label: str, value: str, pct: float, invert=False, note="") -> str:
            arrow = cls._trend_arrow(pct)
            color = cls._trend_color(pct, invert)
            note_html = f"<div style='color:#94a3b8;font-size:11px;margin-top:2px;'>{note}</div>" if note else ""
            return f"""
            <tr>
              <td style='padding:12px 16px;border-bottom:1px solid #1e293b;color:#e2e8f0;font-size:14px;'>{label}</td>
              <td style='padding:12px 16px;border-bottom:1px solid #1e293b;color:#f8fafc;font-weight:700;font-size:14px;text-align:right;'>
                {value}{note_html}
              </td>
              <td style='padding:12px 16px;border-bottom:1px solid #1e293b;font-weight:700;font-size:13px;text-align:right;color:{color};'>{arrow}</td>
            </tr>"""

        revenue = kpis.get("revenue", 0)
        profit = kpis.get("profit", 0)
        margin = kpis.get("profit_margin", 0)
        orders = kpis.get("total_orders", 0)
        aov = kpis.get("average_order_value", 0)
        new_cust = kpis.get("new_customers", 0)
        returning_cust = kpis.get("returning_customers", 0)

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
            + kpi_row("💳 Avg. Order Value", f"Rs. {aov:,.2f}", 0)
            + kpi_row("🆕 New Customers", str(new_cust), comps.get("new_cust_dod_pct", 0))
            + kpi_row("🔁 Returning Customers", str(returning_cust), 0)
        )

        # ── Alert Blocks ────────────────────────────────────────────────────────
        alert_html = ""
        if alerts:
            alert_items = ""
            for a in alerts:
                is_critical = a.get("severity") == "CRITICAL"
                bg = "#450a0a" if is_critical else "#431407"
                border = "#dc2626" if is_critical else "#ea580c"
                badge = "🔴 CRITICAL" if is_critical else "🟡 WARNING"
                alert_items += f"""
                <div style='background:{bg};border-left:4px solid {border};border-radius:6px;padding:12px 16px;margin-bottom:10px;'>
                  <div style='color:#f8fafc;font-weight:700;font-size:13px;'>{badge} &nbsp; {a.get("title","Alert")}</div>
                  <div style='color:#cbd5e1;font-size:12px;margin-top:4px;line-height:1.5;'>{a.get("message","")}</div>
                </div>"""
            alert_html = f"""
            <tr><td colspan='3' style='padding:20px 16px 8px;'>
              <div style='color:#f97316;font-weight:800;font-size:15px;letter-spacing:.5px;margin-bottom:10px;'>⚠️ ACTIVE BUSINESS ALERTS</div>
              {alert_items}
            </td></tr>"""
        else:
            alert_html = """
            <tr><td colspan='3' style='padding:20px 16px 8px;'>
              <div style='background:#052e16;border:1px solid #16a34a;border-radius:8px;padding:12px 16px;color:#4ade80;font-weight:700;font-size:13px;'>
                ✅ No critical alerts detected — all KPIs within acceptable thresholds.
              </div>
            </td></tr>"""

        # ── Root Cause Narrative ────────────────────────────────────────────────
        narrative = root_cause.get("summary_narrative", "Root-cause data unavailable.")
        top_gainers = root_cause.get("top_product_gainers", [])
        top_losers = root_cause.get("top_product_losers", [])

        gainers_html = "".join([
            f"<div style='display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid #1e293b;'>"
            f"<span style='color:#e2e8f0;font-size:12px;'>{g.get('product','')}</span>"
            f"<span style='color:#4ade80;font-weight:700;font-size:12px;'>+Rs. {g.get('delta',0):,.0f}</span></div>"
            for g in top_gainers
        ]) or "<div style='color:#64748b;font-size:12px;'>No data</div>"

        losers_html = "".join([
            f"<div style='display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid #1e293b;'>"
            f"<span style='color:#e2e8f0;font-size:12px;'>{l.get('product','')}</span>"
            f"<span style='color:#f87171;font-weight:700;font-size:12px;'>Rs. {l.get('delta',0):,.0f}</span></div>"
            for l in top_losers
        ]) or "<div style='color:#64748b;font-size:12px;'>No data</div>"

        # ── Action Recommendations ──────────────────────────────────────────────
        recs_html = ""
        if recommendations:
            for i, rec in enumerate(recommendations[:5], 1):
                is_high = rec.get("priority") == "HIGH"
                badge_color = "#dc2626" if is_high else "#d97706"
                recs_html += f"""
                <div style='background:#0f172a;border:1px solid #334155;border-radius:8px;padding:14px;margin-bottom:10px;'>
                  <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;'>
                    <span style='color:#94a3b8;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.5px;'>{rec.get("area","")}</span>
                    <span style='background:{badge_color}22;color:{badge_color};font-size:10px;font-weight:800;padding:2px 8px;border-radius:20px;border:1px solid {badge_color}44;'>{rec.get("priority","")} PRIORITY</span>
                  </div>
                  <div style='color:#f8fafc;font-weight:700;font-size:13px;margin-bottom:4px;'>{i}. {rec.get("title","")}</div>
                  <div style='color:#cbd5e1;font-size:12px;line-height:1.5;'>{rec.get("description","")}</div>
                  <div style='margin-top:8px;padding-top:8px;border-top:1px solid #1e293b;color:#4ade80;font-size:11px;font-weight:700;'>Expected Impact: {rec.get("expected_impact","")}</div>
                </div>"""
        else:
            recs_html = "<div style='color:#64748b;font-size:13px;'>No action items generated.</div>"

        # ── Full HTML Template ──────────────────────────────────────────────────
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Daily Sales Intelligence Report — {date_str}</title>
</head>
<body style='margin:0;padding:0;background:#0a0a0a;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;'>
  <table width='100%' cellpadding='0' cellspacing='0' style='background:#0a0a0a;'>
    <tr><td align='center' style='padding:24px 12px;'>
      <table width='640' cellpadding='0' cellspacing='0' style='max-width:640px;width:100%;'>

        <!-- HEADER -->
        <tr><td style='background:linear-gradient(135deg,#1e3a5f,#1e1b4b);border-radius:16px 16px 0 0;padding:28px 32px;'>
          <div style='color:#93c5fd;font-size:12px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:6px;'>
            🤖 AI Sales Intelligence Engine
          </div>
          <h1 style='margin:0;color:#ffffff;font-size:24px;font-weight:900;letter-spacing:-.5px;'>
            Daily Business Summary
          </h1>
          <div style='color:#a5b4fc;font-size:14px;margin-top:6px;'>
            📅 Report Date: <strong style='color:#e2e8f0;'>{date_str}</strong> &nbsp;|&nbsp;
            ⏰ Generated at 08:00 AM IST
          </div>
        </td></tr>

        <!-- KPI SCORECARD -->
        <tr><td style='background:#0f172a;padding:0;'>
          <table width='100%' cellpadding='0' cellspacing='0'>
            <tr>
              <td style='padding:20px 16px 8px;' colspan='3'>
                <div style='color:#7dd3fc;font-weight:800;font-size:15px;letter-spacing:.5px;'>📊 KPI SCORECARD</div>
              </td>
            </tr>
            <tr style='background:#1e293b22;'>
              <th style='padding:8px 16px;text-align:left;color:#475569;font-size:11px;font-weight:700;letter-spacing:.5px;text-transform:uppercase;'>Metric</th>
              <th style='padding:8px 16px;text-align:right;color:#475569;font-size:11px;font-weight:700;letter-spacing:.5px;text-transform:uppercase;'>Today</th>
              <th style='padding:8px 16px;text-align:right;color:#475569;font-size:11px;font-weight:700;letter-spacing:.5px;text-transform:uppercase;'>DoD Change</th>
            </tr>
            {kpi_rows}
            {alert_html}
          </table>
        </td></tr>

        <!-- ROOT CAUSE SECTION -->
        <tr><td style='background:#0f172a;border-top:1px solid #1e293b;padding:24px 24px 0;'>
          <div style='color:#c4b5fd;font-weight:800;font-size:15px;letter-spacing:.5px;margin-bottom:12px;'>🔍 WHY DID IT HAPPEN? — Root-Cause Diagnosis</div>
          <div style='background:#1e293b;border-left:3px solid #6366f1;border-radius:6px;padding:14px 16px;color:#cbd5e1;font-size:13px;line-height:1.6;'>
            {narrative}
          </div>
          <div style='display:grid;margin-top:16px;'>
            <table width='100%' cellpadding='0' cellspacing='0'>
              <tr>
                <td width='48%' style='vertical-align:top;padding-right:8px;'>
                  <div style='background:#052e16;border:1px solid #166534;border-radius:8px;padding:14px;'>
                    <div style='color:#4ade80;font-weight:700;font-size:12px;text-transform:uppercase;letter-spacing:.5px;margin-bottom:10px;'>▲ Top Revenue Gainers</div>
                    {gainers_html}
                  </div>
                </td>
                <td width='4%'></td>
                <td width='48%' style='vertical-align:top;padding-left:8px;'>
                  <div style='background:#450a0a;border:1px solid #991b1b;border-radius:8px;padding:14px;'>
                    <div style='color:#f87171;font-weight:700;font-size:12px;text-transform:uppercase;letter-spacing:.5px;margin-bottom:10px;'>▼ Top Revenue Drag</div>
                    {losers_html}
                  </div>
                </td>
              </tr>
            </table>
          </div>
        </td></tr>

        <!-- MANAGER ACTIONS -->
        <tr><td style='background:#0f172a;border-top:1px solid #1e293b;padding:24px;'>
          <div style='color:#86efac;font-weight:800;font-size:15px;letter-spacing:.5px;margin-bottom:14px;'>🎯 MANAGER ACTION PLAN</div>
          {recs_html}
        </td></tr>

        <!-- FOOTER -->
        <tr><td style='background:#020617;border-top:1px solid #0f172a;border-radius:0 0 16px 16px;padding:20px 24px;'>
          <div style='color:#334155;font-size:11px;text-align:center;line-height:1.6;'>
            This report was auto-generated by the <strong style='color:#475569;'>AI Sales Intelligence Engine</strong> at 08:00 AM IST.<br>
            All KPI values are computed from verified transactional records in <code>sales_intelligence.db</code>.<br>
            Do not reply to this email. For queries, contact the Data Analytics team.
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

        # ── Fallback: Save HTML locally ─────────────────────────────────────────
        output_dir = Path("data/generated_daily_sales")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"daily_report_{date_str}.html"
        latest_path = output_dir / "latest_8am_business_summary.html"

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        with open(latest_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        msg = f"SMTP not configured or failed. Report saved to: {output_path}"
        logger.warning(f"[EmailService] {msg}")
        return {"sent": False, "method": "file_fallback", "detail": str(output_path)}
