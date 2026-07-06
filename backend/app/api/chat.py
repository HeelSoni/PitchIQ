from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, case
from app.database import get_db
from app.models.models import Startup, Deal, SharkDeal, Shark, Financial
import os
import httpx

router = APIRouter()


def build_db_context(msg: str, db: Session) -> str:
    """Build rich DB context for LLM consumption."""
    context_parts = []

    # Global stats
    total_pitches = db.query(Startup).count()
    total_funded = db.query(Deal).filter(Deal.deal_status == "funded").count()
    total_investment = db.query(func.sum(Deal.final_deal_amount)).filter(Deal.deal_status == "funded").scalar() or 0
    success_rate = round((total_funded / total_pitches * 100), 1) if total_pitches > 0 else 0
    context_parts.append(
        f"GLOBAL STATS: {total_pitches} total pitches, {total_funded} funded deals, "
        f"Rs{total_investment:,.0f} Lakhs total investment, {success_rate}% success rate across Seasons 1-5."
    )

    # Shark stats
    shark_data = db.query(
        Shark.name, Shark.company, Shark.bio,
        func.count(SharkDeal.id).label("deals"),
        func.sum(SharkDeal.amount_invested).label("total_invested")
    ).outerjoin(SharkDeal, SharkDeal.shark_id == Shark.id)\
     .group_by(Shark.id).all()

    shark_lines = []
    for s in shark_data:
        amt = f"Rs{s[4]:,.0f} Lakhs" if s[4] else "Rs0"
        shark_lines.append(f"{s[0]} ({s[1]}): {s[3]} deals, {amt} invested. Bio: {(s[2] or '')[:80]}")
    if shark_lines:
        context_parts.append("SHARKS:\n" + "\n".join(shark_lines))

    # Industry breakdown
    industry_stats = db.query(
        Startup.industry,
        func.count(Startup.id).label("count"),
        func.sum(case((Deal.deal_status == "funded", 1), else_=0)).label("funded")
    ).join(Deal).group_by(Startup.industry).order_by(desc("funded")).limit(15).all()

    if industry_stats:
        ind_lines = [f"{i[0]}: {i[1]} pitches, {i[2]} funded" for i in industry_stats if i[0]]
        context_parts.append("INDUSTRIES:\n" + "\n".join(ind_lines))

    # Season breakdown
    season_stats = db.query(
        Startup.season,
        func.count(Startup.id).label("pitches"),
        func.sum(Deal.final_deal_amount).label("total_inv")
    ).join(Deal).group_by(Startup.season).order_by(Startup.season).all()

    if season_stats:
        season_lines = [
            f"Season {s[0]}: {s[1]} pitches, Rs{s[2]:,.0f} Lakhs invested" if s[2] else f"Season {s[0]}: {s[1]} pitches"
            for s in season_stats
        ]
        context_parts.append("SEASONS:\n" + "\n".join(season_lines))

    # Relevant startups based on keywords
    keywords = [w for w in msg.split() if len(w) > 3]
    found_startups = []
    for kw in keywords[:5]:
        results = db.query(Startup).filter(Startup.name.ilike(f"%{kw}%")).limit(3).all()
        for r in results:
            if r not in found_startups:
                found_startups.append(r)

    if found_startups:
        startup_lines = []
        for s in found_startups[:5]:
            d = s.deal
            if d:
                status = "Funded" if d.deal_status == "funded" else "Not Funded"
                amt = f"Rs{d.final_deal_amount:,.0f}L for {d.final_equity}%" if d.final_deal_amount else "N/A"
                ask = f"Rs{d.ask_amount:,.0f}L for {d.ask_equity}%" if d.ask_amount else "N/A"
                startup_lines.append(
                    f"{s.name} (Season {s.season}, {s.industry}): Asked {ask}, Status: {status}, Deal: {amt}. "
                    f"Desc: {(s.description or '')[:100]}"
                )
        if startup_lines:
            context_parts.append("RELEVANT STARTUPS:\n" + "\n".join(startup_lines))

    return "\n\n".join(context_parts)


