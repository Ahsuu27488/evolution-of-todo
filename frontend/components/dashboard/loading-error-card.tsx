"use client"

/**
 * LoadingErrorCard: inline error for a failed fetch, shown in place of the content it replaces,
 * with a retry button. Solid surface, destructive tone on the icon only.
 */

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { CloudOff, RefreshCw } from "lucide-react"
import { cn } from "@/lib/utils"

interface LoadingErrorCardProps {
  /** Error message to display */
  message: string
  /** Callback function when retry button is clicked */
  onRetry: () => void | Promise<void>
  /** Optional additional CSS class name */
  className?: string
  /** Whether retry action is in progress */
  isRetrying?: boolean
  /** Heading above the message */
  title?: string
}

export function LoadingErrorCard({
  message,
  onRetry,
  className,
  isRetrying = false,
  title = "Couldn't load your tasks",
}: LoadingErrorCardProps) {
  // Busy while the parent says so, or while the retry promise is pending
  const [pending, setPending] = useState(false)
  const busy = isRetrying || pending

  const handleRetry = async () => {
    setPending(true)
    try {
      await onRetry()
    } finally {
      setPending(false)
    }
  }

  return (
    <div
      className={cn(
        "surface flex flex-col items-center gap-4 rounded-[var(--radius-2xl)] px-6 py-12 text-center",
        className
      )}
      role="alert"
    >
      <div className="grid size-12 place-items-center rounded-full bg-destructive/12 text-destructive">
        <CloudOff className="size-5" aria-hidden />
      </div>

      <div className="space-y-1.5">
        <h2 className="font-display text-lg font-semibold">{title}</h2>
        <p className="max-w-sm text-sm text-muted-foreground">{message}</p>
      </div>

      <Button
        onClick={handleRetry}
        disabled={busy}
        aria-busy={busy}
        variant="outline"
        className="rounded-full"
      >
        <RefreshCw className={cn(busy && "animate-spin")} aria-hidden />
        {busy ? "Trying again" : "Try again"}
      </Button>
    </div>
  )
}
