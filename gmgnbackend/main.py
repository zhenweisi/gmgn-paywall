import os
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router

try:
    from core.payout_agent import main as start_agent  
except ImportError as e:
    print(f"❌ Failed to import core.payout_agent: {e}")
    start_agent = None

app = FastAPI(
    title="Arc Paywall Gateway API",
    description="Web3 Paywall Gateway supporting Circle-hosted signing and GMGN / DeepSeek per-use billing",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

app.include_router(router)

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "Arc Paywall Gateway API Running",
        "version": "2.0.0"
    }

@app.on_event("startup")
async def startup_event():
    if start_agent:
        print("📡 [Integration Link] Creating implicit background task for Payout ledger monitoring...")
        asyncio.create_task(start_agent())
    else:
        print("⚠️ [WARNING] No valid core.payout_agent detected. Please run the monitoring stream manually in another window!")