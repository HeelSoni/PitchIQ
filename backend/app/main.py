from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

load_dotenv()

from app.database import engine, Base
from app.api import startups, sharks, analytics, download, chat

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="PitchIQ API",
    description="Shark Tank India Analytics Platform API",
    version="1.0.0",
    lifespan=lifespan
)

origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(startups.router, prefix="/api/startups", tags=["Startups"])
app.include_router(sharks.router, prefix="/api/sharks", tags=["Sharks"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(download.router, prefix="/api/download", tags=["Download"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])

@app.get("/")
def root():
    return {"message": "PitchIQ API is running", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "ok"}
