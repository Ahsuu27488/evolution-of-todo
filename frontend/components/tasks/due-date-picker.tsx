/**
 * Due Date Picker Component
 *
 * Styled datetime-local input for task due dates.
 *
 * Per contracts/components.ts:
 * - Select date/time and format to ISO 8601
 * - Clear date to remove due_date
 * - Allow past dates (for overdue tasks)
 * - Visual indication of required state
 *
 * "use client"
 */

import { useState, useRef, ChangeEvent } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Calendar, X } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"

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
 * Format ISO 8601 datetime string to datetime-local input format (YYYY-MM-DDTHH:mm)
 */
function toDateTimeLocalValue(isoString: string | null): string {
  if (!isoString) return ""

  const date = new Date(isoString)
  if (isNaN(date.getTime())) return ""

  // Get local date components
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, "0")
  const day = String(date.getDate()).padStart(2, "0")
  const hours = String(date.getHours()).padStart(2, "0")
  const minutes = String(date.getMinutes()).padStart(2, "0")

  return `${year}-${month}-${day}T${hours}:${minutes}`
}

/**
 * Format datetime-local input value to ISO 8601 string
 *
 * The datetime-local input gives us "YYYY-MM-DDTHH:mm" which is in local time.
 * We need to convert this to ISO 8601 while preserving the local time.
 */
function fromDateTimeLocalValue(localValue: string): string {
  if (!localValue) return ""

  // Parse the datetime-local value (format: YYYY-MM-DDTHH:mm)
  const [datePart, timePart] = localValue.split("T")
  if (!datePart || !timePart) return ""

  const [year, month, day] = datePart.split("-").map(Number)
  const [hours, minutes] = timePart.split(":").map(Number)

  // Create Date object using local time components
  const date = new Date(year, month - 1, day, hours, minutes)

  // Return ISO string but ensure it represents the local time that was selected
  // by adding the timezone offset
  const tzOffset = date.getTimezoneOffset() * 60000 // offset in milliseconds
  const localISOTime = new Date(date.getTime() - tzOffset).toISOString()

  return localISOTime
}

/**
 * Format date for display (e.g., "Jan 15, 2026 5:00 PM")
 */
function formatDisplayDate(isoString: string): string {
  const date = new Date(isoString)
  return date.toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  })
}

/**
 * Check if a date is overdue
 */
function isOverdue(isoString: string): boolean {
  return new Date(isoString) < new Date()
}

/**
 * Check if a date is due soon (within 24 hours)
 */
function isDueSoon(isoString: string): boolean {
  const date = new Date(isoString)
  const now = new Date()
  const hoursUntil = (date.getTime() - now.getTime()) / (1000 * 60 * 60)
  return hoursUntil > 0 && hoursUntil <= 24
}

export function DueDatePicker({
  value,
  onChange,
  min,
  disabled = false,
  required = false,
  label = "Due Date",
  className,
}: DueDatePickerProps) {
  const [isFocused, setIsFocused] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const inputValue = toDateTimeLocalValue(value)
  const displayValue = value ? formatDisplayDate(value) : ""

  const hasValue = !!value
  const overdue = value && isOverdue(value)
  const dueSoon = value && isDueSoon(value)

  function handleChange(e: ChangeEvent<HTMLInputElement>) {
    const val = e.target.value
    if (val) {
      onChange(fromDateTimeLocalValue(val))
    } else {
      onChange(null)
    }
  }

  function handleClear() {
    onChange(null)
    inputRef.current?.focus()
  }

  return (
    <div className={cn("space-y-2", className)}>
      {/* Label */}
      {label && (
        <label className="text-sm font-medium text-foreground">
          {label}
          {required && <span className="text-destructive ml-1">*</span>}
        </label>
      )}

      {/* Input container */}
      <motion.div
        animate={{
          borderColor: isFocused
            ? "rgb(var(--primary) / 0.5)"
            : "rgb(var(--border) / 0.5)",
        }}
        className={cn(
          "relative flex items-center gap-2",
          "px-3 py-2 rounded-md border",
          "bg-background/50 transition-colors",
          "focus-within:ring-1 focus-within:ring-primary/20",
          disabled && "opacity-50 cursor-not-allowed"
        )}
      >
        {/* Calendar icon */}
        <Calendar
          className={cn(
            "h-4 w-4 shrink-0 transition-colors",
            overdue
              ? "text-destructive"
              : dueSoon
                ? "text-orange-500"
                : "text-muted-foreground"
          )}
        />

        {/* Hidden datetime-local input */}
        <input
          ref={inputRef}
          type="datetime-local"
          value={inputValue}
          onChange={handleChange}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          min={min}
          disabled={disabled}
          className={cn(
            "absolute inset-0 opacity-0 cursor-pointer",
            disabled && "cursor-not-allowed"
          )}
        />

        {/* Display value or placeholder */}
        <button
          type="button"
          onClick={() => inputRef.current?.focus()}
          disabled={disabled}
          className={cn(
            "flex-1 text-left text-sm outline-none",
            !hasValue && "text-muted-foreground",
            overdue && "text-destructive",
            dueSoon && !overdue && "text-orange-500",
            disabled && "cursor-not-allowed"
          )}
        >
          {displayValue || (hasValue ? "" : "Select date and time")}
        </button>

        {/* Clear button */}
        <AnimatePresence>
          {hasValue && !disabled && (
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
            >
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="h-6 w-6 p-0 hover:bg-destructive/20"
                onClick={handleClear}
              >
                <X className="h-3 w-3" />
              </Button>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>

      {/* Helper text */}
      {hasValue && (
        <p
          className={cn(
            "text-xs",
            overdue
              ? "text-destructive"
              : dueSoon
                ? "text-orange-500"
                : "text-muted-foreground"
          )}
        >
          {overdue && "This task is overdue"}
          {dueSoon && !overdue && "Due within 24 hours"}
          {!overdue && !dueSoon && "Due date set"}
        </p>
      )}
    </div>
  )
}
