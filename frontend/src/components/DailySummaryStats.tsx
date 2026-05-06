"use client"

import { useDailySummary } from "@/lib/hooks"
import { formatCurrency, formatPercent, cn } from "@/lib/utils"

export function DailySummaryStats() {
  const { data: summary } = useDailySummary()

  const items = [
    { label: "Total Trades", value: summary?.total_trades },
    { label: "Win Rate", value: summary?.win_rate ? formatPercent(summary.win_rate) : "0%" },
    { label: "Profit Factor", value: summary?.profit_factor?.toFixed(2) },
    { label: "Max Drawdown", value: summary?.max_drawdown ? formatCurrency(summary.max_drawdown) : "₹0", color: "text-red-500" },
  ]

  return (
    <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
      {items.map((item) => (
        <div key={item.label} className="flex flex-col gap-1 rounded-lg border bg-card p-4 shadow-sm">
          <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">{item.label}</span>
          <span className={cn("text-xl font-bold", item.color)}>{item.value}</span>
        </div>
      ))}
    </div>
  )
}
