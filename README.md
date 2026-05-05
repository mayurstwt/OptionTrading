# Autonomous Paper Trading Engine for Indian Markets

## Overview

This is a **fully autonomous, rule-based paper trading engine** for NIFTY and BANKNIFTY indices in the Indian stock market. It operates using **real market data** from Yahoo Finance, simulates trades locally (paper trading), and uses **Supabase** for persistence and automation.

**Key Features:**
- ✅ **Real-time Data**: Uses Yahoo Finance API (`yfinance`) for reliable market quotes.
- ✅ **Paper Trading**: Safely test strategies with simulated orders (no real broker required).
- ✅ **Supabase Integration**: Stores all trades, positions, market snapshots, and daily summaries in the cloud.
- ✅ **Automated Cycles**: Designed for trigger-based execution via Supabase Cron or HTTP hooks.
- ✅ **Rule-based Logic**: Fully configurable entry/exit conditions via YAML.
- ✅ **Daily P&L Tracking**: Automatically calculates realized and unrealized P&L.

## Quick Start

### Prerequisites
- Python 3.9+
- Supabase account and project
- Environment variables configured in `.env`

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/trading-engine.git
cd trading-engine

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with Supabase credentials
cp .env.example .env
# Edit .env and add your SUPABASE_URL and SUPABASE_KEY
nano .env

# Run the engine (locally for testing)
python main.py
```

### Configuration

Edit `config/config_v1.yaml` to customize:
- Trading symbols (`NIFTY`, `BANKNIFTY`)
- Risk limits (position size, daily loss limit)
- Entry/Exit rules

Example:
```yaml
trading_config:
  paper_capital: 1000000
  symbols: ["NIFTY", "BANKNIFTY"]
  default_symbol: "NIFTY"
  risk_limits:
    max_position_size_lots: 3
    daily_loss_limit_pct: -1.5
```

## Architecture

The system follows a **Research -> Strategy -> Execution** pattern optimized for serverless/cron-based environments.

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

## Core Modules

1. **Market Data** (`src/market_data/market_provider.py`)
   - `YahooFinanceProvider`: Fetches reliable real-time quotes using `yfinance`.
   - Maps standard names (NIFTY) to Yahoo symbols (`^NSEI`).

2. **Rules Engine** (`src/rules/rules_engine.py`)
   - Evaluates YAML-defined rules against current market state.
   - Triggers signals for entries and exits.

3. **Paper Trader** (`src/trading/paper_trader.py`)
   - Simulates BUY/SELL orders at current LTP.
   - Handles lot size multipliers (NIFTY: 25, BANKNIFTY: 15).
   - Manages virtual portfolio and P&L.

4. **Database** (`src/db/supabase_db.py`)
   - Cloud-native persistence using Supabase.
   - Stores `paper_trades`, `paper_positions`, `market_data`, and `daily_summary`.

5. **Risk Manager** (`src/risk/risk_manager.py`)
   - Enforces max position sizes and daily loss limits.
   - Queries Supabase for real-time risk assessment.

## API & Automation

The engine includes a FastAPI wrapper (`api.py`) for cloud deployment:

- `POST /trigger-cycle`: Executes one full trading iteration (Fetch data -> Eval rules -> Trade).
- `POST /calculate-eod-pnl`: Generates and saves the daily P&L summary.

**Supabase Automation Setup:**
1. Deploy the API to a public URL (e.g., Render/Railway).
2. Use Supabase `pg_cron` or Edge Functions to hit `/trigger-cycle` every minute during market hours (9:15 AM - 3:30 PM IST).
3. Schedule `/calculate-eod-pnl` at 4:00 PM IST.

## License

MIT License
