/**
 * Notification Empty State component.
 *
 * [Task]: T023
 * [From]: Deep Space theme styling
 *
 * Features:
 * - Friendly empty state illustration
 * - Glassmorphism styling
 * - Consistent with app design
 */

"use client"

import { BellOff } from "lucide-react"

export function NotificationEmptyState() {
  return (
    <div className="flex flex-col items-center justify-center py-8 px-4 text-center">
      <div className="relative">
        {/* Bell icon with muted appearance */}
        <div className="w-12 h-12 rounded-full bg-muted/30 flex items-center justify-center">
          <BellOff className="h-6 w-6 text-muted-foreground/50" />
        </div>

        {/* Subtle glow effect */}
        <div className="absolute inset-0 w-12 h-12 rounded-full bg-primary/5 blur-xl" />
      </div>

      <p className="mt-4 text-sm font-medium text-foreground">
        No notifications yet
      </p>

      <p className="mt-1 text-xs text-muted-foreground/60">
        You&apos;re all caught up!
      </p>
    </div>
  )
}
