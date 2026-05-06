# FRONTEND MASTER PROMPT: Next.js Trading Dashboard with Real-Time Updates

**Purpose**: Complete specification for building the frontend for autonomous trading engine  
**Technology**: Next.js 14, TypeScript, Tailwind CSS, Recharts  
**Deployment**: Netlify  
**Status**: Ready to Build  

---

## OVERVIEW

Build a production-ready, real-time trading dashboard that displays:
- Live market prices (NIFTY/BANKNIFTY)
- Open positions with current P&L
- Trade history with detailed analytics
- Trading rules editor (YAML configuration)
- Alert feed (all trading events)
- Performance charts and metrics
- Manual controls (close positions, run strategies)

The frontend communicates exclusively with a backend API (running on a Python server) via REST endpoints.

---

## TECHNOLOGY STACK

```
Framework:     Next.js 14 (App Router)
Language:      TypeScript
Styling:       Tailwind CSS
Components:    shadcn/ui
Charts:        Recharts
API Client:    fetch API with custom hooks
Real-time:    Polling (5-second interval)
Hosting:       Netlify
Database Sync: Supabase (optional, for caching)
```

---

## API ENDPOINTS EXPECTED FROM BACKEND

All endpoints return JSON. The frontend will make requests to these:

```typescript
// MARKET DATA
GET /api/market-data
Response: {
  nifty: {
    price: 24144.15,
    change: 0.5,
    change_pct: 0.00207,
    iv: 18.5,
    timestamp: "2026-05-06T09:44:04Z"
  },
  banknifty: {
    price: 55138.75,
    change: -10.25,
    change_pct: -0.0186,
    iv: 19.2,
    timestamp: "2026-05-06T09:44:32Z"
  }
}

// OPEN POSITIONS
GET /api/positions
Response: [
  {
    id: "POS_001",
    instrument_key: "NSE_FO|NIFTY24MAY24000CE",
    instrument_name: "NIFTY 24000 CE",
    side: "SELL",
    entry_price: 150.50,
    entry_time: "2026-05-06T09:35:00Z",
    current_price: 165.75,
    quantity: 1,
    unrealized_pnl: 1525,
    unrealized_pnl_pct: 3.02,
    max_pnl: 1525,
    status: "OPEN"
  },
  {
    id: "POS_002",
    instrument_key: "NSE_FO|NIFTY24MAY24000PE",
    instrument_name: "NIFTY 24000 PE",
    side: "SELL",
    entry_price: 142.00,
    entry_time: "2026-05-06T09:35:00Z",
    current_price: 135.50,
    quantity: 1,
    unrealized_pnl: 650,
    unrealized_pnl_pct: 4.58,
    max_pnl: 650,
    status: "OPEN"
  }
]

// CLOSED TRADES
GET /api/trades?limit=20&offset=0
Response: {
  trades: [
    {
      id: "TRADE_001",
      instrument_key: "NSE_FO|NIFTY24APR24000CE",
      instrument_name: "NIFTY 24000 CE",
      side: "SELL",
      entry_time: "2026-05-05T09:40:00Z",
      entry_price: 160.00,
      exit_time: "2026-05-05T11:20:00Z",
      exit_price: 135.50,
      quantity: 1,
      realized_pnl: 2450,
      realized_pnl_pct: 1.53,
      duration_minutes: 100,
      entry_rule: "short_straddle",
      exit_rule: "profit_target"
    }
  ],
  total_count: 245,
  limit: 20,
  offset: 0
}

// DAILY SUMMARY
GET /api/summary?date=2026-05-06
Response: {
  date: "2026-05-06",
  total_trades: 5,
  winning_trades: 3,
  losing_trades: 2,
  realized_pnl: 4500,
  unrealized_pnl: 2175,
  max_drawdown: -1050,
  max_drawdown_pct: -0.105,
  win_rate: 60,
  avg_win: 1500,
  avg_loss: -750,
  profit_factor: 2.0,
  sharpe_ratio: 1.8
}

// ANALYTICS
GET /api/analytics?period=today|week|month
Response: {
  period: "today",
  total_pnl: 6675,
  trades: 5,
  win_rate: 60,
  sharpe_ratio: 1.8,
  profit_factor: 2.0,
  max_dd: -1050,
  daily_pnl_curve: [
    { time: "09:30", pnl: 0 },
    { time: "09:45", pnl: 1500 },
    { time: "10:00", pnl: 2000 },
    { time: "11:20", pnl: 4500 },
    { time: "15:30", pnl: 6675 }
  ]
}

// ALERTS
GET /api/alerts?limit=50&type=all
Response: [
  {
    id: "ALERT_001",
    timestamp: "2026-05-06T09:35:00Z",
    type: "TRADE_ENTRY",
    severity: "INFO",
    message: "Trade entry: NIFTY short straddle",
    details: {
      rule: "short_straddle",
      instruments: ["NIFTY 24000 CE", "NIFTY 24000 PE"],
      quantity: 1,
      entry_price: 150.50
    }
  },
  {
    id: "ALERT_002",
    timestamp: "2026-05-06T10:45:00Z",
    type: "TRADE_EXIT",
    severity: "INFO",
    message: "Trade exit: Profit target hit",
    details: {
      trade_id: "TRADE_001",
      exit_price: 135.50,
      pnl: 2450
    }
  }
]

// HEALTH CHECK
GET /api/health
Response: {
  status: "healthy",
  backend_status: "running",
  last_update: "2026-05-06T09:47:15Z",
  market_hours: true,
  database_connection: "ok"
}

// MANUAL ACTIONS
POST /api/close-position
Body: { position_id: "POS_001" }
Response: { success: true, trade: { ...closed_trade_data } }

POST /api/run-strategy
Body: { strategy_name: "short_straddle", force: true }
Response: { success: true, trades: [...placed_trades] }

POST /api/update-rules
Body: { config_yaml: "..." }
Response: { success: true, errors: [] }
```

