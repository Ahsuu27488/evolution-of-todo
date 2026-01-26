"use client"

/**
 * Ad Blocker Warning Component
 *
 * Displays a one-time toast warning if an ad blocker is detected.
 * Uses session storage to avoid showing the warning on every page load.
 */

import { useEffect } from "react"
import { toast } from "sonner"
import { detectAdBlocker, isChromeBrowser } from "@/lib/utils/adblock-detector"

/**
 * Shows a warning toast if ad blocker is detected
 *
 * Only runs once per session using sessionStorage to avoid annoying users.
 * Only shows on Chrome/Chromium browsers where the issue occurs.
 */
export function AdBlockWarning() {
  useEffect(() => {
    // Only check on Chrome/Chromium browsers
    if (!isChromeBrowser()) {
      return
    }

    // Check if we've already shown the warning this session
    const hasShownWarning = sessionStorage.getItem("adblock-warning-shown")
    if (hasShownWarning) {
      return
    }

    // Small delay to avoid interfering with initial page load
    const timeoutId = setTimeout(() => {
      const hasAdBlocker = detectAdBlocker()

      if (hasAdBlocker) {
        toast.warning("Ad Blocker Detected", {
          description:
            "Dropdown menus may not work with ad blockers enabled. Please whitelist this site or disable the ad blocker.",
          duration: 8000, // Show for 8 seconds
          action: {
            label: "Dismiss",
            onClick: () => {},
          },
          onDismiss: () => {
            // Mark that we've shown the warning this session
            sessionStorage.setItem("adblock-warning-shown", "true")
          },
        })
      } else {
        // No ad blocker detected, mark as checked
        sessionStorage.setItem("adblock-warning-shown", "true")
      }
    }, 2000) // Wait 2 seconds after page load

    return () => clearTimeout(timeoutId)
  }, [])

  // This component doesn't render anything
  return null
}
