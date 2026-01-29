/**
 * SSE stream hook for real-time notification updates.
 *
 * [Task]: T019
 * [From]: spec.md SC-001, contracts/api.yaml §1.5
 * [From]: Context7 /tanstack-query-guide for SSE integration
 *
 * Features:
 * - EventSource connection to /api/notifications/stream
 * - Auto-reconnect on disconnect
 * - Real-time notification updates via TanStack Query cache
 */

"use client"

import { useEffect, useRef, useState } from "react"
import { useQueryClient } from "@tanstack/react-query"
import { isAuthenticated, getCurrentUser } from "@/lib/auth-client"

import { notificationKeys } from "./use-notifications"
import type { Notification } from "@/types/notification"

// =============================================================================
// Configuration
// =============================================================================

const SSE_ENDPOINT = "/api/notifications/stream"
const RECONNECT_DELAY = 3000 // 3 seconds
const MAX_RECONNECT_ATTEMPTS = 5

// =============================================================================
// SSE Stream Hook
// =============================================================================

interface UseNotificationStreamOptions {
  /** Whether to connect to the stream (default: true when authenticated) */
  enabled?: boolean
  /** Callback when a new notification arrives */
  onNotification?: (notification: Notification) => void
  /** Callback on connection errors */
  onError?: (error: Event) => void
}

/**
 * Connect to SSE stream for real-time notification updates.
 *
 * [Task]: T019
 * [From]: spec.md SC-001 - <200ms badge update via SSE
 *
 * Auto-reconnects on disconnect with exponential backoff.
 * Updates TanStack Query cache for instant UI updates.
 *
 * @param options - Stream options
 */
export function useNotificationStream(
  options: UseNotificationStreamOptions = {}
) {
  const { enabled = true, onNotification, onError } = options
  const queryClient = useQueryClient()
  const [authChecked, setAuthChecked] = useState(false)
  const [isAuthenticatedState, setIsAuthenticatedState] = useState(false)
  // Use `any` for EventSource ref to avoid SSR "EventSource is not defined" error
  const eventSourceRef = useRef<any>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const reconnectAttemptsRef = useRef(0)

  // Check authentication status on mount and when localStorage changes
  useEffect(() => {
    // Guard: window is browser-only
    if (typeof window === "undefined") {
      return
    }

    const checkAuth = () => {
      const authStatus = isAuthenticated()
      setIsAuthenticatedState(authStatus)
      setAuthChecked(true)
    }

    // Initial check
    checkAuth()

    // Listen for storage changes (sync across tabs)
    const handleStorageChange = () => {
      checkAuth()
    }

    window.addEventListener("storage", handleStorageChange)
    return () => {
      window.removeEventListener("storage", handleStorageChange)
    }
  }, [])

  // Clean up connection
  const disconnect = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
      eventSourceRef.current = null
    }
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }
  }

  // Connect to SSE stream
  const connect = () => {
    // Don't connect if not authenticated or not enabled
    if (!isAuthenticatedState || !enabled) {
      return
    }

    // Guard: EventSource is browser-only
    if (typeof window === "undefined") {
      return
    }

    // Clean up existing connection
    disconnect()

    try {
      const eventSource = new (window as any).EventSource(SSE_ENDPOINT)
      eventSourceRef.current = eventSource

      // Handle incoming notification events
      eventSource.addEventListener("notification", (event: any) => {
        try {
          const notification = JSON.parse((event as MessageEvent).data) as Notification

          // Update TanStack Query cache for instant UI refresh
          queryClient.setQueryData(
            notificationKeys.list({ limit: 10, offset: 0 }),
            (oldData: unknown) => {
              // Type guard for existing data structure
              if (
                oldData &&
                typeof oldData === "object" &&
                "items" in oldData &&
                Array.isArray(oldData.items)
              ) {
                const data = oldData as {
                  items: unknown[]
                  total?: number
                  unread_count?: number
                }
                return {
                  ...data,
                  items: [notification, ...data.items],
                  total: (data.total ?? 0) + 1,
                  unread_count: (data.unread_count ?? 0) + 1,
                }
              }
              return oldData
            }
          )

          // Also update unread count
          queryClient.setQueryData(
            ["notifications", "unread-count"],
            (oldCount: unknown) => {
              if (typeof oldCount === "number") {
                return oldCount + 1
              }
              return oldCount
            }
          )

          // Call user callback
          onNotification?.(notification)
        } catch (error) {
          console.error("Failed to parse SSE notification:", error)
        }
      })

      // Handle notification marked as read
      eventSource.addEventListener("notification_read", (event: any) => {
        try {
          const { id } = JSON.parse((event as MessageEvent).data)

          // Update cached notification
          queryClient.setQueryData(
            notificationKeys.list({ limit: 10, offset: 0 }),
            (oldData: unknown) => {
              if (
                oldData &&
                typeof oldData === "object" &&
                "items" in oldData &&
                Array.isArray(oldData.items)
              ) {
                const data = oldData as {
                  items: Array<{ id: number; read_status: boolean }>
                  total?: number
                  unread_count?: number
                }
                return {
                  ...data,
                  items: data.items.map((item) =>
                    item.id === id ? { ...item, read_status: true } : item
                  ),
                  unread_count: Math.max(0, (data.unread_count ?? 0) - 1),
                }
              }
              return oldData
            }
          )
        } catch (error) {
          console.error("Failed to parse SSE notification_read event:", error)
        }
      })

      // Handle connection opened
      eventSource.addEventListener("open", () => {
        console.log("SSE connection opened")
        reconnectAttemptsRef.current = 0 // Reset reconnect counter
      })

      // Handle connection errors
      eventSource.addEventListener("error", (error: any) => {
        console.error("SSE connection error:", error)
        onError?.(error)

        // Auto-reconnect with exponential backoff
        if (reconnectAttemptsRef.current < MAX_RECONNECT_ATTEMPTS) {
          reconnectAttemptsRef.current++
          const delay = RECONNECT_DELAY * Math.pow(2, reconnectAttemptsRef.current - 1)

          reconnectTimeoutRef.current = setTimeout(() => {
            connect()
          }, delay)
        } else {
          console.error("Max SSE reconnect attempts reached")
          disconnect()
        }
      })
    } catch (error) {
      console.error("Failed to create SSE connection:", error)
    }
  }

  // Connect on mount and when auth status changes
  useEffect(() => {
    if (isAuthenticatedState && enabled) {
      connect()
    }

    return () => {
      disconnect()
    }
  }, [isAuthenticatedState, enabled])

  // Manual reconnect function
  const reconnect = () => {
    reconnectAttemptsRef.current = 0
    connect()
  }

  return {
    connected: eventSourceRef.current?.readyState === 1, // 1 = EventSource.OPEN
    reconnect,
    disconnect,
  }
}