---

## PAGE SPECIFICATIONS

### PAGE 1: Dashboard (`/`)

**Layout:**
```
Top Bar (Fixed):
  - Title: "Options Trading Engine"
  - Status indicator (🟢 LIVE / 🔴 OFFLINE)
  - Last update time
  - Menu: Dashboard | Rules | Analytics | Alerts | Settings
  - User menu

Main Content (Scrollable):
  1. Market Overview Cards (3 columns)
     - NIFTY card: price, change %, IV
     - BANKNIFTY card: price, change %, IV
     - Status card: trades today, P&L, status

  2. Open Positions Section
     - Table/Cards showing all open positions
     - Columns: Instrument, Entry, Current, P&L, Duration, [Action]
     - Real-time updates (every 5 seconds)
     - [Close] button for each position

  3. Daily Summary (Stats Row)
     - Total Trades, Winning, Losing, Win Rate
     - Realized P&L, Unrealized P&L, Max Drawdown

  4. Trade History (Table)
     - Columns: Time, Instrument, Entry, Exit, P&L, Duration, Rule
     - Pagination (20 per page)
     - Sortable & filterable

  5. Charts (2 columns)
     - Left: Daily P&L Curve (line chart)
     - Right: Drawdown Chart (area chart)

  6. Recent Alerts (Feed)
     - Last 10 alerts
     - Color-coded by type/severity
     - Auto-scroll to latest
```

**Components Needed:**
- `<MarketOverviewCard />` - Display price, change, IV
- `<PositionsTable />` - List all open positions
- `<DailySummaryStats />` - Show key metrics
- `<TradeHistoryTable />` - Show closed trades
- `<PnLCurveChart />` - Line chart of daily P&L
- `<DrawdownChart />` - Area chart of drawdown
- `<RecentAlerts />` - Feed of latest alerts

**Data Flow:**
```
setInterval(() => {
  fetchMarketData() → updateCards()
  fetchPositions() → updatePositions()
  fetchAlerts() → updateAlerts()
}, 5000) // Every 5 seconds
```

---

### PAGE 2: Rules Editor (`/rules`)

