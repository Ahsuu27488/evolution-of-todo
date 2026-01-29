/**
 * Notification Item component with glassmorphism and animations.
 *
 * [Task]: T020
 * [From]: spec.md FR-002, FR-003, FR-006, FR-007
 * [From]: Deep Space theme styling
 *
 * Features:
 * - Glassmorphism card styling
 * - Cyan glow for unread notifications
 * - Relative timestamp display
 * - Hover effects and disintegrate animation
 * - Delete/swipe to dismiss
 */

"use client"

import { motion } from "framer-motion"
import { formatDistanceToNow } from "date-fns"
import { Clock, Trash2 } from "lucide-react"

import { useDeleteNotification } from "@/hooks/use-notifications"
import type { Notification } from "@/types/notification"
import { cn } from "@/lib/utils"

// =============================================================================
// Animation Variants
// =============================================================================

const itemVariants = {
  hidden: {
    opacity: 0,
    height: 0,
    marginBottom: 0,
  },
  visible: {
    opacity: 1,
    height: "auto",
    marginBottom: "0.5rem",
    transition: {
      type: "spring" as const,
      stiffness: 300,
      damping: 25,
    },
  },
  exit: {
    opacity: 0,
    x: -20,
    transition: {
      duration: 0.2,
    },
  },
}

// =============================================================================
// Notification Item Component
// =============================================================================

export interface NotificationItemProps {
  /** Notification data */
  notification: Notification
  /** Click handler */
  onClick: (notification: Notification) => void
  /** Icon to display */
  icon: React.ReactNode
}

export function NotificationItem({
  notification,
  onClick,
  icon,
}: NotificationItemProps) {
  const deleteNotification = useDeleteNotification()

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
      variants={itemVariants}
      initial="hidden"
      animate="visible"
      exit="exit"
      layout
      className="group relative"
    >
      <div
        role="button"
        tabIndex={0}
        onClick={() => onClick(notification)}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault()
            onClick(notification)
          }
        }}
        className={cn(
          // Glassmorphism card styling
          "w-full text-left p-3 rounded-lg cursor-pointer",
          "backdrop-blur-sm bg-background/60",
          "border border-border/50",
          "hover:bg-background/80 transition-colors",
          // Unread glow indicator
          notification.read_status
            ? "opacity-70"
            : "border-l-2 border-l-[oklch(0.91_0.17_195)]", // Cyan glow per FR-003
          "flex items-start gap-3"
        )}
      >
        {/* Icon */}
        <div className={cn(
          "mt-0.5 shrink-0",
          // Glow effect for unread notifications
          !notification.read_status && "drop-shadow-[0_0_8px_oklch(0.91_0.17_195/0.5)]"
        )}>
          {icon}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <p className={cn(
            "text-sm font-medium leading-tight",
            notification.read_status
              ? "text-muted-foreground"
              : "text-foreground"
          )}>
            {notification.title}
          </p>
          {notification.message && (
            <p className="text-xs text-muted-foreground line-clamp-2 mt-0.5">
              {notification.message}
            </p>
          )}
          <p className="text-xs text-muted-foreground/60 mt-1 flex items-center gap-1">
            <Clock className="h-3 w-3" />
            {relativeTime}
          </p>
        </div>

        {/* Delete button */}
        <button
          onClick={handleDelete}
          className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-destructive/10 hover:text-destructive rounded"
          aria-label="Delete notification"
        >
          <Trash2 className="h-3 w-3" />
        </button>
      </div>
    </motion.div>
  )
}
