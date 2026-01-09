"use client"

import { useEffect, useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Moon, Sun, Monitor } from "lucide-react"
import { useTheme } from "next-themes"
import { cn } from "@/lib/utils"

export function ThemeToggle() {
  const { theme, setTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  // Prevent hydration mismatch
  useEffect(() => setMounted(true), [])

  if (!mounted) {
    return (
      <div className="h-9 w-9 rounded-lg bg-muted/50 animate-pulse" />
    )
  }

  const themes = [
    { value: "light", icon: Sun, label: "Light" },
    { value: "dark", icon: Moon, label: "Dark" },
    { value: "system", icon: Monitor, label: "System" },
  ] as const

  return (
    <div className="relative">
      {/* Dropdown menu */}
      <div className="flex items-center gap-1 p-1 rounded-xl glass border-primary/20">
        {themes.map(({ value, icon: Icon, label }) => {
          const isActive = theme === value
          return (
            <motion.button
              key={value}
              onClick={() => setTheme(value)}
              className={cn(
                "relative h-7 w-7 rounded-lg flex items-center justify-center transition-all duration-300",
                isActive
                  ? "bg-primary/20 shadow-[0_0_15px_rgba(0,245,255,0.3)]"
                  : "hover:bg-muted/50"
              )}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              aria-label={label}
            >
              {/* Active glow effect */}
              <AnimatePresence>
                {isActive && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.5 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.5 }}
                    className="absolute inset-0 rounded-lg bg-primary/10"
                    transition={{ duration: 0.15 }}
                  />
                )}
              </AnimatePresence>

              <Icon
                className={cn(
                  "h-3.5 w-3.5 transition-colors duration-300 relative z-10",
                  isActive
                    ? "text-primary"
                    : "text-muted-foreground"
                )}
              />
            </motion.button>
          )
        })}
      </div>

      {/* Tooltip */}
      <div className="sr-only group-hover:not-sr-only">
        Theme: {theme}
      </div>
    </div>
  )
}

/** Compact theme toggle for mobile */
export function ThemeToggleCompact() {
  const { theme, setTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  useEffect(() => setMounted(true), [])

  if (!mounted) {
    return (
      <div className="h-9 w-9 rounded-lg bg-muted/50 animate-pulse" />
    )
  }

  const cycleTheme = () => {
    if (theme === "light") setTheme("dark")
    else if (theme === "dark") setTheme("system")
    else setTheme("light")
  }

  const getIcon = () => {
    switch (theme) {
      case "light":
        return Sun
      case "dark":
        return Moon
      default:
        return Monitor
    }
  }

  const Icon = getIcon()

  return (
    <motion.button
      onClick={cycleTheme}
      className="h-9 w-9 rounded-lg glass border-primary/20 flex items-center justify-center hover:bg-primary/10 hover:border-primary/40 transition-all duration-300"
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      aria-label="Toggle theme"
    >
      <Icon className="h-4 w-4 text-primary" />
    </motion.button>
  )
}
