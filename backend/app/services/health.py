def calculate_health_score(startup_dict):
    """
    Computes a realistic business health score (0-100) based on:
    - Growth: 25 points
    - Profitability: 25 points
    - Margins: 20 points
    - Market Size: 15 points
    - Founder Strength: 15 points
    """
    growth_score = 15 # default average
    profit_score = 10 # default average
    margin_score = 10 # default average
    market_score = 10 # default average
    founder_score = 12 # default average

    # Financials check
    financials = startup_dict.get("financials", [])
    deal = startup_dict.get("deal", {}) or {}
    
    # Calculate Growth (based on revenue presence, deal interest)
    if financials:
        fin = financials[0]
        rev = fin.get("revenue") or 0
        profit = fin.get("profit") or 0
        gross_margin = fin.get("gross_margin") or 0
        net_margin = fin.get("net_margin") or 0

        # Growth
        if rev > 100:  # > 1 Crore (revenue is seeded in Lakhs, so > 100 Lakhs = 1Cr)
            growth_score = 22
        elif rev > 50:
            growth_score = 18
        else:
            growth_score = 14

        # Profitability (based on positive net margin or absolute profit)
        if profit > 0:
            profit_score = 22
        elif net_margin and net_margin > 0:
            profit_score = 20
        elif fin.get("ebitda") and fin.get("ebitda") > 0:
            profit_score = 18
        else:
            profit_score = 8 # burn state

        # Margins
        if gross_margin > 50:
            margin_score = 20
        elif gross_margin > 30:
            margin_score = 16
        elif gross_margin > 15:
            margin_score = 12
        else:
            margin_score = 8
    else:
        # Default fallback when financials are sparse
        if deal.get("deal_status") == "funded":
            growth_score = 18
            profit_score = 15
            margin_score = 14

    # Market size based on industry growth (Healthcare, SaaS, Biotech get premium, traditional gets standard)
    industry = str(startup_dict.get("industry") or "Other").lower()
    tech_industries = ["saas", "tech", "fintech", "biotech", "healthcare", "vehicles/electrical vehicles"]
    fmcg_industries = ["food and beverage", "beauty", "cosmetics", "fashion"]
    
    if any(ti in industry for ti in tech_industries):
        market_score = 14
    elif any(fi in industry for fi in fmcg_industries):
        market_score = 12
    else:
        market_score = 10

    # Founder Strength (based on number of founders, 2 or 3 is premium, 1 or more than 4 is standard)
    founders = startup_dict.get("founder_names") or []
    if 2 <= len(founders) <= 3:
        founder_score = 15
    elif len(founders) == 1:
        founder_score = 12
    else:
        founder_score = 10

    total_score = growth_score + profit_score + margin_score + market_score + founder_score
    return {
        "total": min(max(total_score, 0), 100),
        "breakdown": {
            "growth": growth_score,
            "profitability": profit_score,
            "margins": margin_score,
            "market_size": market_score,
            "founder_strength": founder_score
        }
    }
