import { useState, useEffect } from "react"

function usePollingFetch<T = any>(url: string, interval = 5000) {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch(url)
        if (!res.ok) throw new Error("Network response failed")
        const json = await res.json()
        setData(json)
        setError(null)
      } catch (err) {
        setError(err instanceof Error ? err : new Error("Unknown error"))
      } finally {
        setLoading(false)
      }
    }

    fetchData()
    const timer = setInterval(fetchData, interval)
    
    return () => clearInterval(timer)
  }, [url, interval])

  return { data, loading, error }
}

export function useMarketData() { return usePollingFetch("/api/market-data") }
export function usePositions() { return usePollingFetch("/api/positions") }
export function useTrades() { return usePollingFetch("/api/trades") }
export function useAnalytics() { return usePollingFetch("/api/analytics") }
export function useAlerts() { return usePollingFetch("/api/alerts") }
export function useDailySummary() { return usePollingFetch("/api/summary") }
export function useWallet() { return usePollingFetch("/api/wallet") }
export function useWalletTransactions() { return usePollingFetch("/api/wallet/transactions") }
export function useHealth() { return usePollingFetch("/api/health") }
