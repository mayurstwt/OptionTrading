import { useState, useEffect } from "react"

// A generic hook that fetches data initially and then polls on an interval
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

    fetchData() // Initial fetch
    const timer = setInterval(fetchData, interval) // Start polling
    
    return () => clearInterval(timer) // Cleanup on unmount
  }, [url, interval])

  return { data, loading, error }
}

// Exported specific hooks used by your components
export function useMarketData() { return usePollingFetch("/api/market-data") }
export function usePositions() { return usePollingFetch("/api/positions") }
export function useTrades() { return usePollingFetch("/api/trades") }
export function useAnalytics() { return usePollingFetch("/api/analytics") }
export function useAlerts() { return usePollingFetch("/api/alerts") }
export function useDailySummary() { return usePollingFetch("/api/summary") }
export function useWallet() { return usePollingFetch("/api/wallet") }
export function useWalletTransactions() { return usePollingFetch("/api/wallet/transactions") }
export function useHealth() { return usePollingFetch("/api/health") }
