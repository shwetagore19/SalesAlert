import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from backend.app.services.analytics_service import AnalyticsService

class RootCauseService:
    """
    Mathematical Variance Decomposition Engine:
    Answers "Why did sales/profit change today?" by breaking down day-over-day deltas
    into Category, Product, Region, Sales Channel, and Discount Impact contributors.
    """
    @classmethod
    def analyze_root_cause(cls, db: Session, target_date_str: str = None) -> dict:
        df = AnalyticsService._get_sales_df(db)
        if df.empty:
            return {}

        df["date_str"] = df["order_date"].dt.strftime("%Y-%m-%d")
        all_dates = sorted(df["date_str"].unique())
        
        if target_date_str is None or target_date_str not in all_dates:
            target_date_str = all_dates[-1]

        curr_dt = pd.to_datetime(target_date_str)
        prev_dt_str = (curr_dt - pd.Timedelta(days=1)).strftime("%Y-%m-%d")

        curr_df = df[(df["date_str"] == target_date_str) & (df["order_status"] != "Cancelled")]
        prev_df = df[(df["date_str"] == prev_dt_str) & (df["order_status"] != "Cancelled")]

        tot_rev_curr = float(curr_df["revenue"].sum()) if not curr_df.empty else 0.0
        tot_rev_prev = float(prev_df["revenue"].sum()) if not prev_df.empty else 0.0
        rev_delta = round(tot_rev_curr - tot_rev_prev, 2)
        rev_change_pct = round(((tot_rev_curr - tot_rev_prev) / tot_rev_prev * 100), 2) if tot_rev_prev > 0 else 0.0

        tot_prof_curr = float(curr_df["profit"].sum()) if not curr_df.empty else 0.0
        tot_prof_prev = float(prev_df["profit"].sum()) if not prev_df.empty else 0.0
        prof_delta = round(tot_prof_curr - tot_prof_prev, 2)
        prof_change_pct = round(((tot_prof_curr - tot_prof_prev) / tot_prof_prev * 100), 2) if tot_prof_prev > 0 else 0.0

        avg_disc_curr = float(curr_df["discount_rate"].mean()) * 100 if not curr_df.empty else 0.0
        avg_disc_prev = float(prev_df["discount_rate"].mean()) * 100 if not prev_df.empty else 0.0
        disc_delta_pct = round(avg_disc_curr - avg_disc_prev, 2)

        # 1. Category Decomposition
        cat_curr = curr_df.groupby("category")["revenue"].sum().to_dict()
        cat_prev = prev_df.groupby("category")["revenue"].sum().to_dict()
        all_cats = set(list(cat_curr.keys()) + list(cat_prev.keys()))

        cat_contributors = []
        for c in all_cats:
            rev_c = cat_curr.get(c, 0.0)
            rev_p = cat_prev.get(c, 0.0)
            delta = round(rev_c - rev_p, 2)
            pct = round(((delta / abs(rev_delta)) * 100), 1) if rev_delta != 0 else 0.0
            cat_contributors.append({"name": c, "current": round(rev_c, 2), "previous": round(rev_p, 2), "delta": delta, "share_pct": pct})
        cat_contributors.sort(key=lambda x: x["delta"], reverse=True)

        # 2. Product Drivers (Top Positive & Top Negative)
        prod_curr = curr_df.groupby("product")["revenue"].sum().to_dict()
        prod_prev = prev_df.groupby("product")["revenue"].sum().to_dict()
        all_prods = set(list(prod_curr.keys()) + list(prod_prev.keys()))

        prod_contributors = []
        for p in all_prods:
            r_c = prod_curr.get(p, 0.0)
            r_p = prod_prev.get(p, 0.0)
            delta = round(r_c - r_p, 2)
            prod_contributors.append({"product": p, "current": round(r_c, 2), "previous": round(r_p, 2), "delta": delta})

        top_gainers = sorted([p for p in prod_contributors if p["delta"] > 0], key=lambda x: x["delta"], reverse=True)[:3]
        top_losers = sorted([p for p in prod_contributors if p["delta"] < 0], key=lambda x: x["delta"])[:3]

        # 3. Channel Drivers (Online vs In-Store vs B2B)
        ch_curr = curr_df.groupby("sales_channel")["revenue"].sum().to_dict()
        ch_prev = prev_df.groupby("sales_channel")["revenue"].sum().to_dict()
        all_channels = set(list(ch_curr.keys()) + list(ch_prev.keys()))

        channel_contributors = []
        for ch in all_channels:
            rc = ch_curr.get(ch, 0.0)
            rp = ch_prev.get(ch, 0.0)
            delta = round(rc - rp, 2)
            channel_contributors.append({"channel": ch, "current": round(rc, 2), "previous": round(rp, 2), "delta": delta})
        channel_contributors.sort(key=lambda x: x["delta"], reverse=True)

        # 4. Regional Drivers
        reg_curr = curr_df.groupby("region")["revenue"].sum().to_dict()
        reg_prev = prev_df.groupby("region")["revenue"].sum().to_dict()
        all_regs = set(list(reg_curr.keys()) + list(reg_prev.keys()))

        regional_contributors = []
        for rg in all_regs:
            rc = reg_curr.get(rg, 0.0)
            rp = reg_prev.get(rg, 0.0)
            delta = round(rc - rp, 2)
            regional_contributors.append({"region": rg, "current": round(rc, 2), "previous": round(rp, 2), "delta": delta})
        regional_contributors.sort(key=lambda x: x["delta"], reverse=True)

        # Build Synthesis Narrative
        primary_driver = cat_contributors[0] if cat_contributors else {}
        primary_drag = cat_contributors[-1] if cat_contributors else {}

        summary_narrative = (
            f"Overall revenue changed by {rev_delta:+,.2f} ({rev_change_pct:+.1f}%) today. "
            f"Primary growth contributor was category '{primary_driver.get('name', 'N/A')}' ({primary_driver.get('delta', 0):+,.2f}), "
            f"while primary drag was category '{primary_drag.get('name', 'N/A')}' ({primary_drag.get('delta', 0):+,.2f}). "
            f"Average discount rate moved {disc_delta_pct:+.1f}% points to {avg_disc_curr:.1f}%."
        )

        return {
            "date": target_date_str,
            "previous_date": prev_dt_str,
            "summary_narrative": summary_narrative,
            "total_revenue_delta": rev_delta,
            "revenue_change_pct": rev_change_pct,
            "total_profit_delta": prof_delta,
            "profit_change_pct": prof_change_pct,
            "discount_rate_delta_pct": disc_delta_pct,
            "current_discount_rate_avg": round(avg_disc_curr, 2),
            "category_decomposition": cat_contributors,
            "top_product_gainers": top_gainers,
            "top_product_losers": top_losers,
            "channel_contributors": channel_contributors,
            "regional_contributors": regional_contributors
        }
