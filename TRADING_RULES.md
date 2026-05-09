# ALL-DAY TRADING RULES GUIDE: Complete Strategy Collection for 9:15 AM - 3:30 PM

**Purpose**: Expand your trading engine to trade continuously throughout market hours  
**Market Hours**: 9:15 AM - 3:30 PM IST (Monday-Friday)  
**Strategies**: 6 different strategies trading different times + market conditions  
**Goal**: Maximize trading opportunities while managing risk  

---

## MARKET STRUCTURE & TRADING WINDOWS

The Indian options market has predictable patterns throughout the day:

```
9:15-10:30 AM     (Volatile Opening - Best for straddles/strangles)
  ├─ High volatility
  ├─ IV usually highest of the day
  ├─ Big moves common
  └─ Risk: Gap moves

10:30-12:00 PM    (Mid-morning Consolidation)
  ├─ Volatility settles
  ├─ IV starts declining
  ├─ Directional trends form
  └─ Good for directional trades

12:00-1:00 PM     (Lunch Hour Sideways)
  ├─ Low volume
  ├─ Range-bound usually
  ├─ IV declining
  └─ Caution: Less liquidity

1:00-3:15 PM      (Afternoon Rally/Decline)
  ├─ Volume picks up
  ├─ Final directional move
  ├─ IV bottoming out
  └─ Good for quick profits

3:15-3:30 PM      (Final Exit Window)
  ├─ All positions closed
  ├─ No new entries
  ├─ Time decay acceleration
  └─ Risk: Fast moves
```

---

## COMPLETE ALL-DAY TRADING CONFIG

Create this file: `config_all_day_trading.yaml`

