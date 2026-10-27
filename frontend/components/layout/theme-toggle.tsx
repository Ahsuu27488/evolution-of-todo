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
      <div className="flex items-center gap-0.5 p-1 rounded-full bg-muted/70 border border-border">
        {themes.map(({ value, icon: Icon, label }) => {
          const isActive = theme === value
          return (
            <motion.button
              key={value}
              onClick={() => setTheme(value)}
              className={cn(
                "relative h-8 w-8 rounded-full flex items-center justify-center transition-colors duration-200",
                isActive ? "bg-background" : "hover:bg-accent"
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
                    className="absolute inset-0 rounded-full bg-primary/15"
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
      className="h-9 w-9 rounded-full bg-muted/70 border border-border flex items-center justify-center hover:bg-accent transition-colors duration-200"
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      aria-label="Toggle theme"
    >
      <Icon className="h-4 w-4 text-primary" />
    </motion.button>
  )
}
