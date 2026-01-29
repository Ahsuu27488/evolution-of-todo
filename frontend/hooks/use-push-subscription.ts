/**
 * Push subscription hook for browser push notifications.
 *
 * [Task]: T032
 * [From]: spec.md FR-013-FR-023
 * [From]: Web Push API documentation
 *
 * Features:
 * - Request push permission from browser
 * - Subscribe to push notifications
 * - Unsubscribe from push notifications
 * - Get permission status
 * - Sync subscription with backend
 *
 * [Fix]: Added optimistic updates for instant UI feedback and proper
 * mutation lifecycle handling with rollback on error.
 */

import { useCallback, useEffect, useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

import { api } from "@/lib/api-client"

// =============================================================================
// Types
// =============================================================================

export type PermissionStatus = "granted" | "denied" | "default" | "unsupported"

export interface PushSubscription {
  endpoint: string
  keys: {
    p256dh: string
    auth: string
  }
}

export interface PushStatusResponse {
  status: "subscribed" | "not_subscribed" | "not_requested"
  subscription_count: number
}

// Type for cached query data
type CachedPushStatus = {
  success: boolean
  data: PushStatusResponse
}

// =============================================================================
// Query Keys
// =============================================================================

export const pushKeys = {
  status: ["push", "status"] as const,
}

// =============================================================================
// Helper Functions
// =============================================================================

/**
 * Convert URL-safe base64 string to Uint8Array for Web Push API.
 * VAPID keys need to be in this format for the applicationServerKey parameter.
 */
function urlBase64ToUint8Array(base64String: string): Uint8Array {
  const padding = "=".repeat((4 - (base64String.length % 4)) % 4)
  const base64 = (base64String + padding).replace(/-/g, "+").replace(/_/g, "/")
  const rawData = window.atob(base64)
  const outputArray = new Uint8Array(rawData.length)
  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i)
  }
  return outputArray
}

/**
 * Check if push notifications are supported in this browser
 */
function isPushSupported(): boolean {
  return (
    typeof window !== "undefined" &&
    "serviceWorker" in navigator &&
    "PushManager" in window &&
    "Notification" in window
  )
}

/**
 * Get current permission status from Notification API
 */
function getPermissionStatus(): PermissionStatus {
  if (!isPushSupported()) {
    return "unsupported"
  }

  const status = Notification.permission
  if (status === "granted") return "granted"
  if (status === "denied") return "denied"
  return "default"
}

// =============================================================================
// Push Subscription Hook
// =============================================================================

interface UsePushSubscriptionOptions {
  /** Whether to automatically sync subscription with backend */
  autoSync?: boolean
}