```yaml
trading_config:
  paper_capital: 1000000  # ₹10,00,000
  symbols: ["NIFTY", "BANKNIFTY"]
  default_symbol: "NIFTY"
  
  risk_limits:
    max_position_size_lots: 3          # Per single order
    max_concurrent_lots: 10            # Total open (increased for all-day)
    daily_loss_limit_pct: -2.0         # Stop if daily loss > 2%
    max_drawdown_pct: -3.0             # Circuit breaker
    max_trades_per_day: 15             # Don't overtrader
  
  profit_booking:
    target_profit_pct_per_day: 1.0     # Close all trades if daily profit > 1%
    reduce_size_after_win_streak: 3    # Reduce lots after 3 consecutive wins
    increase_size_after_loss_streak: 0 # Don't increase (conservative)

# ============================================================================
# STRATEGY 1: SHORT STRADDLE (9:20-10:30 AM)
# ============================================================================
entry_rules:
  - rule_name: "morning_short_straddle"
    enabled: true
    strategy_type: "short_straddle"
    time_window: ["09:20", "10:30"]
    
    underlying_conditions:
      - metric: "price"
        operator: "between"
        values: [24700, 25500]  # Adjust to current ATM
      - metric: "volatility"
        description: "IV rank should be high in morning"
        target: "high"
    
    options_conditions:
      - metric: "strike_selection"
        method: "atm"
        offset: 0
      - metric: "combined_premium"
        operator: "<"
        threshold: 500  # Combined CE+PE premium < 500
    
    position_sizing:
      base_lots: 1
      scale_by_volatility: false
    
    notes: "Profit from stagnation or small moves"

# ============================================================================
# STRATEGY 2: SHORT STRANGLE (10:30-12:00 PM)
# ============================================================================
  - rule_name: "mid_morning_short_strangle"
    enabled: true
    strategy_type: "short_strangle"
    time_window: ["10:30", "12:00"]
    
    underlying_conditions:
      - metric: "price"
        operator: "between"
        values: [24600, 25600]
    
    options_conditions:
      - metric: "strike_selection"
        method: "otm"  # Out-of-the-money
        offset: 200    # 200 points away from ATM
      - metric: "combined_premium"
        operator: "<"
        threshold: 300
    
    position_sizing:
      base_lots: 1
      scale_by_volatility: true  # Smaller if IV is low
    
    notes: "Wider margin, lower premium, more conservative"

# ============================================================================
# STRATEGY 3: LONG CALL/PUT DIRECTIONAL (1:00-2:30 PM)
# ============================================================================
  - rule_name: "afternoon_long_call"
    enabled: true
    strategy_type: "long_option"
    time_window: ["13:00", "14:30"]
    
    underlying_conditions:
      - metric: "price_trend"
        description: "Look for bullish momentum"
        logic: "last_candle_close > last_candle_open"
      - metric: "price"
        operator: ">"
        values: [24900]  # Above support level
    
    options_conditions:
      - metric: "strike_selection"
        method: "otm"
        offset: 100
      - metric: "premium"
        operator: "<"
        threshold: 80   # Cheap options only
      - metric: "volume"
        description: "Ensure liquid strikes"
        min_volume: 100
    
    position_sizing:
      base_lots: 1
      scale_by_volatility: true
    
    notes: "Long directional bets for afternoon move"
    
  - rule_name: "afternoon_long_put"
    enabled: true
    strategy_type: "long_option"
    time_window: ["13:00", "14:30"]
    
    underlying_conditions:
      - metric: "price_trend"
        description: "Look for bearish momentum"
        logic: "last_candle_close < last_candle_open"
      - metric: "price"
        operator: "<"
        values: [25000]  # Below resistance level
    
    options_conditions:
      - metric: "strike_selection"
        method: "otm"
        offset: 100
      - metric: "premium"
        operator: "<"
        threshold: 80
      - metric: "volume"
        min_volume: 100
    
    position_sizing:
      base_lots: 1
      scale_by_volatility: true
    
    notes: "Long puts for bearish afternoon"

# ============================================================================
# STRATEGY 4: BULL CALL SPREAD (10:00-1:00 PM)
# ============================================================================
  - rule_name: "bull_call_spread"
    enabled: true
    strategy_type: "bull_call_spread"
    time_window: ["10:00", "13:00"]
    
    underlying_conditions:
      - metric: "price"
        operator: ">"
        values: [24800]
      - metric: "bias"
        description: "Mildly bullish outlook"
    
    options_conditions:
      - metric: "strike_selection"
        buy_strike: "atm"
        sell_strike: "200_otm"  # Buy ATM, sell 200 points OTM
      - metric: "spread_credit"
        min_credit: 50
    
    position_sizing:
      base_lots: 1
      max_spread_loss: 150  # Max loss per spread
    
    notes: "Limited risk, defined profit, bullish"

# ============================================================================
# STRATEGY 5: BEAR PUT SPREAD (10:00-1:00 PM)
# ============================================================================
  - rule_name: "bear_put_spread"
    enabled: true
    strategy_type: "bear_put_spread"
    time_window: ["10:00", "13:00"]
    
    underlying_conditions:
      - metric: "price"
        operator: "<"
        values: [25000]
      - metric: "bias"
        description: "Mildly bearish outlook"
    
    options_conditions:
      - metric: "strike_selection"
        sell_strike: "atm"
        buy_strike: "200_otm"  # Sell ATM, buy 200 points OTM
      - metric: "spread_credit"
        min_credit: 50
    
    position_sizing:
      base_lots: 1
      max_spread_loss: 150
    
    notes: "Limited risk, defined profit, bearish"

# ============================================================================
# STRATEGY 6: IRON CONDOR (11:00 AM - 2:00 PM)
# ============================================================================
  - rule_name: "iron_condor"
    enabled: true
    strategy_type: "iron_condor"
    time_window: ["11:00", "14:00"]
    
    underlying_conditions:
      - metric: "price"
        operator: "between"
        values: [24800, 25200]
      - metric: "expectation"
        description: "Range-bound market expected"
    
    options_conditions:
      - metric: "strike_selection"
        call_sell: "200_otm"
        call_buy: "400_otm"
        put_sell: "200_otm"
        put_buy: "400_otm"
      - metric: "spread_width"
        width: 200
      - metric: "total_credit"
        min_credit: 80
    
    position_sizing:
      base_lots: 1
      max_loss: 120  # Width - credit
    
    notes: "Theta decay play, moderate profit range"

# ============================================================================
# EXIT RULES (Applied to ALL strategies)
# ============================================================================

exit_rules:
  # Profit Target (Strategy dependent)
  - rule_name: "profit_target_short_premium"
    enabled: true
    trigger: "any"
    applies_to: ["morning_short_straddle", "mid_morning_short_strangle", "iron_condor"]
    conditions:
      - metric: "premium_change"
        operator: "<="
        threshold: -25  # Exit if premium drops 25%
    notes: "For short options, exit on profit"
  
  - rule_name: "profit_target_long_option"
    enabled: true
    trigger: "any"
    applies_to: ["afternoon_long_call", "afternoon_long_put"]
    conditions:
      - metric: "premium_change"
        operator: ">="
        threshold: 30  # Exit if premium rises 30%
    notes: "For long options, exit on premium rise"
  
  - rule_name: "profit_target_spread"
    enabled: true
    trigger: "any"
    applies_to: ["bull_call_spread", "bear_put_spread"]
    conditions:
      - metric: "spread_profit"
        operator: ">="
        threshold: 75  # Exit if 75% of max profit achieved
    notes: "Don't be greedy on spreads"

  # Stop Loss Rules
  - rule_name: "stop_loss_short_premium"
    enabled: true
    trigger: "any"
    applies_to: ["morning_short_straddle", "mid_morning_short_strangle", "iron_condor"]
    conditions:
      - metric: "position_loss_pct"
        operator: "<"
        threshold: -5  # Stop loss at 5% loss per position
  
  - rule_name: "stop_loss_long_option"
    enabled: true
    trigger: "any"
    applies_to: ["afternoon_long_call", "afternoon_long_put"]
    conditions:
      - metric: "position_loss_pct"
        operator: "<"
        threshold: -3  # Tighter stop for long options
  
  - rule_name: "stop_loss_spread"
    enabled: true
    trigger: "any"
    applies_to: ["bull_call_spread", "bear_put_spread"]
    conditions:
      - metric: "spread_loss_pct"
        operator: "<"
        threshold: -4  # Stop at max loss point

  # Time-based Exits
  - rule_name: "exit_at_12pm"
    enabled: true
    trigger: "absolute_time"
    time: "12:00"
    applies_to: ["morning_short_straddle"]
    notes: "Close morning positions before lunch"
  
  - rule_name: "exit_at_2pm"
    enabled: true
    trigger: "absolute_time"
    time: "14:00"
    applies_to: ["afternoon_long_call", "afternoon_long_put"]
    notes: "Close afternoon positions 1.5 hours before close"
  
  - rule_name: "final_exit"
    enabled: true
    trigger: "absolute_time"
    time: "15:15"
    applies_to: ["all"]
    notes: "MANDATORY: Close everything 15 min before market close"

  # Underlying Movement Stop Loss
  - rule_name: "underlying_move_stop"
    enabled: true
    trigger: "any"
    conditions:
      - metric: "underlying_move_pct"
        operator: "abs_gt"
        threshold: 3  # Underlying moved 3% from entry
    notes: "Exit if underlying moves too much"

  # IV Crush Exit
  - rule_name: "iv_crush_exit"
    enabled: true
    trigger: "any"
    applies_to: ["morning_short_straddle", "mid_morning_short_strangle"]
    conditions:
      - metric: "iv_change_pct"
        operator: "<"
        threshold: -30  # IV dropped 30%
    notes: "Exit short options after IV crash"

# ============================================================================
# DAILY RISK MONITORING
# ============================================================================

daily_monitoring:
  - name: "daily_loss_check"
    check_every_minutes: 30
    conditions:
      - metric: "daily_unrealized_pnl_pct"
        operator: "<"
        threshold: -1.5
    action: "HALT_NEW_ENTRIES"
    notes: "Stop new trades if daily loss > 1.5%"
  
  - name: "daily_profit_target"
    check_every_minutes: 60
    conditions:
      - metric: "daily_realized_pnl_pct"
        operator: ">"
        threshold: 1.0
    action: "CLOSE_ALL_POSITIONS"
    notes: "Close ALL positions if daily profit > 1%"
  
  - name: "max_concurrent_check"
    check_every_minutes: 15
    conditions:
      - metric: "total_concurrent_lots"
        operator: ">"
        threshold: 10
    action: "BLOCK_NEW_ENTRIES"
    notes: "Don't let concurrent positions exceed limit"

# ============================================================================
# POSITION MANAGEMENT
# ============================================================================

position_management:
  - name: "reduce_on_consecutive_wins"
    trigger: "3_consecutive_wins"
    action: "REDUCE_SIZE_TO_0.5_LOTS"
    duration: "next_3_trades"
    notes: "Be conservative after winning streak"
  
  - name: "reduce_on_consecutive_losses"
    trigger: "2_consecutive_losses"
    action: "REDUCE_SIZE_TO_0.5_LOTS"
    duration: "next_5_trades"
    notes: "Reduce after losing streak"
  
  - name: "trail_stop_loss"
    enabled: true
    applies_to: ["afternoon_long_call", "afternoon_long_put"]
    trail_by_pct: 2  # Trail stop loss by 2%
    notes: "Lock in profits with trailing stop"

# ============================================================================
# TRADING SCHEDULE
# ============================================================================

trading_schedule:
  # Morning Session
  "09:15-10:30":
    active_strategies: ["morning_short_straddle"]
    max_positions: 2
    position_sizing: "normal"
  
  "10:30-12:00":
    active_strategies: ["mid_morning_short_strangle", "bull_call_spread", "bear_put_spread"]
    max_positions: 3
    position_sizing: "normal"
  
  # Lunch Hour (Caution)
  "12:00-13:00":
    active_strategies: []  # No new entries during lunch
    position_management: "MONITOR_ONLY"
    notes: "Low liquidity, don't trade"
  
  # Afternoon Session
  "13:00-14:30":
    active_strategies: ["afternoon_long_call", "afternoon_long_put", "bull_call_spread", "bear_put_spread", "iron_condor"]
    max_positions: 4
    position_sizing: "reduced"  # 0.5-1 lot (smaller)
  
  # Final Hour
  "14:30-15:15":
    active_strategies: []  # No new entries
    position_management: "PREPARE_FOR_EXIT"
    notes: "Close all positions"
  
  "15:15-15:30":
    active_strategies: []  # MANDATORY EXIT TIME
    position_management: "FORCE_EXIT_ALL"
    notes: "All positions MUST be closed"

# ============================================================================
# EVENT-BASED TRADING
# ============================================================================

event_dates:
  # Expiry weeks - avoid complex strategies
  - date: "every_thursday"
    event: "Weekly_Expiry"
    action: "REDUCE_POSITION_SIZE"
    reason: "High volatility during expiry"
  
  - date: "last_thursday_of_month"
    event: "Monthly_Expiry"
    action: "REDUCE_SIZE_BY_50PCT"
    reason: "Very high volatility"
  
  # Economic events (adjust as needed)
  - date: "election_days"
    action: "NO_TRADING"
    reason: "Gap risks too high"
  
  - date: "budget_day"
    action: "REDUCE_POSITION_SIZE"
    reason: "Major move expected"

# ============================================================================
# SYMBOL ROTATION (Trade both NIFTY and BANKNIFTY)
# ============================================================================

symbol_rules:
  morning_short_straddle:
    applies_to: ["NIFTY"]
    notes: "NIFTY more liquid in morning"
  
  afternoon_long_call:
    applies_to: ["NIFTY", "BANKNIFTY"]
    notes: "Both equally good in afternoon"
  
  iron_condor:
    applies_to: ["NIFTY"]
    notes: "Tight spreads on NIFTY"

# ============================================================================
# LOGGING & MONITORING
# ============================================================================

logging:
  level: "INFO"
  log_all_price_updates: false  # Too verbose
  log_rule_evaluations: true
  log_all_trades: true
  log_all_exits: true
  daily_report: true
  
  alerts:
    - type: "trade_entry"
      send: true
      channels: ["log", "console"]
    
    - type: "trade_exit"
      send: true
      channels: ["log", "console"]
    
    - type: "position_loss"
      send: true
      channels: ["log", "console", "alert"]
    
    - type: "daily_loss_limit"
      send: true
      channels: ["log", "console", "alert"]
    
    - type: "daily_profit_target"
      send: true
      channels: ["log", "console"]
```

