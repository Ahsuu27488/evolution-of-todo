/**
 * Conditional Chat Panel - Route-aware ChatPanel rendering.
 *
 * Renders the AI assistant ChatPanel only on the dashboard page.
 * This prevents the FAB from appearing on non-dashboard pages like
 * home, profile, settings, login, and signup.
 *
 * Per spec.md User Story 2 (FR-005 through FR-008):
 * - FAB only visible on dashboard page
 * - FAB hidden on all non-dashboard pages
 * - Chat panel closes when navigating away from dashboard
 * - Chat state preserved when navigating back to dashboard
 *
 * @example
 * ```tsx
 * // In app/providers.tsx
 * import { ConditionalChatPanel } from "@/components/chat/conditional-chat-panel"
 *
 * export function Providers({ children }) {
 *   return (
 *     <ChatProvider>
 *       {children}
 *       <ConditionalChatPanel />
 *     </ChatProvider>
 *   )
 * }
 * ```
 */

"use client"

import { useEffect, useRef } from "react"
import { usePathname } from "next/navigation"
import { ChatPanel } from "./chat-panel"
import { useChatPanelActions } from "@/lib/stores/chat-store"

/**
 * Routes where the chat panel should NOT be displayed.
 */
const EXCLUDED_ROUTES = [
  "/",
  "/login",
  "/signup",
  "/profile",
  "/settings",
  "/auth/callback",
] as const

/**
 * Check if the current path should show the chat panel.
 *
 * @param pathname - Current route pathname
 * @returns true if chat panel should be shown
 */
function shouldShowChat(pathname: string): boolean {
  // Chat only appears on dashboard
  if (pathname === "/dashboard") return true

  // Check excluded routes
  if (EXCLUDED_ROUTES.includes(pathname as typeof EXCLUDED_ROUTES[number])) return false

  // Hide on all other routes (conservative approach)
  return false
}

/**
 * Conditional Chat Panel component.
 *
 * Renders ChatPanel only when on the dashboard page.
 * Automatically closes the panel when navigating away from dashboard.
 * Preserves chat state (messages, conversationId) when navigating back.
 */
export function ConditionalChatPanel() {
  const pathname = usePathname()
  const { setOpen } = useChatPanelActions()
  const showChat = shouldShowChat(pathname)

  // Track previous pathname to detect navigation changes
  const previousPathnameRef = useRef(pathname)

  // Close chat panel when navigating away from dashboard
  useEffect(() => {
    const wasOnDashboard = previousPathnameRef.current === "/dashboard"
    const isOnDashboard = pathname === "/dashboard"

    // Close panel when navigating away from dashboard
    if (wasOnDashboard && !isOnDashboard) {
      setOpen(false)
    }

    // Update ref for next navigation
    previousPathnameRef.current = pathname
  }, [pathname, setOpen])

  // Only render ChatPanel when on dashboard
  if (!showChat) {
    return null
  }

  return <ChatPanel />
}