export function usePushSubscription(options: UsePushSubscriptionOptions = {}) {
  const { autoSync = true } = options
  const queryClient = useQueryClient()

  // Initialize with default to avoid hydration mismatch
  // Real value will be set in useEffect after mount
  const [permissionStatus, setPermissionStatus] = useState<PermissionStatus>("default")
  const [isMounted, setIsMounted] = useState(false)
  const [pushSubscription, setPushSubscription] = useState<PushSubscription | null>(null)

  // Set mounted state and get real permission status after client-side mount
  useEffect(() => {
    setIsMounted(true)
    setPermissionStatus(getPermissionStatus())
  }, [])

  // Check push status from backend - only when mounted and supported
  const { data: pushStatusData, isLoading } = useQuery({
    queryKey: pushKeys.status,
    queryFn: async () => {
      return await api.getPushStatus()
    },
    enabled: autoSync && isMounted && isPushSupported(),
  })

  const pushStatus = pushStatusData?.success ? pushStatusData.data : null

  // Refresh permission status
  const refreshPermission = useCallback(() => {
    setPermissionStatus(getPermissionStatus())
  }, [])

  // Listen for permission changes
  useEffect(() => {
    if (!isPushSupported()) return

    const handlePermissionChange = () => {
      refreshPermission()
    }

    // Some browsers support permission change events
    navigator.permissions?.query({ name: "notifications" }).then((permission) => {
      permission.addEventListener("change", handlePermissionChange)
    })

    return () => {
      navigator.permissions?.query({ name: "notifications" }).then((permission) => {
        permission.removeEventListener("change", handlePermissionChange)
      })
    }
  }, [refreshPermission])

  // =============================================================================
  // Mutations with Optimistic Updates
  // =============================================================================

  // Subscribe mutation with optimistic update
  const subscribeMutation = useMutation({
    mutationFn: async (data: { subscription: PushSubscription; device_info: Record<string, string> }) => {
      return await api.subscribePush(data)
    },
    onMutate: async () => {
      // Cancel outgoing refetches to avoid overwriting optimistic update
      await queryClient.cancelQueries({ queryKey: pushKeys.status })

      // Snapshot previous value for rollback
      const previousStatus = queryClient.getQueryData<CachedPushStatus>(pushKeys.status)

      // Optimistically update to "subscribed"
      queryClient.setQueryData<CachedPushStatus>(pushKeys.status, {
        success: true,
        data: { status: "subscribed", subscription_count: 1 }
      })

      // Return context with previous value for rollback
      return { previousStatus }
    },
    onError: (err, variables, context) => {
      // Rollback on error
      if (context?.previousStatus) {
        queryClient.setQueryData(pushKeys.status, context.previousStatus)
      }
    },
    onSettled: () => {
      // Always refetch to ensure sync with server
      queryClient.invalidateQueries({ queryKey: pushKeys.status })
    },
  })

  // Unsubscribe mutation with optimistic update
  const unsubscribeMutation = useMutation({
    mutationFn: async (subscriptionId?: number) => {
      return await api.unsubscribePush(subscriptionId)
    },
    onMutate: async () => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: pushKeys.status })

      // Snapshot previous value
      const previousStatus = queryClient.getQueryData<CachedPushStatus>(pushKeys.status)

      // Optimistically update to "not_subscribed"
      queryClient.setQueryData<CachedPushStatus>(pushKeys.status, {
        success: true,
        data: { status: "not_subscribed", subscription_count: 0 }
      })

      return { previousStatus }
    },
    onError: (err, variables, context) => {
      // Rollback on error
      if (context?.previousStatus) {
        queryClient.setQueryData(pushKeys.status, context.previousStatus)
      }
    },
    onSettled: async () => {
      // Always refetch
      queryClient.invalidateQueries({ queryKey: pushKeys.status })

      // Also unsubscribe from browser (non-blocking)
      try {
        const registration = await navigator.serviceWorker.ready
        const subscription = await registration.pushManager.getSubscription()
        if (subscription) {
          await subscription.unsubscribe()
        }
        setPushSubscription(null)
      } catch {
        // Browser cleanup failure shouldn't affect UI state
        console.warn("Failed to unsubscribe from browser")
      }
    },
  })

  // =============================================================================
  // Internal Functions
  // =============================================================================

  // Request permission
  const requestPermission = useCallback(async (): Promise<boolean> => {
    if (!isPushSupported()) {
      console.warn("Push notifications not supported")
      return false
    }

    const status = await Notification.requestPermission()
    refreshPermission()

    if (status === "granted") {
      // After permission granted, subscribe
      const subscription = await subscribeInternal()
      return !!subscription
    }

    return false
  }, [refreshPermission])

  // Internal subscribe function
  const subscribeInternal = useCallback(async (): Promise<PushSubscription | null> => {
    if (!isPushSupported()) {
      console.warn("Push notifications not supported")
      return null
    }

    try {
      // Get service worker registration
      const registration = await navigator.serviceWorker.ready

      // Convert VAPID key to Uint8Array (required by Web Push API)
      const vapidKey = process.env.NEXT_PUBLIC_VAPID_PUBLIC_KEY || ""
      if (!vapidKey) {
        console.error("VAPID public key not configured")
        return null
      }

      const applicationServerKey = urlBase64ToUint8Array(vapidKey) as BufferSource

      // Subscribe to push
      const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey,
      })

      if (!subscription) {
        console.error("Failed to subscribe to push")
        return null
      }

      const subscriptionJson = subscription.toJSON() as unknown as PushSubscription
      setPushSubscription(subscriptionJson)

      // Sync with backend (mutation handles optimistic update)
      if (autoSync) {
        await subscribeMutation.mutateAsync({
          subscription: subscriptionJson,
          device_info: {
            user_agent: navigator.userAgent,
            platform: navigator.platform,
          },
        })
      }
      // Note: No manual invalidateQueries here - mutation's onSettled handles it

      return subscriptionJson
    } catch (error) {
      console.error("Error subscribing to push:", error)
      return null
    }
  }, [autoSync, subscribeMutation])

  // =============================================================================
  // Public API
  // =============================================================================

  const subscribe = useCallback(async () => {
    if (permissionStatus === "granted") {
      return await subscribeInternal()
    } else if (permissionStatus === "default") {
      const granted = await requestPermission()
      if (granted) {
        return await subscribeInternal()
      }
    }
    return null
  }, [permissionStatus, requestPermission, subscribeInternal])

  const unsubscribe = useCallback(async () => {
    await unsubscribeMutation.mutateAsync(undefined)
  }, [unsubscribeMutation])

  return {
    // Status
    permissionStatus,
    pushStatus: pushStatus?.status ?? "not_requested",
    isSupported: isMounted && isPushSupported(),
    isSubscribed: pushStatus?.status === "subscribed",
    isLoading,

    // Actions
    requestPermission,
    subscribe,
    unsubscribe,
    refreshPermission,
  }
}
