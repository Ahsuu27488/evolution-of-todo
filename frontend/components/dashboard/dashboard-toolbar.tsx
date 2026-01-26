/** Dashboard Toolbar Component with Deep Space Glassmorphism.
 *
 * Per spec.md US2: Filter tasks by status and priority, search through tasks in real-time.
 * Per contracts/components.ts: DashboardToolbar integrates search, filter, and sort controls.
 *
 * Acceptance Scenarios (US2):
 * - Given an authenticated user with multiple tasks, When they type in the search bar,
 *   Then the task list updates in real-time (debounced) to show only matching tasks
 * - Given a user viewing all tasks, When they click the "Pending" tab,
 *   Then only incomplete tasks are displayed
 * - Given a user viewing filtered tasks, When they select "High" from the priority dropdown,
 *   Then only high-priority tasks matching the current status filter are shown
 */

"use client"

import { motion } from "framer-motion"
import { Search, CheckCircle2, Clock } from "lucide-react"
import { cn } from "@/lib/utils"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import type { FilterState } from "@/lib/stores/ui-store"

interface DashboardToolbarProps {
  // Search
  searchQuery: string
  onSearchChange: (query: string) => void

  // Filters
  statusFilter: FilterState["status"]
  onStatusChange: (status: FilterState["status"]) => void
  priorityFilter: FilterState["priority"]
  onPriorityChange: (priority: FilterState["priority"]) => void

  // Sort
  sortBy: FilterState["sortBy"]
  onSortChange: (sortBy: FilterState["sortBy"]) => void
  sortOrder: FilterState["sortOrder"]
  onSortOrderToggle: () => void

  // Task counts for display
  totalCount?: number
  pendingCount?: number
  completedCount?: number
}

const statusTabs = [
  { value: "all" as const, label: "All", icon: null },
  { value: "pending" as const, label: "Pending", icon: Clock },
  { value: "completed" as const, label: "Done", icon: CheckCircle2 },
]

const priorities = [
  { value: "all" as const, label: "All Priorities" },
  { value: "HIGH" as const, label: "High", color: "text-destructive" },
  { value: "MEDIUM" as const, label: "Medium", color: "text-secondary" },
  { value: "LOW" as const, label: "Low", color: "text-muted-foreground" },
]

const sortOptions = [
  { value: "created_at" as const, label: "Created Date" },
  { value: "due_date" as const, label: "Due Date" },
  { value: "priority" as const, label: "Priority" },
  { value: "title" as const, label: "Title" },
]

export function DashboardToolbar({
  searchQuery,
  onSearchChange,
  statusFilter,
  onStatusChange,
  priorityFilter,
  onPriorityChange,
  sortBy,
  onSortChange,
  sortOrder,
  onSortOrderToggle,
  totalCount = 0,
  pendingCount = 0,
  completedCount = 0,
}: DashboardToolbarProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="mb-6"
    >
      {/* Main toolbar container */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        {/* Left side: Search and filters */}
        <div className="flex flex-1 flex-col gap-2 sm:flex-row sm:items-center sm:gap-3">
          {/* Search input */}
          <div className="relative flex-1 sm:max-w-xs">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
              placeholder="Search tasks..."
              className={cn(
                "glass h-10 w-full rounded-full pl-10 pr-4",
                "border border-border/50 bg-background/50",
                "text-sm placeholder:text-muted-foreground",
                "focus:border-primary/50 focus:ring-1 focus:ring-primary/20",
                "transition-all duration-200"
              )}
            />
            {searchQuery && (
              <button
                type="button"
                onClick={() => onSearchChange("")}
                className="absolute right-3 top-1/2 flex h-6 w-6 -translate-y-1/2 items-center justify-center rounded-full bg-muted-foreground/20 text-muted-foreground hover:bg-muted-foreground/30"
                aria-label="Clear search"
              >
                ×
              </button>
            )}
          </div>

          {/* Status tabs */}
          <div
            className={cn(
              "glass inline-flex flex-wrap rounded-full border border-border/50 bg-background/50 p-1",
              "gap-1 flex-1 sm:flex-initial"
            )}
          >
            {statusTabs.map((tab) => {
              const Icon = tab.icon
              const isActive = statusFilter === tab.value
              const count =
                tab.value === "all"
                  ? totalCount
                  : tab.value === "pending"
                    ? pendingCount
                    : completedCount

              return (
                <button
                  key={tab.value}
                  type="button"
                  onClick={() => onStatusChange(tab.value)}
                  className={cn(
                    "inline-flex flex-1 items-center justify-center gap-1 rounded-full px-2 py-1 text-xs font-medium transition-all duration-200 sm:gap-1.5 sm:px-3 sm:py-1.5 sm:flex-initial",
                    isActive
                      ? "bg-primary/20 text-primary shadow-[0_0_10px_rgba(0,245,255,0.2)]"
                      : "text-muted-foreground hover:bg-muted/50"
                  )}
                >
                  {Icon && <Icon className="h-3 w-3 sm:h-3.5 sm:w-3.5" />}
                  <span>{tab.label}</span>
                  {count > 0 && (
                    <span
                      className={cn(
                        "flex h-5 min-w-[20px] items-center justify-center rounded-full px-1 text-xs font-semibold",
                        isActive
                          ? "bg-primary/30 text-primary"
                          : "bg-muted-foreground/20 text-muted-foreground"
                      )}
                    >
                      {count}
                    </span>
                  )}
                </button>
              )
            })}
          </div>

          {/* Priority dropdown */}
          <Select value={priorityFilter} onValueChange={onPriorityChange}>
            <SelectTrigger
              className={cn(
                "glass h-10 w-full border border-border/50 bg-background/50 sm:w-[140px]",
                "focus:border-primary/50 focus:ring-1 focus:ring-primary/20"
              )}
            >
              <SelectValue placeholder="Priority" />
            </SelectTrigger>
            <SelectContent className="glass-strong">
              {priorities.map((p) => (
                <SelectItem key={p.value} value={p.value} className={p.color}>
                  {p.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Right side: Sort controls */}
        <div className="flex items-center gap-2">
          {/* Sort by dropdown */}
          <Select value={sortBy} onValueChange={onSortChange}>
            <SelectTrigger
              className={cn(
                "glass h-10 w-full border border-border/50 bg-background/50 sm:w-[140px]",
                "focus:border-primary/50 focus:ring-1 focus:ring-primary/20"
              )}
            >
              <SelectValue placeholder="Sort by" />
            </SelectTrigger>
            <SelectContent className="glass-strong">
              {sortOptions.map((opt) => (
                <SelectItem key={opt.value} value={opt.value}>
                  {opt.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          {/* Sort order toggle button */}
          <button
            type="button"
            onClick={onSortOrderToggle}
            className={cn(
              "glass flex h-10 w-10 items-center justify-center rounded-full",
              "border border-border/50 bg-background/50",
              "text-muted-foreground transition-all duration-200",
              "hover:bg-muted/50 hover:text-foreground",
              "focus:border-primary/50 focus:ring-1 focus:ring-primary/20"
            )}
            title={`Sort ${sortOrder === "asc" ? "ascending" : "descending"}`}
            aria-label={`Toggle sort order (currently ${sortOrder})`}
          >
            <span
              className={cn(
                "text-sm font-semibold",
                sortOrder === "asc" ? "rotate-180" : ""
              )}
            >
              ↓
            </span>
          </button>
        </div>
      </div>
    </motion.div>
  )
}
