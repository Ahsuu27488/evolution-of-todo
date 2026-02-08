/**
 * Responsive breakpoint utilities for chat panel UI.
 *
 * Provides useResponsive hook for detecting screen size and applying
 * appropriate layout variants (mobile/tablet/desktop).
 *
 * Per plan.md Phase 1 Design & Contracts - Responsive Breakpoint Helper
 */

"use client"

import { useEffect, useState } from "react"

// =============================================================================
// Types
// =============================================================================

export type Breakpoint = "mobile" | "tablet" | "desktop"

export interface ResponsiveState {
  breakpoint: Breakpoint
  isMobile: boolean
  isTablet: boolean
  isDesktop: boolean
  width: number
}

// =============================================================================
// Constants
// =============================================================================

export const BREAKPOINTS = {
  mobile: 0,      // < 640px
  tablet: 640,    // 640px - 1024px
  desktop: 1024,  // >= 1024px
} as const

// Debounce delay for resize events (prevents animation jank)
const RESIZE_DEBOUNCE_MS = 150

// =============================================================================
// Hook
// =============================================================================

/**
 * Hook for responsive breakpoint detection.
 *
 * Uses debounced resize listener to prevent excessive re-renders and
 * animation jank during rapid window resizing.
 *
 * @returns ResponsiveState with current breakpoint and boolean flags
 *
 * @example
 * ```tsx
 * const { breakpoint, isMobile, isDesktop } = useResponsive()
 *
 * return (
 *   <motion.div
 *     variants={responsiveVariants}
 *     initial={breakpoint}
 *     animate={breakpoint}
 *   />
 * )
 * ```
 */
export function useResponsive(): ResponsiveState {
  const [state, setState] = useState<ResponsiveState>(() =>
    getResponsiveState(typeof window !== "undefined" ? window.innerWidth : 1024)
  )

  useEffect(() => {
    if (typeof window === "undefined") return

    let timeoutId: ReturnType<typeof setTimeout>

    const handleResize = () => {
      // Clear existing timeout to debounce rapid resize events
      clearTimeout(timeoutId)

      // Schedule state update after debounce delay
      timeoutId = setTimeout(() => {
        setState(getResponsiveState(window.innerWidth))
      }, RESIZE_DEBOUNCE_MS)
    }

    // Add resize listener
    window.addEventListener("resize", handleResize, { passive: true })

    // Cleanup on unmount
    return () => {
      clearTimeout(timeoutId)
      window.removeEventListener("resize", handleResize)
    }
  }, [])

  return state
}

// =============================================================================
// Utilities
// =============================================================================

/**
 * Get responsive state from window width.
 *
 * @param width - Current window width in pixels
 * @returns ResponsiveState with breakpoint and flags
 */
function getResponsiveState(width: number): ResponsiveState {
  let breakpoint: Breakpoint

  if (width < BREAKPOINTS.tablet) {
    breakpoint = "mobile"
  } else if (width < BREAKPOINTS.desktop) {
    breakpoint = "tablet"
  } else {
    breakpoint = "desktop"
  }

  return {
    breakpoint,
    isMobile: breakpoint === "mobile",
    isTablet: breakpoint === "tablet",
    isDesktop: breakpoint === "desktop",
    width,
  }
}

/**
 * Check if viewport matches a specific breakpoint.
 *
 * @param breakpoint - Breakpoint to check
 * @param currentBreakpoint - Current breakpoint from useResponsive
 * @returns true if current breakpoint matches
 */
export function isBreakpoint(
  breakpoint: Breakpoint,
  currentBreakpoint: Breakpoint
): boolean {
  return breakpoint === currentBreakpoint
}

/**
 * Check if viewport is at least the given breakpoint size.
 *
 * @param minBreakpoint - Minimum breakpoint required
 * @param currentBreakpoint - Current breakpoint from useResponsive
 * @returns true if current breakpoint is at least minBreakpoint
 */
export function isAtLeast(
  minBreakpoint: Breakpoint,
  currentBreakpoint: Breakpoint
): boolean {
  const order: Breakpoint[] = ["mobile", "tablet", "desktop"]
  const currentIndex = order.indexOf(currentBreakpoint)
  const minIndex = order.indexOf(minBreakpoint)
  return currentIndex >= minIndex
}

/**
 * Check if viewport is at most the given breakpoint size.
 *
 * @param maxBreakpoint - Maximum breakpoint allowed
 * @param currentBreakpoint - Current breakpoint from useResponsive
 * @returns true if current breakpoint is at most maxBreakpoint
 */
export function isAtMost(
  maxBreakpoint: Breakpoint,
  currentBreakpoint: Breakpoint
): boolean {
  const order: Breakpoint[] = ["mobile", "tablet", "desktop"]
  const currentIndex = order.indexOf(currentBreakpoint)
  const maxIndex = order.indexOf(maxBreakpoint)
  return currentIndex <= maxIndex
}
