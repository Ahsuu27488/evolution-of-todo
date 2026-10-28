/** Sort dropdown with a direction toggle (standalone version of the toolbar's sort controls).
 *
 * Not mounted at the moment: the dashboard toolbar renders the same controls inline. Kept on the
 * same tokens so it can be dropped in elsewhere.
 */

"use client"

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { ArrowDown } from "lucide-react"
import { cn } from "@/lib/utils"
import type { FilterState } from "@/lib/stores/ui-store"

interface SortDropdownProps {
  value: FilterState["sortBy"]
  order: FilterState["sortOrder"]
  onSortChange: (sortBy: FilterState["sortBy"]) => void
  onOrderToggle: () => void
}

const sortOptions = [
  { value: "created_at" as const, label: "Created date", description: "Newest or oldest first" },
  { value: "due_date" as const, label: "Due date", description: "Soonest or latest first" },
  { value: "priority" as const, label: "Priority", description: "High to low" },
  { value: "title" as const, label: "Title", description: "Alphabetical" },
]

export function SortDropdown({ value, order, onSortChange, onOrderToggle }: SortDropdownProps) {
  return (
    <div className="flex items-center gap-2">
      <Select value={value} onValueChange={onSortChange}>
        <SelectTrigger aria-label="Sort by" className="h-10 min-w-40 rounded-full bg-card md:h-10">
          <SelectValue placeholder="Sort by" />
        </SelectTrigger>
        <SelectContent>
          {sortOptions.map((opt) => (
            <SelectItem key={opt.value} value={opt.value} description={opt.description}>
              {opt.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      <button
        type="button"
        onClick={onOrderToggle}
        aria-label={`Sort ${order === "asc" ? "ascending" : "descending"}. Switch direction`}
        className="grid size-10 shrink-0 place-items-center rounded-full border border-border bg-card text-muted-foreground outline-none transition-colors hover:bg-accent hover:text-foreground focus-visible:ring-[3px] focus-visible:ring-ring/50 active:scale-95"
      >
        <ArrowDown
          className={cn("size-4 transition-transform duration-200", order === "asc" && "rotate-180")}
          aria-hidden
        />
      </button>
    </div>
  )
}
