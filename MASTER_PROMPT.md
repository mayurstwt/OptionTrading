# MASTER PROMPT: Autonomous Paper Trading Engine with Real Data & Supabase

## PROJECT OVERVIEW

You are building a **fully autonomous, rule-based paper trading engine** for Indian stock market indices (NIFTY/BANKNIFTY) that:
- Requires **ZERO manual intervention** during trading hours.
- Operates in **paper mode** (simulated trades, no real money).
- Uses **Yahoo Finance API** for reliable, real-time index data.
- Uses **Supabase** for database persistence and automated scheduling (via Cron).
- Makes decisions based on **pre-defined rules** in YAML.
- Provides **complete transparency** through cloud logging and daily P&L reports.

## CORE REQUIREMENTS

### 1. Market Data (Yahoo Finance)
- **Library**: `yfinance`
- **Symbols**: `^NSEI` (NIFTY 50), `^NSEBANK` (BANKNIFTY)
- **Frequency**: Data fetched every 30-60 seconds during market hours.
- **Persistence**: Every quote is saved as a `MarketSnapshot` in Supabase.

### 2. Paper Trading Simulation
- **Execution**: Simulates BUY/SELL at current Last Traded Price (LTP).
- **Multipliers**: Uses standard lot sizes (NIFTY: 25, BANKNIFTY: 15) for P&L calculation.
- **P&L Logic**: 
  - Realized P&L = `(exit_price - entry_price) * quantity * lot_size` (reversed for SELL).
- **Virtual Portfolio**: Tracks open positions and unrealized P&L in Supabase.

### 3. Database (Supabase)
- **Tables**:
  - `paper_trades`: Logs all entry/exit events.
  - `paper_positions`: Tracks current open positions.
  - `market_data`: Time-series price data snapshots.
  - `daily_summary`: EOD performance metrics.
- **Auth**: Uses `SUPABASE_URL` and `SUPABASE_KEY` from `.env`.

### 4. Automation & Daily Lifecycle
- **Trigger**: FastAPI endpoints (`/trigger-cycle`, `/calculate-eod-pnl`) hit by external Cron (Supabase Cron).
- **Hours**: 9:15 AM - 3:30 PM IST (Mon-Fri).
- **Intraday**: Every minute: Fetch Data -> Eval Rules -> Execute Signal -> Save State.
- **EOD**: Calculate realized/unrealized P&L and save summary.

### 5. Tech Stack
- **Language**: Python 3.9+
- **Framework**: FastAPI (for automation triggers)
- **Data**: `yfinance`
- **Database**: `supabase-py`
- **Logic**: `pandas`, `PyYAML`
- **Timezone**: IST (Asia/Kolkata)

## SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│                    AUTONOMOUS TRADING ENGINE                │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  [Supabase Cron] → [FastAPI] → [Trading Engine] → [Supabase] │
│         ↓               ↓             ↓               ↓       │
│  (Trigger Job)    (HTTP Endpoint) (Core Logic)   (Data Store) │
│                                                               │
│       [Yahoo Finance] → [Rules Engine] → [Paper Trader]       │
│            (Data)          (Signals)        (Execution)       │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## DETAILED MODULES

### MODULE 1: Market Data Provider
- Fetches `lastPrice` from Yahoo Finance using `yfinance`.
- Normalizes data into `MarketSnapshot` objects.
- Handles symbol mapping between internal names and Yahoo tickers.

### MODULE 2: Paper Trader
- Manages virtual orders and positions.
- Calculates realized P&L with proper lot-size multipliers.
- Updates Supabase `paper_trades` and `paper_positions` tables atomically.

### MODULE 3: Rules Engine
- Parses YAML configuration for entry and exit rules.
- Evaluates conditions (e.g., price between range, time window).
- Generates Buy/Sell signals.

### MODULE 4: Supabase Database
- Implements `SupabaseDatabase` client.
- Handles all CRUD operations for trades, positions, and market data.
- Uses `upsert` for idempotent state management.

### MODULE 5: Risk Manager
- Enforces hard limits: `max_position_size`, `max_concurrent_lots`.
- Checks `daily_loss_limit` against realized P&L fetched from Supabase.

## IMPLEMENTATION PHASES

1. **Setup**: Supabase project creation and `.env` configuration.
2. **Data Pipeline**: Implement `YahooFinanceProvider` and snapshot persistence.
3. **Paper Trading**: Implement P&L logic and position tracking in Supabase.
4. **Automation**: Implement FastAPI endpoints and background task processing.
5. **Testing**: Manual triggers of `/trigger-cycle` to verify the full flow.
6. **Deployment**: Host FastAPI on cloud and configure Supabase Cron.

## SUCCESS CRITERIA
- ✅ Zero manual intervention required for daily operation.
- ✅ Accurate P&L tracking stored in the cloud.
- ✅ Reliable data fetching via Yahoo Finance.
- ✅ Automated EOD reporting.
