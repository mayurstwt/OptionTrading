import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from src.db.supabase_db import SupabaseDatabase
from src.db.models import Position
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class RiskVerdict:
    status: str  # APPROVED, BLOCKED, REDUCED_SIZE
    reason: Optional[str] = None
    suggested_quantity: Optional[int] = None

class RiskManager:
    """
    Enforces risk constraints on trading operations.
    Updated to use SupabaseDatabase.
    """

    def __init__(self, config: Dict[str, Any], db: SupabaseDatabase):
        self.config = config.get("trading_config", {})
        self.risk_limits = self.config.get("risk_limits", {})
        self.db = db

    def check_risk(self, instrument_key: str, side: str, quantity: int) -> RiskVerdict:
        """
        Check if a proposed trade is within risk limits.
        """
        # 1. Position Size Limit
        max_pos_size = self.risk_limits.get("max_position_size_lots", 3)
        if quantity > max_pos_size:
            return RiskVerdict(status="REDUCED_SIZE", reason=f"Quantity {quantity} exceeds max pos size {max_pos_size}", 
                               suggested_quantity=max_pos_size)

        # 2. Max Concurrent Lots
        current_positions = self.db.get_positions()
        current_total_lots = sum(abs(p.net_quantity) for p in current_positions)
        max_concurrent_lots = self.risk_limits.get("max_concurrent_lots", 6)
        
        if current_total_lots + quantity > max_concurrent_lots:
            remaining_lots = max_concurrent_lots - current_total_lots
            if remaining_lots <= 0:
                return RiskVerdict(status="BLOCKED", reason="Max concurrent lots reached")
            return RiskVerdict(status="REDUCED_SIZE", reason=f"Total lots would exceed {max_concurrent_lots}", 
                               suggested_quantity=remaining_lots)

        # 3. Daily Loss Limit
        if not self._check_daily_loss_limit():
            return RiskVerdict(status="BLOCKED", reason="Daily loss limit exceeded")

        return RiskVerdict(status="APPROVED")

    def _check_daily_loss_limit(self) -> bool:
        """
        Calculate daily P&L and compare with limit using Supabase.
        """
        daily_loss_limit_pct = self.risk_limits.get("daily_loss_limit_pct", -1.5)
        capital = self.config.get("paper_capital", 1000000)
        limit_amount = (daily_loss_limit_pct / 100) * capital

        today_str = datetime.now().strftime("%Y-%m-%d")
        trades = self.db.get_trades_by_date(today_str)
        daily_pnl = sum(t.realized_pnl for t in trades if t.realized_pnl is not None)

        if daily_pnl < limit_amount:
            logger.warning(f"Daily loss limit reached: {daily_pnl} < {limit_amount}")
            return False
        
        return True
