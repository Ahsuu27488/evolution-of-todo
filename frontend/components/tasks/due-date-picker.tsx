/**
 * Due Date Picker Component
 *
 * Custom date-time picker with calendar, time selection, and timezone support.
 * Uses react-day-picker with glassmorphism styling matching the app theme.
 *
 * Per contracts/components.ts:
 * - Select date/time and format to ISO 8601
 * - Clear date to remove due_date
 * - Allow past dates (for overdue tasks)
 * - Visual indication of required state
 * - Timezone aware for global users
 *
 * "use client"
 */

import { useState, useMemo } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Calendar as CalendarIcon, X, Clock } from "lucide-react"
import { isBefore } from "date-fns"
import { Calendar } from "@/components/ui/calendar"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"
import { cn } from "@/lib/utils"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

interface DueDatePickerProps {
  value: string | null // ISO 8601
  onChange: (date: string | null) => void
  min?: string // ISO 8601
  disabled?: boolean
  required?: boolean
  label?: string
  className?: string
}

/**
 * Parse ISO 8601 string to Date object, preserving local timezone
 */
function parseISODate(isoString: string | null): Date | null {
  if (!isoString) return null
  const date = new Date(isoString)
  return isNaN(date.getTime()) ? null : date
}

/**
 * Format Date object to ISO 8601 string in UTC format.
 * Creates a UTC timestamp that backend can parse as naive datetime.
 */
function toISOWithTimezone(date: Date): string {
  // Create a Date object and use toISOString() to get UTC format
  // This preserves the local time values but outputs in UTC
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, "0")
  const day = String(date.getDate()).padStart(2, "0")
  const hours = String(date.getHours()).padStart(2, "0")
  const minutes = String(date.getMinutes()).padStart(2, "0")
  const seconds = String(date.getSeconds()).padStart(2, "0")

  // Return ISO format without timezone info (naive datetime)
  // Backend will store this as-is in TIMESTAMP WITHOUT TIME ZONE column
  return `${year}-${month}-${day}T${hours}:${minutes}:${seconds}`
}

/**
 * Format date for display (e.g., "Jan 15, 2026 5:00 PM")
 * Shows timezone abbreviation for global users
 */
function formatDisplayDate(isoString: string, timezone?: string): string {
  const date = new Date(isoString)
  return date.toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
    timeZone: timezone,
  })
}

/**
 * Check if a date is overdue
 */
function isOverdue(date: Date): boolean {
  return isBefore(date, new Date())
}

/**
 * Check if a date is due soon (within 24 hours)
 */
function isDueSoon(date: Date): boolean {
  const now = new Date()
  const tomorrow = new Date(now)
  tomorrow.setDate(tomorrow.getDate() + 1)
  return !isBefore(date, now) && isBefore(date, tomorrow)
}

/**
 * Get user's local timezone
 */
function getUserTimezone(): string {
  if (typeof window === "undefined") return "UTC"
  return Intl.DateTimeFormat().resolvedOptions().timeZone
}

/**
 * Get timezone abbreviation (e.g., "PST", "EST")
 */
function getTimezoneAbbreviation(timezone: string): string {
  try {
    const tz = new Intl.DateTimeFormat("en-US", {
      timeZone: timezone,
      timeZoneName: "short",
    })
    return tz.formatToParts(new Date()).find((part) => part.type === "timeZoneName")?.value || timezone
  } catch {
    return timezone
  }
}

