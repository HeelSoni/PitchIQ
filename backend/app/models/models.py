from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class Shark(Base):
    __tablename__ = "sharks"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    company = Column(String)
    title = Column(String)
    seasons = Column(JSON)
    expertise = Column(JSON)
    bio = Column(Text)
    net_worth = Column(String)
    image_url = Column(String)
    deals = relationship("SharkDeal", back_populates="shark")

class Episode(Base):
    __tablename__ = "episodes"
    id = Column(Integer, primary_key=True)
    season = Column(Integer, nullable=False)
    episode_number = Column(Integer, nullable=False)
    air_date = Column(String)
    startups = relationship("Startup", back_populates="episode")

class Startup(Base):
    __tablename__ = "startups"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    industry = Column(String)
    business_model = Column(String)
    season = Column(Integer)
    episode_id = Column(Integer, ForeignKey("episodes.id"))
    episode = relationship("Episode", back_populates="startups")
    founder_names = Column(JSON)
    founder_background = Column(Text)
    description = Column(Text)
    website = Column(String)
    logo_url = Column(String)
    deal = relationship("Deal", back_populates="startup", uselist=False)
    financials = relationship("Financial", back_populates="startup")
    shark_deals = relationship("SharkDeal", back_populates="startup")

class Deal(Base):
    __tablename__ = "deals"
    id = Column(Integer, primary_key=True)
    startup_id = Column(Integer, ForeignKey("startups.id"), unique=True)
    startup = relationship("Startup", back_populates="deal")
    ask_amount = Column(Float)
    ask_equity = Column(Float)
    ask_valuation = Column(Float)
    final_deal_amount = Column(Float)
    final_equity = Column(Float)
    final_valuation = Column(Float)
    deal_status = Column(String)  # funded / not_funded
    counter_offer = Column(Boolean, default=False)
    royalty = Column(Float)
    debt_component = Column(Float)
    notes = Column(Text)

class SharkDeal(Base):
    __tablename__ = "shark_deals"
    id = Column(Integer, primary_key=True)
    startup_id = Column(Integer, ForeignKey("startups.id"))
    shark_id = Column(Integer, ForeignKey("sharks.id"))
    amount_invested = Column(Float)
    equity_taken = Column(Float)
    startup = relationship("Startup", back_populates="shark_deals")
    shark = relationship("Shark", back_populates="deals")

class Financial(Base):
    __tablename__ = "financials"
    id = Column(Integer, primary_key=True)
    startup_id = Column(Integer, ForeignKey("startups.id"))
    startup = relationship("Startup", back_populates="financials")
    year = Column(Integer)
    revenue = Column(Float)
    profit = Column(Float)
    ebitda = Column(Float)
    gross_margin = Column(Float)
    net_margin = Column(Float)
    ebitda_margin = Column(Float)
    burn_rate = Column(Float)
    runway = Column(Float)
    debt = Column(Float)
    cac = Column(Float)
    ltv = Column(Float)
    aov = Column(Float)
    repeat_rate = Column(Float)
