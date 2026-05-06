"use client"

import { useTrades } from "@/lib/hooks"
import { Card, CardContent, CardHeader, CardTitle } from "./ui/Card"
import { formatCurrency, cn } from "@/lib/utils"
import { format } from "date-fns"

export function TradeHistoryTable() {
  const { data } = useTrades()
  const trades = data?.trades || []

  return (
    <Card className="col-span-full">
      <CardHeader>
        <CardTitle className="text-lg">Trade History</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="relative w-full overflow-auto">
          <table className="w-full caption-bottom text-sm">
            <thead className="[&_tr]:border-b">
              <tr className="border-b transition-colors hover:bg-muted/50">
                <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Time</th>
                <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Instrument</th>
                <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Entry</th>
                <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Exit</th>
                <th className="h-12 px-4 text-right align-middle font-medium text-muted-foreground">P&L</th>
                <th className="h-12 px-4 text-right align-middle font-medium text-muted-foreground">Rule</th>
              </tr>
            </thead>
            <tbody className="[&_tr:last-child]:border-0">
              {!trades.length ? (
                <tr>
                  <td colSpan={6} className="h-24 text-center align-middle text-muted-foreground">
                    No trade history available.
                  </td>
                </tr>
              ) : (
                trades.map((trade) => (
                  <tr key={trade.id} className="border-b transition-colors hover:bg-muted/50">
                    <td className="p-4 align-middle whitespace-nowrap">
                      {format(new Date(trade.exit_time), "HH:mm:ss")}
                    </td>
                    <td className="p-4 align-middle font-medium">{trade.instrument_name}</td>
                    <td className="p-4 align-middle">{formatCurrency(trade.entry_price)}</td>
                    <td className="p-4 align-middle">{formatCurrency(trade.exit_price)}</td>
                    <td className={cn(
                      "p-4 align-middle text-right font-bold",
                      trade.realized_pnl >= 0 ? "text-green-500" : "text-red-500"
                    )}>
                      {formatCurrency(trade.realized_pnl)}
                    </td>
                    <td className="p-4 align-middle text-right text-xs text-muted-foreground">
                      {trade.entry_rule}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  )
}
