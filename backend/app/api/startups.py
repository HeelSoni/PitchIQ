from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc
from typing import List, Optional
from app.database import get_db
from app.models.models import Startup, Deal, Financial, SharkDeal
from app.schemas.schemas import StartupBase, StartupDetail, StatsBar
from app.services.health import calculate_health_score
from app.services.insights import generate_ai_insight

router = APIRouter()

@router.get("/seed")
@router.post("/seed")
def seed_endpoint(db: Session = Depends(get_db)):
    from app.scripts.seed import seed_database
    from app.database import db_type
    try:
        metrics = seed_database()
        return {
            "status": "success",
            "message": "Database seeded successfully with Shark Tank India Season 1-5 data.",
            "database_type": db_type,
            "metrics": metrics
        }
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        raise HTTPException(status_code=500, detail=f"Database seeding failed: {str(e)}. Traceback: {error_details}")

@router.get("/db-debug")
def db_debug():
    import os
    raw_url = os.getenv("DATABASE_URL", "not set")
    # Mask password
    masked_url = raw_url
    if "@" in raw_url and "://" in raw_url:
        parts = raw_url.split("@", 1)
        prefix = parts[0]
        suffix = parts[1]
        scheme_and_user = prefix.split("://", 1)
        if len(scheme_and_user) == 2:
            scheme, user_pass = scheme_and_user
            if ":" in user_pass:
                user = user_pass.split(":", 1)[0]
                masked_url = f"{scheme}://{user}:****@{suffix}"
            else:
                masked_url = f"{scheme}://{user_pass}:****@{suffix}"
    
    from app.database import db_type
    return {
        "raw_url_length": len(raw_url),
        "masked_url": masked_url,
        "starts_with_postgres_proto": raw_url.startswith("postgres://"),
        "starts_with_postgresql": raw_url.startswith("postgresql"),
        "db_type": db_type
    }

@router.get("/query-debug")
def query_debug(db: Session = Depends(get_db)):
    try:
        startups_count = db.query(Startup).count()
        deals_count = db.query(Deal).count()
        financials_count = db.query(Financial).count()
        
        # Test basic startup query
        startups_list = []
        raw_startups = db.query(Startup).limit(5).all()
        for s in raw_startups:
            startups_list.append({
                "id": s.id,
                "name": s.name,
                "slug": s.slug
            })
            
        # Test join query
        join_query = db.query(Startup).join(Deal).outerjoin(Financial)
        join_results = join_query.limit(5).all()
        join_list = []
        for s in join_results:
            join_list.append({
                "id": s.id,
                "name": s.name
            })
            
        return {
            "status": "success",
            "counts": {
                "startups": startups_count,
                "deals": deals_count,
                "financials": financials_count
            },
            "sample_startups": startups_list,
            "join_results_count": len(join_results),
            "sample_join_results": join_list
        }
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }

@router.get("/stats", response_model=StatsBar)
def get_global_stats(db: Session = Depends(get_db)):
    total_pitches = db.query(Startup).count()
    total_deals = db.query(Deal).filter(Deal.deal_status == "funded").count()
    
    # Calculate total investment in lakhs
    investment_sum = db.query(Deal).filter(Deal.deal_status == "funded").with_entities(Deal.final_deal_amount).all()
    total_investment = sum([x[0] for x in investment_sum if x[0] is not None])
    
    success_rate = (total_deals / total_pitches * 100) if total_pitches > 0 else 0.0
    
    return {
        "total_pitches": total_pitches,
        "total_deals": total_deals,
        "total_investment": round(total_investment, 2),
        "success_rate": round(success_rate, 2)
    }

