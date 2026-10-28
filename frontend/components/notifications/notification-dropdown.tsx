/**
 * Notification menu: the list that opens from the header bell.
 *
 * [Task]: T022
 * [From]: spec.md FR-002, FR-003, FR-007, FR-011
 *
 * Solid floating surface (it opens over the glass nav). Rows, not cards: unread rows carry a
 * gold dot. States: loading (skeleton rows), error (retry), empty, and "Show more".
 */

"use client"

import { useState } from "react"
import Link from "next/link"
import * as DropdownMenu from "@radix-ui/react-dropdown-menu"
import { AlertCircle, Bell, Check, CheckCheck, Clock, Info, Loader2, RefreshCw, Sparkles, Settings } from "lucide-react"
import { AnimatePresence } from "framer-motion"

import { useMarkAsRead, useMarkAllAsRead, useNotifications, useUnreadCount } from "@/hooks/use-notifications"
import type { Notification } from "@/types/notification"
import { NotificationType } from "@/types/notification"
import { NotificationItem } from "./notification-item"
import { NotificationEmptyState } from "./notification-empty-state"
import { Skeleton } from "@/components/ui/skeleton"
import { cn } from "@/lib/utils"

const PAGE = 10

/** Icon and tone per notification type (status tokens only) */
function iconFor(type: string) {
  switch (type) {
    case NotificationType.TASK_OVERDUE:
      return { icon: <AlertCircle />, tone: "bg-destructive/12 text-destructive" }
    case NotificationType.TASK_DUE:
      return { icon: <Clock />, tone: "bg-warning/14 text-warning" }
    case NotificationType.TASK_ASSIGNED:
      return { icon: <Sparkles />, tone: "bg-primary/14 text-primary" }
    case NotificationType.TASK_COMPLETED:
      return { icon: <Check />, tone: "bg-success/14 text-success" }
    case NotificationType.TASK_REMINDER:
      return { icon: <Bell />, tone: "bg-secondary/14 text-secondary" }
    default:
      return { icon: <Info />, tone: "bg-muted text-muted-foreground" }
  }
}

