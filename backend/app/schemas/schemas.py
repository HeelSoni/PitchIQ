from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class SharkBase(BaseModel):
    id: int
    name: str
    company: Optional[str] = None
    title: Optional[str] = None
    seasons: Optional[List[int]] = None
    expertise: Optional[List[str]] = None
    bio: Optional[str] = None
    net_worth: Optional[str] = None
    image_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class FinancialBase(BaseModel):
    id: int
    startup_id: int
    year: Optional[int] = None
    revenue: Optional[float] = None
    profit: Optional[float] = None
    ebitda: Optional[float] = None
    gross_margin: Optional[float] = None
    net_margin: Optional[float] = None
    ebitda_margin: Optional[float] = None
    burn_rate: Optional[float] = None
    runway: Optional[float] = None
    debt: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)

class DealBase(BaseModel):
    id: int
    startup_id: int
    ask_amount: Optional[float] = None
    ask_equity: Optional[float] = None
    ask_valuation: Optional[float] = None
    final_deal_amount: Optional[float] = None
    final_equity: Optional[float] = None
    final_valuation: Optional[float] = None
    deal_status: Optional[str] = None
    royalty: Optional[float] = None
    debt_component: Optional[float] = None
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class SharkDealBase(BaseModel):
    id: int
    startup_id: int
    shark_id: int
    amount_invested: Optional[float] = None
    equity_taken: Optional[float] = None
    shark: SharkBase

    model_config = ConfigDict(from_attributes=True)

class StartupBase(BaseModel):
    id: int
    name: str
    slug: str
    industry: Optional[str] = None
    business_model: Optional[str] = None
    season: Optional[int] = None
    founder_names: Optional[List[str]] = None
    founder_background: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class StartupDetail(StartupBase):
    deal: Optional[DealBase] = None
    financials: List[FinancialBase] = []
    shark_deals: List[SharkDealBase] = []

    model_config = ConfigDict(from_attributes=True)

# Statistics & Analytics
class StatsBar(BaseModel):
    total_pitches: int
    total_deals: int
    total_investment: float
    success_rate: float
