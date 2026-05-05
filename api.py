import logging
from fastapi import FastAPI, BackgroundTasks, HTTPException
from main import TradingEngine
from src.market_data.market_provider import NSEScraperProvider
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TradingAPI")

app = FastAPI(title="Autonomous Trading Engine API")

# Global engine instance
engine = TradingEngine()

@app.get("/")
def read_root():
    return {"status": "online", "message": "Trading Engine API is running"}

@app.post("/trigger-cycle")
def trigger_cycle(background_tasks: BackgroundTasks):
    """
    Endpoint for Supabase Cron to trigger a single trading cycle.
    Runs in background to avoid timeout.
    """
    try:
        background_tasks.add_task(engine.run_cycle)
        return {"status": "success", "message": "Trading cycle triggered in background"}
    except Exception as e:
        logger.error(f"Failed to trigger cycle: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/calculate-eod-pnl")
def calculate_eod_pnl():
    """
    Endpoint to calculate and store daily P&L.
    Usually triggered once at the end of the day.
    """
    try:
        summary = engine.calculate_daily_pnl()
        return {
            "status": "success", 
            "date": summary.date, 
            "pnl": summary.realized_pnl,
            "total_trades": summary.total_trades
        }
    except Exception as e:
        logger.error(f"Failed to calculate P&L: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
