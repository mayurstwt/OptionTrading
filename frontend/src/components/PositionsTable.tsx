"use client"

import { usePositions } from "@/lib/hooks"
import { Card, CardContent, CardHeader, CardTitle } from "./ui/Card"
import { formatCurrency, cn } from "@/lib/utils"
import { XCircle } from "lucide-react"

export function PositionsTable() {
  const { data: positions } = usePositions()

  return (
    <Card className="col-span-full">
      <CardHeader>
        <CardTitle className="text-lg">Open Positions</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="relative w-full overflow-auto">
          <table className="w-full caption-bottom text-sm">
            <thead className="[&_tr]:border-b">
              <tr className="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
                <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Instrument</th>
                <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Side</th>
                <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Qty</th>
                <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Entry Price</th>
                <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">LTP</th>
                <th className="h-12 px-4 text-right align-middle font-medium text-muted-foreground">P&L</th>
                <th className="h-12 px-4 text-right align-middle font-medium text-muted-foreground">Action</th>
              </tr>
            </thead>
            <tbody className="[&_tr:last-child]:border-0">
              {!positions?.length ? (
                <tr>
                  <td colSpan={7} className="h-24 text-center align-middle text-muted-foreground">
                    No open positions.
                  </td>
                </tr>
              ) : (
                positions.map((pos) => (
                  <tr key={pos.id} className="border-b transition-colors hover:bg-muted/50">
                    <td className="p-4 align-middle font-medium">{pos.instrument_name}</td>
                    <td className="p-4 align-middle">
                      <span className={cn(
                        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
                        pos.side === 'BUY' ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100" : "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100"
                      )}>
                        {pos.side}
                      </span>
                    </td>
                    <td className="p-4 align-middle">{pos.quantity}</td>
                    <td className="p-4 align-middle">{formatCurrency(pos.entry_price)}</td>
                    <td className="p-4 align-middle">{formatCurrency(pos.current_price)}</td>
                    <td className={cn(
                      "p-4 align-middle text-right font-bold",
                      pos.unrealized_pnl >= 0 ? "text-green-500" : "text-red-500"
                    )}>
                      {formatCurrency(pos.unrealized_pnl)}
                    </td>
                    <td className="p-4 align-middle text-right">
                      <button className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 hover:bg-accent hover:text-accent-foreground h-9 w-9 text-red-500">
                        <XCircle className="h-5 w-5" />
                      </button>
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
