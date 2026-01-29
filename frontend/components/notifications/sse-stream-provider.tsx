/**
 * SSE Stream Provider - Client-only component for real-time notifications.
 *
 * [Task]: T019
 * [From]: spec.md SC-001, contracts/api.yaml §1.5
 * [From]: Context7 /tanstack-query-guide for SSE integration
 *
 * This component is dynamically imported with ssr: false to avoid
 * EventSource SSR errors. It manages the SSE connection and updates
 * TanStack Query cache for real-time UI updates.
 */

"use client"

import { useEffect } from "react"
import { useQueryClient } from "@tanstack/react-query"

import { notificationKeys } from "@/hooks/use-notifications"
import type { Notification } from "@/types/notification"
import { isAuthenticated } from "@/lib/auth-client"

// =============================================================================
// Configuration
// =============================================================================

const SSE_ENDPOINT = "/api/notifications/stream"
const RECONNECT_DELAY = 3000 // 3 seconds
const MAX_RECONNECT_ATTEMPTS = 5

// =============================================================================
// SSE Stream Provider Component
// =============================================================================

interface SSEStreamProviderProps {
  /** Callback when a new notification arrives */
  onNotification?: (notification: Notification) => void
  /** Callback on connection errors */
  onError?: (error: Event) => void
}

/**
 * SSE Stream Provider - Manages real-time notification updates.
 *
 * [Task]: T019
 * [From]: spec.md SC-001 - <200ms badge update via SSE
 *
 * This component MUST be imported with { ssr: false } to prevent
 * EventSource SSR errors. It connects to the SSE stream and updates
 * the TanStack Query cache for instant UI updates.
 */
export function SSEStreamProvider({
  onNotification,
  onError,
}: SSEStreamProviderProps) {
  const queryClient = useQueryClient()

  useEffect(() => {
    // EventSource is browser-only
    if (typeof window === "undefined") {
      return
    }

    // Check if user is authenticated
    if (!isAuthenticated()) {
      return
    }

    let eventSource: EventSource | null = null
    let reconnectTimeout: NodeJS.Timeout | null = null
    let reconnectAttempts = 0

    // Clean up connection
    const disconnect = () => {
      if (eventSource) {
        eventSource.close()
        eventSource = null
      }
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout)
        reconnectTimeout = null
      }
    }

    // Connect to SSE stream
    const connect = () => {
      disconnect()

      try {
        eventSource = new EventSource(SSE_ENDPOINT)

        // Handle incoming notification events
        eventSource.addEventListener("notification", (event: Event) => {
          try {
            const notification = JSON.parse((event as MessageEvent).data) as Notification

            // Update TanStack Query cache for instant UI refresh
            const listKey = notificationKeys.list({ limit: 10, offset: 0 })
            queryClient.setQueryData(listKey, (oldData: unknown) => {
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
            })

            // Also update unread count
            queryClient.setQueryData(["notifications", "unread-count"], (oldCount: unknown) => {
              if (typeof oldCount === "number") {
                return oldCount + 1
              }
              return oldCount
            })

            // Call user callback
            onNotification?.(notification)
          } catch (error) {
            console.error("Failed to parse SSE notification:", error)
          }
        })

        // Handle notification marked as read
        eventSource.addEventListener("notification_read", (event: Event) => {
          try {
            const { id } = JSON.parse((event as MessageEvent).data)

            // Update cached notification
            const listKey = notificationKeys.list({ limit: 10, offset: 0 })
            queryClient.setQueryData(listKey, (oldData: unknown) => {
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
            })
          } catch (error) {
            console.error("Failed to parse SSE notification_read event:", error)
          }
        })

        // Handle connection opened
        eventSource.addEventListener("open", () => {
          console.log("[SSE] Connection opened")
          reconnectAttempts = 0 // Reset reconnect counter
        })

        // Handle connection errors
        eventSource.addEventListener("error", (error: Event) => {
          console.error("[SSE] Connection error:", error)
          onError?.(error)

          // Auto-reconnect with exponential backoff
          if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
            reconnectAttempts++
            const delay = RECONNECT_DELAY * Math.pow(2, reconnectAttempts - 1)

            reconnectTimeout = setTimeout(() => {
              connect()
            }, delay)
          } else {
            console.error("[SSE] Max reconnect attempts reached")
            disconnect()
          }
        })
      } catch (error) {
        console.error("[SSE] Failed to create connection:", error)
      }
    }

    // Connect on mount
    connect()

    // Clean up on unmount
    return () => {
      disconnect()
    }
  }, [queryClient, onNotification, onError])

  // This component doesn't render anything - it just manages the SSE connection
  return null
}