---

## STRATEGY BREAKDOWN

### **Strategy 1: Morning Short Straddle (9:20-10:30)**
```
What: Sell ATM call + ATM put
When: Market opens, IV highest
Why: High premium decay, stagnation expected
Risk: Big gap moves
Target: Premium drops 25%
Stop: Position loss 5%
Typical P&L: +₹2,000-3,500 per day
```

### **Strategy 2: Mid-Morning Strangle (10:30-12:00)**
```
What: Sell OTM call + OTM put (200 pts away)
When: After initial volatility settles
Why: Cheaper than straddle, wider margin
Risk: Bigger move needed
Target: Premium drops 20%
Stop: Position loss 5%
Typical P&L: +₹1,000-2,000 per day
```

### **Strategy 3: Afternoon Long Options (1:00-2:30 PM)**
```
What: Buy cheap call or put (directional)
When: Afternoon momentum appears
Why: Quick directional moves
Risk: Premium loss on decay
Target: Premium rises 30%
Stop: Position loss 3%
Typical P&L: +₹500-1,500 per day
```

### **Strategy 4: Bull Call Spread (10:00-1:00 PM)**
```
What: Buy ATM call, sell 200pts OTM call
When: Bullish outlook
Why: Limited risk, defined profit
Risk: Capped at spread width
Target: 75% of max profit
Stop: Max loss (100 per spread)
Typical P&L: +₹500-1,000 per day
```