**Layout:**
```
Top Bar:
  - Title: "Trading Rules Configuration"
  - [Save] [Reset] [Validate] buttons
  - Help tooltip

Main Content (2 Columns):
  Left Column (40%):
    - Rule List (Entry Rules & Exit Rules)
    - Each rule shows: name, enabled?, conditions count
    - [+ Add Entry Rule] [+ Add Exit Rule] buttons
    - Click rule to edit

  Right Column (60%):
    - YAML Editor (code editor with syntax highlighting)
    - Editable config_v1.yaml
    - Real-time validation
    - Errors/warnings display
    - [Save] [Cancel] buttons at bottom
```

**YAML Editor Features:**
```typescript
<YAMLEditor>
  - Syntax highlighting (keys, strings, numbers)
  - Line numbers
  - Auto-indentation
  - Copy/paste support
  - Validation on blur
  - Show errors inline
</YAMLEditor>
```

**Sample YAML Structure (read-only reference):**
```yaml
trading_config:
  paper_capital: 1000000
  risk_limits:
    max_position_size_lots: 3
    max_concurrent_lots: 6
    daily_loss_limit_pct: -1.5

  entry_rules:
    - rule_name: "short_straddle"
      enabled: true
      time_window: ["09:20", "10:30"]
      conditions:
        - metric: "price"
          operator: "between"
          values: [24000, 25000]
        - metric: "iv_rank"
          operator: ">="
          values: [40]
      position_sizing:
        base_lots: 1

  exit_rules:
    - rule_name: "profit_target"
      enabled: true
      trigger: "premium_change"
      threshold: -25  # Premium dropped 25%
```

**Components Needed:**
- `<RulesList />` - Show all rules
- `<YAMLEditor />` - Code editor
- `<ValidationPanel />` - Show errors/warnings
- `<RuleForm />` - Modal to add/edit rules

---

### PAGE 3: Analytics (`/analytics`)

**Layout:**
```
Top Bar:
  - Title: "Trading Analytics"
  - Date Range Selector: [Today] [Week] [Month] [Custom]

Main Content:
  1. Key Metrics (4-column grid)
     - Total P&L (large number, green/red)
     - Win Rate (%)
     - Sharpe Ratio
     - Profit Factor

  2. Charts (2x2 grid)
     - Top-Left: P&L Curve (line chart, cumulative)
     - Top-Right: Win/Loss Distribution (bar chart)
     - Bottom-Left: Trade Duration Distribution (histogram)
     - Bottom-Right: P&L Distribution (scatter plot)

  3. Detailed Stats (Table)
     - Days traded, avg daily P&L, best day, worst day
     - Best trade, worst trade, avg win/loss
     - Consecutive wins, consecutive losses
```

**Charts Library:** Recharts

**Example Chart:**
```typescript
<LineChart data={pnlData} width={600} height={300}>
  <CartesianGrid strokeDasharray="3 3" />
  <XAxis dataKey="time" />
  <YAxis />
  <Tooltip />
  <Line type="monotone" dataKey="pnl" stroke="#8884d8" />
</LineChart>
```

---

### PAGE 4: Alerts (`/alerts`)

**Layout:**
```
Top Bar:
  - Title: "Trading Alerts"
  - Filter tabs: [All] [Trades] [Risks] [Errors] [Warnings]
  - Search bar
  - Auto-refresh toggle

Main Content:
  - Alert Feed (reverse chronological)
  - Each alert shows:
    - Timestamp (formatted)
    - Type icon & color
    - Severity badge
    - Message
    - Expandable details
  - Load more button / infinite scroll

Alert Types & Colors:
  - 🟢 TRADE_ENTRY (green)
  - 🟠 TRADE_EXIT (orange)
  - 🟡 POSITION_UPDATE (yellow)
  - 🔴 RISK_BLOCK (red)
  - ⚠️  WARNING (orange)
  - 🔵 ERROR (blue)
```

**Components Needed:**
- `<AlertFeed />` - Main feed
- `<AlertCard />` - Individual alert
- `<FilterTabs />` - Filter by type
- `<SearchBar />` - Search alerts

