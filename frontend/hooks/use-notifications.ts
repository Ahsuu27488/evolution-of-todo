/**
 * TanStack Query hooks for notification operations.
 *
 * [Task]: T018
 * [From]: spec.md FR-001, FR-005, FR-008, FR-009
 * [From]: Context7 /tanstack-query-guide for useQuery, useMutation patterns
 */

"use client"

import {
  useMutation,
  useQuery,
  useQueryClient,
  type UseQueryResult,
} from "@tanstack/react-query"

import { api } from "@/lib/api-client"
import type {
  Notification,
  NotificationList,
  NotificationSettings,
  NotificationType,
} from "@/types/notification"

// =============================================================================
// Query Keys
// =============================================================================

export const notificationKeys = {
  all: ["notifications"] as const,
  lists: () => [...notificationKeys.all, "list"] as const,
  list: (filters: { limit?: number; offset?: number; unread_only?: boolean }) =>
    [...notificationKeys.lists(), filters] as const,
  settings: () => ["notification-settings"] as const,
}

// =============================================================================
// Hooks - Notifications
// =============================================================================

/**
 * Fetch notifications for the current user.
 *
 * [Task]: T018
 * [From]: spec.md FR-001, FR-009, contracts/api.yaml §1.1
 *
 * @param filters - Optional filters (limit, offset, unread_only)
 * @returns Query result with NotificationList
 */
export function useNotifications(
  filters: { limit?: number; offset?: number; unread_only?: boolean } = {},
): UseQueryResult<NotificationList> {
  return useQuery({
    queryKey: notificationKeys.list(filters),
    queryFn: async (): Promise<NotificationList> => {
      const result = await api.getNotifications(filters)
      if (!result.success) {
        throw result.error
      }
      // Cast the response to match our types - the backend returns valid enum values
      return result.data as NotificationList
    },
    // Refetch every 60 seconds - SSE provides real-time updates
    refetchInterval: 60000,
    // Don't refetch on window focus (SSE handles real-time)
    refetchOnWindowFocus: false,
  })
}

/**
 * Fetch unread notification count.
 *
 * [From]: spec.md SC-005 - Badge update <200ms
 *
 * Note: SSE provides real-time updates. This is a fallback.
 *
 * @returns Query result with unread count
 */
export function useUnreadCount(): UseQueryResult<number> {
  return useQuery({
    queryKey: ["notifications", "unread-count"],
    queryFn: async () => {
      const result = await api.getNotifications({ limit: 1 })
      if (!result.success) {
        throw result.error
      }
      return result.data.unread_count
    },
    // Refetch every 30 seconds - SSE provides real-time updates
    refetchInterval: 30000,
    // Don't refetch on window focus
    refetchOnWindowFocus: false,
  })
}

/**
 * Mark a notification as read.
 *
 * [Task]: T018
 * [From]: spec.md FR-005, contracts/api.yaml §1.2
 *
 * @returns Mutation function
 */
export function useMarkAsRead() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (notificationId: number) => {
      const result = await api.markNotificationAsRead(notificationId)
      if (!result.success) {
        throw result.error
      }
      return result.data
    },
    onSuccess: () => {
      // Invalidate notifications list to refresh data
      queryClient.invalidateQueries({ queryKey: notificationKeys.lists() })
    },
  })
}

/**
 * Mark all notifications as read.
 *
 * [Task]: T018
 * [From]: spec.md FR-008, contracts/api.yaml §1.3
 *
 * @returns Mutation function
 */
export function useMarkAllAsRead() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async () => {
      const result = await api.markAllNotificationsAsRead()
      if (!result.success) {
        throw result.error
      }
      return result.data
    },
    onSuccess: () => {
      // Invalidate notifications list to refresh data
      queryClient.invalidateQueries({ queryKey: notificationKeys.lists() })
    },
  })
}

/**
 * Delete a notification.
 *
 * [Task]: T018
 * [From]: spec.md FR-006, contracts/api.yaml §1.4
 *
 * @returns Mutation function
 */
export function useDeleteNotification() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (notificationId: number) => {
      const result = await api.deleteNotification(notificationId)
      if (!result.success) {
        throw result.error
      }
      return result.data
    },
    onSuccess: () => {
      // Invalidate notifications list to refresh data
      queryClient.invalidateQueries({ queryKey: notificationKeys.lists() })
    },
  })
}

// =============================================================================
// Hooks - Settings
// =============================================================================

/**
 * Fetch notification settings.
 *
 * [From]: spec.md FR-033, contracts/api.yaml §4.1
 *
 * @returns Query result with NotificationSettings
 */
export function useNotificationSettings(): UseQueryResult<NotificationSettings> {
  return useQuery({
    queryKey: notificationKeys.settings(),
    queryFn: async (): Promise<NotificationSettings> => {
      const result = await api.getNotificationSettings()
      if (!result.success) {
        throw result.error
      }
      // Cast the response to match our types - the backend returns valid data
      return result.data as unknown as NotificationSettings
    },
    staleTime: 300000, // 5 minutes
  })
}

/**
 * Update notification settings.
 *
 * [From]: spec.md FR-033, contracts/api.yaml §4.2
 *
 * @returns Mutation function
 */
export function useUpdateSettings() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (settings: Partial<NotificationSettings>) => {
      const result = await api.updateNotificationSettings(settings)
      if (!result.success) {
        throw result.error
      }
      return result.data as unknown as NotificationSettings
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: notificationKeys.settings() })
    },
  })
}

// =============================================================================
// Hooks - Email Preferences
// =============================================================================

/**
 * Query keys for email preferences.
 */
export const emailPreferencesKeys = {
  all: ["email-preferences"] as const,
  details: () => [...emailPreferencesKeys.all, "detail"] as const,
}

/**
 * Fetch email notification preferences.
 *
 * [Task]: T047
 * [From]: spec.md FR-026, FR-033, contracts/api.yaml §3.1
 *
 * @returns Query result with email preferences
 */
export function useEmailPreferences(): UseQueryResult<{
  preferences: Array<{
    notification_type: string
    enabled: boolean
    frequency: "immediate" | "daily" | "weekly" | "none"
  }>
  email_address: string | null
  bounced: boolean
}> {
  return useQuery({
    queryKey: emailPreferencesKeys.details(),
    queryFn: async () => {
      const result = await api.getEmailPreferences()
      if (!result.success) {
        throw result.error
      }
      return result.data
    },
    staleTime: 300000, // 5 minutes
  })
}

/**
 * Update email notification preferences.
 *
 * [Task]: T047
 * [From]: spec.md FR-026, contracts/api.yaml §3.2
 *
 * @returns Mutation function
 */
export function useUpdateEmailPreferences() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (preferences: Array<{
      notification_type: string
      enabled: boolean
      frequency: "immediate" | "daily" | "weekly" | "none"
    }>) => {
      const result = await api.updateEmailPreferences(preferences)
      if (!result.success) {
        throw result.error
      }
      return result.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: emailPreferencesKeys.all })
    },
  })
}