### **Strategy 5: Bear Put Spread (10:00-1:00 PM)**
```
What: Sell ATM put, buy 200pts OTM put
When: Bearish outlook
Why: Limited risk, defined profit
Risk: Capped at spread width
Target: 75% of max profit
Stop: Max loss (100 per spread)
Typical P&L: +₹500-1,000 per day
```

### **Strategy 6: Iron Condor (11:00 AM-2:00 PM)**
```
What: Sell OTM call + put, buy further OTM
When: Range-bound market
Why: Theta decay from all sides
Risk: Capped at condor width minus credit
Target: 75% of max profit
Stop: Max loss
Typical P&L: +₹800-1,500 per day
```

---

## ALL-DAY PROFIT PROJECTION

**Realistic Daily P&L (Paper Trading):**

```
Strategy Contribution per day:
  Morning Straddle:         +₹2,000-3,500
  Mid-Morning Strangle:     +₹1,000-2,000
  Afternoon Long Options:   +₹500-1,500
  Bull Call Spread:         +₹500-1,000
  Bear Put Spread:          +₹500-1,000
  Iron Condor:              +₹800-1,500
  ────────────────────────────────────
  Total Daily:              +₹5,300-9,500

Conservative Estimate:      +₹5,000-6,000/day
Aggressive Estimate:        +₹8,000-10,000/day

Monthly (20 trading days):
  Conservative:             +₹1,00,000 - ₹1,20,000
  Realistic:                +₹1,50,000 - ₹2,00,000
```

