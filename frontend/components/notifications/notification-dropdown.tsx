/**
 * Notification Dropdown component with glassmorphism styling.
 *
 * [Task]: T022
 * [From]: spec.md FR-002, FR-003, FR-007, FR-011
 * [From]: Context7 /radix-ui/website for DropdownMenu patterns
 *
 * Features:
 * - Glassmorphism backdrop blur
 * - Cyan glow for unread notifications
 * - Relative timestamps
 * - "Mark all as read" button
 * - Scrollable with virtualization support
 * - Framer Motion slideInBottom animation
 */

"use client"

import { useEffect, useRef, useState } from "react"
import * as DropdownMenu from "@radix-ui/react-dropdown-menu"
import {
  Check,
  CheckCheck,
  Clock,
  Info,
  AlertCircle,
  Sparkles,
  Bell,
} from "lucide-react"
import { AnimatePresence } from "framer-motion"

import { useMarkAsRead, useMarkAllAsRead, useNotifications, useUnreadCount } from "@/hooks/use-notifications"
import type { Notification } from "@/types/notification"
import { NotificationType } from "@/types/notification"
import { NotificationItem } from "./notification-item"
import { NotificationEmptyState } from "./notification-empty-state"
import { cn } from "@/lib/utils"

// =============================================================================
// Props
// =============================================================================

export interface NotificationDropdownProps {
  /** Callback when user wants to open push settings */
  onOpenPushSettings?: () => void
}

// =============================================================================
// Notification Dropdown Component
// =============================================================================

export function NotificationDropdown({ onOpenPushSettings }: NotificationDropdownProps) {
  const [isLoading, setIsLoading] = useState(true)
  const [offset, setOffset] = useState(0)
  const limit = 10
  const scrollRef = useRef<HTMLDivElement>(null)

  const { data } = useNotifications({ limit, offset })
  const { data: unreadData } = useUnreadCount()
  const markAsRead = useMarkAsRead()
  const markAllAsRead = useMarkAllAsRead()

  const unreadCount = unreadData ?? 0
  const hasMore = data ? data.total > offset + limit : false
  const allItems = data?.items ?? []
  const total = data?.total ?? 0

  // Update loading state when data changes
  useEffect(() => {
    if (data?.items) {
      setIsLoading(false)
    }
  }, [data])

  // Handle notification click - mark as read
  const handleNotificationClick = async (notification: Notification) => {
    if (!notification.read_status) {
      await markAsRead.mutateAsync(notification.id)
    }

    // Navigate to related task if available
    if (notification.related_task_id) {
      window.location.href = `/dashboard?task=${notification.related_task_id}`
    }
  }

  // Handle mark all as read
  const handleMarkAllAsRead = async () => {
    await markAllAsRead.mutateAsync(undefined)
  }

  // Handle load more
  const handleLoadMore = () => {
    setOffset((prev) => prev + limit)
  }

  // Get icon for notification type
  const getNotificationIcon = (type: string) => {
    switch (type) {
      case NotificationType.TASK_OVERDUE:
        return <AlertCircle className="h-4 w-4 text-rose-500" />
      case NotificationType.TASK_DUE:
        return <Clock className="h-4 w-4 text-amber-500" />
      case NotificationType.TASK_ASSIGNED:
        return <Sparkles className="h-4 w-4 text-cyan-500" />
      case NotificationType.TASK_COMPLETED:
        return <Check className="h-4 w-4 text-emerald-500" />
      case NotificationType.TASK_REMINDER:
        return <Bell className="h-4 w-4 text-blue-500" />
      default:
        return <Info className="h-4 w-4 text-muted-foreground" />
    }
  }

  return (
    <DropdownMenu.Portal>
      <DropdownMenu.Content
        align="end"
        className={cn(
          // Glassmorphism styling per Deep Space theme
          "glass-modal z-[100] w-80 md:w-96",
          "backdrop-blur-md bg-background/80",
          "border border-border/50 shadow-2xl",
          "rounded-lg p-0",
          // Animation
          "data-[state=open]:animate-in data-[state=closed]:animate-out",
          "data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0",
          "data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95",
          "data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2",
          "data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2"
        )}
      >
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border/50">
        <div className="flex items-center gap-2">
          <Bell className="h-4 w-4 text-foreground" />
          <span className="font-semibold text-foreground">Notifications</span>
        </div>

        {unreadCount > 0 && (
          <button
            onClick={(e) => {
              e.preventDefault()
              e.stopPropagation()
              handleMarkAllAsRead()
            }}
            className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors px-2 py-1 rounded hover:bg-muted/50"
          >
            <CheckCheck className="h-3 w-3" />
            Mark all read
          </button>
        )}
      </div>

      {/* Notification List */}
      <div
        ref={scrollRef}
        className="max-h-96 overflow-y-auto custom-scrollbar"
      >
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <div className="flex flex-col items-center gap-2 text-muted-foreground">
              <div className="h-6 w-6 animate-spin rounded-full border-2 border-border border-t-foreground/20" />
              <span className="text-sm">Loading notifications...</span>
            </div>
          </div>
        ) : allItems.length === 0 ? (
          <NotificationEmptyState />
        ) : (
          <AnimatePresence mode="popLayout">
            {allItems.map((notification) => (
              <NotificationItem
                key={notification.id}
                notification={notification}
                onClick={handleNotificationClick}
                icon={getNotificationIcon(notification.type)}
              />
            ))}
          </AnimatePresence>
        )}

        {/* Load More */}
        {hasMore && !isLoading && (
          <button
            onClick={(e) => {
              e.preventDefault()
              e.stopPropagation()
              handleLoadMore()
            }}
            className="w-full py-2 text-sm text-muted-foreground hover:text-foreground hover:bg-muted/30 transition-colors border-t border-border/50"
          >
            Load more ({total - offset - limit} remaining)
          </button>
        )}
      </div>

      {/* Footer */}
      {total > 0 && (
        <div className="px-4 py-2 border-t border-border/50 flex items-center justify-between">
          <a
            href="/settings/notifications"
            className="text-xs text-muted-foreground hover:text-foreground transition-colors"
          >
            Notification Settings
          </a>
          {onOpenPushSettings && (
            <button
              onClick={(e) => {
                e.preventDefault()
                e.stopPropagation()
                onOpenPushSettings()
              }}
              className="text-xs text-[oklch(0.91_0.17_195)] hover:text-[oklch(0.8_0.2_195)] transition-colors"
            >
              Push Settings
            </button>
          )}
        </div>
      )}
    </DropdownMenu.Content>
    </DropdownMenu.Portal>
  )
}

// Re-export for convenience
export { NotificationBell } from "./notification-bell"
