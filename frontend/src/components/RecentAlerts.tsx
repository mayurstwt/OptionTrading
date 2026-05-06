"use client"

import { useAlerts } from "@/lib/hooks"
import { Card, CardContent, CardHeader, CardTitle } from "./ui/Card"
import { format } from "date-fns"
import { cn } from "@/lib/utils"
import { Bell, Info, AlertTriangle, AlertCircle } from "lucide-react"

export function RecentAlerts() {
  const { data: alerts } = useAlerts()

  const getIcon = (severity: string) => {
    switch (severity) {
      case 'CRITICAL': return <AlertCircle className="h-4 w-4 text-red-500" />
      case 'WARNING': return <AlertTriangle className="h-4 w-4 text-yellow-500" />
      default: return <Info className="h-4 w-4 text-blue-500" />
    }
  }

  return (
    <Card className="col-span-full lg:col-span-1">
      <CardHeader className="flex flex-row items-center justify-between space-y-0">
        <CardTitle className="text-lg">Recent Alerts</CardTitle>
        <Bell className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {!alerts?.length ? (
            <p className="text-sm text-muted-foreground text-center py-4">No recent alerts.</p>
          ) : (
            alerts.slice(0, 5).map((alert) => (
              <div key={alert.id} className="flex items-start gap-3 border-b pb-3 last:border-0 last:pb-0">
                <div className="mt-0.5">{getIcon(alert.severity)}</div>
                <div className="flex-1 space-y-1">
                  <p className="text-sm font-medium leading-none">{alert.message}</p>
                  <p className="text-xs text-muted-foreground">
                    {format(new Date(alert.timestamp), "HH:mm:ss")} • {alert.type}
                  </p>
                </div>
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  )
}
