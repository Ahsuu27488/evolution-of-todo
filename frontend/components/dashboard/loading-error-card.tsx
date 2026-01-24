"use client"

/**
 * LoadingErrorCard Component
 *
 * [T020] Inline error card for loading failures with retry functionality.
 * Displays contextual error message within task list area.
 *
 * Features:
 * - Inline error display (non-blocking)
 * - Clear retry button to re-initiate request
 * - Helpful error messages
 * - Accessible error handling
 *
 * [From]: research.md §Research Area 1: Decision: Inline Error Card for Loading Failures
 * [From]: spec.md FR-006: Display error state with retry option
 */

import { Button } from "@/components/ui/button"
import { AlertCircle, RefreshCw } from "lucide-react"
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
}

/**
 * Loading error card component.
 *
 * Displays inline error message with retry button.
 * Designed to appear within the task list area when data fetch fails.
 *
 * @example
 * ```tsx
 * {isError && (
 *   <LoadingErrorCard
 *     message="Unable to load tasks. Please check your connection."
 *     onRetry={() => refetch()}
 *     isRetrying={isRefetching}
 *   />
 * )}
 * ```
 */
export function LoadingErrorCard({
  message,
  onRetry,
  className,
  isRetrying = false,
}: LoadingErrorCardProps) {
  const handleRetry = async () => {
    await onRetry()
  }

  return (
    <div
      className={cn(
        "loading-error-card",
        "flex flex-col items-center justify-center gap-4",
        "p-8 rounded-lg",
        "glass border border-destructive/30",
        "text-center",
        className
      )}
      role="alert"
      aria-live="assertive"
    >
      {/* Error icon with glow effect */}
      <div className="flex items-center justify-center w-12 h-12 rounded-full bg-destructive/10 glow-destructive">
        <AlertCircle className="w-6 h-6 text-destructive" aria-hidden="true" />
      </div>

      {/* Error message */}
      <div className="space-y-2">
        <h3 className="text-lg font-semibold text-foreground">
          Unable to Load
        </h3>
        <p className="text-sm text-muted-foreground max-w-md">
          {message}
        </p>
      </div>

      {/* Retry button */}
      <Button
        onClick={handleRetry}
        disabled={isRetrying}
        variant="default"
        className="gap-2"
        aria-label="Retry loading tasks"
      >
        <RefreshCw
          className={cn(
            "w-4 h-4",
            isRetrying && "animate-spin"
          )}
          aria-hidden="true"
        />
        {isRetrying ? "Retrying..." : "Retry"}
      </Button>

      {/* Additional help text */}
      <p className="text-xs text-muted-foreground">
        If the problem persists, check your network connection or try again later.
      </p>
    </div>
  )
}
