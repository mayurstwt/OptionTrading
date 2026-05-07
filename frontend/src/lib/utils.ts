import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"
import { format } from "date-fns"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatCurrency(value: number) {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 2
  }).format(value)
}

export function formatPercent(value: number) {
  return `${value.toFixed(2)}%`
}

export function formatDateTime(dateStr: string | Date) {
  return format(new Date(dateStr), "MMM dd, HH:mm:ss")
}
