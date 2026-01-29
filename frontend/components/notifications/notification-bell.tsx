/**
 * Notification Bell component with unread badge.
 *
 * [Task]: T021
 * [From]: spec.md FR-001, FR-003, FR-011
 * [From]: Context7 /radix-ui/website for DropdownMenu patterns
 *
 * Features:
 * - Bell icon with Badge showing unread count
 * - DropdownMenu for notification list
 * - Framer Motion animations
 * - Deep Space glassmorphism styling
 */

"use client"

import * as DropdownMenu from "@radix-ui/react-dropdown-menu"
import { Bell } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"
import { forwardRef } from "react"

import { Badge } from "@/components/ui/badge"
import { useUnreadCount } from "@/hooks/use-notifications"

// =============================================================================
// Notification Bell Component
// =============================================================================

export interface NotificationBellProps {
  /** Callback when bell is clicked (before dropdown opens) */
  onBellClick?: () => void
}

export const NotificationBell = forwardRef<HTMLButtonElement, NotificationBellProps>(
  ({ onBellClick }, ref) => {
    const { data: unreadCount } = useUnreadCount()

    return (
      <DropdownMenu.Root>
        <DropdownMenu.Trigger asChild>
          <motion.button
            ref={ref}
            type="button"
            className="relative p-2 sm:p-2.5 rounded-md hover:bg-muted/50 transition-colors touch-manipulation"
            onClick={onBellClick}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            aria-label="Notifications"
          >
            <Bell className="h-5 w-5 sm:h-5 sm:w-5 text-foreground/80" />

            <AnimatePresence>
              {unreadCount && unreadCount > 0 && (
                <motion.div
                  initial={{ scale: 0, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  exit={{ scale: 0, opacity: 0 }}
                  transition={{ type: "spring", stiffness: 500, damping: 30 }}
                >
                  <Badge
                    variant="destructive"
                    className="absolute -top-0.5 -right-0.5 sm:-top-1 sm:-right-1 h-5 w-5 flex items-center justify-center text-xs p-0 bg-rose-500 hover:bg-rose-600"
                  >
                    {unreadCount > 9 ? "9+" : unreadCount}
                  </Badge>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.button>
        </DropdownMenu.Trigger>
      </DropdownMenu.Root>
    )
  }
)

NotificationBell.displayName = "NotificationBell"
