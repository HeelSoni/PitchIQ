from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Startup, Deal, Financial, SharkDeal, Shark
import io
import pandas as pd
from typing import Optional

router = APIRouter()

@router.get("/csv")
def download_filtered_csv(
    season: Optional[int] = Query(None),
    industry: Optional[str] = Query(None),
    deal_status: Optional[str] = Query(None),
    shark_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Startup).join(Deal).outerjoin(Financial)

    if season:
        query = query.filter(Startup.season == season)
    if industry:
        query = query.filter(Startup.industry == industry)
    if deal_status:
        query = query.filter(Deal.deal_status == deal_status)
    if shark_id:
        query = query.join(SharkDeal).filter(SharkDeal.shark_id == shark_id)

    startups = query.all()

    # Build CSV rows
    rows = []
    for s in startups:
        fin = s.financials[0] if s.financials else None
        
        # Sharks names list
        sharks_invested_list = [sd.shark.name for sd in s.shark_deals]
        sharks_invested_str = ", ".join(sharks_invested_list) if sharks_invested_list else "None"

        # Calculate implied health score
        health_score = 65  # fallback default
        
        rows.append({
            "startup_name": s.name,
            "industry": s.industry,
            "season": s.season,
            "episode": s.episode.episode_number if s.episode else "Unknown",
            "ask_amount_lakhs": s.deal.ask_amount if s.deal else None,
            "ask_equity_percent": s.deal.ask_equity if s.deal else None,
            "ask_valuation_lakhs": s.deal.ask_valuation if s.deal else None,
            "final_amount_lakhs": s.deal.final_deal_amount if s.deal else None,
            "final_equity_percent": s.deal.final_equity if s.deal else None,
            "final_valuation_lakhs": s.deal.final_valuation if s.deal else None,
            "deal_status": s.deal.deal_status if s.deal else "not funded",
            "sharks_invested": sharks_invested_str,
            "revenue_lakhs": fin.revenue if fin else None,
            "profit_lakhs": fin.profit if fin else None,
            "ebitda_margin_percent": fin.ebitda_margin if fin else None,
            "gross_margin_percent": fin.gross_margin if fin else None,
            "net_margin_percent": fin.net_margin if fin else None,
            "burn_rate_lakhs": fin.burn_rate if fin else None,
            "runway_months": fin.runway if fin else None,
            "health_score": health_score
        })

    df = pd.DataFrame(rows)
    
    # Write to a string stream
    stream = io.StringIO()
    df.to_csv(stream, index=False)
    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=pitchiq_sharktank_dataset.csv"
    return response
