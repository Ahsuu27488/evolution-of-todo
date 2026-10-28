/**
 * Notification row inside the notification menu.
 *
 * [Task]: T020
 * [From]: spec.md FR-002, FR-003, FR-006, FR-007
 *
 * A row (not a card): type icon in a tinted circle, title, message, relative time.
 * Unread rows show a gold dot and full-strength text. Delete appears on hover or focus
 * (always on touch screens). The row is a menu item, so arrow keys and Enter work inside the menu.
 */

"use client"

import * as DropdownMenu from "@radix-ui/react-dropdown-menu"
import { motion } from "framer-motion"
import { formatDistanceToNow } from "date-fns"
import { Loader2, X } from "lucide-react"

import { useDeleteNotification } from "@/hooks/use-notifications"
import type { Notification } from "@/types/notification"
import { cn } from "@/lib/utils"

export interface NotificationItemProps {
  /** Notification data */
  notification: Notification
  /** Click handler */
  onClick: (notification: Notification) => void
  /** Icon to display */
  icon: React.ReactNode
  /** Classes for the icon circle (status tint) */
  iconTone?: string
}

export function NotificationItem({
  notification,
  onClick,
  icon,
  iconTone = "bg-muted text-muted-foreground",
}: NotificationItemProps) {
  const deleteNotification = useDeleteNotification()
  const unread = !notification.read_status

  const handleDelete = async (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    await deleteNotification.mutateAsync(notification.id)
  }

  const relativeTime = formatDistanceToNow(new Date(notification.created_at), {
    addSuffix: true,
  })

  return (
    <motion.div
      layout
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0, x: -12, transition: { duration: 0.15 } }}
      className="group relative"
    >
      <DropdownMenu.Item
        onSelect={(e) => {
          // Stay open unless the click navigates to a task
          if (!notification.related_task_id) e.preventDefault()
          onClick(notification)
        }}
        aria-label={`${unread ? "Unread: " : ""}${notification.title}, ${relativeTime}`}
        className={cn(
          "flex w-full cursor-pointer items-start gap-3 rounded-[var(--radius-lg)] py-3 pr-11 pl-2.5 text-left outline-none transition-colors",
          "hover:bg-accent data-[highlighted]:bg-accent"
        )}
      >
        <div className={cn("relative mt-0.5 grid size-8 shrink-0 place-items-center rounded-full [&_svg]:size-4", iconTone)}>
          {icon}
          {unread && (
            <span
              aria-hidden
              className="absolute -top-0.5 -right-0.5 size-2.5 rounded-full bg-primary ring-2 ring-[var(--custom-popover)]"
            />
          )}
        </div>

        <div className="min-w-0 flex-1">
          <p className={cn("text-sm leading-snug", unread ? "font-medium text-foreground" : "text-muted-foreground")}>
            {notification.title}
          </p>
          {notification.message && (
            <p className="mt-0.5 line-clamp-2 text-[13px] text-muted-foreground">{notification.message}</p>
          )}
          <p className="mt-1 text-xs text-muted-foreground/80">{relativeTime}</p>
        </div>
      </DropdownMenu.Item>

      <button
        type="button"
        onClick={handleDelete}
        disabled={deleteNotification.isPending}
        aria-label={`Dismiss "${notification.title}"`}
        className={cn(
          "absolute top-2.5 right-1.5 grid size-9 place-items-center rounded-full text-muted-foreground outline-none transition-[opacity,background-color,color]",
          "hover:bg-destructive/12 hover:text-destructive focus-visible:opacity-100 focus-visible:ring-[3px] focus-visible:ring-ring/50",
          "opacity-0 group-hover:opacity-100 group-focus-within:opacity-100 [@media(hover:none)]:opacity-100"
        )}
      >
        {deleteNotification.isPending ? (
          <Loader2 className="size-3.5 animate-spin" aria-hidden />
        ) : (
          <X className="size-4" aria-hidden />
        )}
      </button>
    </motion.div>
  )
}
