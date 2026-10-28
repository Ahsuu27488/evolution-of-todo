/**
 * Notifications Client - Wrapper component for notification features.
 *
 * [Task]: T024, T036
 * [From]: spec.md FR-001, FR-005, SC-001, FR-013-FR-017
 *
 * Features:
 * - Bell trigger with unread count, and the notification menu
 * - Manages SSE stream connection
 * - Handles real-time updates
 * - Integrates push permission modal
 */

"use client"

import { useState, useEffect } from "react"
import * as DropdownMenu from "@radix-ui/react-dropdown-menu"
import dynamic from "next/dynamic"

import { usePushSubscription } from "@/hooks/use-push-subscription"
import { NotificationBell } from "./notification-bell"
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

  return (
    <>
      <DropdownMenu.Root open={open} onOpenChange={setOpen}>
        <DropdownMenu.Trigger asChild>
          <NotificationBell />
        </DropdownMenu.Trigger>
        <NotificationDropdown onNavigate={() => setOpen(false)} />
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
export { NotificationBell } from "./notification-bell"
export { NotificationDropdown } from "./notification-dropdown"
