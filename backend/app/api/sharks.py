from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.database import get_db
from app.models.models import Shark, SharkDeal, Startup, Deal
from app.schemas.schemas import SharkBase

router = APIRouter()

@router.get("/")
def list_sharks(db: Session = Depends(get_db)):
    sharks = db.query(Shark).all()
    res = []
    
    for s in sharks:
        # Compute aggregates
        deals = db.query(SharkDeal).filter(SharkDeal.shark_id == s.id).all()
        total_deals = len(deals)
        total_invested = sum([d.amount_invested for d in deals if d.amount_invested is not None])
        avg_equity = sum([d.equity_taken for d in deals if d.equity_taken is not None]) / len([d for d in deals if d.equity_taken is not None]) if len([d for d in deals if d.equity_taken is not None]) > 0 else 0
        
        # Calculate favorite industries
        industries = db.query(Startup.industry, func.count(Startup.industry))\
            .join(SharkDeal, SharkDeal.startup_id == Startup.id)\
            .filter(SharkDeal.shark_id == s.id)\
            .group_by(Startup.industry)\
            .order_by(func.count(Startup.industry).desc())\
            .limit(3).all()
            
        fav_industries = [ind[0] for ind in industries if ind[0] is not None]

        res.append({
            "id": s.id,
            "name": s.name,
            "company": s.company,
            "title": s.title,
            "bio": s.bio,
            "net_worth": s.net_worth,
            "expertise": s.expertise,
            "seasons": s.seasons,
            "image_url": s.image_url,
            "stats": {
                "total_deals": total_deals,
                "total_invested_lakhs": round(total_invested, 2),
                "avg_equity_percent": round(avg_equity, 2),
                "avg_ticket_size_lakhs": round(total_invested / total_deals, 2) if total_deals > 0 else 0,
                "favorite_industries": fav_industries
            }
        })
    return res

@router.get("/{shark_id}")
def get_shark_details(shark_id: int, db: Session = Depends(get_db)):
    shark = db.query(Shark).filter(Shark.id == shark_id).first()
    if not shark:
        raise HTTPException(status_code=404, detail="Shark not found")

    deals = db.query(SharkDeal).filter(SharkDeal.shark_id == shark_id).all()
    
    portfolio = []
    for d in deals:
        startup = db.query(Startup).filter(Startup.id == d.startup_id).first()
        if startup:
            portfolio.append({
                "id": startup.id,
                "name": startup.name,
                "slug": startup.slug,
                "industry": startup.industry,
                "season": startup.season,
                "deal_amount_lakhs": d.amount_invested,
                "equity_taken": d.equity_taken
            })
            
    # Aggregated stats
    total_deals = len(deals)
    total_invested = sum([d.amount_invested for d in deals if d.amount_invested is not None])
    avg_equity = sum([d.equity_taken for d in deals if d.equity_taken is not None]) / len([d for d in deals if d.equity_taken is not None]) if len([d for d in deals if d.equity_taken is not None]) > 0 else 0

    # Calculate favorite industries
    industries = db.query(Startup.industry, func.count(Startup.industry))\
        .join(SharkDeal, SharkDeal.startup_id == Startup.id)\
        .filter(SharkDeal.shark_id == shark_id)\
        .group_by(Startup.industry)\
        .order_by(func.count(Startup.industry).desc())\
        .limit(3).all()
        
    fav_industries = [ind[0] for ind in industries if ind[0] is not None]

    return {
        "id": shark.id,
        "name": shark.name,
        "company": shark.company,
        "title": shark.title,
        "bio": shark.bio,
        "net_worth": shark.net_worth,
        "expertise": shark.expertise,
        "seasons": shark.seasons,
        "image_url": shark.image_url,
        "stats": {
            "total_deals": total_deals,
            "total_invested_lakhs": round(total_invested, 2),
            "avg_equity_percent": round(avg_equity, 2),
            "avg_ticket_size_lakhs": round(total_invested / total_deals, 2) if total_deals > 0 else 0,
            "favorite_industries": fav_industries
        },
        "portfolio": portfolio
    }
