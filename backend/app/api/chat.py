from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.database import get_db
from app.models.models import Startup, Deal, SharkDeal, Shark, Financial
import os
import httpx

router = APIRouter()


def query_huggingface(prompt: str):
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    if not api_key:
        return None
    try:
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


def smart_answer(msg: str, db: Session) -> str | None:
    """
    Smart intent engine - tries to detect what the user is asking
    and answers using live database queries.
    Returns None if no intent matched.
    """

    # ── Intent: Specific startup lookup ──────────────────────────────────────
    # e.g. "tell me about skippi", "what happened with boat hearing", "skippi deal"
    startup_keywords = ["tell me about", "what about", "info on", "details about", "what happened with", "startup called"]
    matched_startup_phrase = next((kw for kw in startup_keywords if kw in msg), None)
    if matched_startup_phrase:
        query_term = msg.split(matched_startup_phrase)[-1].strip().strip("?").strip()
        if query_term:
            startup = db.query(Startup).filter(Startup.name.ilike(f"%{query_term}%")).first()
            if startup and startup.deal:
                d = startup.deal
                status = "✅ Funded" if d.deal_status == "funded" else "❌ Not Funded"
                amt = f"₹{d.final_deal_amount:,.0f} Lakhs" if d.final_deal_amount else "N/A"
                eq = f"{d.final_equity}%" if d.final_equity else "N/A"
                ask = f"₹{d.ask_amount:,.0f} Lakhs for {d.ask_equity}% equity" if d.ask_amount else "N/A"
                return (
                    f"📋 **{startup.name}** — Season {startup.season}\n\n"
                    f"• **Industry:** {startup.industry or 'N/A'}\n"
                    f"• **Original Ask:** {ask}\n"
                    f"• **Deal Status:** {status}\n"
                    f"• **Final Deal:** {amt} for {eq}\n\n"
                    f"_{startup.description[:200] + '...' if startup.description and len(startup.description) > 200 else startup.description or 'No description available.'}_"
                )

    # ── Intent: Named startup by name directly ────────────────────────────────
    # e.g. "skippi ice pops", "boAt", "sugar cosmetics deal"
    # Try to find a startup whose name is mentioned in the message
    words = msg.replace("?", "").replace("!", "").strip()
    if len(words) > 2:
        # Try matching 2-3 word combos
        all_startups = db.query(Startup).filter(
            Startup.name.ilike(f"%{words[:20]}%")
        ).first()
        if not all_startups:
            # Try first word
            first_word = words.split()[0] if words.split() else ""
            if len(first_word) > 3:
                all_startups = db.query(Startup).filter(
                    Startup.name.ilike(f"%{first_word}%")
                ).first()

        if all_startups and all_startups.deal:
            s = all_startups
            d = s.deal
            status = "✅ Funded" if d.deal_status == "funded" else "❌ Not Funded"
            amt = f"₹{d.final_deal_amount:,.0f} Lakhs" if d.final_deal_amount else "N/A"
            eq = f"{d.final_equity}%" if d.final_equity else "N/A"
            ask = f"₹{d.ask_amount:,.0f} Lakhs for {d.ask_equity}% equity" if d.ask_amount else "N/A"
            return (
                f"📋 **{s.name}** — Season {s.season}\n\n"
                f"• **Industry:** {s.industry or 'N/A'}\n"
                f"• **Original Ask:** {ask}\n"
                f"• **Deal Status:** {status}\n"
                f"• **Final Deal:** {amt} for {eq}\n\n"
                f"_{s.description[:200] + '...' if s.description and len(s.description) > 200 else s.description or 'No description available.'}_"
            )

    # ── Intent: Which shark invested the most ────────────────────────────────
    if any(kw in msg for kw in ["most invest", "top shark", "highest invest", "best shark", "most deal", "most money", "richest shark"]):
        sharks = db.query(
            Shark.name,
            func.count(SharkDeal.id).label("deals"),
            func.sum(SharkDeal.amount_invested).label("total")
        ).join(SharkDeal, SharkDeal.shark_id == Shark.id)\
         .group_by(Shark.id)\
         .order_by(desc("total")).limit(5).all()

        if sharks:
            lines = "\n".join([
                f"• **{s[0]}:** {s[1]} deals | ₹{s[2]:,.0f} Lakhs" if s[2] else f"• **{s[0]}:** {s[1]} deals"
                for s in sharks
            ])
            top = sharks[0]
            return (
                f"💰 **Top Sharks by Total Investment:**\n\n{lines}\n\n"
                f"**{top[0]}** leads overall with the highest capital deployed across Shark Tank India!"
            )

    # ── Intent: Success rate / funded stats ─────────────────────────────────
    if any(kw in msg for kw in ["success rate", "how many funded", "funded startup", "percentage funded", "get deal", "get funded"]):
        total = db.query(Startup).count()
        funded = db.query(Deal).filter(Deal.deal_status == "funded").count()
        rate = round((funded / total * 100), 1) if total > 0 else 0
        return (
            f"📊 **Shark Tank India Funding Statistics:**\n\n"
            f"• **Total Pitches:** {total}\n"
            f"• **Funded Deals:** {funded}\n"
            f"• **Not Funded:** {total - funded}\n"
            f"• **Success Rate:** {rate}%\n\n"
            f"So roughly **{rate}%** of entrepreneurs who entered the tank walked out with a deal!"
        )

    # ── Intent: Industry-specific queries ────────────────────────────────────
    industries = ["food", "health", "tech", "fashion", "beauty", "edtech", "fintech",
                  "agri", "farm", "ev", "electric", "d2c", "saas", "retail", "education",
                  "medical", "wellness", "fitness"]
    matched_industry = next((ind for ind in industries if ind in msg), None)
    if matched_industry and any(kw in msg for kw in ["funded", "invest", "deal", "startup", "industry", "which", "how many"]):
        startups = db.query(Startup).join(Deal)\
            .filter(Startup.industry.ilike(f"%{matched_industry}%"))\
            .filter(Deal.deal_status == "funded").all()
        count = len(startups)
        names = ", ".join([s.name for s in startups[:5]])
        return (
            f"🏭 **{matched_industry.upper()} Industry on Shark Tank India:**\n\n"
            f"• **Total Funded:** {count} startups\n"
            f"• **Notable Names:** {names}{'...' if count > 5 else ''}\n\n"
            f"You can explore all {matched_industry} startups in detail using the Industry filter on the PitchIQ dashboard!"
        )

    # ── Intent: Specific shark stats ─────────────────────────────────────────
    shark_names = {
        "aman": "aman gupta",
        "namita": "namita thapar",
        "anupam": "anupam mittal",
        "vineeta": "vineeta singh",
        "peyush": "peyush bansal",
        "ashneer": "ashneer grover",
        "amit": "amit jain",
        "ritesh": "ritesh agarwal",
    }
    matched_shark_key = next((k for k in shark_names if k in msg), None)

    # Handle comparison (two sharks mentioned)
    mentioned_sharks = [k for k in shark_names if k in msg]
    if len(mentioned_sharks) == 2:
        results = []
        for key in mentioned_sharks:
            shark = db.query(Shark).filter(Shark.name.ilike(f"%{key}%")).first()
            if shark:
                deals = db.query(SharkDeal).filter(SharkDeal.shark_id == shark.id).count()
                total_amt = db.query(func.sum(SharkDeal.amount_invested))\
                    .filter(SharkDeal.shark_id == shark.id).scalar() or 0
                results.append((shark.name, deals, total_amt))
        if len(results) == 2:
            a, b = results[0], results[1]
            return (
                f"🤝 **Investment Comparison:**\n\n"
                f"• **{a[0]}:** {a[1]} deals | ₹{a[2]:,.0f} Lakhs invested\n"
                f"• **{b[0]}:** {b[1]} deals | ₹{b[2]:,.0f} Lakhs invested\n\n"
                f"**{'  ' + a[0] if a[2] > b[2] else b[0]}** has deployed more capital overall!"
            )

    # Single shark stats
    if matched_shark_key and any(kw in msg for kw in ["invest", "deal", "how many", "stats", "portfolio", "much", "total"]):
        shark = db.query(Shark).filter(Shark.name.ilike(f"%{matched_shark_key}%")).first()
        if shark:
            deals = db.query(SharkDeal).filter(SharkDeal.shark_id == shark.id).count()
            total_amt = db.query(func.sum(SharkDeal.amount_invested))\
                .filter(SharkDeal.shark_id == shark.id).scalar() or 0
            return (
                f"🦈 **{shark.name} — Investment Portfolio:**\n\n"
                f"• **Total Deals:** {deals}\n"
                f"• **Total Invested:** ₹{total_amt:,.0f} Lakhs\n"
                f"• **Company:** {shark.company}\n"
                f"• **Bio:** {shark.bio[:200] + '...' if shark.bio and len(shark.bio) > 200 else shark.bio or 'N/A'}"
            )

    # ── Intent: Season-based queries ─────────────────────────────────────────
    if "season" in msg and any(kw in msg for kw in ["best", "most", "deal", "investment", "how many", "total"]):
        season_stats = db.query(
            Startup.season,
            func.count(Startup.id).label("pitches"),
            func.sum(Deal.final_deal_amount).label("total_inv")
        ).join(Deal).group_by(Startup.season).order_by(Startup.season).all()

        if season_stats:
            lines = "\n".join([
                f"• **Season {s[0]}:** {s[1]} pitches | ₹{s[2]:,.0f} Lakhs invested" if s[2] else f"• **Season {s[0]}:** {s[1]} pitches"
                for s in season_stats
            ])
            return f"📅 **Season-by-Season Breakdown:**\n\n{lines}"

    # ── Intent: EBITDA / financial terms ─────────────────────────────────────
    if "ebitda" in msg:
        return (
            "📈 **What is EBITDA?**\n\n"
            "**EBITDA** = Earnings Before Interest, Taxes, Depreciation, and Amortization.\n\n"
            "It measures a startup's core operational profitability before accounting treatments.\n\n"
            "**Example:** A D2C brand earns ₹1 Cr revenue, spends ₹60L on materials and marketing, "
            "₹20L on salaries. EBITDA = **₹20 Lakhs** (20% margin).\n\n"
            "Sharks use EBITDA margin to check if the business model is viable before any debt or tax impact."
        )

    if any(kw in msg for kw in ["valuation", "how is valuation", "calculate valuation"]):
        return (
            "💡 **How is Valuation Calculated on Shark Tank India?**\n\n"
            "**Formula:** Valuation = (Investment Amount ÷ Equity %) × 100\n\n"
            "**Example:** If a startup asks for ₹50 Lakhs for 10% equity:\n"
            "Valuation = (50 ÷ 10) × 100 = **₹500 Lakhs (₹5 Crore)**\n\n"
            "Sharks negotiate the valuation by either adjusting the investment amount or equity percentage."
        )

    if any(kw in msg for kw in ["equity", "what is equity", "explain equity"]):
        return (
            "📊 **What is Equity?**\n\n"
            "Equity is the ownership percentage in a company. When a shark invests for 10% equity, "
            "they own 10% of that business.\n\n"
            "**Example:** If PitchIQ is valued at ₹10 Crore and Aman Gupta takes 10% equity "
            "for ₹1 Crore, he now owns 10% of the company."
        )

    # ── Intent: All sharks list ───────────────────────────────────────────────
    if any(kw in msg for kw in ["list shark", "all shark", "who are the shark", "which shark"]) and "invest" not in msg:
        sharks = db.query(Shark).limit(10).all()
        lines = "\n".join([f"• **{s.name}** — {s.company}" for s in sharks])
        return f"🦈 **Sharks on Shark Tank India:**\n\n{lines}"

    # ── Intent: Total investment overall ─────────────────────────────────────
    if any(kw in msg for kw in ["total investment", "total money", "how much invested", "overall investment"]):
        total = db.query(func.sum(Deal.final_deal_amount))\
            .filter(Deal.deal_status == "funded").scalar() or 0
        count = db.query(Deal).filter(Deal.deal_status == "funded").count()
        return (
            f"💰 **Total Investment on Shark Tank India:**\n\n"
            f"• **Total Capital Deployed:** ₹{total:,.0f} Lakhs\n"
            f"• **Across:** {count} funded deals\n\n"
            f"That is roughly ₹{total/100:,.1f} Crores invested across all seasons!"
        )

    return None


@router.post("/")
def chat_with_pitch_iq(
    message: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    msg = message.strip().lower()

    # 1. Try smart intent engine first
    smart_response = smart_answer(msg, db)
    if smart_response:
        return {"response": smart_response}

    # 2. Try HuggingFace if API key available
    hf_response = query_huggingface(message)
    if hf_response:
        return {"response": hf_response}

    # 3. Helpful fallback with context
    return {
        "response": (
            "🤔 I didn't quite catch that! I'm built to answer questions about Shark Tank India data. Try asking:\n\n"
            "• _\"Tell me about Skippi Ice Pops\"_\n"
            "• _\"Which shark invested the most?\"_\n"
            "• _\"How many food startups got funded?\"_\n"
            "• _\"What is EBITDA?\"_\n"
            "• _\"Compare Aman Gupta vs Namita Thapar\"_\n"
            "• _\"What is the success rate?\"_\n"
            "• _\"Show me season-wise investments\"_"
        )
    }
