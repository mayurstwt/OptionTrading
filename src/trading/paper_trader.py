import uuid
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from src.db.supabase_db import SupabaseDatabase
from src.db.models import Trade, Position, WalletTransaction
from src.market_data.market_cache import MarketCache

logger = logging.getLogger(__name__)

class PaperTrader:
    """
    Simulates order execution for paper trading.
    Updates the Supabase database and manages positions.
    """

    def __init__(self, db: SupabaseDatabase, market_cache: MarketCache):
        self.db = db
        self.market_cache = market_cache

    def place_order(self, strategy: str, instrument_key: str, side: str, quantity: int, 
                    entry_rule: str = None) -> Optional[Trade]:
        """
        Simulate an order execution at current LTP.
        """
        current_ltp = self.market_cache.get_ltp(instrument_key)
        if current_ltp is None:
            logger.error(f"Cannot place order for {instrument_key}: LTP not available")
            return None

        trade_id = str(uuid.uuid4())
        trade = Trade(
            trade_id=trade_id,
            strategy=strategy,
            instrument_key=instrument_key,
            side=side.upper(),
            quantity=quantity,
            entry_time=datetime.now(),
            entry_price=current_ltp,
            status="OPEN",
            entry_rule=entry_rule
        )

        # Save to DB
        self.db.save_trade(trade)
        
        # Update Position
        self._update_position(trade)
        
        # Block Margin in Wallet
        self._handle_margin(trade, "BLOCK")
        
        logger.info(f"PAPER ORDER PLACED: {side} {quantity} lots of {instrument_key} @ {current_ltp}")
        return trade

    def close_position(self, instrument_key: str, exit_rule: str = None) -> Optional[Trade]:
        """
        Close all open trades for a given instrument.
        Simplification: Closes the first open trade found. 
        In production, we should handle multiple open trades per instrument.
        """
        open_trades = [t for t in self.db.get_open_trades() if t.instrument_key == instrument_key]
        if not open_trades:
            logger.warning(f"No open trades found for {instrument_key}")
            return None

        # For now, close the first one (assuming 1 trade per instrument for simplicity)
        trade = open_trades[0]
        current_ltp = self.market_cache.get_ltp(instrument_key)
        if current_ltp is None:
            logger.error(f"Cannot close position for {instrument_key}: LTP not available")
            return None

        trade.status = "CLOSED"
        trade.exit_time = datetime.now()
        trade.exit_price = current_ltp
        trade.exit_rule = exit_rule
        
        # Calculate P&L with lot size multipliers
        lot_sizes = {"NIFTY": 25, "BANKNIFTY": 15}
        multiplier = lot_sizes.get(trade.instrument_key, 1) # Default to 1 if not found
        
        price_diff = trade.exit_price - trade.entry_price
        if trade.side == "SELL":
            trade.realized_pnl = -price_diff * trade.quantity * multiplier
        else:
            trade.realized_pnl = price_diff * trade.quantity * multiplier

        duration = (trade.exit_time - trade.entry_time).total_seconds() / 60
        trade.trade_duration_minutes = int(duration)

        # Save updated trade
        self.db.save_trade(trade)
        
        # Remove from positions
        self.db.delete_position(instrument_key)
        
        # Release Margin and Settle P&L
        self._handle_margin(trade, "RELEASE")
        self._settle_pnl(trade)
        
        logger.info(f"PAPER POSITION CLOSED: {instrument_key} @ {current_ltp}. P&L: {trade.realized_pnl}")
        return trade

    def _handle_margin(self, trade: Trade, action: str):
        """Block or release margin in the wallet."""
        try:
            wallet = self.db.get_wallet()
            # Simplified margin: 1L for sell, 20k for buy per lot
            margin_per_lot = 100000 if trade.side == "SELL" else 20000
            total_margin = margin_per_lot * trade.quantity
            
            if action == "BLOCK":
                wallet.used_margin += total_margin
                description = f"Margin Blocked: {trade.instrument_key} {trade.side}"
                tx_type = "MARGIN_BLOCKED"
            else:
                wallet.used_margin -= total_margin
                description = f"Margin Released: {trade.instrument_key} {trade.side}"
                tx_type = "MARGIN_RELEASED"
                
            self.db.save_wallet(wallet)
            self.db.save_wallet_transaction(WalletTransaction(
                type=tx_type,
                amount=-total_margin if action == "BLOCK" else total_margin,
                description=description,
                timestamp=datetime.now(),
                reference_id=trade.trade_id
            ))
        except Exception as e:
            logger.error(f"Failed to handle margin: {str(e)}")

    def _settle_pnl(self, trade: Trade):
        """Settle realized P&L to the wallet balance."""
        try:
            wallet = self.db.get_wallet()
            wallet.balance += trade.realized_pnl
            self.db.save_wallet(wallet)
            
            self.db.save_wallet_transaction(WalletTransaction(
                type="PNL_SETTLEMENT",
                amount=trade.realized_pnl,
                description=f"P&L Settlement: {trade.instrument_key}",
                timestamp=datetime.now(),
                reference_id=trade.trade_id
            ))
        except Exception as e:
            logger.error(f"Failed to settle P&L: {str(e)}")

    def _update_position(self, trade: Trade):
        """Update the paper_positions table."""
        positions = self.db.get_positions()
        pos = next((p for p in positions if p.instrument_key == trade.instrument_key), None)

        if pos:
            # Update existing position (averaging)
            new_qty = pos.net_quantity + (trade.quantity if trade.side == "BUY" else -trade.quantity)
            if new_qty == 0:
                self.db.delete_position(trade.instrument_key)
                return
            
            # Simplified average price calculation
            total_cost = (pos.avg_entry_price * abs(pos.net_quantity)) + (trade.entry_price * trade.quantity)
            pos.avg_entry_price = total_cost / abs(new_qty)
            pos.net_quantity = new_qty
            pos.updated_at = datetime.now()
        else:
            # Create new position
            qty = trade.quantity if trade.side == "BUY" else -trade.quantity
            pos = Position(
                instrument_key=trade.instrument_key,
                net_quantity=qty,
                avg_entry_price=trade.entry_price,
                current_ltp=trade.entry_price,
                unrealized_pnl=0.0,
                updated_at=datetime.now()
            )
        
        self.db.save_position(pos)
