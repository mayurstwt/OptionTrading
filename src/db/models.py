from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict

@dataclass
class Trade:
    trade_id: str
    strategy: str
    instrument_key: str
    side: str  # BUY or SELL
    quantity: int
    entry_time: datetime
    entry_price: float
    status: str = "OPEN"  # OPEN, CLOSED
    entry_rule: Optional[str] = None
    exit_time: Optional[datetime] = None
    exit_price: Optional[float] = None
    exit_rule: Optional[str] = None
    realized_pnl: float = 0.0
    trade_duration_minutes: Optional[int] = None
    notes: Optional[str] = None

@dataclass
class Position:
    instrument_key: str
    net_quantity: int
    avg_entry_price: float
    current_ltp: float = 0.0
    unrealized_pnl: float = 0.0
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class DailySummary:
    date: str
    total_trades: int
    winning_trades: int
    losing_trades: int
    realized_pnl: float
    max_drawdown_pct: float
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class MarketSnapshot:
    instrument_key: str
    ltp: Optional[float] = None
    bid: Optional[float] = None
    ask: Optional[float] = None
    volume: Optional[int] = None
    oi: Optional[int] = None
    iv: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class Wallet:
    balance: float
    used_margin: float = 0.0
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class WalletTransaction:
    type: str  # DEPOSIT, WITHDRAWAL, MARGIN_BLOCKED, MARGIN_RELEASED, PNL_SETTLEMENT
    amount: float
    description: str
    timestamp: datetime = field(default_factory=datetime.now)
    reference_id: Optional[str] = None
    wallet_id: Optional[int] = None
    id: Optional[int] = None
