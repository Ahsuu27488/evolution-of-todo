/**
 * Toast helpers. Every toast goes through the app Toaster (components/ui/sonner.tsx), so they
 * all share one look: the solid floating surface, status shown by the icon colour.
 *
 * Per spec.md US7: Themed Toast Notifications (FR-028, FR-029, FR-030, FR-031)
 */

import { toast as sonnerToast } from "sonner"

export type ThemedToastType = "success" | "error" | "info"

export interface ThemedToastOptions {
  message: string
  type?: ThemedToastType
  duration?: number
  description?: string
}

// =============================================================================
// Toast API
// =============================================================================

/**
 * Themed toast notification API.
 *
 * success, error and info, on the app Toaster.
 *
 * @example
 * ```tsx
 * import { themedToast } from "@/lib/utils/toast"
 *
 * // Success toast
 * themedToast.success("Task created successfully")
 *
 * // Error toast
 * themedToast.error("Failed to create task")
 *
 * // Info toast with description
 * themedToast.info("Sync complete", { description: "3 tasks updated" })
 * ```
 */
export const themedToast = {
  /**
   * Show a success toast.
   */
  success: (message: string, options?: Omit<ThemedToastOptions, "type" | "message">) => {
    return sonnerToast.success(message, { description: options?.description, duration: options?.duration ?? 3000 })
  },

  /**
   * Show an error toast.
   */
  error: (message: string, options?: Omit<ThemedToastOptions, "type" | "message">) => {
    // Errors stay longer
    return sonnerToast.error(message, { description: options?.description, duration: options?.duration ?? 5000 })
  },

  /**
   * Show an info toast.
   */
  info: (message: string, options?: Omit<ThemedToastOptions, "type" | "message">) => {
    return sonnerToast.info(message, { description: options?.description, duration: options?.duration ?? 3000 })
  },

  /**
   * Dismiss all toasts.
   */
  dismiss: () => {
    sonnerToast.dismiss()
  },
}

// =============================================================================
// AI Action Toast Helper
// =============================================================================

/**
 * Show toast notification for AI-triggered task actions.
 *
 * Phase 1 T014: Integrate SSE cache updates with toast notifications
 *
 * @param mutation - Task mutation from SSE tool_result event
 *
 * @example
 * ```tsx
 * import { showToastForAIMutation } from "@/lib/utils/toast"
 *
 * await streamChat(message, conversationId, {
 *   onTaskMutation: (mutation) => {
 *     updateTaskCache(queryClient, mutation)
 *     showToastForAIMutation(mutation)
 *   }
 * })
 * ```
 */
export function showToastForAIMutation(
  mutation: {
    type: string
    taskId: number | null
    success?: boolean
    error?: string
  }
): void {
  if (!mutation.success) {
    themedToast.error(`Kairos couldn't finish that: ${mutation.error || "please try again"}`)
    return
  }

  const messages = {
    create: "Kairos added a task",
    complete: "Kairos completed a task",
    update: "Kairos updated a task",
    delete: "Kairos deleted a task",
  } as const

  const type = mutation.type as keyof typeof messages
  const message = messages[type]

  if (message) {
    themedToast.success(message, {
      description: mutation.type === "complete" ? "One less thing in orbit." : undefined,
    })
  }
}

// Re-export for convenience
export { toast } from "sonner"
