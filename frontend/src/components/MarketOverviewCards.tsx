"use client"

import { useMarketData, useDailySummary } from "@/lib/hooks"
import { Card, CardContent, CardHeader, CardTitle } from "./ui/Card"
import { TrendingUp, TrendingDown, Activity, DollarSign } from "lucide-react"
import { formatCurrency, formatPercent, cn } from "@/lib/utils"

export function MarketOverviewCards() {
  const { data: marketData } = useMarketData()
  const { data: summary } = useDailySummary()

  const stats = [
    {
      title: "NIFTY 50",
      value: marketData?.nifty.price,
      change: marketData?.nifty.change_pct,
      iv: marketData?.nifty.iv,
      icon: Activity,
    },
    {
      title: "BANKNIFTY",
      value: marketData?.banknifty.price,
      change: marketData?.banknifty.change_pct,
      iv: marketData?.banknifty.iv,
      icon: Activity,
    },
    {
      title: "Today's P&L",
      value: (summary?.realized_pnl || 0) + (summary?.unrealized_pnl || 0),
      isCurrency: true,
      icon: DollarSign,
    },
  ]

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {stats.map((stat) => (
        <Card key={stat.title}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
            <stat.icon className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stat.isCurrency ? formatCurrency(stat.value as number) : stat.value?.toLocaleString()}
            </div>
            {stat.change !== undefined && (
              <p className={cn(
                "text-xs font-medium mt-1 flex items-center gap-1",
                stat.change >= 0 ? "text-green-500" : "text-red-500"
              )}>
                {stat.change >= 0 ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                {formatPercent(Math.abs(stat.change * 100))}
                <span className="text-muted-foreground ml-1">IV: {stat.iv}%</span>
              </p>
            )}
            {stat.isCurrency && (
              <p className="text-xs text-muted-foreground mt-1">
                Realized: {formatCurrency(summary?.realized_pnl || 0)}
              </p>
            )}
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
