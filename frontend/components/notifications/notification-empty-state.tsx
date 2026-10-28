/**
 * Notification Empty State: shown in the notification menu when there is nothing to read.
 *
 * [Task]: T023
 */

"use client"

import { BellOff } from "lucide-react"

export function NotificationEmptyState() {
  return (
    <div className="flex flex-col items-center px-6 py-10 text-center">
      <div className="grid size-11 place-items-center rounded-full bg-muted text-muted-foreground">
        <BellOff className="size-5" aria-hidden />
      </div>
      <p className="mt-3 text-sm font-medium">You&apos;re all caught up</p>
      <p className="mt-1 max-w-56 text-[13px] text-muted-foreground">
        Due dates, overdue tasks and reminders show up here.
      </p>
    </div>
  )
}
