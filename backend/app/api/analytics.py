from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.database import get_db
from app.models.models import Startup, Deal, Financial, Shark, SharkDeal

router = APIRouter()

@router.get("/dashboard")
def get_dashboard_analytics(db: Session = Depends(get_db)):
    # 1. Season-by-season revenue and profit averages
    seasons = [1, 2, 3, 4, 5]
    season_trends = []
    
    for s in seasons:
        startups_in_season = db.query(Startup.id).filter(Startup.season == s).subquery()
        fin_stats = db.query(
            func.avg(Financial.revenue).label("avg_revenue"),
            func.avg(Financial.profit).label("avg_profit"),
            func.avg(Financial.gross_margin).label("avg_gross_margin"),
            func.avg(Financial.net_margin).label("avg_net_margin")
        ).filter(Financial.startup_id.in_(startups_in_season)).first()

        season_trends.append({
            "season": f"Season {s}",
            "avg_revenue_lakhs": round(fin_stats.avg_revenue or 0, 2),
            "avg_profit_lakhs": round(fin_stats.avg_profit or 0, 2),
            "avg_gross_margin": round(fin_stats.avg_gross_margin or 0, 2),
            "avg_net_margin": round(fin_stats.avg_net_margin or 0, 2),
        })

    # 2. Valuation asked vs final comparison (Top 10 biggest valuations)
    valuation_comparisons = []
    top_deals = db.query(Startup.name, Deal.ask_valuation, Deal.final_valuation, Deal.ask_equity, Deal.final_equity)\
        .join(Deal, Deal.startup_id == Startup.id)\
        .filter(Deal.deal_status == "funded")\
        .filter(Deal.final_valuation.isnot(None))\
        .order_by(desc(Deal.final_valuation))\
        .limit(15).all()

    for row in top_deals:
        valuation_comparisons.append({
            "name": row[0],
            "asked_valuation_lakhs": row[1],
            "final_valuation_lakhs": row[2],
            "asked_equity": row[3],
            "final_equity": row[4],
            "dilution_percentage": round(abs((row[4] or 0) - (row[3] or 0)), 2)
        })

    return {
        "season_trends": season_trends,
        "valuation_comparisons": valuation_comparisons
    }

@router.get("/leaderboard")
def get_leaderboard(db: Session = Depends(get_db)):
    # 1. Biggest Deal Ever
    biggest_deal = db.query(Startup.name, Startup.slug, Deal.final_deal_amount)\
        .join(Deal).filter(Deal.deal_status == "funded")\
        .order_by(desc(Deal.final_deal_amount)).first()

    # 2. Biggest Valuation Ever
    biggest_val = db.query(Startup.name, Startup.slug, Deal.final_valuation)\
        .join(Deal).filter(Deal.deal_status == "funded")\
        .order_by(desc(Deal.final_valuation)).first()

    # 3. Highest Revenue Startup
    highest_rev = db.query(Startup.name, Startup.slug, Financial.revenue)\
        .join(Financial).order_by(desc(Financial.revenue)).first()

    # 4. Lowest Valuation that got funded
    lowest_val = db.query(Startup.name, Startup.slug, Deal.final_valuation)\
        .join(Deal).filter(Deal.deal_status == "funded")\
        .filter(Deal.final_valuation > 0)\
        .order_by(Deal.final_valuation).first()

    # 5. Most Active Shark (by number of deals)
    most_active_shark = db.query(Shark.name, func.count(SharkDeal.id).label("deal_count"))\
        .join(SharkDeal, SharkDeal.shark_id == Shark.id)\
        .group_by(Shark.id).order_by(desc("deal_count")).first()

    # 6. Industry with most deals
    most_active_industry = db.query(Startup.industry, func.count(Startup.id).label("startup_count"))\
        .join(Deal).filter(Deal.deal_status == "funded")\
        .group_by(Startup.industry).order_by(desc("startup_count")).first()

    # 7. Highest EBITDA margin startup
    highest_ebitda_margin = db.query(Startup.name, Startup.slug, Financial.ebitda_margin)\
        .join(Financial)\
        .filter(Financial.ebitda_margin.isnot(None))\
        .order_by(desc(Financial.ebitda_margin)).first()

    # 8. Fastest growing startup (standing in: highest revenue to valuation ratio, or highest net profit)
    fastest_growing = db.query(Startup.name, Startup.slug, Financial.profit)\
        .join(Financial)\
        .filter(Financial.profit.isnot(None))\
        .order_by(desc(Financial.profit)).first()

    return {
        "biggest_deal": {
            "name": biggest_deal[0] if biggest_deal else "Not Disclosed",
            "slug": biggest_deal[1] if biggest_deal else "",
            "value": f"₹{biggest_deal[2]} Lakhs" if biggest_deal and biggest_deal[2] else "Not Disclosed"
        },
        "biggest_valuation": {
            "name": biggest_val[0] if biggest_val else "Not Disclosed",
            "slug": biggest_val[1] if biggest_val else "",
            "value": f"₹{biggest_val[2]/100:.2f} Cr" if biggest_val and biggest_val[2] else "Not Disclosed"
        },
        "highest_revenue": {
            "name": highest_rev[0] if highest_rev else "Not Disclosed",
            "slug": highest_rev[1] if highest_rev else "",
            "value": f"₹{highest_rev[2]} Lakhs" if highest_rev and highest_rev[2] else "Not Disclosed"
        },
        "lowest_valuation_funded": {
            "name": lowest_val[0] if lowest_val else "Not Disclosed",
            "slug": lowest_val[1] if lowest_val else "",
            "value": f"₹{lowest_val[2]} Lakhs" if lowest_val and lowest_val[2] else "Not Disclosed"
        },
        "most_active_shark": {
            "name": most_active_shark[0] if most_active_shark else "Not Disclosed",
            "value": f"{most_active_shark[1]} Deals Made" if most_active_shark else "Not Disclosed"
        },
        "industry_most_deals": {
            "name": most_active_industry[0] if most_active_industry else "Not Disclosed",
            "value": f"{most_active_industry[1]} Startups Funded" if most_active_industry else "Not Disclosed"
        },
        "highest_ebitda_margin": {
            "name": highest_ebitda_margin[0] if highest_ebitda_margin else "Not Disclosed",
            "slug": highest_ebitda_margin[1] if highest_ebitda_margin else "",
            "value": f"{highest_ebitda_margin[2]:.1f}% Margin" if highest_ebitda_margin and highest_ebitda_margin[2] else "Not Disclosed"
        },
        "fastest_growing": {
            "name": fastest_growing[0] if fastest_growing else "Not Disclosed",
            "slug": fastest_growing[1] if fastest_growing else "",
            "value": f"₹{fastest_growing[2]:.2f} Lakhs Net Profit" if fastest_growing and fastest_growing[2] else "Not Disclosed"
        }
    }
