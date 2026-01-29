/**
 * Push Permission Modal - Glassmorphism modal for requesting push notification permission.
 *
 * [Task]: T031
 * [From]: spec.md FR-013-FR-017
 * [From]: Deep Space theme styling
 *
 * Features:
 * - Glassmorphism backdrop blur
 * - Clear permission request explanation
 * - "Allow" and "Deny" buttons
 * - Framer Motion scale/fade animation
 */

"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Bell, BellOff, X } from "lucide-react"
import * as Dialog from "@radix-ui/react-dialog"

import { usePushSubscription } from "@/hooks/use-push-subscription"
import { cn } from "@/lib/utils"

// =============================================================================
// Animation Variants
// =============================================================================

const backdropVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1 },
  exit: { opacity: 0 },
}

const modalVariants = {
  hidden: {
    opacity: 0,
    scale: 0.95,
    y: 10,
  },
  visible: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: {
      type: "spring" as const,
      stiffness: 300,
      damping: 25,
    },
  },
  exit: {
    opacity: 0,
    scale: 0.95,
    y: 10,
    transition: { duration: 0.15 },
  },
}

// =============================================================================
// Props
// =============================================================================

export interface PushPermissionModalProps {
  /** Whether to show the modal (controlled) */
  open?: boolean
  /** Callback when modal is closed */
  onOpenChange?: (open: boolean) => void
  /** Whether to automatically show on first visit */
  autoShow?: boolean
}

// =============================================================================
// Push Permission Modal Component
// =============================================================================

