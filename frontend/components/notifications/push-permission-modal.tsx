/**
 * Push Permission Modal: asks once whether to turn on browser push notifications.
 *
 * [Task]: T031
 * [From]: spec.md FR-013-FR-017
 *
 * Built on the shared Dialog (glass floating layer). "Not now" remembers the answer
 * in localStorage so the question is not repeated.
 */

"use client"

import { useEffect, useState } from "react"
import { Bell, Check, Loader2 } from "lucide-react"

import { usePushSubscription } from "@/hooks/use-push-subscription"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"

export interface PushPermissionModalProps {
  /** Whether to show the modal (controlled) */
  open?: boolean
  /** Callback when modal is closed */
  onOpenChange?: (open: boolean) => void
  /** Whether to automatically show on first visit */
  autoShow?: boolean
}

const benefits = ["Reminders before a task is due", "A heads-up when something is overdue", "New tasks assigned to you"]

export function PushPermissionModal({
  open: controlledOpen,
  onOpenChange,
  autoShow = false,
}: PushPermissionModalProps) {
  const [internalOpen, setInternalOpen] = useState(false)
  const [isRequesting, setIsRequesting] = useState(false)
  const [denied, setDenied] = useState(false)
  const { permissionStatus, requestPermission } = usePushSubscription()

  const open = controlledOpen !== undefined ? controlledOpen : internalOpen

  const setOpen = (newOpen: boolean) => {
    if (controlledOpen === undefined) {
      setInternalOpen(newOpen)
    }
    onOpenChange?.(newOpen)
  }

  // Auto-show on first visit if permission is default and enabled
  useEffect(() => {
    if (autoShow && permissionStatus === "default" && !localStorage.getItem("push_permission_asked")) {
      setInternalOpen(true)
    }
  }, [autoShow, permissionStatus])

  const handleAllow = async () => {
    setIsRequesting(true)
    try {
      const granted = await requestPermission()
      localStorage.setItem("push_permission_asked", "true")
      if (granted) {
        setOpen(false)
      } else {
        setDenied(true)
      }
    } finally {
      setIsRequesting(false)
    }
  }

  const handleNotNow = () => {
    localStorage.setItem("push_permission_asked", "true")
    setOpen(false)
  }

  return (
    <Dialog open={open} onOpenChange={(next) => (next ? setOpen(true) : handleNotNow())}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <div aria-hidden className="mb-2 grid size-12 place-items-center rounded-full bg-primary/14 text-primary">
            <Bell className="size-5" />
          </div>
          <DialogTitle>Get reminders on this device?</DialogTitle>
          <DialogDescription>
            Chronos can notify you even when this tab is closed. Your browser will ask to confirm.
          </DialogDescription>
        </DialogHeader>

        <ul className="space-y-2.5 text-sm">
          {benefits.map((item) => (
            <li key={item} className="flex items-center gap-3">
              <span aria-hidden className="grid size-5 shrink-0 place-items-center rounded-full bg-success/14 text-success">
                <Check className="size-3" strokeWidth={3} />
              </span>
              {item}
            </li>
          ))}
        </ul>

        {denied && (
          <p role="alert" className="text-[13px] text-warning">
            Notifications are blocked for this site. You can allow them later from your browser&apos;s site
            settings.
          </p>
        )}

        <DialogFooter>
          <Button variant="ghost" onClick={handleNotNow} disabled={isRequesting}>
            Not now
          </Button>
          <Button onClick={handleAllow} disabled={isRequesting || denied} aria-busy={isRequesting}>
            {isRequesting ? <Loader2 className="animate-spin" /> : <Bell />}
            Turn on notifications
          </Button>
        </DialogFooter>
        <p className="-mt-1 text-center text-xs text-muted-foreground sm:text-right">
          You can change this any time in notification settings.
        </p>
      </DialogContent>
    </Dialog>
  )
}
