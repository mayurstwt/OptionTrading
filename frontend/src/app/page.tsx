"use client"

import { MarketOverviewCards } from "@/components/MarketOverviewCards"
import { DailySummaryStats } from "@/components/DailySummaryStats"
import { PositionsTable } from "@/components/PositionsTable"
import { TradeHistoryTable } from "@/components/TradeHistoryTable"
import { PnLCurveChart } from "@/components/PnLCurveChart"
import { RecentAlerts } from "@/components/RecentAlerts"

export default function DashboardPage() {
  return (
    <div className="flex flex-col gap-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="space-y-2">
        <h1 className="text-4xl font-bold tracking-tight bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">Dashboard</h1>
        <p className="text-muted-foreground text-lg">
          Real-time overview of your autonomous trading engine.
        </p>
      </div>

      <MarketOverviewCards />
      
      <DailySummaryStats />

      <div className="grid gap-8 lg:grid-cols-2">
        <PnLCurveChart />
        <RecentAlerts />
      </div>

      <PositionsTable />

      <TradeHistoryTable />
    </div>
  )
}
