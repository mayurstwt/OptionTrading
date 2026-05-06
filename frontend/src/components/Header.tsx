"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { Activity, LayoutDashboard, FileCode, BarChart3, Bell, Wallet } from "lucide-react"
import { useHealth } from "@/lib/hooks"

const navigation = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Rules", href: "/rules", icon: FileCode },
  { name: "Analytics", href: "/analytics", icon: BarChart3 },
  { name: "Alerts", href: "/alerts", icon: Bell },
  { name: "Wallet", href: "/wallet", icon: Wallet },
]

export function Header() {
  const pathname = usePathname()
  const { data: health } = useHealth()

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="mx-auto flex h-14 w-full max-w-7xl items-center px-4 sm:px-6 lg:px-8">
        <div className="mr-4 flex">
          <Link href="/" className="mr-6 flex items-center space-x-2">
            <Activity className="h-6 w-6 text-blue-500" />
            <span className="hidden font-bold sm:inline-block">
              OptionTrading Engine
            </span>
          </Link>
          <nav className="flex items-center space-x-6 text-sm font-medium">
            {navigation.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "transition-colors hover:text-foreground/80 flex items-center gap-2",
                  pathname === item.href ? "text-foreground" : "text-foreground/60"
                )}
              >
                <item.icon className="h-4 w-4" />
                {item.name}
              </Link>
            ))}
          </nav>
        </div>
        <div className="flex flex-1 items-center justify-end space-x-4">
          <div className="flex items-center gap-2 text-xs font-medium">
            <span className={cn(
              "h-2 w-2 rounded-full",
              health?.status === "healthy" ? "bg-green-500" : "bg-red-500"
            )} />
            <span className="text-foreground/60 uppercase">
              {health?.status === "healthy" ? "Live" : "Offline"}
            </span>
          </div>
        </div>
      </div>
    </header>
  )
}
