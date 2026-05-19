import os
import json
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from app.database import engine, Base, SessionLocal
from app.models.models import Shark, Episode, Startup, Deal, SharkDeal, Financial

def clean_val(val):
    if pd.isna(val) or val == "" or val == "null" or val == "nan":
        return None
    return val

def clean_float(val):
    if pd.isna(val) or val == "" or val == "null" or val == "nan":
        return None
    try:
        return float(val)
    except:
        return None

def clean_int(val):
    if pd.isna(val) or val == "" or val == "null" or val == "nan":
        return None
    try:
        return int(val)
    except:
        return None

def slugify(name):
    import re
    return re.sub(r'[^a-z0-9]+', '-', str(name).lower()).strip('-')

def seed_database():
    # Re-create tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()

    # Metrics
    metrics = {
        "sharks": 0,
        "episodes": 0,
        "startups": 0,
        "deals": 0,
        "financials": 0,
        "shark_deals": 0
    }

    # 1. Seed Sharks from JSON if exists, otherwise create them
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sharks_file = os.path.join(base_dir, "data", "sharks.json")
    sharks_map = {} # name -> id

    default_sharks = [
        {"name": "Aman Gupta", "company": "boAt", "title": "Co-founder & CMO, boAt", "expertise": ["Consumer Electronics", "D2C", "Marketing"]},
        {"name": "Namita Thapar", "company": "Emcure Pharmaceuticals", "title": "Executive Director, Emcure", "expertise": ["Healthcare", "Pharma"]},
        {"name": "Anupam Mittal", "company": "Shaadi.com", "title": "Founder & CEO, People Group", "expertise": ["Internet", "Marketplaces"]},
        {"name": "Vineeta Singh", "company": "SUGAR Cosmetics", "title": "CEO & Co-founder, SUGAR Cosmetics", "expertise": ["Beauty", "D2C", "Retail"]},
        {"name": "Peyush Bansal", "company": "Lenskart", "title": "CEO & Co-founder, Lenskart", "expertise": ["D2C", "Omnichannel", "Technology"]},
        {"name": "Ritesh Agarwal", "company": "OYO Rooms", "title": "Founder & CEO, OYO Rooms", "expertise": ["Hospitality", "SaaS", "Real Estate"]},
        {"name": "Amit Jain", "company": "CarDekho", "title": "CEO & Co-founder, CarDekho", "expertise": ["Automobile", "Marketplace"]},
        {"name": "Ashneer Grover", "company": "BharatPe", "title": "Former Co-founder, BharatPe", "expertise": ["Fintech", "Payments"]},
        {"name": "Ghazal Alagh", "company": "Mamaearth", "title": "Co-founder, Mamaearth", "expertise": ["D2C", "Baby Care"]}
    ]

    if os.path.exists(sharks_file):
        with open(sharks_file, "r") as f:
            sharks_data = json.load(f)
            # Merge with default info to make it super rich
            for sd in sharks_data:
                existing = next((x for x in default_sharks if x["name"].lower() == sd["name"].lower()), None)
                if existing:
                    sd.update(existing)
    else:
        sharks_data = default_sharks

    for sd in sharks_data:
        shark_obj = Shark(
            name=sd["name"],
            company=sd.get("company", "Not Disclosed"),
            title=sd.get("title", "Investor"),
            seasons=sd.get("seasons", [1,2,3,4,5]),
            expertise=sd.get("expertise", []),
            bio=sd.get("bio", f"{sd['name']} is a prominent Indian entrepreneur and investor."),
            net_worth=sd.get("net_worth", "Not Disclosed"),
            image_url=sd.get("image_url")
        )
        db.add(shark_obj)
        db.flush()
        sharks_map[sd["name"].lower()] = shark_obj.id
        metrics["sharks"] += 1

    # 2. Read CSV file
    csv_path = os.path.join(base_dir, "data", "Shark Tank India.csv")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found at {csv_path}. Please verify the path.")

    df = pd.read_csv(csv_path)

    # Let's clean the column names to remove spaces and dots just in case
    df.columns = [c.strip() for c in df.columns]

    print("Seeding episodes, startups, deals and financials...")
    episodes_map = {} # (season, ep_num) -> id

    for idx, row in df.iterrows():
        season = clean_int(row.get("Season Number"))
        ep_num = clean_int(row.get("Episode Number"))
        
        if season is None or ep_num is None:
            continue

        # Get or create episode
        ep_key = (season, ep_num)
        if ep_key not in episodes_map:
            episode = Episode(
                season=season,
                episode_number=ep_num,
                air_date=clean_val(row.get("Original Air Date")) or clean_val(row.get("Season Start"))
            )
            db.add(episode)
            db.flush()
            episodes_map[ep_key] = episode.id
            metrics["episodes"] += 1

        ep_id = episodes_map[ep_key]

        # Get or create Startup
        startup_name = clean_val(row.get("Startup Name"))
        if not startup_name:
            continue

        slug = slugify(startup_name)
        # Ensure slug uniqueness
        existing_startup = db.query(Startup).filter_by(slug=slug).first()
        if existing_startup:
            slug = f"{slug}-{season}-{ep_num}"

        # Parse founders
        presenters_cnt = clean_int(row.get("Number of Presenters"))
        males = clean_int(row.get("Male Presenters")) or 0
        females = clean_int(row.get("Female Presenters")) or 0
        trans = clean_int(row.get("Transgender Presenters")) or 0
        
        founder_names = []
        if presenters_cnt:
            founder_names = [f"Founder {i+1}" for i in range(presenters_cnt)]
        
        # Build business model representation
        business_model = "D2C"
        desc = clean_val(row.get("Business Description")) or ""
        if "app" in desc.lower() or "platform" in desc.lower() or "saas" in desc.lower() or "software" in desc.lower():
            business_model = "SaaS / Tech Platform"
        elif "brand" in desc.lower() or "direct" in desc.lower() or "website" in desc.lower() or "e-commerce" in desc.lower():
            business_model = "D2C"
        elif "store" in desc.lower() or "retail" in desc.lower():
            business_model = "Retail"
        elif "manufacturing" in desc.lower() or "factory" in desc.lower():
            business_model = "Manufacturing"
        else:
            business_model = "B2C / FMCG"

        startup = Startup(
            name=startup_name,
            slug=slug,
            industry=clean_val(row.get("Industry")) or "Other",
            business_model=business_model,
            season=season,
            episode_id=ep_id,
            founder_names=founder_names,
            founder_background="Not Disclosed",
            description=desc or "No description provided.",
            website=clean_val(row.get("Company Website")) or "Not Disclosed",
            logo_url=None
        )
        db.add(startup)
        db.flush()
        metrics["startups"] += 1

        # Seed financials
        rev = clean_float(row.get("Yearly Revenue"))
        margin = clean_float(row.get("Gross Margin"))
        net = clean_float(row.get("Net Margin"))
        ebitda = clean_float(row.get("EBITDA"))
        burn = clean_float(row.get("Cash Burn"))
        
        # In Indian Shark Tank, revenue is often in Lakhs. Let's make sure it handles correct formats.
        financial = Financial(
            startup_id=startup.id,
            year=2021 + season,  # approximate year
            revenue=rev,
            profit=None if rev is None or net is None else (rev * net / 100.0),
            ebitda=ebitda,
            gross_margin=margin,
            net_margin=net,
            ebitda_margin=None if rev is None or ebitda is None or rev == 0 else (ebitda / rev * 100.0),
            burn_rate=burn,
            runway=None if burn is None or burn == 0 else 12.0, # default placeholder runway calculation
            debt=clean_float(row.get("Total Deal Debt")),
            cac=None,
            ltv=None,
            aov=None,
            repeat_rate=None
        )
        db.add(financial)
        metrics["financials"] += 1

        # Seed Deal
        received_offer = clean_int(row.get("Received Offer"))
        accepted_offer = clean_int(row.get("Accepted Offer"))
        deal_status = "funded" if (received_offer == 1 and accepted_offer == 1) else "not funded"

        ask_amt = clean_float(row.get("Original Ask Amount"))
        ask_eq = clean_float(row.get("Original Offered Equity"))
        ask_val = clean_float(row.get("Valuation Requested"))

        final_amt = clean_float(row.get("Total Deal Amount"))
        final_eq = clean_float(row.get("Total Deal Equity"))
        final_val = clean_float(row.get("Deal Valuation"))

        # Calculate implied valuation if missing
        if ask_val is None and ask_amt is not None and ask_eq is not None and ask_eq > 0:
            ask_val = (ask_amt / ask_eq) * 100

        if final_val is None and final_amt is not None and final_eq is not None and final_eq > 0:
            final_val = (final_amt / final_eq) * 100

        deal = Deal(
            startup_id=startup.id,
            ask_amount=ask_amt,
            ask_equity=ask_eq,
            ask_valuation=ask_val,
            final_deal_amount=final_amt if deal_status == "funded" else None,
            final_equity=final_eq if deal_status == "funded" else None,
            final_valuation=final_val if deal_status == "funded" else None,
            deal_status=deal_status,
            counter_offer=None,
            royalty=clean_float(row.get("Royalty Percentage")),
            debt_component=clean_float(row.get("Total Deal Debt")),
            notes=clean_val(row.get("Episode Title"))
        )
        db.add(deal)
        db.flush()
        metrics["deals"] += 1

        # Seed Shark Investments
        if deal_status == "funded":
            sharks_list = ["Namita", "Vineeta", "Anupam", "Aman", "Peyush", "Ritesh", "Amit"]
            for sname in sharks_list:
                amt_col = f"{sname} Investment Amount"
                eq_col = f"{sname} Investment Equity"
                
                s_amt = clean_float(row.get(amt_col))
                s_eq = clean_float(row.get(eq_col))

                if (s_amt is not None and s_amt > 0) or (s_eq is not None and s_eq > 0):
                    # Check if shark exists in DB
                    full_name = next((k for k in sharks_map.keys() if sname.lower() in k), None)
                    if full_name:
                        shark_id = sharks_map[full_name]
                        s_deal = SharkDeal(
                            startup_id=startup.id,
                            shark_id=shark_id,
                            amount_invested=s_amt,
                            equity_taken=s_eq
                        )
                        db.add(s_deal)
                        metrics["shark_deals"] += 1

            # Seed guest investments
            guest_amt = clean_float(row.get("Guest Investment Amount"))
            guest_eq = clean_float(row.get("Guest Investment Equity"))
            guest_name = clean_val(row.get("Invested Guest Name"))

            if guest_name and ((guest_amt is not None and guest_amt > 0) or (guest_eq is not None and guest_eq > 0)):
                # Ensure guest shark is registered
                g_key = guest_name.lower()
                if g_key not in sharks_map:
                    g_shark = Shark(
                        name=guest_name,
                        company="Guest Investor",
                        title="Guest Shark",
                        seasons=[season],
                        expertise=["Venture Capital", "Strategy"],
                        bio=f"{guest_name} appeared as a guest shark on Shark Tank India Season {season}.",
                        net_worth="Not Disclosed"
                    )
                    db.add(g_shark)
                    db.flush()
                    sharks_map[g_key] = g_shark.id
                    metrics["sharks"] += 1

                g_id = sharks_map[g_key]
                s_deal = SharkDeal(
                    startup_id=startup.id,
                    shark_id=g_id,
                    amount_invested=guest_amt,
                    equity_taken=guest_eq
                )
                db.add(s_deal)
                metrics["shark_deals"] += 1

    db.commit()
    db.close()
    print("Database seeding completed successfully!")
    return metrics

if __name__ == "__main__":
    seed_database()
