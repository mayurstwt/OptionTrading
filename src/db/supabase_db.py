import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from supabase import create_client, Client
from src.db.models import Trade, Position, DailySummary, MarketSnapshot
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class SupabaseDatabase:
    """
    Handles all Supabase database operations.
    Replaces the local SQLite implementation.
    """

    def __init__(self, url: str = None, key: str = None):
        self.url = url or os.getenv("SUPABASE_URL")
        self.key = key or os.getenv("SUPABASE_KEY")
        
        if not self.url or not self.key:
            logger.error("SUPABASE_URL or SUPABASE_KEY missing in environment variables")
            raise ValueError("Supabase credentials missing")
            
        self.client: Client = create_client(self.url, self.key)
        logger.info("Supabase client initialized successfully")

    def save_trade(self, trade: Trade):
        """Save a new trade or update an existing one."""
        data = {
            "trade_id": trade.trade_id,
            "strategy": trade.strategy,
            "instrument_key": trade.instrument_key,
            "side": trade.side,
            "quantity": trade.quantity,
            "entry_time": trade.entry_time.isoformat(),
            "entry_price": trade.entry_price,
            "status": trade.status,
            "entry_rule": trade.entry_rule,
            "exit_time": trade.exit_time.isoformat() if trade.exit_time else None,
            "exit_price": trade.exit_price,
            "exit_rule": trade.exit_rule,
            "realized_pnl": trade.realized_pnl,
            "trade_duration_minutes": trade.trade_duration_minutes,
            "notes": trade.notes
        }
        
        try:
            # upsert based on trade_id
            self.client.table("paper_trades").upsert(data, on_conflict="trade_id").execute()
        except Exception as e:
            logger.error(f"Error saving trade to Supabase: {str(e)}")

    def get_open_trades(self) -> List[Trade]:
        """Fetch all open trades."""
        try:
            response = self.client.table("paper_trades").select("*").eq("status", "OPEN").execute()
            return [self._row_to_trade(row) for row in response.data]
        except Exception as e:
            logger.error(f"Error fetching open trades from Supabase: {str(e)}")
            return []

    def _row_to_trade(self, row) -> Trade:
        return Trade(
            trade_id=row['trade_id'],
            strategy=row['strategy'],
            instrument_key=row['instrument_key'],
            side=row['side'],
            quantity=row['quantity'],
            entry_time=datetime.fromisoformat(row['entry_time']),
            entry_price=row['entry_price'],
            status=row['status'],
            entry_rule=row['entry_rule'],
            exit_time=datetime.fromisoformat(row['exit_time']) if row['exit_time'] else None,
            exit_price=row['exit_price'],
            exit_rule=row['exit_rule'],
            realized_pnl=row['realized_pnl'],
            trade_duration_minutes=row['trade_duration_minutes'],
            notes=row['notes']
        )

    def save_position(self, position: Position):
        """Update or insert a position."""
        data = {
            "instrument_key": position.instrument_key,
            "net_quantity": position.net_quantity,
            "avg_entry_price": position.avg_entry_price,
            "current_ltp": position.current_ltp,
            "unrealized_pnl": position.unrealized_pnl,
            "updated_at": position.updated_at.isoformat()
        }
        try:
            self.client.table("paper_positions").upsert(data, on_conflict="instrument_key").execute()
        except Exception as e:
            logger.error(f"Error saving position to Supabase: {str(e)}")

    def get_positions(self) -> List[Position]:
        """Fetch all current positions."""
        try:
            response = self.client.table("paper_positions").select("*").execute()
            return [Position(
                instrument_key=row['instrument_key'],
                net_quantity=row['net_quantity'],
                avg_entry_price=row['avg_entry_price'],
                current_ltp=row['current_ltp'],
                unrealized_pnl=row['unrealized_pnl'],
                updated_at=datetime.fromisoformat(row['updated_at'])
            ) for row in response.data]
        except Exception as e:
            logger.error(f"Error fetching positions from Supabase: {str(e)}")
            return []

    def delete_position(self, instrument_key: str):
        """Remove a position when it's closed."""
        try:
            self.client.table("paper_positions").delete().eq("instrument_key", instrument_key).execute()
        except Exception as e:
            logger.error(f"Error deleting position from Supabase: {str(e)}")

    def save_daily_summary(self, summary: DailySummary):
        """Save EOD summary."""
        data = {
            "date": summary.date,
            "total_trades": summary.total_trades,
            "winning_trades": summary.winning_trades,
            "losing_trades": summary.losing_trades,
            "realized_pnl": summary.realized_pnl,
            "max_drawdown_pct": summary.max_drawdown_pct
        }
        try:
            self.client.table("daily_summary").upsert(data, on_conflict="date").execute()
        except Exception as e:
            logger.error(f"Error saving daily summary to Supabase: {str(e)}")

    def save_market_snapshot(self, snapshot: MarketSnapshot):
        """Save a market data snapshot."""
        data = {
            "instrument_key": snapshot.instrument_key,
            "ltp": snapshot.ltp,
            "bid": snapshot.bid,
            "ask": snapshot.ask,
            "volume": snapshot.volume,
            "oi": snapshot.oi,
            "iv": snapshot.iv,
            "timestamp": snapshot.timestamp.isoformat()
        }
        try:
            self.client.table("market_data").insert(data).execute()
        except Exception as e:
            logger.error(f"Error saving market snapshot to Supabase: {str(e)}")

    def get_trades_by_date(self, date_str: str) -> List[Trade]:
        """Fetch all trades for a specific date (YYYY-MM-DD)."""
        try:
            # Filtering by entry_time starting with the date
            response = self.client.table("paper_trades").select("*").ilike("entry_time", f"{date_str}%").execute()
            return [self._row_to_trade(row) for row in response.data]
        except Exception as e:
            logger.error(f"Error fetching trades by date: {str(e)}")
            return []
