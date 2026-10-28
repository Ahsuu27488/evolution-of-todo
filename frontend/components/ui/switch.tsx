"use client"

import * as React from "react"
import * as SwitchPrimitives from "@radix-ui/react-switch"

import { cn } from "@/lib/utils"

/**
 * Switch Component
 *
 * A toggle switch component built on Radix UI primitives.
 * Used for boolean settings like enabling/disabling notifications.
 *
 * [From]: spec.md FR-033 - Notification settings toggles
 */
function Switch({
  className,
  ...props
}: React.ComponentProps<typeof SwitchPrimitives.Root>) {
  return (
    <SwitchPrimitives.Root
      data-slot="switch"
      className={cn(
        "peer relative inline-flex h-[26px] w-11 shrink-0 cursor-pointer items-center rounded-full border-2 border-transparent transition-colors duration-200 outline-none after:absolute after:-inset-y-2 after:-inset-x-1 after:content-[''] focus-visible:ring-[3px] focus-visible:ring-ring/50 disabled:cursor-not-allowed disabled:opacity-50 data-[state=checked]:bg-primary data-[state=unchecked]:bg-foreground/20 hover:data-[state=unchecked]:bg-foreground/28",
        className
      )}
      {...props}
    >
      <SwitchPrimitives.Thumb
        data-slot="switch-thumb"
        className={cn(
          "pointer-events-none block size-[22px] rounded-full bg-[var(--switch-thumb)] shadow-[0_1px_3px_oklch(0.1_0.03_265/0.35)] ring-0 transition-transform duration-200 ease-[var(--ease-out)] data-[state=checked]:translate-x-[18px] data-[state=unchecked]:translate-x-0"
        )}
      />
    </SwitchPrimitives.Root>
  )
}

export { Switch }
