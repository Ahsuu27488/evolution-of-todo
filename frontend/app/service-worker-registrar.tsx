/**
 * Service Worker Registrar - Client-only component for SW registration.
 *
 * [Task]: T034
 * [From]: spec.md FR-018
 * [From]: Web Push API documentation
 *
 * This component is dynamically imported with ssr: false to avoid
 * navigator/serviceWorker SSR errors.
 */

"use client"

import { useEffect, useRef } from "react"

/**
 * Service Worker Registrar Component.
 *
 * Registers the service worker for push notification support.
 * Must be client-only to avoid SSR errors with navigator APIs.
 */
export function ServiceWorkerRegistrar() {
  const hasRegistered = useRef(false)

  useEffect(() => {
    // Only register once and only in browser
    if (
      hasRegistered.current ||
      typeof window === "undefined" ||
      !("serviceWorker" in navigator)
    ) {
      return
    }

    hasRegistered.current = true

    // Register service worker
    navigator.serviceWorker
      .register("/sw.js")
      .then((registration) => {
        console.log("[SW] Service worker registered:", registration.scope)

        // Listen for updates
        registration.addEventListener("updatefound", () => {
          const newWorker = registration.installing
          if (newWorker) {
            newWorker.addEventListener("statechange", () => {
              if (newWorker.state === "installed" && navigator.serviceWorker.controller) {
                // New version available
                console.log("[SW] New service worker available, refresh to update")
              }
            })
          }
        })
      })
      .catch((error) => {
        console.error("[SW] Service worker registration failed:", error)
      })

    // Handle messages from service worker
    const handleMessage = (event: MessageEvent) => {
      if (event.data.type === "NAVIGATE_TO_TASK" && event.data.taskId) {
        // Navigate to the task
        window.location.href = `/dashboard?task=${event.data.taskId}`
      }
    }

    navigator.serviceWorker.addEventListener("message", handleMessage)

    return () => {
      navigator.serviceWorker.removeEventListener("message", handleMessage)
    }
  }, [])

  // This component doesn't render anything
  return null
}
