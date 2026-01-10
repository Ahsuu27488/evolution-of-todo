/** Sort Dropdown Component with Direction Toggle.
 *
 * Per spec.md US3: Sort tasks by created date, due date, priority, or title with ascending/descending toggle.
 * Per contracts/components.ts: SortDropdown with sort criterion options and direction toggle button.
 *
 * Acceptance Scenarios (US3):
 * - Given an authenticated user with tasks, When they select "Due Date" from the sort dropdown,
 *   Then tasks reorder with those having due dates at the top
 * - Given a user with tasks sorted by due date, When they click the sort direction toggle,
 *   Then the sort order reverses (ascending vs descending)
 */

"use client"

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Button } from "@/components/ui/button"
import { ArrowUpDown } from "lucide-react"
import { cn } from "@/lib/utils"
import type { FilterState } from "@/lib/stores/ui-store"

interface SortDropdownProps {
  value: FilterState["sortBy"]
  order: FilterState["sortOrder"]
  onSortChange: (sortBy: FilterState["sortBy"]) => void
  onOrderToggle: () => void
}

const sortOptions = [
  { value: "created_at" as const, label: "Created Date", description: "When task was added" },
  { value: "due_date" as const, label: "Due Date", description: "Task deadline" },
  { value: "priority" as const, label: "Priority", description: "Task importance" },
  { value: "title" as const, label: "Title", description: "Alphabetical order" },
]

export function SortDropdown({
  value,
  order,
  onSortChange,
  onOrderToggle,
}: SortDropdownProps) {
  const selectedOption = sortOptions.find((opt) => opt.value === value)

  return (
    <div className="flex items-center gap-2">
      {/* Sort by dropdown */}
      <Select value={value} onValueChange={onSortChange}>
        <SelectTrigger
          className={cn(
            "glass h-10 min-w-[140px] border border-border/50 bg-background/50",
            "focus:border-primary/50 focus:ring-1 focus:ring-primary/20"
          )}
        >
          <SelectValue placeholder="Sort by">
            <span className="flex items-center gap-2">
              <span className="text-xs text-muted-foreground">Sort:</span>
              <span>{selectedOption?.label}</span>
            </span>
          </SelectValue>
        </SelectTrigger>
        <SelectContent className="glass-strong">
          {sortOptions.map((opt) => (
            <SelectItem key={opt.value} value={opt.value}>
              <div className="flex flex-col">
                <span>{opt.label}</span>
                <span className="text-xs text-muted-foreground">
                  {opt.description}
                </span>
              </div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      {/* Sort direction toggle */}
      <Button
        type="button"
        variant="ghost"
        size="sm"
        onClick={onOrderToggle}
        className={cn(
          "glass h-10 px-3",
          "border border-border/50 bg-background/50",
          "text-muted-foreground transition-all duration-200",
          "hover:bg-muted/50 hover:text-foreground"
        )}
        title={`Currently: ${order === "asc" ? "Ascending (A→Z)" : "Descending (Z→A)"}`}
      >
        <ArrowUpDown
          className={cn(
            "h-4 w-4 transition-transform duration-200",
            order === "asc" ? "rotate-180" : ""
          )}
        />
        <span className="ml-2 text-xs">
          {order === "asc" ? "Asc" : "Desc"}
        </span>
      </Button>
    </div>
  )
}