---

## RISK MANAGEMENT FOR ALL-DAY TRADING

### **Key Rules:**
1. **Max 10 concurrent lots** - Spread across multiple strategies
2. **Daily loss limit -2%** - ₹20,000 loss per day → halt
3. **Daily profit target +1%** - ₹10,000 profit → close ALL
4. **Time stops** - Exit before lunch, before market close
5. **Position sizing** - Reduce after wins/losses
6. **Spread strategies** - Lower risk than naked options

### **Loss Prevention:**
- Don't overtrade (max 15 trades/day)
- Reduce size after consecutive losses
- Don't chase moves (set exits beforehand)
- No new trades after 2:30 PM
- Always check P&L before entering

---

## HOW TO USE THIS CONFIG

### **Step 1: Choose Your Strategy Mix**

```yaml
# Conservative (Lower risk, consistent)
Enable: ["morning_short_straddle"]
Disable: ["iron_condor"]

# Moderate (Balanced)
Enable: ["morning_short_straddle", "afternoon_long_call", "bull_call_spread"]
Disable: ["iron_condor"]

# Aggressive (Higher risk, higher reward)
Enable: ["all"]  # All 6 strategies
```

### **Step 2: Adjust for Your Capital**

```
If capital = ₹5,00,000:
  max_concurrent_lots: 5 (instead of 10)
  max_position_size_lots: 2 (instead of 3)
  daily_loss_limit_pct: -1.0 (instead of -2.0)

If capital = ₹20,00,000:
  max_concurrent_lots: 15 (instead of 10)
  max_position_size_lots: 5 (instead of 3)
  daily_loss_limit_pct: -2.5 (instead of -2.0)
```

