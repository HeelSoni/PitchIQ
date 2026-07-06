from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, case
from app.database import get_db
from app.models.models import Startup, Deal, SharkDeal, Shark, Financial
import os
import httpx
import json

router = APIRouter()


def build_db_context(msg: str, db: Session) -> str:
    """
    Fetches relevant data from the database based on keywords in the message
    and formats it as a rich context string for the LLM to use.
    """
    context_parts = []

    # --- Global stats always included ---
    total_pitches = db.query(Startup).count()
    total_funded = db.query(Deal).filter(Deal.deal_status == "funded").count()
    total_investment = db.query(func.sum(Deal.final_deal_amount)).filter(Deal.deal_status == "funded").scalar() or 0
    success_rate = round((total_funded / total_pitches * 100), 1) if total_pitches > 0 else 0

    context_parts.append(
        f"GLOBAL STATS: {total_pitches} total pitches, {total_funded} funded deals, "
        f"₹{total_investment:,.0f} Lakhs total investment, {success_rate}% success rate across Seasons 1-5."
    )

    # --- Shark stats ---
    shark_data = db.query(
        Shark.name, Shark.company, Shark.bio,
        func.count(SharkDeal.id).label("deals"),
        func.sum(SharkDeal.amount_invested).label("total_invested")
    ).outerjoin(SharkDeal, SharkDeal.shark_id == Shark.id)\
     .group_by(Shark.id).all()

    shark_lines = []
    for s in shark_data:
        amt = f"₹{s[4]:,.0f} Lakhs" if s[4] else "₹0"
        shark_lines.append(f"{s[0]} ({s[1]}): {s[3]} deals, {amt} invested. Bio: {(s[2] or '')[:100]}")
    if shark_lines:
        context_parts.append("SHARKS:\n" + "\n".join(shark_lines))

    # --- Industry breakdown ---
    industry_stats = db.query(
        Startup.industry,
        func.count(Startup.id).label("count"),
        func.sum(case([(Deal.deal_status == "funded", 1)], else_=0)).label("funded")
    ).join(Deal).group_by(Startup.industry).order_by(desc("funded")).limit(15).all()

    if industry_stats:
        ind_lines = [f"{i[0]}: {i[1]} pitches, {i[2]} funded" for i in industry_stats if i[0]]
        context_parts.append("INDUSTRIES:\n" + "\n".join(ind_lines))

    # --- Season breakdown ---
    season_stats = db.query(
        Startup.season,
        func.count(Startup.id).label("pitches"),
        func.sum(Deal.final_deal_amount).label("total_inv")
    ).join(Deal).group_by(Startup.season).order_by(Startup.season).all()

    if season_stats:
        season_lines = [
            f"Season {s[0]}: {s[1]} pitches, ₹{s[2]:,.0f} Lakhs invested" if s[2] else f"Season {s[0]}: {s[1]} pitches"
            for s in season_stats
        ]
        context_parts.append("SEASONS:\n" + "\n".join(season_lines))

    # --- Relevant startups based on message keywords ---
    keywords = [w for w in msg.split() if len(w) > 3]
    found_startups = []
    for kw in keywords[:5]:  # check first 5 meaningful words
        results = db.query(Startup).filter(Startup.name.ilike(f"%{kw}%")).limit(3).all()
        for r in results:
            if r not in found_startups:
                found_startups.append(r)

    # Also try full message match
    full_match = db.query(Startup).filter(Startup.name.ilike(f"%{msg[:30]}%")).limit(3).all()
    for r in full_match:
        if r not in found_startups:
            found_startups.append(r)

    if found_startups:
        startup_lines = []
        for s in found_startups[:5]:
            d = s.deal
            if d:
                status = "Funded" if d.deal_status == "funded" else "Not Funded"
                amt = f"₹{d.final_deal_amount:,.0f}L for {d.final_equity}%" if d.final_deal_amount else "N/A"
                ask = f"₹{d.ask_amount:,.0f}L for {d.ask_equity}%" if d.ask_amount else "N/A"
                startup_lines.append(
                    f"{s.name} (Season {s.season}, {s.industry}): Asked {ask}, Status: {status}, Deal: {amt}. "
                    f"Desc: {(s.description or '')[:100]}"
                )
        if startup_lines:
            context_parts.append("RELEVANT STARTUPS:\n" + "\n".join(startup_lines))

    return "\n\n".join(context_parts)