def query_gemini(question: str, context: str):
    """Call Google Gemini free API with database context."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        full_prompt = (
            "You are PitchIQ AI, an expert analyst on Shark Tank India. "
            "Use the real database context below to answer accurately. "
            "Be friendly, concise, and use **bold** and bullet points.\n\n"
            f"DATABASE CONTEXT:\n{context}\n\n"
            f"USER QUESTION: {question}\n\nAnswer:"
        )
        payload = {
            "contents": [{"parts": [{"text": full_prompt}]}],
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 500}
        }
        response = httpx.post(url, json=payload, timeout=12.0)
        if response.status_code == 200:
            data = response.json()
            candidates = data.get("candidates", [])
            if candidates:
                return candidates[0]["content"]["parts"][0]["text"].strip()
        else:
            print(f"Gemini API error {response.status_code}: {response.text[:200]}")
    except Exception as e:
        print(f"Gemini query failed: {e}")
    return None


def query_huggingface(question: str, context: str):
    """Fallback: HuggingFace with context."""
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    if not api_key:
        return None
    try:
        API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
        headers = {"Authorization": f"Bearer {api_key}"}
        prompt = (
            f"[INST] You are PitchIQ AI, an expert on Shark Tank India. "
            f"Use this data:\n{context[:1200]}\n\n"
            f"Question: {question}\nAnswer concisely: [/INST]"
        )
        payload = {
            "inputs": prompt,
            "parameters": {"max_new_tokens": 300, "temperature": 0.7, "return_full_text": False}
        }
        response = httpx.post(API_URL, headers=headers, json=payload, timeout=8.0)
        if response.status_code == 200:
            res_json = response.json()
            if isinstance(res_json, list) and res_json:
                text = res_json[0].get("generated_text", "").strip()
                if text and len(text) > 20:
                    return text
    except Exception as e:
        print(f"HuggingFace query failed: {e}")
    return None


def smart_db_answer(msg: str, db: Session):
    """
    Answers common questions directly from the database
    when no LLM API is available. Covers the most frequent question types.
    """
    m = msg.lower()

    # --- Success rate ---
    if any(k in m for k in ["success rate", "how many funded", "percentage", "what percent", "funded startup"]):
        total = db.query(Startup).count()
        funded = db.query(Deal).filter(Deal.deal_status == "funded").count()
        rate = round((funded / total * 100), 1) if total > 0 else 0
        return (
            f"**Shark Tank India Funding Stats:**\n\n"
            f"- **Total Pitches:** {total}\n"
            f"- **Funded Deals:** {funded}\n"
            f"- **Not Funded:** {total - funded}\n"
            f"- **Success Rate:** {rate}%\n\n"
            f"Roughly **{rate}%** of entrepreneurs who entered the tank walked out with a deal!"
        )

    # --- Top investor / most investment ---
    if any(k in m for k in ["most invest", "top shark", "highest invest", "most deal", "most money", "best shark", "which shark"]):
        sharks = db.query(
            Shark.name,
            func.count(SharkDeal.id).label("deals"),
            func.sum(SharkDeal.amount_invested).label("total")
        ).join(SharkDeal, SharkDeal.shark_id == Shark.id)\
         .group_by(Shark.id).order_by(desc("total")).limit(5).all()

        if sharks:
            lines = "\n".join([
                f"- **{s[0]}:** {s[1]} deals | Rs{s[2]:,.0f} Lakhs" if s[2] else f"- **{s[0]}:** {s[1]} deals"
                for s in sharks
            ])
            return f"**Top Sharks by Investment:**\n\n{lines}\n\n**{sharks[0][0]}** leads with the most capital deployed!"

    # --- Shark comparison ---
    shark_keys = {"aman": "aman", "namita": "namita", "anupam": "anupam",
                  "vineeta": "vineeta", "peyush": "peyush", "ashneer": "ashneer",
                  "amit": "amit", "ritesh": "ritesh"}
    found_sharks = [k for k in shark_keys if k in m]

    if len(found_sharks) == 2:
        results = []
        for key in found_sharks:
            shark = db.query(Shark).filter(Shark.name.ilike(f"%{key}%")).first()
            if shark:
                deals = db.query(SharkDeal).filter(SharkDeal.shark_id == shark.id).count()
                total_amt = db.query(func.sum(SharkDeal.amount_invested)).filter(SharkDeal.shark_id == shark.id).scalar() or 0
                results.append((shark.name, deals, total_amt))
        if len(results) == 2:
            a, b = results[0], results[1]
            winner = a[0] if a[2] > b[2] else b[0]
            return (
                f"**Investment Comparison:**\n\n"
                f"- **{a[0]}:** {a[1]} deals | Rs{a[2]:,.0f} Lakhs\n"
                f"- **{b[0]}:** {b[1]} deals | Rs{b[2]:,.0f} Lakhs\n\n"
                f"**{winner}** has deployed more capital overall!"
            )

    # --- Single shark stats ---
    if len(found_sharks) == 1 and any(k in m for k in ["invest", "deal", "how many", "stats", "portfolio", "total"]):
        key = found_sharks[0]
        shark = db.query(Shark).filter(Shark.name.ilike(f"%{key}%")).first()
        if shark:
            deals = db.query(SharkDeal).filter(SharkDeal.shark_id == shark.id).count()
            total_amt = db.query(func.sum(SharkDeal.amount_invested)).filter(SharkDeal.shark_id == shark.id).scalar() or 0
            return (
                f"**{shark.name} — Investment Portfolio:**\n\n"
                f"- **Total Deals:** {deals}\n"
                f"- **Total Invested:** Rs{total_amt:,.0f} Lakhs\n"
                f"- **Company:** {shark.company or 'N/A'}\n\n"
                f"_{(shark.bio or '')[:200]}_"
            )

    # --- Industry queries ---
    industries = ["food", "health", "tech", "fashion", "beauty", "edtech", "fintech",
                  "agri", "ev", "electric", "d2c", "saas", "retail", "education",
                  "medical", "wellness", "fitness", "fmcg"]
    matched_ind = next((i for i in industries if i in m), None)
    if matched_ind and any(k in m for k in ["funded", "invest", "deal", "startup", "how many"]):
        startups = db.query(Startup).join(Deal)\
            .filter(Startup.industry.ilike(f"%{matched_ind}%"))\
            .filter(Deal.deal_status == "funded").all()
        names = ", ".join([s.name for s in startups[:6]])
        return (
            f"**{matched_ind.upper()} Startups on Shark Tank India:**\n\n"
            f"- **Total Funded:** {len(startups)}\n"
            f"- **Notable Names:** {names}{'...' if len(startups) > 6 else ''}\n\n"
            f"Explore all {matched_ind} startups using the Industry filter on the dashboard!"
        )

    # --- Season queries ---
    if "season" in m:
        season_stats = db.query(
            Startup.season,
            func.count(Startup.id).label("pitches"),
            func.sum(Deal.final_deal_amount).label("total_inv")
        ).join(Deal).group_by(Startup.season).order_by(Startup.season).all()

        if season_stats:
            lines = "\n".join([
                f"- **Season {s[0]}:** {s[1]} pitches | Rs{s[2]:,.0f} Lakhs invested" if s[2]
                else f"- **Season {s[0]}:** {s[1]} pitches"
                for s in season_stats
            ])
            return f"**Season-by-Season Breakdown:**\n\n{lines}"

    # --- Named startup lookup ---
    words = [w for w in m.split() if len(w) > 3]
    for word in words[:4]:
        startup = db.query(Startup).filter(Startup.name.ilike(f"%{word}%")).first()
        if startup and startup.deal:
            d = startup.deal
            status = "Funded" if d.deal_status == "funded" else "Not Funded"
            amt = f"Rs{d.final_deal_amount:,.0f} Lakhs for {d.final_equity}% equity" if d.final_deal_amount else "N/A"
            ask = f"Rs{d.ask_amount:,.0f} Lakhs for {d.ask_equity}% equity" if d.ask_amount else "N/A"
            return (
                f"**{startup.name}** — Season {startup.season}\n\n"
                f"- **Industry:** {startup.industry or 'N/A'}\n"
                f"- **Original Ask:** {ask}\n"
                f"- **Deal Status:** {status}\n"
                f"- **Final Deal:** {amt}\n\n"
                f"_{(startup.description or '')[:250]}_"
            )

    # --- EBITDA / financial terms ---
    if "ebitda" in m:
        return (
            "**What is EBITDA?**\n\n"
            "EBITDA = Earnings Before Interest, Taxes, Depreciation, and Amortization.\n\n"
            "It measures a startup's core operational profitability.\n\n"
            "**Example:** Revenue Rs1 Cr - Costs Rs80L = **EBITDA Rs20L (20% margin)**\n\n"
            "Sharks use EBITDA margin to judge if the business model is fundamentally viable."
        )

    if any(k in m for k in ["valuation", "how valuation", "calculate valuation"]):
        return (
            "**How is Valuation Calculated?**\n\n"
            "**Formula:** Valuation = (Investment / Equity%) x 100\n\n"
            "**Example:** Rs50 Lakhs for 10% equity = **Rs500 Lakhs valuation (Rs5 Crore)**\n\n"
            "Sharks negotiate by adjusting either the investment amount or equity percentage."
        )

    if any(k in m for k in ["total investment", "how much invested", "total money"]):
        total = db.query(func.sum(Deal.final_deal_amount)).filter(Deal.deal_status == "funded").scalar() or 0
        count = db.query(Deal).filter(Deal.deal_status == "funded").count()
        return (
            f"**Total Investment on Shark Tank India:**\n\n"
            f"- **Total Capital Deployed:** Rs{total:,.0f} Lakhs\n"
            f"- **Across:** {count} funded deals\n"
            f"- **That's:** Rs{total/100:,.1f} Crores total!"
        )

    return None


@router.post("/")
def chat_with_pitch_iq(
    message: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    msg = message.strip()
    msg_lower = msg.lower()

    # 1. Build DB context
    context = build_db_context(msg_lower, db)

    # 2. Try Gemini (best quality, free tier)
    gemini_response = query_gemini(msg, context)
    if gemini_response:
        return {"response": gemini_response}

    # 3. Try HuggingFace fallback
    hf_response = query_huggingface(msg, context)
    if hf_response:
        return {"response": hf_response}

    # 4. Smart DB-driven answer (works without any API key)
    db_answer = smart_db_answer(msg_lower, db)
    if db_answer:
        return {"response": db_answer}

    # 5. Generic helpful fallback
    return {
        "response": (
            "I couldn't find a specific answer for that, but here's what I can help with:\n\n"
            "- _\"Which shark invested the most?\"_\n"
            "- _\"Compare Aman Gupta vs Namita Thapar\"_\n"
            "- _\"How many food startups got funded?\"_\n"
            "- _\"Tell me about Skippi Ice Pops\"_\n"
            "- _\"What is the success rate?\"_\n"
            "- _\"Show me season-wise investments\"_"
        )
    }


@router.get("/test-gemini")
def test_gemini_connection():
    """Test if Gemini API key is configured and working."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"status": "error", "message": "GEMINI_API_KEY not set in environment variables"}
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        payload = {"contents": [{"parts": [{"text": "Say: PitchIQ Gemini OK"}]}]}
        response = httpx.post(url, json=payload, timeout=10.0)
        if response.status_code == 200:
            data = response.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            return {"status": "success", "gemini_says": text.strip(), "key_preview": api_key[:10] + "..."}
        else:
            return {"status": "api_error", "code": response.status_code, "detail": response.text[:300]}
    except Exception as e:
        return {"status": "exception", "error": str(e)}