export function PushPermissionModal({
  open: controlledOpen,
  onOpenChange,
  autoShow = false,
}: PushPermissionModalProps) {
  const [internalOpen, setInternalOpen] = useState(false)
  const { permissionStatus, requestPermission } = usePushSubscription()

  const open = controlledOpen !== undefined ? controlledOpen : internalOpen

  const setOpen = (newOpen: boolean) => {
    if (controlledOpen === undefined) {
      setInternalOpen(newOpen)
    }
    onOpenChange?.(newOpen)
  }

  // Auto-show on first visit if permission is default and enabled
  useState(() => {
    if (autoShow && permissionStatus === "default" && typeof window !== "undefined") {
      // Check if we've already asked before
      const hasAsked = localStorage.getItem("push_permission_asked")
      if (!hasAsked) {
        setInternalOpen(true)
      }
    }
  })

  const handleAllow = async () => {
    const granted = await requestPermission()
    if (granted) {
      // Subscribe will be called after permission granted
      localStorage.setItem("push_permission_asked", "true")
      setOpen(false)
    }
  }

  const handleDeny = () => {
    localStorage.setItem("push_permission_asked", "true")
    setOpen(false)
  }

  const handleClose = () => {
    setOpen(false)
  }

  return (
    <AnimatePresence>
      {open && (
        <Dialog.Root open={open} onOpenChange={setOpen}>
          <Dialog.Portal>
            <Dialog.Overlay asChild>
              <motion.div
                variants={backdropVariants}
                initial="hidden"
                animate="visible"
                exit="exit"
                className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm"
              />
            </Dialog.Overlay>

            <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6">
              <Dialog.Content asChild>
                <motion.div
                  variants={modalVariants}
                  initial="hidden"
                  animate="visible"
                  exit="exit"
                  className={cn(
                    "glass-modal w-full max-w-md",
                    "backdrop-blur-md bg-background/90",
                    "border border-border/50 shadow-2xl",
                    "rounded-2xl p-5 sm:p-6 relative mx-4",
                    "data-[state=open]:animate-in",
                    "data-[state=closed]:animate-out",
                    "data-[state=closed]:fade-out-0",
                    "data-[state=open]:fade-in-0",
                  )}
                >
                  {/* Close button */}
                  <button
                    onClick={handleClose}
                    className="absolute top-3 sm:top-4 right-3 sm:right-4 p-1.5 rounded-full hover:bg-muted/50 transition-colors touch-manipulation"
                    aria-label="Close"
                  >
                    <X className="h-4 w-4 text-muted-foreground" />
                  </button>

                  {/* Icon */}
                  <div className="flex justify-center mb-4">
                    <div className="relative">
                      <div className="absolute inset-0 bg-[oklch(0.91_0.17_195/0.3)] rounded-full blur-xl" />
                      <div className="relative w-14 h-14 sm:w-16 sm:h-16 rounded-full bg-gradient-to-br from-[oklch(0.91_0.17_195)] to-[oklch(0.7_0.2_260)] flex items-center justify-center">
                        <Bell className="h-7 w-7 sm:h-8 sm:w-8 text-white" />
                      </div>
                    </div>
                  </div>

                  {/* Title */}
                  <Dialog.Title className="text-lg sm:text-xl font-semibold text-center text-foreground mb-2 px-2">
                    Enable Push Notifications
                  </Dialog.Title>

                  {/* Description */}
                  <Dialog.Description className="text-sm text-muted-foreground text-center mb-6 px-2">
                    Stay updated with your tasks even when the browser is closed.
                    We&apos;ll notify you about due dates, reminders, and task assignments.
                  </Dialog.Description>

                  {/* Features list */}
                  <div className="space-y-2 mb-6 text-sm">
                    <div className="flex items-start gap-3">
                      <div className="h-5 w-5 rounded-full bg-[oklch(0.91_0.17_195/0.2)] flex items-center justify-center shrink-0 mt-0.5">
                        <div className="h-2 w-2 rounded-full bg-[oklch(0.91_0.17_195)]" />
                      </div>
                      <span className="text-foreground">Task due date reminders</span>
                    </div>
                    <div className="flex items-start gap-3">
                      <div className="h-5 w-5 rounded-full bg-[oklch(0.91_0.17_195/0.2)] flex items-center justify-center shrink-0 mt-0.5">
                        <div className="h-2 w-2 rounded-full bg-[oklch(0.91_0.17_195)]" />
                      </div>
                      <span className="text-foreground">Overdue task alerts</span>
                    </div>
                    <div className="flex items-start gap-3">
                      <div className="h-5 w-5 rounded-full bg-[oklch(0.91_0.17_195/0.2)] flex items-center justify-center shrink-0 mt-0.5">
                        <div className="h-2 w-2 rounded-full bg-[oklch(0.91_0.17_195)]" />
                      </div>
                      <span className="text-foreground">New task assignments</span>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex flex-col sm:flex-row gap-2 sm:gap-3">
                    <button
                      onClick={handleDeny}
                      className={cn(
                        "flex-1 px-4 py-2.5 rounded-lg touch-manipulation",
                        "border border-border/50",
                        "hover:bg-muted/50 transition-colors",
                        "text-sm font-medium text-foreground"
                      )}
                    >
                      <BellOff className="h-4 w-4 inline mr-2" />
                      Not Now
                    </button>
                    <button
                      onClick={handleAllow}
                      className={cn(
                        "flex-1 px-4 py-2.5 rounded-lg touch-manipulation",
                        "bg-gradient-to-r from-[oklch(0.91_0.17_195)] to-[oklch(0.7_0.2_260)]",
                        "hover:opacity-90 transition-opacity",
                        "text-sm font-medium text-white shadow-lg",
                        "shadow-[oklch(0.91_0.17_195/0.3)]"
                      )}
                    >
                      <Bell className="h-4 w-4 inline mr-2" />
                      Allow
                    </button>
                  </div>

                  {/* Privacy note */}
                  <p className="text-xs text-muted-foreground/60 text-center mt-4 px-2">
                    You can change this anytime in notification settings
                  </p>
                </motion.div>
              </Dialog.Content>
            </div>
          </Dialog.Portal>
        </Dialog.Root>
      )}
    </AnimatePresence>
  )
}

// Re-export for convenience
// export type { PushPermissionModalProps } from "./push-permission-modal"
