"use client"

/**
 * DualRingSpinner Component
 *
 * [T017] Creative loading animation with dual rotating rings.
 * Uses pure CSS animations for optimal performance.
 *
 * Features:
 * - Outer ring: Neon cyan (clockwise rotation)
 * - Inner ring: Neon purple (counter-clockwise rotation)
 * - Minimum display duration to prevent flash
 * - Smooth fade-out transition
 *
 * [From]: research.md §Research Area 1: Loading Animation Implementation
 * [From]: spec.md FR-001: Display a themed loading animation
 */

import { useEffect, useState } from "react"
import { cn } from "@/lib/utils"

interface DualRingSpinnerProps {
  /** Optional CSS class name for styling overrides */
  className?: string
  /** Minimum display duration in milliseconds to prevent flash (default: 400ms) */
  minDisplayDuration?: number
  /** Show/hide the spinner */
  show?: boolean
}

/**
 * Dual-ring loading spinner component.
 *
 * Performance targets (SC-001, SC-002):
 * - Visible within 100ms of data fetch
 * - Fades out within 300ms of data arrival
 * - Minimum 400ms display duration (FR-005)
 *
 * @example
 * ```tsx
 * <DualRingSpinner show={isLoading} />
 * ```
 */
export function DualRingSpinner({
  className,
  minDisplayDuration = 400,
  show = true,
}: DualRingSpinnerProps) {
  // [T019] Minimum display duration logic to prevent flash
  const [shouldShow, setShouldShow] = useState(false)
  const [isFadingOut, setIsFadingOut] = useState(false)

  useEffect(() => {
    if (!show) {
      // Start fade out
      setIsFadingOut(true)
      const fadeTimer = setTimeout(() => {
        setShouldShow(false)
        setIsFadingOut(false)
      }, 300) // 300ms fade-out transition (SC-002)
      return () => clearTimeout(fadeTimer)
    }

    // Show spinner immediately (within 100ms target per SC-001)
    const showTimer = setTimeout(() => {
      setShouldShow(true)
      setIsFadingOut(false)
    }, 100)

    return () => clearTimeout(showTimer)
  }, [show, minDisplayDuration])

  if (!shouldShow && !isFadingOut) {
    return null
  }

  return (
    <div
      className={cn(
        "dual-ring-spinner",
        isFadingOut && "fade-out",
        className
      )}
      role="status"
      aria-label="Loading"
      aria-live="polite"
    >
      <div className="outer-ring" aria-hidden="true" />
      <div className="inner-ring" aria-hidden="true" />
      <span className="sr-only">Loading...</span>
    </div>
  )
}
