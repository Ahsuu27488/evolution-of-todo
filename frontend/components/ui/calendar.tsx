"use client"

import * as React from "react"
import { DayPicker } from "react-day-picker"

import { cn } from "@/lib/utils"
import { buttonVariants } from "@/components/ui/button"

export type CalendarProps = React.ComponentProps<typeof DayPicker>

function Calendar({
  className,
  classNames,
  showOutsideDays = true,
  ...props
}: CalendarProps) {
  return (
    <DayPicker
      showOutsideDays={showOutsideDays}
      className={cn("", className)}
      style={{ height: "275px" } as React.CSSProperties}
      classNames={{
        months: "flex flex-col sm:flex-row gap-0.5",
        month: "flex flex-col gap-1",
        month_caption: "flex items-center justify-center pt-2 pb-2 relative w-full",
        caption_label: "text-xs font-semibold text-foreground pl-10",
        nav: "flex items-center gap-0.5 absolute left-2",
        button_previous: cn(
          buttonVariants({ variant: "ghost" }),
          "h-6 w-6 p-0 !text-foreground/80 hover:!text-foreground hover:!bg-accent/50 z-10 relative"
        ),
        button_next: cn(
          buttonVariants({ variant: "ghost" }),
          "h-6 w-6 p-0 !text-foreground/80 hover:!text-foreground hover:!bg-accent/50 z-10 relative"
        ),
        month_grid: "w-full border-collapse space-x-0",
        weekdays: "flex",
        weekday: "text-muted-foreground rounded-md w-10 font-normal text-[0.75rem]",
        week: "flex w-full mt-0.5 justify-between",
        day: cn(
          "relative p-0 text-center text-sm focus-within:relative focus-within:z-20 rounded-md transition-colors",
          "h-9 w-10 flex-1 flex items-center justify-center",
          "hover:bg-accent/50 hover:text-accent-foreground",
          "[&:has([data-selected])]:bg-accent [&:has([data-selected])]:text-accent-foreground"
        ),
        day_button: cn(
          buttonVariants({ variant: "ghost" }),
          "h-9 w-10 p-0 font-normal aria-selected:opacity-100 rounded-md flex-1"
        ),
        range_start: "range-start rounded-md",
        range_end: "range-end rounded-md",
        selected:
          "bg-primary text-primary-foreground hover:bg-primary hover:text-primary-foreground focus:bg-primary focus:text-primary-foreground rounded-md glow-cyan",
        today: "border-2 border-primary/30 rounded-md",
        outside:
          "text-muted-foreground opacity-50 aria-selected:bg-muted/50 aria-selected:text-muted-foreground aria-selected:opacity-30",
        disabled: "text-muted-foreground opacity-50 pointer-events-none",
        range_middle:
          "aria-selected:bg-accent/50 aria-selected:text-accent-foreground aria-selected:opacity-50 rounded-md",
        hidden: "invisible",
        ...classNames,
      }}
      {...props}
    />
  )
}

export { Calendar }
