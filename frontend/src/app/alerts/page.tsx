"use client"

import { useState } from "react"
import { useAlerts } from "@/lib/hooks"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { format } from "date-fns"
import { cn } from "@/lib/utils"
import { Info, AlertTriangle, AlertCircle, Search, Filter } from "lucide-react"

export default function AlertsPage() {
  const { data: alerts } = useAlerts()
  const [filter, setFilter] = useState('ALL')
  const [search, setSearch] = useState('')

  const filteredAlerts = alerts?.filter(alert => {
    const matchesFilter = filter === 'ALL' || alert.type.includes(filter)
    const matchesSearch = alert.message.toLowerCase().includes(search.toLowerCase()) || 
                          alert.type.toLowerCase().includes(search.toLowerCase())
    return matchesFilter && matchesSearch
  })

  const getIcon = (severity: string) => {
    switch (severity) {
      case 'CRITICAL': return <AlertCircle className="h-5 w-5 text-red-500" />
      case 'WARNING': return <AlertTriangle className="h-5 w-5 text-yellow-500" />
      default: return <Info className="h-5 w-5 text-blue-500" />
    }
  }

  return (
    <div className="flex flex-col gap-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Alerts Feed</h1>
        <p className="text-muted-foreground">
          Real-time event log for all trading activities.
        </p>
      </div>

      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search alerts..."
            className="w-full rounded-md border bg-background pl-9 pr-4 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-muted-foreground" />
          <select 
            className="rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          >
            <option value="ALL">All Types</option>
            <option value="TRADE">Trades Only</option>
            <option value="RISK">Risk Management</option>
            <option value="ERROR">Errors</option>
          </select>
        </div>
      </div>

      <Card>
        <CardContent className="p-0">
          <div className="divide-y">
            {!filteredAlerts?.length ? (
              <div className="p-8 text-center text-muted-foreground">
                No alerts found matching your criteria.
              </div>
            ) : (
              filteredAlerts.map((alert) => (
                <div key={alert.id} className="flex gap-4 p-4 hover:bg-muted/30 transition-colors">
                  <div className="mt-1">{getIcon(alert.severity)}</div>
                  <div className="flex-1 space-y-1">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-semibold">{alert.message}</p>
                      <span className="text-xs text-muted-foreground">
                        {format(new Date(alert.timestamp), "MMM dd, HH:mm:ss")}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={cn(
                        "rounded-full px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider",
                        alert.severity === 'CRITICAL' ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400" :
                        alert.severity === 'WARNING' ? "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400" :
                        "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
                      )}>
                        {alert.type}
                      </span>
                      {alert.details?.rule && (
                        <span className="text-[10px] text-muted-foreground">
                          Rule: {alert.details.rule}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
