/**
 * Notifications Client - Wrapper component for notification features.
 *
 * [Task]: T024, T036
 * [From]: spec.md FR-001, FR-005, SC-001, FR-013-FR-017
 *
 * Features:
 * - Wraps NotificationBell and NotificationDropdown
 * - Manages SSE stream connection
 * - Handles real-time updates
 * - Integrates push permission modal
 */

"use client"

import { useState, useEffect } from "react"
import * as DropdownMenu from "@radix-ui/react-dropdown-menu"
import { Bell } from "lucide-react"
import dynamic from "next/dynamic"

import { useUnreadCount } from "@/hooks/use-notifications"
import { usePushSubscription } from "@/hooks/use-push-subscription"
import { NotificationDropdown } from "./notification-dropdown"
import { PushPermissionModal } from "./push-permission-modal"

// Dynamically import SSE stream provider to avoid SSR issues
// EventSource is browser-only and causes "EventSource is not defined" during SSR
const SSEStreamProvider = dynamic(
  () => import("./sse-stream-provider").then(mod => ({ default: mod.SSEStreamProvider })),
  { ssr: false }
)

// =============================================================================
// Notifications Client Component
// =============================================================================

export function NotificationsClient() {
  const [open, setOpen] = useState(false)
  const [showPushModal, setShowPushModal] = useState(false)
  const { data: unreadCount } = useUnreadCount()
  const { permissionStatus, isSupported } = usePushSubscription()

  // Check if we should show push permission modal
  useEffect(() => {
    if (isSupported && permissionStatus === "default" && typeof window !== "undefined") {
      // Only show if user hasn't been asked before
      const hasAsked = localStorage.getItem("push_permission_asked")
      if (!hasAsked) {
        // Delay showing modal to avoid interrupting initial page load
        const timer = setTimeout(() => {
          setShowPushModal(true)
        }, 3000)
        return () => clearTimeout(timer)
      }
    }
  }, [isSupported, permissionStatus])

  // Only show badge when there are actual unread notifications (> 0)
  const showBadge = typeof unreadCount === "number" && unreadCount > 0

  return (
    <>
      <DropdownMenu.Root open={open} onOpenChange={setOpen}>
        <DropdownMenu.Trigger
          className="relative inline-flex items-center justify-center p-2 rounded-md hover:bg-muted/50 transition-colors cursor-pointer"
          aria-label="Notifications"
        >
          <Bell className="h-5 w-5 text-foreground" />
          {showBadge && (
            <span className="absolute -top-0.5 -right-0.5 h-4 min-w-[1rem] px-0.5 flex items-center justify-center text-[10px] font-bold text-white bg-rose-500 rounded-full">
              {unreadCount && unreadCount > 9 ? "9+" : unreadCount}
            </span>
          )}
        </DropdownMenu.Trigger>
        <NotificationDropdown />
        {/* SSE streaming for real-time updates - client only */}
        <SSEStreamProvider />
      </DropdownMenu.Root>

      {/* Push Permission Modal */}
      {isSupported && (
        <PushPermissionModal
          open={showPushModal}
          onOpenChange={setShowPushModal}
          autoShow={false}
        />
      )}
    </>
  )
}

// Re-export for convenience
export { NotificationBell, NotificationDropdown } from "./notification-dropdown"
