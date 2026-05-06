"use client"

import { useState } from "react"
import { useWallet, useWalletTransactions } from "@/lib/hooks"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { formatCurrency, formatDateTime } from "@/lib/utils"
import { Wallet, ArrowUpCircle, ArrowDownCircle, History, Plus } from "lucide-react"
import { cn } from "@/lib/utils"

export default function WalletPage() {
  const { data: wallet, loading: walletLoading } = useWallet()
  const { data: transactions, loading: transLoading } = useWalletTransactions()
  const [isAddingFunds, setIsAddingFunds] = useState(false)
  const [amount, setAmount] = useState("")

  const handleAddFunds = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!amount || isNaN(Number(amount))) return

    try {
      const res = await fetch("/api/wallet/add-funds", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ amount: Number(amount) }),
      })
      if (res.ok) {
        setIsAddingFunds(false)
        setAmount("")
        // Refresh page or data (since we are using polling hooks, it will update automatically)
      }
    } catch (err) {
      console.error("Failed to add funds", err)
    }
  }

  return (
    <div className="flex flex-col gap-8 p-4 md:p-8 max-w-7xl mx-auto w-full">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Wallet & Funds</h1>
          <p className="text-muted-foreground">Manage your paper trading capital and margins.</p>
        </div>
        <button 
          onClick={() => setIsAddingFunds(true)}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md transition-colors"
        >
          <Plus className="h-4 w-4" />
          Add Funds
        </button>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Balance</CardTitle>
            <Wallet className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{walletLoading ? "---" : formatCurrency(wallet?.balance || 0)}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Used Margin</CardTitle>
            <ArrowDownCircle className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-500">{walletLoading ? "---" : formatCurrency(wallet?.used_margin || 0)}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Available Margin</CardTitle>
            <ArrowUpCircle className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-500">{walletLoading ? "---" : formatCurrency(wallet?.available_margin || 0)}</div>
          </CardContent>
        </Card>
      </div>

      {isAddingFunds && (
        <Card className="border-blue-500/50 bg-blue-500/5">
          <CardHeader>
            <CardTitle className="text-lg">Add Paper Money</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleAddFunds} className="flex gap-4">
              <input
                type="number"
                placeholder="Enter amount (e.g. 100000)"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                className="flex-1 bg-background border rounded-md px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500"
                autoFocus
              />
              <button 
                type="submit"
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-md"
              >
                Deposit
              </button>
              <button 
                type="button"
                onClick={() => setIsAddingFunds(false)}
                className="bg-muted hover:bg-muted/80 px-6 py-2 rounded-md"
              >
                Cancel
              </button>
            </form>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader className="flex flex-row items-center gap-2">
          <History className="h-5 w-5" />
          <CardTitle>Transaction History</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="relative w-full overflow-auto">
            <table className="w-full caption-bottom text-sm">
              <thead className="[&_tr]:border-b">
                <tr className="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
                  <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Date</th>
                  <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Type</th>
                  <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Description</th>
                  <th className="h-12 px-4 text-right align-middle font-medium text-muted-foreground">Amount</th>
                </tr>
              </thead>
              <tbody className="[&_tr:last-child]:border-0">
                {transLoading ? (
                  <tr><td colSpan={4} className="h-24 text-center">Loading transactions...</td></tr>
                ) : !transactions?.length ? (
                  <tr><td colSpan={4} className="h-24 text-center">No transactions found.</td></tr>
                ) : (
                  transactions.map((t) => (
                    <tr key={t.id} className="border-b transition-colors hover:bg-muted/50">
                      <td className="p-4 align-middle font-medium">{formatDateTime(t.timestamp)}</td>
                      <td className="p-4 align-middle">
                        <span className={cn(
                          "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold",
                          t.type === 'DEPOSIT' || t.type === 'MARGIN_RELEASED' || (t.type === 'PNL_SETTLEMENT' && t.amount > 0) 
                            ? "bg-green-500/10 text-green-500" 
                            : "bg-red-500/10 text-red-500"
                        )}>
                          {t.type.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="p-4 align-middle text-muted-foreground">{t.description}</td>
                      <td className={cn(
                        "p-4 align-middle text-right font-bold",
                        t.amount >= 0 ? "text-green-500" : "text-red-500"
                      )}>
                        {t.amount >= 0 ? "+" : ""}{formatCurrency(t.amount)}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