---

## API CLIENT HOOKS

**Custom hooks for data fetching:**

```typescript
// Hook 1: Fetch market data
useMarketData() → { nifty, banknifty, loading, error }

// Hook 2: Fetch positions
usePositions() → { positions, loading, error }

// Hook 3: Fetch trades
useTrades(limit, offset) → { trades, total, loading, error }

// Hook 4: Fetch analytics
useAnalytics(period) → { metrics, charts, loading, error }

// Hook 5: Fetch alerts
useAlerts(limit, type) → { alerts, loading, error }

// Hook 6: Fetch health
useHealth() → { status, lastUpdate, loading }

// Mutation hooks
useClosePosition() → { closePosition, loading, error }
useRunStrategy() → { runStrategy, loading, error }
useUpdateRules() → { updateRules, loading, error }
```

**Implementation Pattern:**
```typescript
export function useMarketData() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch('/api/market-data');
        setData(await res.json());
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5000); // Poll every 5s
    return () => clearInterval(interval);
  }, []);

  return { data, loading, error };
}
```

---

## COMPONENT LIBRARY (shadcn/ui)

**Use these pre-built components:**
```
Button
Card
Table
Badge
Alert
Toast (for notifications)
Dropdown Menu
Dialog/Modal
Tabs
Input
Select
Chart components (integrate Recharts)
```

---

## STYLING GUIDELINES

**Color Scheme:**
```
Primary: Blue (#3b82f6)
Success: Green (#10b981)
Warning: Orange (#f59e0b)
Danger: Red (#ef4444)
Background: Dark (#1f2937)
Text: Light (#f3f4f6)
Borders: Gray (#4b5563)

Profit: Green
Loss: Red
Neutral: Gray
```

**Responsive Design:**
- Mobile-first approach
- Breakpoints: sm (640px), md (768px), lg (1024px), xl (1280px)
- Dashboard responsive: cards stack on mobile
- Charts responsive: scale down on small screens

---

## REAL-TIME UPDATE STRATEGY

**Polling Approach (Recommended for Netlify):**

```typescript
// App-level hook
export function useAutoRefresh(interval = 5000) {
  useEffect(() => {
    const timer = setInterval(() => {
      // Refetch all data
      queryClient.refetchQueries(); // if using React Query
      // Or manually update state
    }, interval);
    
    return () => clearInterval(timer);
  }, []);
}

// Usage in Dashboard
function Dashboard() {
  useAutoRefresh(5000); // Refresh every 5 seconds
  
  return (
    <div>
      <MarketOverview /> {/* Updates every 5s */}
      <PositionsList /> {/* Updates every 5s */}
      <AlertsFeed /> {/* Updates every 5s */}
    </div>
  );
}
```

**Alternative: WebSocket (if backend supports)**

```typescript
export function useWebSocket(url) {
  useEffect(() => {
    const ws = new WebSocket(url);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      updateState(data); // Update Redux/Zustand store
    };
    
    return () => ws.close();
  }, []);
}
```

---

## STATE MANAGEMENT

**Option 1: React Context + useState (Simple)**
```typescript
<MarketDataProvider>
  <Dashboard />
</MarketDataProvider>
```

**Option 2: Zustand (Recommended)**
```typescript
const useStore = create((set) => ({
  marketData: null,
  positions: [],
  alerts: [],
  
  setMarketData: (data) => set({ marketData: data }),
  addAlert: (alert) => set((state) => ({ 
    alerts: [alert, ...state.alerts] 
  })),
}));
```

**Option 3: React Query (For data fetching)**
```typescript
const { data: marketData } = useQuery({
  queryKey: ['marketData'],
  queryFn: () => fetch('/api/market-data').then(r => r.json()),
  refetchInterval: 5000,
});
```

---

## ERROR HANDLING

**Graceful degradation:**

```typescript
<ErrorBoundary fallback={<ErrorPage />}>
  <Dashboard />
</ErrorBoundary>

// Component-level error handling
{loading && <Spinner />}
{error && <ErrorAlert message={error.message} />}
{data && <Content data={data} />}
```