def query_gemini(question: str, context: str) -> str | None:
    """Call Google Gemini free API with database context."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        system_prompt = (
            "You are PitchIQ AI — an expert analyst specializing in Shark Tank India. "
            "You have access to real-time data from all 5 seasons of Shark Tank India. "
            "Answer questions naturally, helpfully, and in a friendly but professional tone. "
            "Use the database context provided to give accurate, data-backed answers. "
            "Format responses with markdown bold (**text**) and bullet points where helpful. "
            "Keep responses concise but complete. If asked about something not in the data, "
            "say so honestly and offer related insights you do have."
        )

        full_prompt = (
            f"{system_prompt}\n\n"
            f"DATABASE CONTEXT (real-time data from PitchIQ):\n{context}\n\n"
            f"USER QUESTION: {question}\n\n"
            f"Answer:"
        )

        payload = {
            "contents": [{"parts": [{"text": full_prompt}]}],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 400,
                "topP": 0.9
            }
        }

        response = httpx.post(url, json=payload, timeout=10.0)
        if response.status_code == 200:
            data = response.json()
            candidates = data.get("candidates", [])
            if candidates:
                return candidates[0]["content"]["parts"][0]["text"]
    except Exception as e:
        print(f"Gemini query failed: {e}")
    return None


def query_huggingface(question: str, context: str) -> str | None:
    """Fallback: HuggingFace with context."""
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    if not api_key:
        return None
    try:
        API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
        headers = {"Authorization": f"Bearer {api_key}"}
        prompt = (
            f"[INST] You are PitchIQ AI, an expert on Shark Tank India. "
            f"Use this data to answer the question:\n\n{context[:1500]}\n\n"
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
                text = res_json[0].get("generated_text", "")
                if text and len(text) > 20:
                    return text.strip()
    except Exception as e:
        print(f"HuggingFace query failed: {e}")
    return None


@router.post("/")
def chat_with_pitch_iq(
    message: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    msg = message.strip()
    msg_lower = msg.lower()

    # Build rich DB context for this question
    context = build_db_context(msg_lower, db)

    # 1. Try Gemini (best quality, free tier)
    gemini_response = query_gemini(msg, context)
    if gemini_response:
        return {"response": gemini_response.strip()}

    # 2. Try HuggingFace fallback
    hf_response = query_huggingface(msg, context)
    if hf_response:
        return {"response": hf_response}

    # 3. No API key configured — return the context-based data directly
    # This at least gives the user relevant data even without an LLM
    stats_line = context.split("GLOBAL STATS: ")[-1].split("\n")[0] if "GLOBAL STATS:" in context else ""
    relevant_startup = ""
    if "RELEVANT STARTUPS:" in context:
        first_startup = context.split("RELEVANT STARTUPS:\n")[-1].split("\n")[0]
        relevant_startup = f"\n\n📋 **Most Relevant Match:** {first_startup}"

    return {
        "response": (
            f"📊 Here's what PitchIQ's database says:\n\n"
            f"**{stats_line}**"
            f"{relevant_startup}\n\n"
            f"💡 _To get full AI answers to any question, add a **GEMINI_API_KEY** in your Render environment variables. "
            f"Get a free key at [Google AI Studio](https://aistudio.google.com/app/apikey)._\n\n"
            f"Meanwhile, try asking:\n"
            f"• _\"Which shark invested the most?\"_\n"
            f"• _\"Tell me about Skippi Ice Pops\"_\n"
            f"• _\"How many food startups got funded?\"_"
        )
    }
