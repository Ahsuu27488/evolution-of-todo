/**
 * SSE Stream Provider - Client-only component for real-time notifications.
 *
 * [Task]: T019
 * [From]: spec.md SC-001, contracts/api.yaml §1.5
 *
 * The backend stream (`GET {API_URL}/api/notifications/stream`) requires a
 * Bearer token, which the browser's EventSource cannot send, so this reads the
 * stream with fetch() and parses it with parseSSEStream(). Events update the
 * TanStack Query cache for instant UI updates.
 */

"use client"

import { useEffect } from "react"
import { useQueryClient } from "@tanstack/react-query"

import { notificationKeys } from "@/hooks/use-notifications"
import type { Notification } from "@/types/notification"
import { API_URL } from "@/lib/config/api"
import { getAuthToken } from "@/lib/auth/token"
import { parseSSEStream } from "@/lib/utils/sse"

// =============================================================================
// Configuration
// =============================================================================

const SSE_ENDPOINT = `${API_URL}/api/notifications/stream`
const RECONNECT_DELAY = 3000 // 3 seconds
const MAX_RECONNECT_ATTEMPTS = 5

// =============================================================================
// SSE Stream Provider Component
// =============================================================================

interface SSEStreamProviderProps {
  /** Callback when a new notification arrives */
  onNotification?: (notification: Notification) => void
  /** Callback on connection errors */
  onError?: (error: unknown) => void
}

export function SSEStreamProvider({
  onNotification,
  onError,
}: SSEStreamProviderProps) {
  const queryClient = useQueryClient()

  useEffect(() => {
    let controller: AbortController | null = null
    let reconnectTimeout: ReturnType<typeof setTimeout> | null = null
    let reconnectAttempts = 0
    let stopped = false

    const listKey = notificationKeys.list({ limit: 10, offset: 0 })

    const handleNotification = (notification: Notification) => {
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

      queryClient.setQueryData(["notifications", "unread-count"], (oldCount: unknown) =>
        typeof oldCount === "number" ? oldCount + 1 : oldCount
      )

      onNotification?.(notification)
    }

    const handleRead = (id: number) => {
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
    }

    const scheduleReconnect = () => {
      if (stopped) return
      if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
        console.error("[SSE] Max reconnect attempts reached")
        return
      }
      reconnectAttempts++
      const delay = RECONNECT_DELAY * Math.pow(2, reconnectAttempts - 1)
      reconnectTimeout = setTimeout(connect, delay)
    }

    async function connect() {
      const token = await getAuthToken()
      // Not signed in: nothing to stream.
      if (!token || stopped) return

      controller = new AbortController()
      try {
        const response = await fetch(SSE_ENDPOINT, {
          headers: { Authorization: `Bearer ${token}`, Accept: "text/event-stream" },
          signal: controller.signal,
          cache: "no-store",
        })
        if (!response.ok || !response.body) {
          throw new Error(`SSE stream failed: HTTP ${response.status}`)
        }

        reconnectAttempts = 0
        const reader = response.body.getReader()
        for await (const { eventType, data } of parseSSEStream(reader)) {
          if (eventType === "notification") {
            handleNotification(data as Notification)
          } else if (eventType === "notification_read") {
            handleRead((data as { id: number }).id)
          }
        }
        // Server closed the stream: reconnect.
        scheduleReconnect()
      } catch (error) {
        if (stopped || (error instanceof Error && error.name === "AbortError")) return
        console.error("[SSE] Connection error:", error)
        onError?.(error)
        scheduleReconnect()
      }
    }

    connect()

    return () => {
      stopped = true
      controller?.abort()
      if (reconnectTimeout) clearTimeout(reconnectTimeout)
    }
  }, [queryClient, onNotification, onError])

  // This component doesn't render anything - it just manages the SSE connection
  return null
}
