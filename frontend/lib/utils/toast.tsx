/**
 * Themed toast notifications with glassmorphism styling.
 *
 * Provides a toast notification system that matches the app's deep space theme
 * with backdrop blur, neon borders, and OKLCH colors.
 *
 * Per spec.md US7: Themed Toast Notifications (FR-028, FR-029, FR-030, FR-031)
 */

import { toast as sonnerToast } from "sonner"
import { CheckCircle2, XCircle, Info } from "lucide-react"

// =============================================================================
// Types
// =============================================================================

export type ThemedToastType = "success" | "error" | "info"

export interface ThemedToastOptions {
  message: string
  type?: ThemedToastType
  duration?: number
  description?: string
}

// =============================================================================
// Themed Toast Component
// =============================================================================

/**
 * Glassmorphism-styled toast component.
 *
 * Matches the dashboard's deep space theme with:
 * - Backdrop blur effect
 * - Neon border colors (cyan for success, red for error, blue for info)
 * - OKLCH color system
 *
 * @param props - Toast props from Sonner
 */
function ThemedToast({ message, description, type = "info" }: ThemedToastOptions & { id: string | number }) {
  // Define type configurations
  const configs = {
    success: {
      icon: <CheckCircle2 className="h-4 w-4 text-cyan-400" />,
      borderColor: "border-cyan-500/50",
      bgColor: "bg-cyan-500/10",
      glowColor: "shadow-[0_0_20px_rgba(0,245,255,0.3)]",
    },
    error: {
      icon: <XCircle className="h-4 w-4 text-red-400" />,
      borderColor: "border-red-500/50",
      bgColor: "bg-red-500/10",
      glowColor: "shadow-[0_0_20px_rgba(239,68,68,0.3)]",
    },
    info: {
      icon: <Info className="h-4 w-4 text-blue-400" />,
      borderColor: "border-blue-500/50",
      bgColor: "bg-blue-500/10",
      glowColor: "shadow-[0_0_20px_rgba(59,130,246,0.3)]",
    },
  } as const

  // Get the config for the current type, defaulting to info
  const typeConfig = configs[type as keyof typeof configs] || configs.info

  return (
    <div
      className={`
        flex items-start gap-3 p-4 rounded-lg border
        backdrop-blur-md bg-surface/80
        ${typeConfig.borderColor} ${typeConfig.bgColor} ${typeConfig.glowColor}
        shadow-lg
        min-w-[300px] max-w-md
      `}
    >
      <div className="shrink-0 mt-0.5">{typeConfig.icon}</div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-foreground">{message}</p>
        {description && (
          <p className="text-xs text-muted-foreground mt-1">{description}</p>
        )}
      </div>
    </div>
  )
}

// =============================================================================
// Toast API
// =============================================================================

/**
 * Themed toast notification API.
 *
 * Provides success, error, and info methods that display glassmorphism-styled
 * toasts matching the app's theme.
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
   * Show a success toast with glassmorphism styling.
   */
  success: (message: string, options?: Omit<ThemedToastOptions, "type" | "message">) => {
    return sonnerToast.custom((t: string | number) => (
      <ThemedToast message={message} type="success" {...options} id={t} />
    ), {
      duration: options?.duration ?? 3000,
    })
  },

  /**
   * Show an error toast with glassmorphism styling.
   */
  error: (message: string, options?: Omit<ThemedToastOptions, "type" | "message">) => {
    return sonnerToast.custom((t: string | number) => (
      <ThemedToast message={message} type="error" {...options} id={t} />
    ), {
      duration: options?.duration ?? 5000, // Errors stay longer
    })
  },

  /**
   * Show an info toast with glassmorphism styling.
   */
  info: (message: string, options?: Omit<ThemedToastOptions, "type" | "message">) => {
    return sonnerToast.custom((t: string | number) => (
      <ThemedToast message={message} type="info" {...options} id={t} />
    ), {
      duration: options?.duration ?? 3000,
    })
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
    themedToast.error(`AI action failed: ${mutation.error || "Unknown error"}`)
    return
  }

  const messages = {
    create: "Task created",
    complete: "Task completed",
    update: "Task updated",
    delete: "Task deleted",
  } as const

  const type = mutation.type as keyof typeof messages
  const message = messages[type]

  if (message) {
    themedToast.success(message, {
      description: mutation.type === "complete"
        ? "Great job making progress!"
        : undefined,
    })
  }
}

// Re-export for convenience
export { toast } from "sonner"
