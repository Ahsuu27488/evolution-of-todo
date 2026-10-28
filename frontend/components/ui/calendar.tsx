"use client"

import * as React from "react"
import { DayPicker } from "react-day-picker"
import { ChevronLeft, ChevronRight } from "lucide-react"

import { cn } from "@/lib/utils"

export type CalendarProps = React.ComponentProps<typeof DayPicker>

/**
 * Month grid on the Chronos tokens: 40 px day targets, today marked with a gold ring,
 * the selected day filled gold. Modifier classes land on the cell; the button inherits.
 */
function Calendar({
  className,
  classNames,
  showOutsideDays = true,
  ...props
}: CalendarProps) {
  return (
    <DayPicker
      showOutsideDays={showOutsideDays}
      className={cn("p-1", className)}
      classNames={{
        months: "relative flex flex-col",
        month: "flex flex-col gap-2",
        month_caption: "flex h-10 items-center px-2",
        caption_label: "font-display text-sm font-semibold",
        nav: "absolute right-0 top-0 flex items-center gap-1",
        button_previous:
          "grid size-10 place-items-center rounded-full text-muted-foreground transition-colors hover:bg-accent hover:text-foreground focus-visible:ring-[3px] focus-visible:ring-ring/50 outline-none disabled:opacity-40",
        button_next:
          "grid size-10 place-items-center rounded-full text-muted-foreground transition-colors hover:bg-accent hover:text-foreground focus-visible:ring-[3px] focus-visible:ring-ring/50 outline-none disabled:opacity-40",
        month_grid: "w-full border-collapse",
        weekdays: "flex",
        weekday: "w-10 flex-1 pb-1 text-center text-xs font-medium text-muted-foreground",
        week: "flex w-full",
        day: "group/day relative flex-1 p-0 text-center text-sm",
        day_button: cn(
          "mx-auto grid size-10 place-items-center rounded-full tabular-nums outline-none transition-colors duration-100",
          "hover:bg-accent focus-visible:ring-[3px] focus-visible:ring-ring/50",
          "group-data-[selected=true]/day:bg-primary group-data-[selected=true]/day:font-semibold group-data-[selected=true]/day:text-primary-foreground"
        ),
        selected: "",
        today: "[&>button]:ring-1 [&>button]:ring-inset [&>button]:ring-primary/70 [&>button]:font-semibold",
        outside: "text-muted-foreground/60",
        disabled: "pointer-events-none opacity-40",
        range_start: "",
        range_end: "",
        range_middle: "",
        hidden: "invisible",
        ...classNames,
      }}
      components={{
        Chevron: ({ orientation, className: chevronClass }) =>
          orientation === "left" ? (
            <ChevronLeft className={cn("size-4", chevronClass)} aria-hidden />
          ) : (
            <ChevronRight className={cn("size-4", chevronClass)} aria-hidden />
          ),
      }}
      {...props}
    />
  )
}

export { Calendar }
