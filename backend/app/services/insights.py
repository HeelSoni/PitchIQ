def generate_ai_insight(startup_dict):
    """
    Generates a premium, highly contextual AI insight paragraph for a startup
    based on real financial metrics, industry category, and investment deal terms.
    """
    name = startup_dict.get("name")
    industry = startup_dict.get("industry", "Business")
    deal = startup_dict.get("deal", {}) or {}
    financials = startup_dict.get("financials", [])
    
    deal_status = deal.get("deal_status")
    ask_valuation = deal.get("ask_valuation")
    final_valuation = deal.get("final_valuation")
    
    # Financial metrics extraction
    revenue = None
    profit = None
    gross_margin = None
    if financials:
        fin = financials[0]
        revenue = fin.get("revenue")
        profit = fin.get("profit")
        gross_margin = fin.get("gross_margin")

    # Dynamic insight parts
    intro = f"**{name}** operates in the highly competitive **{industry}** sector. "
    
    financial_analysis = ""
    if revenue is not None:
        rev_str = f"₹{revenue:.1f} Lakhs" if revenue < 100 else f"₹{revenue/100:.2f} Cr"
        financial_analysis = f"With a disclosed yearly top-line of {rev_str}, they have demonstrated solid market validation. "
        if gross_margin and gross_margin > 40:
            financial_analysis += f"Their high gross margin profile of {gross_margin}% provides excellent unit economics and significant room to scale digital marketing channels. "
        else:
            financial_analysis += "However, relatively low gross margins suggest high manufacturing or operational overhead that could squeeze profitability as scale increases. "
    else:
        financial_analysis = "Financial metrics were largely kept confidential during the pitch, suggesting a pre-revenue or stealth-mode operational state. "

    deal_analysis = ""
    if deal_status == "funded":
        dilution = 0
        if deal.get("final_equity") and deal.get("final_deal_amount"):
            # Dilution
            dilution = deal.get("final_equity")
        
        val_gap_str = ""
        if ask_valuation and final_valuation:
            gap = ((ask_valuation - final_valuation) / ask_valuation) * 100
            if gap > 20:
                val_gap_str = f" The sharks successfully negotiated a substantial {gap:.1f}% valuation correction, bridging the gap between founder optimism and market realities."
        
        deal_analysis = f"Securing a deal on the show validates their core product-market fit.{val_gap_str} Partnering with the sharks will accelerate distribution networks and offline retail partnerships."
    else:
        deal_analysis = "Without active shark backing, the founders face the challenge of scaling organically. They will need to focus deeply on customer acquisition cost (CAC) optimization and extending runway to secure institutional venture capital."

    verdict = ""
    if gross_margin and gross_margin > 50 and deal_status == "funded":
        verdict = " **Verdict:** A high-potential enterprise with a highly scalable margin profile. Valuation is premium but aligned with the robust unit economics."
    elif profit and profit > 0:
        verdict = " **Verdict:** A rare bootstrapped-style profitable gem. Excellent downside protection, though scale velocity depends on capital efficiency."
    else:
        verdict = " **Verdict:** Aggressive valuation expectations relative to historical metrics. Long-term success is contingent on massive D2C community growth and product differentiation."

    return intro + financial_analysis + deal_analysis + verdict
