#!/usr/bin/env python3
"""
Daily Alert Service — Standalone Runner
========================================
Runs the 8:00 AM automated stakeholder email alert system.

Usage:
  Start persistent 8:00 AM daily scheduler:
    python run_daily_alert_service.py

  Trigger the pipeline immediately (for testing / on-demand):
    python run_daily_alert_service.py --trigger-now

  Trigger for a specific date:
    python run_daily_alert_service.py --trigger-now --date 2026-08-20
"""

import sys
import logging
import argparse
from datetime import datetime
from pathlib import Path

# ── Load .env file if it exists ────────────────────────────────────────────────
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=env_file)

# ── Logging configuration ──────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("data/daily_alert_service.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("DailyAlertRunner")


def main():
    Path("data").mkdir(exist_ok=True)
    Path("data/generated_daily_sales").mkdir(parents=True, exist_ok=True)

    parser = argparse.ArgumentParser(
        description="AI Sales Intelligence — Daily 8:00 AM Email Alert Service"
    )
    parser.add_argument(
        "--trigger-now",
        action="store_true",
        help="Run the daily alert pipeline immediately instead of waiting for 8:00 AM.",
    )
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="Target date (YYYY-MM-DD) to generate the report for. Defaults to next business date.",
    )
    args = parser.parse_args()

    if args.trigger_now:
        # ── Immediate on-demand execution ────────────────────────────────────
        target = args.date
        logger.info("=" * 70)
        logger.info("  AI SALES INTELLIGENCE — IMMEDIATE PIPELINE TRIGGER")
        logger.info(f"  Target Date : {target or 'Auto (next day from DB)'}")
        logger.info(f"  Triggered At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 70)

        from backend.app.services.daily_scheduler_service import run_daily_alert_workflow
        result = run_daily_alert_workflow(target_date_str=target)

        logger.info("\n" + "=" * 70)
        logger.info("  PIPELINE EXECUTION SUMMARY")
        logger.info("=" * 70)
        logger.info(f"  Status     : {result.get('status')}")
        logger.info(f"  Date       : {result.get('date')}")
        logger.info(f"  Started At : {result.get('started_at')}")
        logger.info(f"  Completed  : {result.get('completed_at')}")

        for step in result.get("steps", []):
            step_name = step.get("step", "").upper().ljust(18)
            details = {k: v for k, v in step.items() if k != "step"}
            logger.info(f"    [{step_name}]  {details}")

        if result.get("status") == "SUCCESS":
            # Find and display the output path
            email_step = next((s for s in result.get("steps", []) if s.get("step") == "email"), {})
            method = email_step.get("method", "")
            if method == "smtp":
                logger.info(f"\n  ✅ Email delivered via SMTP to: {email_step.get('detail')}")
            else:
                detail = email_step.get("detail", "data/generated_daily_sales/")
                logger.info(f"\n  ⚠️  SMTP not configured. Report saved to:\n     {detail}")
                logger.info("     Open this file in any browser to preview the email.")
        else:
            logger.error(f"\n  ❌ Pipeline failed: {result.get('error')}")
            sys.exit(1)

    else:
        # ── Persistent 8:00 AM scheduler mode ───────────────────────────────
        logger.info("=" * 70)
        logger.info("  AI SALES INTELLIGENCE — DAILY ALERT SERVICE STARTING")
        logger.info("  Schedule    : Every day at 08:00 AM IST (Asia/Kolkata)")
        logger.info(f"  Started At  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("  Press Ctrl+C to stop.")
        logger.info("=" * 70)

        from backend.app.services.daily_scheduler_service import start_scheduler
        try:
            start_scheduler(blocking=True)
        except (KeyboardInterrupt, SystemExit):
            logger.info("\n[DailyAlertRunner] Scheduler stopped by user.")


if __name__ == "__main__":
    main()
