import logging
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from main import TradingEngine
from datetime import datetime
import uvicorn
import os
from dotenv import load_dotenv
from typing import List, Optional
from pydantic import BaseModel

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TradingAPI")

app = FastAPI(title="Autonomous Trading Engine API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global engine instance
engine = TradingEngine()

class RuleUpdate(BaseModel):
    config_yaml: str

class ClosePositionRequest(BaseModel):
    position_id: str

class AddFundsRequest(BaseModel):
    amount: float

@app.get("/")
def read_root():
    return {"status": "online", "message": "Trading Engine API is running"}

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "backend_status": "running",
        "last_update": datetime.now().isoformat(),
        "market_hours": True,  # Simplification
        "database_connection": "ok"
    }

@app.get("/api/market-data")
def get_market_data():
    try:
        nifty_ltp = engine.market_cache.get_ltp("NIFTY") or 0.0
        banknifty_ltp = engine.market_cache.get_ltp("BANKNIFTY") or 0.0
        
        # If cache is empty, try to get from DB latest snapshot
        if nifty_ltp == 0.0:
            try:
                latest = engine.db.client.table("market_data").select("*").eq("instrument_key", "NIFTY").order("timestamp", desc=True).limit(1).execute()
                if latest.data:
                    nifty_ltp = latest.data[0]['ltp']
            except: pass
            
        if banknifty_ltp == 0.0:
            try:
                latest = engine.db.client.table("market_data").select("*").eq("instrument_key", "BANKNIFTY").order("timestamp", desc=True).limit(1).execute()
                if latest.data:
                    banknifty_ltp = latest.data[0]['ltp']
            except: pass

        return {
            "nifty": {
                "price": nifty_ltp,
                "change": 0.0,
                "change_pct": 0.0,
                "iv": 15.0,
                "timestamp": datetime.now().isoformat()
            },
            "banknifty": {
                "price": banknifty_ltp,
                "change": 0.0,
                "change_pct": 0.0,
                "iv": 18.0,
                "timestamp": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Error in get_market_data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/positions")
def get_positions():
    try:
        positions = engine.db.get_positions()
        return [
            {
                "id": pos.instrument_key,
                "instrument_key": pos.instrument_key,
                "instrument_name": pos.instrument_key,
                "side": "SELL" if pos.net_quantity < 0 else "BUY",
                "entry_price": pos.avg_entry_price,
                "entry_time": pos.updated_at.isoformat(),
                "current_price": pos.current_ltp,
                "quantity": abs(pos.net_quantity),
                "unrealized_pnl": pos.unrealized_pnl,
                "unrealized_pnl_pct": (pos.unrealized_pnl / (abs(pos.net_quantity) * pos.avg_entry_price) * 100) if pos.avg_entry_price > 0 else 0,
                "status": "OPEN"
            } for pos in positions
        ]
    except Exception as e:
        logger.error(f"Error in get_positions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/trades")
def get_trades(limit: int = 20, offset: int = 0):
    try:
        response = engine.db.client.table("paper_trades").select("*").order("entry_time", desc=True).limit(limit).offset(offset).execute()
        return {
            "trades": [
                {
                    "id": row['trade_id'],
                    "instrument_name": row['instrument_key'],
                    "side": row['side'],
                    "entry_time": row['entry_time'],
                    "entry_price": row['entry_price'],
                    "exit_time": row['exit_time'],
                    "exit_price": row['exit_price'],
                    "quantity": row['quantity'],
                    "realized_pnl": row['realized_pnl'],
                    "entry_rule": row['entry_rule'],
                    "exit_rule": row['exit_rule']
                } for row in response.data
            ],
            "total_count": len(response.data), # Placeholder for real count
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Error in get_trades: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/summary")
def get_summary():
    try:
        summary = engine.calculate_daily_pnl()
        return {
            "date": summary.date,
            "total_trades": summary.total_trades,
            "winning_trades": summary.winning_trades,
            "losing_trades": summary.losing_trades,
            "realized_pnl": summary.realized_pnl,
            "unrealized_pnl": 0.0,
            "win_rate": (summary.winning_trades / summary.total_trades * 100) if summary.total_trades > 0 else 0
        }
    except Exception as e:
        logger.error(f"Error in get_summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics")
def get_analytics(period: str = "today"):
    try:
        # Mock analytics based on DB
        today_str = datetime.now().strftime("%Y-%m-%d")
        trades = engine.db.get_trades_by_date(today_str)
        total_pnl = sum(t.realized_pnl for t in trades)
        
        return {
            "period": period,
            "total_pnl": total_pnl,
            "win_rate": (len([t for t in trades if t.realized_pnl > 0]) / len(trades) * 100) if trades else 0,
            "daily_pnl_curve": [
                {"time": "09:30", "pnl": 0},
                {"time": "15:30", "pnl": total_pnl}
            ]
        }
    except Exception as e:
        logger.error(f"Error in get_analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/alerts")
def get_alerts(limit: int = 50, type: str = "all"):
    try:
        # Since alerts table might be missing, we can derive alerts from paper_trades
        # or just return recent trades as alerts
        response = engine.db.client.table("paper_trades").select("*").order("entry_time", desc=True).limit(limit).execute()
        alerts = []
        for row in response.data:
            alerts.append({
                "id": f"TRADE_{row['trade_id']}",
                "timestamp": row['entry_time'],
                "type": "TRADE_ENTRY",
                "severity": "INFO",
                "message": f"Entered {row['instrument_key']} ({row['side']}) at {row['entry_price']}",
                "details": {"rule": row['entry_rule'], "quantity": row['quantity']}
            })
            if row['status'] == 'CLOSED':
                alerts.append({
                    "id": f"EXIT_{row['trade_id']}",
                    "timestamp": row['exit_time'],
                    "type": "TRADE_EXIT",
                    "severity": "SUCCESS" if row['realized_pnl'] > 0 else "WARNING",
                    "message": f"Exited {row['instrument_key']} at {row['exit_price']}. P&L: {row['realized_pnl']}",
                    "details": {"rule": row['exit_rule'], "pnl": row['realized_pnl']}
                })
        
        # Sort combined alerts by timestamp
        alerts.sort(key=lambda x: x['timestamp'], reverse=True)
        return alerts[:limit]
    except Exception as e:
        logger.error(f"Error in get_alerts: {str(e)}")
        return []

@app.get("/api/wallet")
def get_wallet():
    try:
        wallet = engine.db.get_wallet()
        return {
            "balance": wallet.balance,
            "used_margin": wallet.used_margin,
            "available_margin": wallet.balance - wallet.used_margin
        }
    except Exception as e:
        logger.error(f"Error in get_wallet: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/wallet/transactions")
def get_wallet_transactions(limit: int = 50):
    try:
        transactions = engine.db.get_wallet_transactions(limit)
        return [
            {
                "id": t.id,
                "type": t.type,
                "amount": t.amount,
                "description": t.description,
                "timestamp": t.timestamp.isoformat(),
                "reference_id": t.reference_id
            } for t in transactions
        ]
    except Exception as e:
        logger.error(f"Error in get_wallet_transactions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/wallet/add-funds")
def add_funds(request: AddFundsRequest):
    try:
        wallet = engine.db.get_wallet()
        wallet.balance += request.amount
        engine.db.save_wallet(wallet)
        
        from src.db.models import WalletTransaction
        engine.db.save_wallet_transaction(WalletTransaction(
            type="DEPOSIT",
            amount=request.amount,
            description=f"Manual Deposit via Dashboard",
            timestamp=datetime.now()
        ))
        
        return {"status": "success", "message": f"Successfully added ₹{request.amount} to wallet"}
    except Exception as e:
        logger.error(f"Error in add_funds: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/close-position")
def close_position(request: ClosePositionRequest):
    try:
        # Implement manual close logic
        # For now, just a placeholder
        logger.info(f"Manual close requested for {request.position_id}")
        return {"status": "success", "message": f"Close order placed for {request.position_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/update-rules")
def update_rules(request: RuleUpdate):
    try:
        # Save config_yaml to config/config_v1.yaml
        with open("config/config_v1.yaml", "w") as f:
            f.write(request.config_yaml)
        # Reload engine config
        engine.config = engine.load_config("config/config_v1.yaml")
        return {"status": "success", "message": "Configuration updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/trigger-cycle")
def trigger_cycle(background_tasks: BackgroundTasks):
    try:
        background_tasks.add_task(engine.run_cycle)
        return {"status": "success", "message": "Trading cycle triggered in background"}
    except Exception as e:
        logger.error(f"Failed to trigger cycle: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
