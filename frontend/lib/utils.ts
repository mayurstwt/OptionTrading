import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"
import { format } from "date-fns"

// Used by shadcn/ui and your components for merging tailwind classes safely
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// Formats numbers into INR currency strings
export function formatCurrency(value: number) {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 2
  }).format(value)
}

// Formats numbers into percentage strings
export function formatPercent(value: number) {
  return `${value.toFixed(2)}%`
}

// Standardizes date-time formatting across the app
export function formatDateTime(dateStr: string | Date) {
  return format(new Date(dateStr), "MMM dd, yyyy HH:mm:ss")
}
