/**
 * Notification bell: the header button with the unread count.
 *
 * A plain button (ref-forwarding) so it can sit inside any trigger, e.g.
 * `<DropdownMenu.Trigger asChild><NotificationBell /></DropdownMenu.Trigger>`.
 */

"use client"

import { Bell } from "lucide-react"
import { forwardRef } from "react"

import { useUnreadCount } from "@/hooks/use-notifications"
import { cn } from "@/lib/utils"

export type NotificationBellProps = React.ComponentPropsWithoutRef<"button">

export const NotificationBell = forwardRef<HTMLButtonElement, NotificationBellProps>(
  ({ className, ...props }, ref) => {
    const { data: unreadCount } = useUnreadCount()
    const count = typeof unreadCount === "number" ? unreadCount : 0
    const label = count > 0 ? `Notifications, ${count} unread` : "Notifications"

    return (
      <button
        ref={ref}
        type="button"
        aria-label={label}
        className={cn(
          "relative grid size-10 place-items-center rounded-full text-foreground/80 outline-none transition-colors duration-150",
          "hover:bg-accent hover:text-foreground focus-visible:ring-[3px] focus-visible:ring-ring/50 active:scale-95",
          "data-[state=open]:bg-accent data-[state=open]:text-foreground",
          className
        )}
        {...props}
      >
        <Bell className="size-[18px]" aria-hidden />
        {count > 0 && (
          <span
            aria-hidden
            className="absolute top-1 right-0.5 flex h-[18px] min-w-[18px] items-center justify-center rounded-full bg-primary px-1 text-[10px] leading-none font-semibold text-primary-foreground tabular-nums ring-2 ring-[var(--custom-popover)]"
          >
            {count > 9 ? "9+" : count}
          </span>
        )}
      </button>
    )
  }
)

NotificationBell.displayName = "NotificationBell"
