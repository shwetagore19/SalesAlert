from sqlalchemy.orm import Session
from backend.app.services.root_cause_service import RootCauseService
from backend.app.services.alert_service import AlertService

class RecommendationService:
    """
    Action Recommendation Engine:
    Answers "What action should the manager take next?" by analyzing
    root causes, active business alerts, and discount margin erosion.
    """
    @classmethod
    def generate_recommendations(cls, db: Session, target_date_str: str = None) -> list:
        root_cause = RootCauseService.analyze_root_cause(db, target_date_str)
        alerts = AlertService.evaluate_daily_alerts(db, target_date_str)

        recommendations = []

        # 1. Evaluate Discount Erosion & High Discount Rates
        disc_rate = root_cause.get("current_discount_rate_avg", 0.0)
        disc_delta = root_cause.get("discount_rate_delta_pct", 0.0)
        prof_delta = root_cause.get("total_profit_delta", 0.0)

        if disc_delta > 1.5 and prof_delta < 0:
            recommendations.append({
                "priority": "HIGH",
                "area": "Discount Management",
                "title": "Cap Category Discount Rates",
                "description": f"Average discount rate increased by {disc_delta:+.1f}% points today (current average: {disc_rate:.1f}%), causing profit margin erosion. Restrict discount approvals to maximum 12%.",
                "expected_impact": "Recover 2.5% - 4.0% in net profit margin."
            })

        # 2. Evaluate Product Drag / Losers
        top_losers = root_cause.get("top_product_losers", [])
        if top_losers:
            worst = top_losers[0]
            recommendations.append({
                "priority": "HIGH",
                "area": "Product Strategy",
                "title": f"Investigate Demand Decline in '{worst['product']}'",
                "description": f"Product '{worst['product']}' experienced a revenue drop of Rs. {abs(worst['delta']):,.2f} today. Review stock levels and check if pricing or channel availability changed.",
                "expected_impact": f"Re-stabilize daily sales volume for '{worst['product']}'."
            })

        # 3. Evaluate Regional Underperformance
        reg_contribs = root_cause.get("regional_contributors", [])
        declining_regs = [r for r in reg_contribs if r["delta"] < -50000]
        if declining_regs:
            worst_reg = declining_regs[0]
            recommendations.append({
                "priority": "MEDIUM",
                "area": "Regional Operations",
                "title": f"Regional Sales Recovery for {worst_reg['region']}",
                "description": f"Territory {worst_reg['region']} dropped by Rs. {abs(worst_reg['delta']):,.2f} compared to yesterday. Audit local distribution and targeted promotional campaigns.",
                "expected_impact": f"Regain market share in {worst_reg['region']}."
            })

        # 4. Evaluate Channel Performance (Online vs Store vs B2B)
        ch_contribs = root_cause.get("channel_contributors", [])
        declining_channels = [c for c in ch_contribs if c["delta"] < 0]
        if declining_channels:
            worst_ch = declining_channels[0]
            recommendations.append({
                "priority": "MEDIUM",
                "area": "Sales Channels",
                "title": f"Optimize Channel Performance: {worst_ch['channel']}",
                "description": f"Sales via {worst_ch['channel']} channel fell by Rs. {abs(worst_ch['delta']):,.2f}. Check conversion rate and checkout friction on this channel.",
                "expected_impact": f"Improve {worst_ch['channel']} conversion rate by 15%."
            })

        # 5. Leverage High-Performing Product Growth
        top_gainers = root_cause.get("top_product_gainers", [])
        if top_gainers:
            best = top_gainers[0]
            recommendations.append({
                "priority": "LOW",
                "area": "Inventory & Promotion",
                "title": f"Ensure Inventory Availability for '{best['product']}'",
                "description": f"'{best['product']}' surged by Rs. {best['delta']:+,.2f} today. Ensure distribution centers are restocked to capture ongoing demand.",
                "expected_impact": "Prevent stockouts and maximize top-line revenue growth."
            })

        return recommendations
