"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card"
import { Save, RotateCcw, CheckCircle2 } from "lucide-react"

const initialYaml = `trading_config:
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
      threshold: -25  # Premium dropped 25%`

export default function RulesPage() {
  const [yaml, setYaml] = useState(initialYaml)
  const [isSaving, setIsSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  const handleSave = () => {
    setIsSaving(true)
    setTimeout(() => {
      setIsSaving(false)
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    }, 1000)
  }

  return (
    <div className="flex flex-col gap-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Rules Editor</h1>
          <p className="text-muted-foreground">
            Configure entry and exit rules for your trading engine.
          </p>
        </div>
        <div className="flex gap-2">
          <button 
            onClick={() => setYaml(initialYaml)}
            className="inline-flex items-center gap-2 rounded-md border bg-background px-4 py-2 text-sm font-medium hover:bg-accent transition-colors"
          >
            <RotateCcw className="h-4 w-4" />
            Reset
          </button>
          <button 
            onClick={handleSave}
            disabled={isSaving}
            className="inline-flex items-center gap-2 rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition-colors disabled:opacity-50"
          >
            {saved ? <CheckCircle2 className="h-4 w-4" /> : <Save className="h-4 w-4" />}
            {isSaving ? "Saving..." : saved ? "Saved" : "Save Changes"}
          </button>
        </div>
      </div>

      <div className="grid gap-8 lg:grid-cols-3">
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle className="text-lg">Rules Overview</CardTitle>
            <CardDescription>Quick summary of active rules.</CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-4">
              <li className="flex items-center justify-between border-b pb-2">
                <div>
                  <p className="font-medium">short_straddle</p>
                  <p className="text-xs text-muted-foreground">Entry Rule</p>
                </div>
                <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-800 dark:bg-green-900 dark:text-green-100">
                  Enabled
                </span>
              </li>
              <li className="flex items-center justify-between border-b pb-2">
                <div>
                  <p className="font-medium">profit_target</p>
                  <p className="text-xs text-muted-foreground">Exit Rule</p>
                </div>
                <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-800 dark:bg-green-900 dark:text-green-100">
                  Enabled
                </span>
              </li>
            </ul>
          </CardContent>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-lg">YAML Configuration</CardTitle>
            <CardDescription>Edit your trading rules directly.</CardDescription>
          </CardHeader>
          <CardContent>
            <textarea
              value={yaml}
              onChange={(e) => setYaml(e.target.value)}
              className="min-h-[500px] w-full rounded-md border bg-slate-950 p-4 font-mono text-sm text-slate-300 focus:outline-none focus:ring-1 focus:ring-blue-500"
              spellCheck={false}
            />
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
