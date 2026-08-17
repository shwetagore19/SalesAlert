import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from pipeline.models import Sale

class AnalyticsService:
    @staticmethod
    def _get_sales_df(db: Session, start_date=None, end_date=None) -> pd.DataFrame:
        query = db.query(Sale)
        if start_date:
            query = query.filter(Sale.order_date >= start_date)
        if end_date:
            query = query.filter(Sale.order_date <= end_date)
            
        sales = query.all()
        if not sales:
            return pd.DataFrame()
            
        data = [{
            "id": s.id,
            "order_id": s.order_id,
            "order_date": s.order_date,
            "customer_id": s.customer_id,
            "product": s.product,
            "category": s.category,
            "region": s.region,
            "city": s.city,
            "sales_channel": s.sales_channel,
            "customer_type": s.customer_type,
            "quantity": s.quantity,
            "unit_price": s.unit_price,
            "discount_rate": s.discount_rate,
            "discount_amount": s.discount_amount,
            "revenue": s.revenue,
            "cost": s.cost,
            "profit": s.profit,
            "profit_margin": s.profit_margin,
            "payment_method": s.payment_method,
            "order_status": s.order_status
        } for s in sales]
        
        df = pd.DataFrame(data)
        df["order_date"] = pd.to_datetime(df["order_date"])
        return df

    @classmethod
    def get_daily_kpis(cls, db: Session, target_date_str: str = None) -> dict:
        df = cls._get_sales_df(db)
        if df.empty:
            return {}
            
        df["date_str"] = df["order_date"].dt.strftime("%Y-%m-%d")
        all_dates = sorted(df["date_str"].unique())
        
        if target_date_str is None or target_date_str not in all_dates:
            target_date_str = all_dates[-1]
            
        target_df = df[(df["date_str"] == target_date_str) & (df["order_status"] != "Cancelled")]
        
        # Calculate current day facts
        tot_rev = float(target_df["revenue"].sum()) if not target_df.empty else 0.0
        tot_cost = float(target_df["cost"].sum()) if not target_df.empty else 0.0
        tot_prof = float(target_df["profit"].sum()) if not target_df.empty else 0.0
        tot_orders = int(len(target_df))
        tot_qty = int(target_df["quantity"].sum()) if not target_df.empty else 0
        
        margin_pct = float(tot_prof / tot_rev * 100) if tot_rev > 0 else 0.0
        aov = float(tot_rev / tot_orders) if tot_orders > 0 else 0.0
        
        new_cust = int(len(target_df[target_df["customer_type"] == "New"]["customer_id"].unique())) if not target_df.empty else 0
        ret_cust = int(len(target_df[target_df["customer_type"] == "Returning"]["customer_id"].unique())) if not target_df.empty else 0

        # Day-over-Day (DoD) Comparison (T vs T-1)
        curr_dt = pd.to_datetime(target_date_str)
        prev_dt_str = (curr_dt - timedelta(days=1)).strftime("%Y-%m-%d")
        prev_df = df[(df["date_str"] == prev_dt_str) & (df["order_status"] != "Cancelled")]
        
        prev_rev = float(prev_df["revenue"].sum()) if not prev_df.empty else 0.0
        prev_prof = float(prev_df["profit"].sum()) if not prev_df.empty else 0.0
        prev_orders = int(len(prev_df))
        prev_margin = float(prev_prof / prev_rev * 100) if prev_rev > 0 else 0.0
        prev_new_cust = int(len(prev_df[prev_df["customer_type"] == "New"]["customer_id"].unique())) if not prev_df.empty else 0
        
        rev_dod_pct = round(((tot_rev - prev_rev) / prev_rev * 100), 2) if prev_rev > 0 else 0.0
        prof_dod_pct = round(((tot_prof - prev_prof) / prev_prof * 100), 2) if prev_prof > 0 else 0.0
        orders_dod_pct = round(((tot_orders - prev_orders) / prev_orders * 100), 2) if prev_orders > 0 else 0.0
        margin_dod_pct = round(margin_pct - prev_margin, 2)
        new_cust_dod_pct = round(((new_cust - prev_new_cust) / prev_new_cust * 100), 2) if prev_new_cust > 0 else 0.0

        # Week-over-Week (WoW) Comparison (T vs T-7)
        wow_dt_str = (curr_dt - timedelta(days=7)).strftime("%Y-%m-%d")
        wow_df = df[(df["date_str"] == wow_dt_str) & (df["order_status"] != "Cancelled")]
        
        wow_rev = float(wow_df["revenue"].sum()) if not wow_df.empty else 0.0
        wow_prof = float(wow_df["profit"].sum()) if not wow_df.empty else 0.0
        wow_orders = int(len(wow_df))
        wow_margin = float(wow_prof / wow_rev * 100) if wow_rev > 0 else 0.0
        
        rev_wow_pct = round(((tot_rev - wow_rev) / wow_rev * 100), 2) if wow_rev > 0 else 0.0
        prof_wow_pct = round(((tot_prof - wow_prof) / wow_prof * 100), 2) if wow_prof > 0 else 0.0
        orders_wow_pct = round(((tot_orders - wow_orders) / wow_orders * 100), 2) if wow_orders > 0 else 0.0

        return {
            "date": target_date_str,
            "previous_date": prev_dt_str,
            "revenue": round(tot_rev, 2),
            "cost": round(tot_cost, 2),
            "profit": round(tot_prof, 2),
            "profit_margin": round(margin_pct, 2),
            "total_orders": tot_orders,
            "quantity_sold": tot_qty,
            "average_order_value": round(aov, 2),
            "new_customers": new_cust,
            "returning_customers": ret_cust,
            "comparisons": {
                "revenue_dod_pct": rev_dod_pct,
                "profit_dod_pct": prof_dod_pct,
                "orders_dod_pct": orders_dod_pct,
                "margin_dod_diff": margin_dod_pct,
                "new_cust_dod_pct": new_cust_dod_pct,
                "prev_revenue": round(prev_rev, 2),
                "prev_profit": round(prev_prof, 2),
                "revenue_wow_pct": rev_wow_pct,
                "profit_wow_pct": prof_wow_pct,
                "orders_wow_pct": orders_wow_pct,
                "wow_revenue": round(wow_rev, 2)
            }
        }

    @classmethod
    def get_data_source_metadata(cls, db: Session) -> dict:
        total_records = db.query(Sale).count()
        first_record = db.query(Sale).order_by(Sale.order_date.asc()).first()
        last_record = db.query(Sale).order_by(Sale.order_date.desc()).first()

        return {
            "data_source": "SQLAlchemy Database (PostgreSQL / SQLite)",
            "total_sales_records": total_records,
            "start_date": first_record.order_date.strftime("%Y-%m-%d") if first_record else "N/A",
            "latest_date": last_record.order_date.strftime("%Y-%m-%d") if last_record else "N/A",
            "status": "Verified Real Data Engine"
        }

    @classmethod
    def get_product_performance(cls, db: Session, target_date_str: str = None) -> dict:
        df = cls._get_sales_df(db)
        if df.empty:
            return {}
            
        df["date_str"] = df["order_date"].dt.strftime("%Y-%m-%d")
        if target_date_str:
            subset = df[(df["date_str"] == target_date_str) & (df["order_status"] != "Cancelled")]
        else:
            subset = df[df["order_status"] != "Cancelled"]
            
        p_grp = subset.groupby("product").agg(
            revenue=("revenue", "sum"),
            profit=("profit", "sum"),
            quantity=("quantity", "sum"),
            order_count=("order_id", "count"),
            category=("category", "first"),
            avg_discount=("discount_rate", "mean")
        ).reset_index()

        p_grp["margin_pct"] = np.where(p_grp["revenue"] > 0, (p_grp["profit"] / p_grp["revenue"]) * 100, 0.0)
        p_grp = p_grp.round({"revenue": 2, "profit": 2, "margin_pct": 2, "avg_discount": 4})

        top_by_revenue = p_grp.sort_values(by="revenue", ascending=False).to_dict(orient="records")
        top_by_profit = p_grp.sort_values(by="profit", ascending=False).to_dict(orient="records")
        worst_by_profit = p_grp.sort_values(by="profit", ascending=True).to_dict(orient="records")

        # Category breakdown
        cat_grp = subset.groupby("category").agg(
            revenue=("revenue", "sum"),
            profit=("profit", "sum"),
            quantity=("quantity", "sum")
        ).reset_index()
        cat_grp["margin_pct"] = np.where(cat_grp["revenue"] > 0, (cat_grp["profit"] / cat_grp["revenue"]) * 100, 0.0)
        cat_breakdown = cat_grp.round({"revenue": 2, "profit": 2, "margin_pct": 2}).to_dict(orient="records")

        return {
            "top_products_by_revenue": top_by_revenue[:5],
            "top_products_by_profit": top_by_profit[:5],
            "underperforming_products": worst_by_profit[:5],
            "category_breakdown": cat_breakdown,
            "all_products": top_by_revenue
        }

    @classmethod
    def get_regional_performance(cls, db: Session, target_date_str: str = None) -> dict:
        df = cls._get_sales_df(db)
        if df.empty:
            return {}

        df["date_str"] = df["order_date"].dt.strftime("%Y-%m-%d")
        all_dates = sorted(df["date_str"].unique())
        
        if target_date_str is None or target_date_str not in all_dates:
            target_date_str = all_dates[-1]

        curr_df = df[(df["date_str"] == target_date_str) & (df["order_status"] != "Cancelled")]
        curr_dt = pd.to_datetime(target_date_str)
        prev_dt_str = (curr_dt - timedelta(days=1)).strftime("%Y-%m-%d")
        prev_df = df[(df["date_str"] == prev_dt_str) & (df["order_status"] != "Cancelled")]

        reg_curr = curr_df.groupby("region").agg(
            revenue=("revenue", "sum"),
            profit=("profit", "sum"),
            orders=("order_id", "count")
        ).reset_index()
        reg_curr["margin_pct"] = np.where(reg_curr["revenue"] > 0, (reg_curr["profit"] / reg_curr["revenue"]) * 100, 0.0)

        reg_prev = prev_df.groupby("region").agg(
            prev_revenue=("revenue", "sum"),
            prev_profit=("profit", "sum")
        ).reset_index()

        reg_merged = pd.merge(reg_curr, reg_prev, on="region", how="outer").fillna(0.0)
        reg_merged["growth_pct"] = np.where(
            reg_merged["prev_revenue"] > 0,
            ((reg_merged["revenue"] - reg_merged["prev_revenue"]) / reg_merged["prev_revenue"]) * 100,
            0.0
        )
        reg_merged = reg_merged.round({"revenue": 2, "profit": 2, "margin_pct": 2, "prev_revenue": 2, "growth_pct": 2})

        return {
            "date": target_date_str,
            "regional_summary": reg_merged.to_dict(orient="records"),
            "top_region": reg_merged.sort_values(by="revenue", ascending=False).iloc[0].to_dict() if not reg_merged.empty else {},
            "declining_regions": reg_merged[reg_merged["growth_pct"] < 0].to_dict(orient="records")
        }

    @classmethod
    def get_trend_series(cls, db: Session, days: int = 30) -> list:
        df = cls._get_sales_df(db)
        if df.empty:
            return []

        df["date_str"] = df["order_date"].dt.strftime("%Y-%m-%d")
        valid_df = df[df["order_status"] != "Cancelled"]
        
        daily_grp = valid_df.groupby("date_str").agg(
            revenue=("revenue", "sum"),
            profit=("profit", "sum"),
            cost=("cost", "sum"),
            orders=("order_id", "count"),
            quantity=("quantity", "sum"),
            new_customers=("customer_type", lambda x: (x == "New").sum())
        ).reset_index()

        daily_grp["profit_margin"] = np.where(daily_grp["revenue"] > 0, (daily_grp["profit"] / daily_grp["revenue"]) * 100, 0.0)
        daily_grp = daily_grp.round({"revenue": 2, "profit": 2, "cost": 2, "profit_margin": 2}).sort_values(by="date_str")

        return daily_grp.tail(days).to_dict(orient="records")

    @classmethod
    def get_channel_performance(cls, db: Session, target_date_str: str = None) -> list:
        df = cls._get_sales_df(db)
        if df.empty:
            return []

        df["date_str"] = df["order_date"].dt.strftime("%Y-%m-%d")
        if target_date_str:
            subset = df[(df["date_str"] == target_date_str) & (df["order_status"] != "Cancelled")]
        else:
            subset = df[df["order_status"] != "Cancelled"]

        ch_grp = subset.groupby("sales_channel").agg(
            revenue=("revenue", "sum"),
            profit=("profit", "sum"),
            orders=("order_id", "count"),
            quantity=("quantity", "sum")
        ).reset_index()

        ch_grp["margin_pct"] = np.where(ch_grp["revenue"] > 0, (ch_grp["profit"] / ch_grp["revenue"]) * 100, 0.0)
        ch_grp["aov"] = np.where(ch_grp["orders"] > 0, ch_grp["revenue"] / ch_grp["orders"], 0.0)
        ch_grp = ch_grp.round({"revenue": 2, "profit": 2, "margin_pct": 2, "aov": 2})

        return ch_grp.to_dict(orient="records")

    @classmethod
    def get_discount_impact(cls, db: Session) -> dict:
        df = cls._get_sales_df(db)
        if df.empty:
            return {}

        valid_df = df[df["order_status"] != "Cancelled"].copy()
        
        # Bin discount rates into tiers
        bins = [-0.01, 0.05, 0.10, 0.15, 0.20, 1.0]
        labels = ["0-5%", "5-10%", "10-15%", "15-20%", ">20%"]
        valid_df["discount_tier"] = pd.cut(valid_df["discount_rate"], bins=bins, labels=labels)

        tier_grp = valid_df.groupby("discount_tier", observed=False).agg(
            revenue=("revenue", "sum"),
            profit=("profit", "sum"),
            orders=("order_id", "count"),
            avg_discount=("discount_rate", "mean")
        ).reset_index()

        tier_grp["margin_pct"] = np.where(tier_grp["revenue"] > 0, (tier_grp["profit"] / tier_grp["revenue"]) * 100, 0.0)
        tier_grp["avg_discount_pct"] = (tier_grp["avg_discount"] * 100).round(1)
        tier_grp = tier_grp.round({"revenue": 2, "profit": 2, "margin_pct": 2})

        return {
            "discount_tiers": tier_grp.to_dict(orient="records"),
            "overall_avg_discount_pct": round(float(valid_df["discount_rate"].mean() * 100), 2)
        }