export function NotificationDropdown({ onNavigate }: { onNavigate?: () => void }) {
  // "Show more" grows the page instead of moving an offset, so earlier rows stay in the list
  const [limit, setLimit] = useState(PAGE)

  const { data, isLoading, isError, refetch, isFetching } = useNotifications({ limit, offset: 0 })
  const { data: unreadData } = useUnreadCount()
  const markAsRead = useMarkAsRead()
  const markAllAsRead = useMarkAllAsRead()

  const unreadCount = unreadData ?? 0
  const items = data?.items ?? []
  const total = data?.total ?? 0
  const remaining = Math.max(0, total - items.length)

  const handleNotificationClick = async (notification: Notification) => {
    if (!notification.read_status) {
      await markAsRead.mutateAsync(notification.id)
    }
    if (notification.related_task_id) {
      onNavigate?.()
      window.location.href = `/dashboard?task=${notification.related_task_id}`
    }
  }

  return (
    <DropdownMenu.Portal>
      <DropdownMenu.Content
        align="end"
        sideOffset={10}
        collisionPadding={12}
        aria-label="Notifications"
        className={cn(
          "surface-pop z-[100] flex w-[min(24rem,calc(100vw-1.5rem))] flex-col overflow-hidden rounded-[var(--radius-2xl)] outline-none",
          "max-h-[min(36rem,calc(100dvh-6rem))]",
          "data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0",
          "data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[side=bottom]:slide-in-from-top-2 duration-150"
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between gap-3 border-b border-border py-2 pr-2 pl-4">
          <div className="flex items-baseline gap-2">
            <h2 className="font-display text-base font-semibold">Notifications</h2>
            {unreadCount > 0 && (
              <span className="hidden text-xs text-muted-foreground tabular-nums min-[380px]:inline">{unreadCount} unread</span>
            )}
          </div>
          {unreadCount > 0 && (
            <DropdownMenu.Item
              onSelect={(e) => {
                e.preventDefault()
                markAllAsRead.mutate(undefined)
              }}
              disabled={markAllAsRead.isPending}
              className="inline-flex h-9 shrink-0 cursor-pointer items-center gap-1.5 whitespace-nowrap rounded-full px-3 text-xs font-medium text-muted-foreground outline-none transition-colors hover:bg-accent hover:text-foreground data-[disabled]:opacity-50 data-[highlighted]:bg-accent data-[highlighted]:text-foreground"
            >
              {markAllAsRead.isPending ? (
                <Loader2 className="size-3.5 animate-spin" aria-hidden />
              ) : (
                <CheckCheck className="size-3.5" aria-hidden />
              )}
              Mark all read
            </DropdownMenu.Item>
          )}
        </div>

        {/* List */}
        <div className="chat-scroll min-h-0 flex-1 overflow-y-auto p-1.5">
          {isLoading ? (
            <div className="space-y-1" aria-label="Loading notifications" role="status">
              {[0, 1, 2].map((i) => (
                <div key={i} className="flex items-start gap-3 rounded-[var(--radius-lg)] px-2.5 py-3">
                  <Skeleton className="size-8 rounded-full" />
                  <div className="flex-1 space-y-2 pt-0.5">
                    <Skeleton className="h-3.5 w-3/4" />
                    <Skeleton className="h-3 w-1/2" />
                  </div>
                </div>
              ))}
            </div>
          ) : isError ? (
            <div className="flex flex-col items-center gap-3 px-6 py-10 text-center" role="alert">
              <p className="text-sm text-muted-foreground">Notifications didn&apos;t load.</p>
              <DropdownMenu.Item
                onSelect={(e) => {
                  e.preventDefault()
                  refetch()
                }}
                className="inline-flex h-9 cursor-pointer items-center gap-1.5 rounded-full border border-border px-3.5 text-sm font-medium outline-none transition-colors hover:bg-accent data-[highlighted]:bg-accent"
              >
                <RefreshCw className={cn("size-3.5", isFetching && "animate-spin")} aria-hidden />
                Try again
              </DropdownMenu.Item>
            </div>
          ) : items.length === 0 ? (
            <NotificationEmptyState />
          ) : (
            <AnimatePresence mode="popLayout" initial={false}>
              {items.map((notification) => {
                const { icon, tone } = iconFor(notification.type)
                return (
                  <NotificationItem
                    key={notification.id}
                    notification={notification}
                    onClick={handleNotificationClick}
                    icon={icon}
                    iconTone={tone}
                  />
                )
              })}
            </AnimatePresence>
          )}

          {remaining > 0 && !isLoading && (
            <DropdownMenu.Item
              onSelect={(e) => {
                e.preventDefault()
                setLimit((l) => l + PAGE)
              }}
              disabled={isFetching}
              className="mt-1 flex h-10 w-full cursor-pointer items-center justify-center gap-2 rounded-[var(--radius-lg)] text-sm text-muted-foreground outline-none transition-colors hover:bg-accent hover:text-foreground data-[highlighted]:bg-accent data-[highlighted]:text-foreground"
            >
              {isFetching && <Loader2 className="size-3.5 animate-spin" aria-hidden />}
              Show {Math.min(PAGE, remaining)} more
            </DropdownMenu.Item>
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-border p-1.5">
          <DropdownMenu.Item asChild>
            <Link
              href="/settings/notifications"
              onClick={onNavigate}
              className="flex h-10 items-center gap-2.5 rounded-[var(--radius-lg)] px-2.5 text-sm text-muted-foreground outline-none transition-colors hover:bg-accent hover:text-foreground data-[highlighted]:bg-accent data-[highlighted]:text-foreground"
            >
              <Settings className="size-4" aria-hidden />
              Notification settings
            </Link>
          </DropdownMenu.Item>
        </div>
      </DropdownMenu.Content>
    </DropdownMenu.Portal>
  )
}

// Re-export for convenience
export { NotificationBell } from "./notification-bell"
