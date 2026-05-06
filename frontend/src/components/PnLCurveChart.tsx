"use client"

import { useAnalytics } from "@/lib/hooks"
import { Card, CardContent, CardHeader, CardTitle } from "./ui/Card"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from "recharts"
import { formatCurrency } from "@/lib/utils"

export function PnLCurveChart() {
  const { data: analytics } = useAnalytics()
  const data = analytics?.daily_pnl_curve || []

  return (
    <Card className="col-span-full lg:col-span-1">
      <CardHeader>
        <CardTitle className="text-lg">Cumulative P&L</CardTitle>
      </CardHeader>
      <CardContent className="h-[300px]">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data}>
            <defs>
              <linearGradient id="colorPnl" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#333" />
            <XAxis 
              dataKey="time" 
              stroke="#888" 
              fontSize={12} 
              tickLine={false} 
              axisLine={false}
            />
            <YAxis 
              stroke="#888" 
              fontSize={12} 
              tickLine={false} 
              axisLine={false}
              tickFormatter={(value) => `₹${value}`}
            />
            <Tooltip 
              contentStyle={{ backgroundColor: "#1f2937", border: "none", borderRadius: "8px" }}
              formatter={(value: any) => [formatCurrency(value), "P&L"]}
            />
            <Area 
              type="monotone" 
              dataKey="pnl" 
              stroke="#3b82f6" 
              fillOpacity={1} 
              fill="url(#colorPnl)" 
              strokeWidth={2}
            />
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
