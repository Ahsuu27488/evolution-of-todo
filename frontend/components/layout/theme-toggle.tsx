"use client"

import { useEffect, useState } from "react"
import { motion } from "framer-motion"
import { Moon, Sun, Monitor } from "lucide-react"
import { useTheme } from "next-themes"
import { cn } from "@/lib/utils"

const themes = [
  { value: "light", icon: Sun, label: "Light" },
  { value: "dark", icon: Moon, label: "Dark" },
  { value: "system", icon: Monitor, label: "System" },
] as const

/** Light / dark / system as a three-way switch (radio group); the active pill slides between them */
export function ThemeToggle() {
  const { theme, setTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  // Prevent hydration mismatch
  useEffect(() => setMounted(true), [])

  if (!mounted) {
    return <div className="h-10 w-[7.25rem] rounded-full bg-muted/60" aria-hidden />
  }

  return (
    <div
      role="radiogroup"
      aria-label="Theme"
      className="flex h-10 items-center gap-0.5 rounded-full border border-border bg-muted/60 p-0.5"
    >
      {themes.map(({ value, icon: Icon, label }) => {
        const isActive = theme === value
        return (
          <button
            key={value}
            type="button"
            role="radio"
            aria-checked={isActive}
            aria-label={label}
            title={label}
            onClick={() => setTheme(value)}
            className={cn(
              "relative grid size-9 place-items-center rounded-full outline-none transition-colors duration-150",
              "focus-visible:ring-[3px] focus-visible:ring-ring/50 active:scale-95",
              isActive ? "text-foreground" : "text-muted-foreground hover:text-foreground"
            )}
          >
            {isActive && (
              <motion.span
                layoutId="theme-toggle-active"
                className="absolute inset-0 rounded-full bg-card shadow-[0_1px_2px_oklch(0.1_0.03_265/0.3)] ring-1 ring-border"
                transition={{ type: "spring", stiffness: 500, damping: 38 }}
              />
            )}
            <Icon className={cn("relative size-4", isActive && value !== "system" && "text-primary")} aria-hidden />
          </button>
        )
      })}
    </div>
  )
}

/** Compact theme toggle for phones: one button that cycles light, dark, system */
export function ThemeToggleCompact() {
  const { theme, setTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  useEffect(() => setMounted(true), [])

  if (!mounted) {
    return <div className="size-10 rounded-full bg-muted/60" aria-hidden />
  }

  const order = ["light", "dark", "system"] as const
  const current = themes.find((t) => t.value === theme) ?? themes[2]
  const next = order[(order.indexOf(current.value) + 1) % order.length]
  const Icon = current.icon

  return (
    <button
      type="button"
      onClick={() => setTheme(next)}
      className="grid size-10 place-items-center rounded-full text-foreground/80 outline-none transition-colors hover:bg-accent hover:text-foreground focus-visible:ring-[3px] focus-visible:ring-ring/50 active:scale-95"
      aria-label={`Theme: ${current.label}. Switch to ${next}`}
    >
      <Icon className="size-[18px]" aria-hidden />
    </button>
  )
}
