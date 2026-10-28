/**
 * Due date picker: a field-styled trigger that opens a calendar with quick picks and a time.
 *
 * - Value in and out is a naive local ISO string (YYYY-MM-DDTHH:mm:ss); the backend stores it as is.
 * - Past dates are allowed (overdue tasks); `min` can restrict them.
 * - Overdue and "due within a day" are shown in the destructive and warning tones.
 */

"use client"

import { useState, useMemo } from "react"
import { Calendar as CalendarIcon, X } from "lucide-react"
import { addDays, isBefore, nextMonday, startOfDay } from "date-fns"
import { Calendar } from "@/components/ui/calendar"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { cn } from "@/lib/utils"

interface DueDatePickerProps {
  value: string | null // ISO 8601
  onChange: (date: string | null) => void
  min?: string // ISO 8601
  disabled?: boolean
  required?: boolean
  label?: string
  className?: string
}

function parseISODate(isoString: string | null): Date | null {
  if (!isoString) return null
  const date = new Date(isoString)
  return isNaN(date.getTime()) ? null : date
}

/** Local wall-clock time without an offset (the backend column is naive) */
function toNaiveISO(date: Date): string {
  const pad = (n: number) => String(n).padStart(2, "0")
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`
}

/** "Fri 30 Oct, 17:00" in the user's locale */
function formatDisplayDate(date: Date): string {
  return date.toLocaleString(undefined, {
    weekday: "short",
    day: "numeric",
    month: "short",
    year: date.getFullYear() === new Date().getFullYear() ? undefined : "numeric",
    hour: "2-digit",
    minute: "2-digit",
  })
}

function getTimezoneAbbreviation(): string {
  try {
    return (
      new Intl.DateTimeFormat(undefined, { timeZoneName: "short" })
        .formatToParts(new Date())
        .find((part) => part.type === "timeZoneName")?.value ?? ""
    )
  } catch {
    return ""
  }
}

export function DueDatePicker({
  value,
  onChange,
  min,
  disabled = false,
  required = false,
  label = "Due date",
  className: classNameProp,
}: DueDatePickerProps) {
  const [isOpen, setIsOpen] = useState(false)
  const tzAbbrev = useMemo(getTimezoneAbbreviation, [])
  const minDate = useMemo(() => parseISODate(min ?? null), [min])

  const currentDate = parseISODate(value)
  const hasValue = !!currentDate
  const now = new Date()
  const overdue = !!currentDate && isBefore(currentDate, now)
  const dueSoon = !!currentDate && !overdue && isBefore(currentDate, addDays(now, 1))

  // Keep the chosen time when the day changes; new dates default to 09:00
  const hours = currentDate?.getHours() ?? 9
  const minutes = currentDate?.getMinutes() ?? 0

  function setDay(day: Date) {
    const next = new Date(day)
    next.setHours(hours, minutes, 0, 0)
    onChange(toNaiveISO(next))
  }

  function handleTimeChange(time: string) {
    const [h, m] = time.split(":").map((n) => parseInt(n, 10))
    if (isNaN(h) || isNaN(m)) return
    const next = new Date(currentDate ?? startOfDay(now))
    next.setHours(h, m, 0, 0)
    onChange(toNaiveISO(next))
  }

  const quickPicks = [
    { label: "Today", day: now },
    { label: "Tomorrow", day: addDays(now, 1) },
    { label: "Next week", day: nextMonday(now) },
  ]

  const toneText = overdue ? "text-destructive" : dueSoon ? "text-warning" : undefined

  return (
    <div className={cn("grid gap-2", classNameProp)}>
      {label && (
        <Label>
          {label}
          {required && <span className="text-destructive">*</span>}
        </Label>
      )}

      <div className="relative">
        <Popover open={isOpen && !disabled} onOpenChange={(open) => !disabled && setIsOpen(open)}>
          <PopoverTrigger asChild>
            <button
              type="button"
              disabled={disabled}
              aria-label={hasValue ? `Due ${formatDisplayDate(currentDate)}. Change date` : "Pick a due date"}
              className={cn(
                "flex h-11 w-full items-center gap-2.5 rounded-[var(--radius-md)] border border-input bg-transparent pl-3.5 text-left text-sm outline-none md:h-10 dark:bg-input/30",
                "transition-[border-color,box-shadow] hover:border-foreground/25 focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50",
                "disabled:cursor-not-allowed disabled:opacity-50 data-[state=open]:border-ring",
                hasValue ? "pr-11" : "pr-3.5"
              )}
            >
              <CalendarIcon className={cn("size-4 shrink-0 text-muted-foreground", toneText)} aria-hidden />
              <span className={cn("flex-1 truncate tabular-nums", !hasValue && "text-muted-foreground", toneText)}>
                {hasValue ? formatDisplayDate(currentDate) : "No due date"}
              </span>
            </button>
          </PopoverTrigger>

          <PopoverContent className="w-[min(20.5rem,calc(100vw-1.5rem))] p-2" align="start" sideOffset={6}>
            <div className="flex gap-1.5 px-1 pt-1 pb-2">
              {quickPicks.map((pick) => (
                <button
                  key={pick.label}
                  type="button"
                  onClick={() => {
                    setDay(pick.day)
                    setIsOpen(false)
                  }}
                  className="h-9 flex-1 rounded-full border border-border text-xs font-medium text-muted-foreground outline-none transition-colors hover:bg-accent hover:text-foreground focus-visible:ring-[3px] focus-visible:ring-ring/50 active:scale-[0.97]"
                >
                  {pick.label}
                </button>
              ))}
            </div>

            <Calendar
              mode="single"
              selected={currentDate ?? undefined}
              defaultMonth={currentDate ?? undefined}
              onSelect={(day) => day && setDay(day)}
              disabled={(date) => (minDate ? isBefore(date, startOfDay(minDate)) : false)}
            />

            <div className="mt-1 flex items-center gap-2 border-t border-border px-1 pt-3 pb-1">
              <Label htmlFor="due-time" className="text-muted-foreground font-normal">
                Time
              </Label>
              <Input
                id="due-time"
                type="time"
                value={`${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}`}
                onChange={(e) => handleTimeChange(e.target.value)}
                className="h-10 w-[8.5rem] tabular-nums dark:[color-scheme:dark]"
              />
              {tzAbbrev && <span className="text-xs text-muted-foreground">{tzAbbrev}</span>}
              <Button type="button" size="sm" className="ml-auto rounded-full" onClick={() => setIsOpen(false)}>
                Done
              </Button>
            </div>
          </PopoverContent>
        </Popover>

        {hasValue && !disabled && (
          <button
            type="button"
            onClick={() => onChange(null)}
            aria-label="Clear due date"
            className="absolute top-1/2 right-1 grid size-9 -translate-y-1/2 place-items-center rounded-full text-muted-foreground outline-none transition-colors hover:bg-accent hover:text-foreground focus-visible:ring-[3px] focus-visible:ring-ring/50"
          >
            <X className="size-4" />
          </button>
        )}
      </div>

      {(overdue || dueSoon) && (
        <p className={cn("text-[13px]", toneText)}>{overdue ? "This date has passed" : "Due within 24 hours"}</p>
      )}
    </div>
  )
}