export function DueDatePicker({
  value,
  onChange,
  min,
  disabled = false,
  required = false,
  label = "Due Date",
  className: classNameProp,
}: DueDatePickerProps) {
  const [isOpen, setIsOpen] = useState(false)

  // Get user's timezone once (memoized)
  const userTimezone = useMemo(getUserTimezone, [])
  const tzAbbrev = useMemo(() => getTimezoneAbbreviation(userTimezone), [userTimezone])

  // Parse current value
  const currentDate = parseISODate(value)

  // Extract time components
  const hours = currentDate?.getHours() ?? 12
  const minutes = currentDate?.getMinutes() ?? 0

  const hasValue = !!value && !!currentDate
  const overdue = currentDate && isOverdue(currentDate)
  const dueSoon = currentDate && isDueSoon(currentDate)

  // Min date constraint
  const minDate = useMemo(() => parseISODate(min ?? null), [min])

  /**
   * Handle date selection from calendar
   */
  function handleDateSelect(date: Date | undefined) {
    if (!date) {
      onChange(null)
      setIsOpen(false)
      return
    }

    // Create new Date with selected date and existing time
    const newDate = new Date(date)
    newDate.setHours(hours, minutes, 0, 0)

    onChange(toISOWithTimezone(newDate))
  }

  /**
   * Handle time input changes
   */
  function handleTimeChange(field: "hours" | "minutes", value: string) {
    const num = parseInt(value, 10)
    if (isNaN(num)) return

    const baseDate = currentDate || new Date()
    const newDate = new Date(baseDate)

    if (field === "hours") {
      newDate.setHours(Math.max(0, Math.min(23, num)))
    } else {
      newDate.setMinutes(Math.max(0, Math.min(59, num)))
    }

    newDate.setSeconds(0, 0)
    onChange(toISOWithTimezone(newDate))
  }

  /**
   * Clear the date value
   */
  function handleClear() {
    onChange(null)
  }

  /**
   * Handle calendar close
   */
  function handleOpenChange(open: boolean) {
    // Only allow opening if not disabled
    if (!disabled) {
      setIsOpen(open)
    }
  }

  return (
    <div className={cn("space-y-3", classNameProp)}>
      {/* Label */}
      {label && (
        <Label className="text-sm font-medium">
          {label}
          {required && <span className="text-destructive ml-1">*</span>}
        </Label>
      )}

      {/* Date picker button */}
      <div className="relative">
        <Popover open={isOpen && !disabled} onOpenChange={handleOpenChange}>
          <PopoverTrigger asChild>
            <motion.button
              type="button"
              disabled={disabled}
              whileHover={{ scale: disabled ? 1 : 1.01 }}
              whileTap={{ scale: disabled ? 1 : 0.99 }}
              className={cn(
                "glass-strong w-full flex items-center gap-3 px-4 py-3 rounded-md border",
                "text-left transition-all duration-200",
                "hover:border-primary/30",
                "focus:outline-none focus:ring-2 focus:ring-primary/20",
                disabled && "opacity-50 cursor-not-allowed",
                isOpen && "ring-2 ring-primary/20 border-primary/30"
              )}
            >
              {/* Calendar icon with status color */}
              <CalendarIcon
                className={cn(
                  "h-4 w-4 shrink-0 transition-colors",
                  overdue
                    ? "text-destructive"
                    : dueSoon
                      ? "text-orange-500"
                      : "text-primary"
                )}
              />

              {/* Display value or placeholder */}
              <span
                className={cn(
                  "flex-1 text-sm",
                  !hasValue && "text-muted-foreground",
                  overdue && "text-destructive",
                  dueSoon && !overdue && "text-orange-500"
                )}
              >
                {hasValue
                  ? formatDisplayDate(value!, userTimezone)
                  : "Select date and time"}
              </span>

              {/* Spacer for clear button */}
              {hasValue && !disabled && <div className="w-6" />}
            </motion.button>
          </PopoverTrigger>

        {/* Popover content with calendar and time picker */}
        <PopoverContent className="w-[320px] p-0" side="top" align="start" sideOffset={8}>
          <div className="p-2 space-y-2">
            {/* Calendar */}
            <Calendar
              mode="single"
              selected={currentDate ?? undefined}
              onSelect={handleDateSelect}
              disabled={(date) => minDate ? isBefore(date, minDate) : false}
            />

            {/* Divider */}
            <div className="border-t border-border/50 my-1" />

            {/* Time picker */}
            <div className="flex items-center gap-2">
              <Clock className="h-3 w-3 text-muted-foreground shrink-0" />
              <Input
                type="number"
                min="0"
                max="23"
                value={String(hours).padStart(2, "0")}
                onChange={(e) => handleTimeChange("hours", e.target.value)}
                className="h-7 w-14 text-center font-mono text-xs px-2 [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none [-moz-appearance:textfield]"
                disabled={disabled}
              />
              <span className="text-muted-foreground">:</span>
              <Input
                type="number"
                min="0"
                max="59"
                value={String(minutes).padStart(2, "0")}
                onChange={(e) => handleTimeChange("minutes", e.target.value)}
                className="h-7 w-14 text-center font-mono text-xs px-2 [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none [-moz-appearance:textfield]"
                disabled={disabled}
              />
              <span className="text-[9px] text-muted-foreground ml-auto">
                {tzAbbrev}
              </span>
            </div>
          </div>
        </PopoverContent>
      </Popover>

        {/* Clear button - positioned absolutely over the trigger */}
        <AnimatePresence>
          {hasValue && !disabled && (
            <motion.button
              type="button"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              onClick={handleClear}
              className="absolute right-3 top-1/2 -translate-y-1/2 h-6 w-6 p-0 rounded-md hover:bg-destructive/20 flex items-center justify-center transition-colors z-10"
            >
              <X className="h-3 w-3 text-muted-foreground hover:text-destructive" />
            </motion.button>
          )}
        </AnimatePresence>
      </div>

      {/* Helper text */}
      {hasValue && (
        <motion.p
          initial={{ opacity: 0, y: -4 }}
          animate={{ opacity: 1, y: 0 }}
          className={cn(
            "text-xs flex items-center gap-1",
            overdue
              ? "text-destructive"
              : dueSoon
                ? "text-orange-500"
                : "text-muted-foreground"
          )}
        >
          {overdue && (
            <>
              <span className="inline-block w-1.5 h-1.5 rounded-full bg-destructive animate-pulse" />
              This task is overdue
            </>
          )}
          {dueSoon && !overdue && (
            <>
              <span className="inline-block w-1.5 h-1.5 rounded-full bg-orange-500 animate-pulse" />
              Due within 24 hours
            </>
          )}
          {!overdue && !dueSoon && "Due date set"}
        </motion.p>
      )}
    </div>
  )
}