@router.get("/", response_model=List[StartupDetail])
def list_startups(
    search: Optional[str] = Query(None, description="Search by name"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    season: Optional[int] = Query(None, description="Filter by season"),
    deal_status: Optional[str] = Query(None, description="Filter by funded/not funded"),
    shark_id: Optional[int] = Query(None, description="Filter by shark invested"),
    profitable: Optional[bool] = Query(None, description="Profitable only"),
    revenue_gt_1cr: Optional[bool] = Query(None, description="Revenue greater than 1 Cr (100 Lakhs)"),
    margin_gt_30: Optional[bool] = Query(None, description="Gross margin > 30%"),
    order_by: Optional[str] = Query("name", description="Sort by name, valuation, revenue"),
    db: Session = Depends(get_db)
):
    query = db.query(Startup).join(Deal).outerjoin(Financial)

    filters = []

    if search:
        query = query.filter(Startup.name.ilike(f"%{search}%"))
    
    if industry:
        query = query.filter(Startup.industry == industry)
        
    if season:
        query = query.filter(Startup.season == season)
        
    if deal_status:
        query = query.filter(Deal.deal_status == deal_status)
        
    if shark_id:
        query = query.join(SharkDeal).filter(SharkDeal.shark_id == shark_id)
        
    if profitable:
        query = query.filter(Financial.profit > 0)
        
    if revenue_gt_1cr:
        query = query.filter(Financial.revenue >= 100)
        
    if margin_gt_30:
        query = query.filter(Financial.gross_margin >= 30)

    # Sorting
    if order_by == "valuation":
        query = query.order_by(desc(Deal.final_valuation))
    elif order_by == "revenue":
        query = query.order_by(desc(Financial.revenue))
    else:
        query = query.order_by(Startup.name)

    # Cap output to avoid huge payload size issues
    results = query.all()
    
    # We will attach dynamic attributes like health_score and ai_insight
    for item in results:
        # Pydantic schemas will capture startup attributes
        pass
        
    return results

@router.get("/industries", response_model=List[str])
def list_industries(db: Session = Depends(get_db)):
    industries = db.query(Startup.industry).distinct().all()
    return sorted([i[0] for i in industries if i[0] is not None])

@router.get("/detail/{slug}")
def get_startup_detail(slug: str, db: Session = Depends(get_db)):
    startup = db.query(Startup).filter(Startup.slug == slug).first()
    if not startup:
        raise HTTPException(status_code=404, detail="Startup not found")

    # Serialize
    startup_dict = {
        "id": startup.id,
        "name": startup.name,
        "slug": startup.slug,
        "industry": startup.industry,
        "business_model": startup.business_model,
        "season": startup.season,
        "founder_names": startup.founder_names,
        "founder_background": startup.founder_background,
        "description": startup.description,
        "website": startup.website,
        "logo_url": startup.logo_url,
        "deal": {
            "id": startup.deal.id,
            "startup_id": startup.deal.startup_id,
            "ask_amount": startup.deal.ask_amount,
            "ask_equity": startup.deal.ask_equity,
            "ask_valuation": startup.deal.ask_valuation,
            "final_deal_amount": startup.deal.final_deal_amount,
            "final_equity": startup.deal.final_equity,
            "final_valuation": startup.deal.final_valuation,
            "deal_status": startup.deal.deal_status,
            "royalty": startup.deal.royalty,
            "debt_component": startup.deal.debt_component,
            "notes": startup.deal.notes,
        } if startup.deal else None,
        "financials": [
            {
                "id": f.id,
                "startup_id": f.startup_id,
                "year": f.year,
                "revenue": f.revenue,
                "profit": f.profit,
                "ebitda": f.ebitda,
                "gross_margin": f.gross_margin,
                "net_margin": f.net_margin,
                "ebitda_margin": f.ebitda_margin,
                "burn_rate": f.burn_rate,
                "runway": f.runway,
                "debt": f.debt
            } for f in startup.financials
        ],
        "shark_deals": [
            {
                "id": sd.id,
                "shark_id": sd.shark_id,
                "amount_invested": sd.amount_invested,
                "equity_taken": sd.equity_taken,
                "shark": {
                    "id": sd.shark.id,
                    "name": sd.shark.name,
                    "company": sd.shark.company,
                    "title": sd.shark.title,
                }
            } for sd in startup.shark_deals
        ]
    }

    # Calculate dynamic stats
    startup_dict["health_score"] = calculate_health_score(startup_dict)
    startup_dict["ai_insight"] = generate_ai_insight(startup_dict)

    return startup_dict

@router.get("/compare")
def compare_startups(a_slug: str, b_slug: str, db: Session = Depends(get_db)):
    startup_a = get_startup_detail(a_slug, db)
    startup_b = get_startup_detail(b_slug, db)
    return {
        "startup_a": startup_a,
        "startup_b": startup_b
    }
