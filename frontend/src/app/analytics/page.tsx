"use client"

import { useAnalytics } from "@/lib/hooks"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, PieChart, Pie } from "recharts"
import { formatCurrency, formatPercent, cn } from "@/lib/utils"

export default function AnalyticsPage() {
  const { data: analytics } = useAnalytics()

  const metrics = [
    { label: "Total P&L", value: analytics?.total_pnl ? formatCurrency(analytics.total_pnl) : "₹0", color: (analytics?.total_pnl || 0) >= 0 ? "text-green-500" : "text-red-500" },
    { label: "Win Rate", value: analytics?.win_rate ? formatPercent(analytics.win_rate) : "0%" },
    { label: "Sharpe Ratio", value: analytics?.sharpe_ratio?.toFixed(2) },
    { label: "Profit Factor", value: analytics?.profit_factor?.toFixed(2) },
  ]

  const winLossData = [
    { name: "Wins", value: analytics?.win_rate || 0, color: "#10b981" },
    { name: "Losses", value: 100 - (analytics?.win_rate || 0), color: "#ef4444" },
  ]

  return (
    <div className="flex flex-col gap-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Analytics</h1>
        <p className="text-muted-foreground">
          Detailed performance metrics and trade analysis.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {metrics.map((metric) => (
          <Card key={metric.label}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{metric.label}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className={cn("text-2xl font-bold", metric.color)}>{metric.value}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-8 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Win/Loss Distribution</CardTitle>
          </CardHeader>
          <CardContent className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={winLossData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {winLossData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ backgroundColor: "#1f2937", border: "none", borderRadius: "8px" }}
                  formatter={(value: any) => [`${value}%`, ""]}
                />
              </PieChart>
            </ResponsiveContainer>
            <div className="flex justify-center gap-4 mt-4">
              {winLossData.map((item) => (
                <div key={item.name} className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full" style={{ backgroundColor: item.color }} />
                  <span className="text-xs text-muted-foreground">{item.name}: {item.value}%</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">P&L by Strategy</CardTitle>
          </CardHeader>
          <CardContent className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={[
                { name: "Straddle", pnl: 4500 },
                { name: "Strangle", pnl: 2175 },
                { name: "Iron Condor", pnl: -1200 },
              ]}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#333" />
                <XAxis dataKey="name" stroke="#888" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#888" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `₹${value}`} />
                <Tooltip contentStyle={{ backgroundColor: "#1f2937", border: "none", borderRadius: "8px" }} />
                <Bar dataKey="pnl" radius={[4, 4, 0, 0]}>
                  {[4500, 2175, -1200].map((val, index) => (
                    <Cell key={`cell-${index}`} fill={val >= 0 ? "#10b981" : "#ef4444"} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
