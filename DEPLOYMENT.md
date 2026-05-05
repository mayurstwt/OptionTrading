# Deployment & Automation Guide

This guide explains how to deploy the Autonomous Trading Engine to the cloud and automate it using **Render** and **Supabase**.

## 1. Prerequisites

- A [GitHub](https://github.com/) repository containing your code.
- A [Supabase](https://supabase.com/) project (with tables initialized via `docs/supabase_schema.sql`).
- A [Render](https://render.com/) account.

---

## 2. Deploying to Render (Web Service)

Render will host the FastAPI application (`api.py`) which acts as the gateway to your trading engine.

1. **Create a New Web Service**:
   - Log in to Render and click **New +** > **Web Service**.
   - Connect your GitHub repository.

2. **Configure the Service**:
   - **Name**: `trading-engine-api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn api:app --host 0.0.0.0 --port $PORT`

3. **Add Environment Variables**:
   Click the **Environment** tab and add the following keys from your `.env` file:
   - `SUPABASE_URL`: Your Supabase Project URL.
   - `SUPABASE_KEY`: Your Supabase Anon Key.
   - `LOG_LEVEL`: `INFO`
   - `TZ`: `Asia/Kolkata`
   - `TRADING_SYMBOLS`: `NIFTY,BANKNIFTY`
   - `DEFAULT_SYMBOL`: `NIFTY`

4. **Deploy**: Click **Create Web Service**. Once deployed, Render will provide you with a public URL (e.g., `https://trading-engine-api.onrender.com`).

---

## 3. Automating with Supabase Cron

Since the engine is designed to be "triggered," we will use Supabase's built-in `pg_cron` extension to hit the API endpoints automatically during market hours.

### Step A: Enable the Cron Extension
1. Go to your **Supabase Dashboard** > **SQL Editor**.
2. Run the following command:
   ```sql
   create extension if not exists pg_cron;
   ```

### Step B: Schedule Trading Cycles
Run this SQL to trigger the trading engine every minute from **Monday to Friday**, between **9:15 AM and 3:30 PM IST**.

*Note: Supabase Cron uses UTC. IST is UTC+5:30. So 9:15 AM - 3:30 PM IST is approximately **03:45 AM - 10:00 AM UTC**.*

```sql
-- Trigger trading cycle every minute
SELECT cron.schedule(
  'run-trading-cycle',
  '* 4-9 * * 1-5', -- Every minute between 4 AM and 9 AM UTC (approx market hours)
  $$
  select
    net.http_post(
      url:='https://your-render-url.onrender.com/trigger-cycle',
      headers:='{"Content-Type": "application/json"}'::jsonb
    );
  $$
);
```

### Step C: Schedule End-of-Day P&L
Run this SQL to calculate the final P&L every day at **4:00 PM IST (10:30 AM UTC)**.

```sql
-- Calculate P&L at 4:00 PM IST
SELECT cron.schedule(
  'calculate-eod-pnl',
  '30 10 * * 1-5', -- 10:30 AM UTC
  $$
  select
    net.http_post(
      url:='https://your-render-url.onrender.com/calculate-eod-pnl',
      headers:='{"Content-Type": "application/json"}'::jsonb
    );
  $$
);
```

---

## 4. Monitoring Your Trading Day

Once automated, you can monitor the engine's health from your phone or laptop using the following tools:

### A. The "Heartbeat" Check (Supabase `market_data`)
The easiest way to see if the engine is "alive" is to check the `market_data` table in Supabase:
1. Go to **Supabase** > **Table Editor** > `market_data`.
2. Sort by `timestamp` (Descending).
3. If you see a new row every minute with the current LTP of NIFTY/BANKNIFTY, the engine is successfully fetching and storing data.

### B. The "Action" Check (Supabase `paper_trades`)
To see if any trades have been placed:
1. Check the `paper_trades` table.
2. Rows with `status = 'OPEN'` represent active trades.
3. Rows with `status = 'CLOSED'` represent completed trades with calculated `realized_pnl`.

### C. The "Logic" Check (Render Logs)
If you want to know *why* a trade was or wasn't placed:
1. Go to your **Render Dashboard** > `trading-engine-api` > **Logs**.
2. Look for lines like:
   - `INFO - Updated and persisted LTP for NIFTY: 22450.5`
   - `INFO - PAPER ORDER PLACED: SELL 1 lots of NIFTY @ 22450.5`
   - `WARNING - Daily loss limit reached...`

### D. The "Trigger" Check (Supabase Cron Logs)
If no rows are appearing in `market_data`, check if Supabase is actually hitting your API:
1. In Supabase **SQL Editor**, run:
   ```sql
   select * from cron.job_run_details order by start_time desc limit 10;
   ```
2. Look for `status = 'succeeded'`. If you see `failed`, it means Render is unreachable or your URL is incorrect.

---

## 5. End-of-Day Verification

At **4:00 PM IST**, the system should automatically generate a summary.
1. Check the `daily_summary` table in Supabase.
2. You should see a new row for the day with:
   - `total_trades`
   - `realized_pnl` (your profit/loss for the day)
   - `winning_trades` vs `losing_trades`

---

## 6. Pro-Tip: Building a Real-time Dashboard

Since all your data is in Supabase, you can easily visualize your P&L curve:
- **Google Looker Studio**: Connect Supabase (Postgres) as a data source for free charts.
- **Streamlit**: Build a 10-line Python script to display your `daily_summary` and `paper_trades`.
- **Supabase Dashboards**: Use the "Reports" section in Supabase to create custom SQL charts.

---

## 7. Maintenance Tips

1. **Render Sleeping**: If using Render's Free Tier, the service will "sleep" after 15 minutes of inactivity. The first Cron job of the day might take an extra 30 seconds to wake it up. This is usually fine for trading.
2. **Updating Rules**: To change your trading strategy, edit `config/config_v1.yaml`, commit, and push to GitHub. Render will automatically re-deploy the new rules.
3. **Health Check**: Periodically check the **Supabase Cron logs** (in the `cron` schema) to ensure the HTTP requests are succeeding.

---

**Congratulations!** Your trading engine is now fully autonomous and running in the cloud. 🚀