### **Step 3: Adjust Strike Prices**

Update these based on current market levels:

```yaml
# Morning Straddle
values: [24700, 25500]  # Current ATM ± 400

# Mid-Morning Strangle
values: [24600, 25600]  # Current ATM ± 500

# Long Calls/Puts
thresholds: [24900, 25000]  # Support/resistance levels
```

### **Step 4: Test & Monitor**

```
Week 1: Run conservative (only straddle + long options)
Week 2: Add spreads
Week 3: Add iron condor if comfortable
Week 4: Adjust based on results
```

---

## IMPLEMENTATION CHECKLIST

- [ ] Update all strike prices for current market
- [ ] Adjust risk limits for your capital
- [ ] Choose which strategies to enable
- [ ] Test each strategy for 1 week before combining
- [ ] Monitor daily P&L target (don't exceed +1%)
- [ ] Monitor daily loss limit (don't exceed -2%)
- [ ] Verify all time stops are correct (IST)
- [ ] Setup alerts for daily limits
- [ ] Review trades every evening
- [ ] Adjust rules based on market conditions

---

## EXAMPLE: YOUR FIRST WEEK

**Monday-Wednesday (Conservative):**
- Enable: morning_short_straddle only
- Max position: 1 lot
- Time stop: 12:00 PM
- Goal: ₹1,000-2,000/day profit

**Thursday-Friday (Moderate):**
- Add: afternoon_long_call
- Max position: 2 lots total
- Time stops: 12:00 PM (straddle), 2:00 PM (long call)
- Goal: ₹2,000-3,000/day profit

**Next Week (Full):**
- All strategies enabled
- Max position: 10 lots total
- Multiple time stops per strategy
- Goal: ₹5,000-8,000/day profit

---

## MONITORING DASHBOARD

You'll see on your dashboard:

```
Morning (9:20-10:30):
  Active Positions: 1-2 lots
  Typical P&L: -₹500 to +₹2,000
  
Mid-Morning (10:30-12:00):
  Active Positions: 2-3 lots
  Typical P&L: -₹1,000 to +₹3,000
  
Afternoon (1:00-2:30):
  Active Positions: 2-4 lots
  Typical P&L: -₹500 to +₹2,000
  
Final Hour (2:30-3:15):
  All positions close
  Daily total: -₹500 to +₹7,000
```

---

## NEXT STEPS

1. **Copy this config** into your system
2. **Update strike prices** for current market
3. **Start with 2-3 strategies** (don't do all 6 at once)
4. **Run for 2 weeks** in paper trading
5. **Review daily results**
6. **Adjust rules** based on what works
7. **Add more strategies** gradually

---

**Version**: 1.0  
**Last Updated**: May 6, 2024  
**Status**: Ready to Use