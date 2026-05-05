import sqlite3
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from src.db.models import Trade, Position, DailySummary

logger = logging.getLogger(__name__)

class Database:
    """
    Handles all SQLite database operations.
    """

    def __init__(self, db_path: str = "data/trading.db"):
        self.db_path = db_path
        self._ensure_data_dir()
        self.init_db()

    def _ensure_data_dir(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Initialize the database schema."""
        schema = """
        CREATE TABLE IF NOT EXISTS paper_trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trade_id TEXT UNIQUE NOT NULL,
            strategy TEXT,
            instrument_key TEXT NOT NULL,
            side TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            entry_time TIMESTAMP NOT NULL,
            entry_price REAL NOT NULL,
            status TEXT DEFAULT 'OPEN',
            entry_rule TEXT,
            exit_time TIMESTAMP,
            exit_price REAL,
            exit_rule TEXT,
            realized_pnl REAL DEFAULT 0.0,
            trade_duration_minutes INTEGER,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS paper_positions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            instrument_key TEXT UNIQUE NOT NULL,
            net_quantity INTEGER NOT NULL,
            avg_entry_price REAL NOT NULL,
            current_ltp REAL DEFAULT 0.0,
            unrealized_pnl REAL DEFAULT 0.0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS daily_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE UNIQUE NOT NULL,
            total_trades INTEGER,
            winning_trades INTEGER,
            losing_trades INTEGER,
            realized_pnl REAL,
            max_drawdown_pct REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        with self._get_connection() as conn:
            conn.executescript(schema)
        logger.info("Database initialized successfully")

    def save_trade(self, trade: Trade):
        """Save a new trade or update an existing one."""
        query = """
        INSERT OR REPLACE INTO paper_trades (
            trade_id, strategy, instrument_key, side, quantity, 
            entry_time, entry_price, status, entry_rule, 
            exit_time, exit_price, exit_rule, realized_pnl, 
            trade_duration_minutes, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            trade.trade_id, trade.strategy, trade.instrument_key, trade.side, trade.quantity,
            trade.entry_time.isoformat(), trade.entry_price, trade.status, trade.entry_rule,
            trade.exit_time.isoformat() if trade.exit_time else None,
            trade.exit_price, trade.exit_rule, trade.realized_pnl,
            trade.trade_duration_minutes, trade.notes
        )
        with self._get_connection() as conn:
            conn.execute(query, params)

    def get_open_trades(self) -> List[Trade]:
        """Fetch all open trades."""
        query = "SELECT * FROM paper_trades WHERE status = 'OPEN'"
        with self._get_connection() as conn:
            rows = conn.execute(query).fetchall()
            return [self._row_to_trade(row) for row in rows]

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
        query = """
        INSERT OR REPLACE INTO paper_positions (
            instrument_key, net_quantity, avg_entry_price, 
            current_ltp, unrealized_pnl, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?)
        """
        params = (
            position.instrument_key, position.net_quantity, position.avg_entry_price,
            position.current_ltp, position.unrealized_pnl, position.updated_at.isoformat()
        )
        with self._get_connection() as conn:
            conn.execute(query, params)

    def get_positions(self) -> List[Position]:
        """Fetch all current positions."""
        query = "SELECT * FROM paper_positions"
        with self._get_connection() as conn:
            rows = conn.execute(query).fetchall()
            return [Position(
                instrument_key=row['instrument_key'],
                net_quantity=row['net_quantity'],
                avg_entry_price=row['avg_entry_price'],
                current_ltp=row['current_ltp'],
                unrealized_pnl=row['unrealized_pnl'],
                updated_at=datetime.fromisoformat(row['updated_at'])
            ) for row in rows]

    def delete_position(self, instrument_key: str):
        """Remove a position when it's closed."""
        query = "DELETE FROM paper_positions WHERE instrument_key = ?"
        with self._get_connection() as conn:
            conn.execute(query, (instrument_key,))

    def save_daily_summary(self, summary: DailySummary):
        """Save EOD summary."""
        query = """
        INSERT OR REPLACE INTO daily_summary (
            date, total_trades, winning_trades, losing_trades, 
            realized_pnl, max_drawdown_pct
        ) VALUES (?, ?, ?, ?, ?, ?)
        """
        params = (
            summary.date, summary.total_trades, summary.winning_trades, 
            summary.losing_trades, summary.realized_pnl, summary.max_drawdown_pct
        )
        with self._get_connection() as conn:
            conn.execute(query, params)
