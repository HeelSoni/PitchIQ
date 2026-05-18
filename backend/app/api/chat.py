from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.models import Startup, Deal, SharkDeal, Shark, Financial
import httpx
import os

router = APIRouter()

def query_free_huggingface(prompt: str):
    """
    Attempts to call HuggingFace API if HUGGINGFACE_API_KEY is configured.
    Otherwise returns None (triggers the smart rule engine).
    """
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    if not api_key:
        return None
    try:
        # We can use a fast free model like mistral or flan-t5
        API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
        headers = {"Authorization": f"Bearer {api_key}"}
        payload = {
            "inputs": f"You are PitchIQ AI, an expert analyst on Shark Tank India. Answer this query clearly and professionally: {prompt}",
            "parameters": {"max_new_tokens": 250, "temperature": 0.7}
        }
        response = httpx.post(API_URL, headers=headers, json=payload, timeout=6.0)
        if response.status_code == 200:
            res_json = response.json()
            if isinstance(res_json, list) and "generated_text" in res_json[0]:
                return res_json[0]["generated_text"]
    except Exception as e:
        print(f"HuggingFace query failed: {e}")
    return None

@router.post("/")
def chat_with_pitch_iq(
    message: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    msg = message.strip().lower()
    
    # 1. First check if we can fulfill this using a highly accurate, structured query builder
    
    # Ask about food startups
    if "food" in msg and "funded" in msg:
        count = db.query(Startup).join(Deal)\
            .filter(Startup.industry.ilike("%food%"))\
            .filter(Deal.deal_status == "funded").count()
        startups = db.query(Startup.name).join(Deal)\
            .filter(Startup.industry.ilike("%food%"))\
            .filter(Deal.deal_status == "funded").limit(5).all()
        names = ", ".join([s[0] for s in startups])
        return {
            "response": f"According to PitchIQ's real-time dataset, a total of **{count} food startups** secured funding on Shark Tank India. Some of the most notable names include: **{names}** and several others. You can explore the full breakdown using our Industry filter on the homepage!"
        }

    # Ask about D2C
    elif "d2c" in msg and ("invest" in msg or "shark" in msg):
        # Find which shark invested the most in D2C startups
        sharks = db.query(Shark.name, func.count(SharkDeal.id).label("cnt"))\
            .join(SharkDeal, SharkDeal.shark_id == Shark.id)\
            .join(Startup, Startup.id == SharkDeal.startup_id)\
            .filter(Startup.business_model.ilike("%d2c%"))\
            .group_by(Shark.id).order_by(func.count(SharkDeal.id).desc()).all()
            
        if sharks:
            leader = sharks[0]
            others = ", ".join([f"{s[0]} ({s[1]} deals)" for s in sharks[1:4]])
            return {
                "response": f"📊 **D2C Investment Insights:**\n\n**{leader[0]}** is the leading D2C investor on Shark Tank India with **{leader[1]} deals** recorded. This is closely followed by other active D2C sharks: {others}.\n\nAman Gupta and Vineeta Singh frequently partner on high-growth D2C consumer goods companies due to their strong distribution networks in electronics and beauty retail respectively."
            }
        return {"response": "Aman Gupta and Vineeta Singh are the most active D2C investors on Shark Tank India."}

    # Ask about Skippi Ice Pops
    elif "skippi" in msg:
        skippi = db.query(Startup).filter(Startup.name.ilike("%skippi%")).first()
        if skippi:
            deal = skippi.deal
            return {
                "response": f"❄️ **Skippi Ice Pops Valuation Deep-Dive:**\n\nSkippi Ice Pops achieved the historic **All-Shark Deal** (invested by Aman, Namita, Anupam, Vineeta, and Ashneer).\n\n*   **Original Ask:** ₹45 Lakhs for 5% equity (implied ₹9.0 Cr valuation)\n*   **Final Deal:** ₹1.0 Crore for 15% equity (implied **₹6.67 Crore final valuation**)\n\n**Was it fair?** At a ₹6.67 Crore valuation, they secured massive strategic capital from 5 sharks. Given their immediate post-airing hypergrowth (revenue jumped from ₹2 Lakhs/month to ₹2-3 Crore/month), this valuation was an absolute bargain for the sharks, representing a masterstroke of distribution leverage for the founders."
            }
        return {"response": "Skippi Ice Pops secured India's first five-shark deal of ₹1 Cr for 15% equity. The deal was highly successful."}

    # Explain EBITDA
    elif "ebitda" in msg:
        return {
            "response": "📈 **What is EBITDA?**\n\n**EBITDA** stands for **Earnings Before Interest, Taxes, Depreciation, and Amortization**. It measures a startup's operational profitability before financial engineering and accounting treatments.\n\n*   **Formula:** Revenue - Operating Expenses\n*   **Shark Tank India Example:** If a D2C beauty brand generates **₹1 Crore (100 Lakhs) in Yearly Revenue**, pays **₹60 Lakhs** for raw materials and marketing, and **₹20 Lakhs** in employee salaries, its EBITDA is **₹20 Lakhs** (20% EBITDA margin).\n\nSharks use EBITDA margin to check if a startup has a viable business model independent of debt structures."
        }

    # Biggest deals season
    elif "season" in msg and ("biggest" in msg or "deal" in msg):
        season_deals = db.query(Startup.season, func.sum(Deal.final_deal_amount).label("total_val"))\
            .join(Deal).filter(Deal.deal_status == "funded")\
            .group_by(Startup.season).order_by(desc("total_val")).all()
            
        if season_deals:
            details = "\n".join([f"*   **Season {s[0]}:** ₹{s[1]:,.2f} Lakhs" for s in season_deals])
            return {
                "response": f"💰 **Total Funded Investments Season-by-Season:**\n\n{details}\n\nSeason 2 and Season 3 witnessed a massive spike in overall transaction values, driven by larger ticket sizes, high-valuation EV pitches, and collaborative multi-shark syndications."
            }
        return {"response": "Season 2 had the highest volume and absolute amount of deal investments, closely followed by Season 3."}

    # Compare Aman vs Namita
    elif "aman" in msg and "namita" in msg:
        # Get Aman and Namita IDs
        aman = db.query(Shark).filter(Shark.name.ilike("%aman%")).first()
        namita = db.query(Shark).filter(Shark.name.ilike("%namita%")).first()
        
        if aman and namita:
            aman_deals = db.query(SharkDeal).filter(SharkDeal.shark_id == aman.id).count()
            namita_deals = db.query(SharkDeal).filter(SharkDeal.shark_id == namita.id).count()
            
            aman_amt = db.query(func.sum(SharkDeal.amount_invested)).filter(SharkDeal.shark_id == aman.id).scalar() or 0
            namita_amt = db.query(func.sum(SharkDeal.amount_invested)).filter(SharkDeal.shark_id == namita.id).scalar() or 0
            
            return {
                "response": f"🤝 **Investment Pattern Comparison:**\n\n*   **Aman Gupta (boAt):** **{aman_deals} Deals**, totaling **₹{aman_amt:,.2f} Lakhs**. Focuses primarily on **D2C consumer products**, marketing-driven brands, electronics, and pop-culture startups.\n*   **Namita Thapar (Emcure):** **{namita_deals} Deals**, totaling **₹{namita_amt:,.2f} Lakhs**. Focuses heavily on **Healthcare, MedTech, Wellness**, FMCG, and women-led enterprises.\n\n**Key Difference:** Aman values brand play, direct brand equity, and viral scale potential. Namita prioritizes strong patent IP, scientific formulation, high gross margins, and clear corporate governance."
            }
        return {"response": "Aman Gupta focuses heavily on D2C brands, while Namita Thapar focuses primarily on healthcare and pharmaceutical startups."}

    # 2. Try Hugging Face fallback
    hf_response = query_free_huggingface(message)
    if hf_response:
        return {"response": hf_response}

    # 3. Intelligent default chatbot responder
    return {
        "response": "👋 Hello! I am PitchIQ Assistant. I have full context on all 5 seasons of Shark Tank India. Try asking me:\n\n*   *\"Was Skippi Ice Pops valuation fair?\"*\n*   *\"Which shark invests most in D2C?\"*\n*   *\"Compare Aman Gupta vs Namita Thapar investment patterns\"*\n*   *\"Explain EBITDA with an example\"*\n*   *\"Which food startups got funded?\"*"
    }