**Connection errors:**
```
If API unreachable:
  - Show offline banner
  - Use cached data (localStorage)
  - Retry with exponential backoff
  - Show "reconnecting..." status
```

---

## PERFORMANCE OPTIMIZATION

**Code splitting:**
```typescript
const AnalyticsPage = dynamic(
  () => import('./analytics'),
  { loading: () => <Spinner /> }
);
```

**Image optimization:**
```typescript
import Image from 'next/image';
// Automatic optimization for all images
```

**Caching:**
```typescript
// Cache responses for 5 minutes
const response = await fetch(url, {
  headers: { 'Cache-Control': 'max-age=300' }
});
```

---

## DEPLOYMENT TO NETLIFY

**Setup:**

```bash
# 1. Create Git repository
git init
git add .
git commit -m "Initial commit"
git push origin main

# 2. Connect to Netlify
# Go to netlify.com → New site from Git
# Select GitHub repo
# Build command: npm run build
# Publish directory: .next/public

# 3. Environment variables (in Netlify dashboard)
NEXT_PUBLIC_API_URL=https://your-backend-api.com
```

**Build Configuration (netlify.toml):**

```toml
[build]
  command = "npm run build"
  publish = ".next/public"

[functions]
  directory = "netlify/functions"

[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/:splat"
  status = 200

[[headers]]
  for = "/*"
  [headers.values]
    Cache-Control = "public, max-age=3600"
```

**Environment Variables:**
```
NEXT_PUBLIC_BACKEND_URL=https://your-vps-ip:port
NEXT_PUBLIC_API_TIMEOUT=30000
NEXT_PUBLIC_POLLING_INTERVAL=5000
```

---

## FILE STRUCTURE

```
frontend/
├── app/
│   ├── layout.tsx
│   ├── page.tsx (Dashboard)
│   ├── rules/
│   │   └── page.tsx
│   ├── analytics/
│   │   └── page.tsx
│   ├── alerts/
│   │   └── page.tsx
│   ├── settings/
│   │   └── page.tsx
│   ├── api/
│   │   ├── market-data/
│   │   │   └── route.ts
│   │   ├── positions/
│   │   │   └── route.ts
│   │   ├── trades/
│   │   │   └── route.ts
│   │   ├── analytics/
│   │   │   └── route.ts
│   │   ├── alerts/
│   │   │   └── route.ts
│   │   ├── health/
│   │   │   └── route.ts
│   │   ├── close-position/
│   │   │   └── route.ts
│   │   ├── run-strategy/
│   │   │   └── route.ts
│   │   └── update-rules/
│   │       └── route.ts
│   └── components/
│       ├── Dashboard.tsx
│       ├── MarketOverview.tsx
│       ├── PositionsTable.tsx
│       ├── TradeHistory.tsx
│       ├── Charts.tsx
│       ├── AlertsFeed.tsx
│       ├── RulesList.tsx
│       ├── YAMLEditor.tsx
│       └── Header.tsx
├── lib/
│   ├── api-client.ts
│   ├── hooks.ts (custom hooks)
│   ├── utils.ts
│   ├── store.ts (Zustand or Context)
│   └── types.ts
├── public/
│   └── assets/
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── next.config.ts
└── netlify.toml
```

---

## TESTING CHECKLIST

- [ ] Dashboard loads and displays market data
- [ ] Positions update every 5 seconds
- [ ] Charts render correctly with sample data
- [ ] Alerts feed displays correctly
- [ ] Rules page editor is functional
- [ ] Close position button works
- [ ] All pages responsive on mobile
- [ ] Error states handled gracefully
- [ ] API calls have proper error handling
- [ ] Performance acceptable (<2s load time)
- [ ] Deployed to Netlify successfully
- [ ] All API routes accessible
- [ ] CORS configured correctly

---

**Version**: 1.0.0  
**Last Updated**: May 6, 2024  
**Status**: ✅ Ready to Build with AI

