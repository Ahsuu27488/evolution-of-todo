/** Dashboard toolbar: search, status filter, priority filter and sort, on solid surfaces.
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
import { ArrowDown, Search, CheckCircle2, Clock, X } from "lucide-react"
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
  { value: "all" as const, label: "All priorities" },
  { value: "HIGH" as const, label: "High", dot: "bg-destructive" },
  { value: "MEDIUM" as const, label: "Medium", dot: "bg-primary" },
  { value: "LOW" as const, label: "Low", dot: "bg-muted-foreground/60" },
]

const sortOptions = [
  { value: "created_at" as const, label: "Date added" },
  { value: "due_date" as const, label: "Due date" },
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
      <div className="flex flex-wrap items-center gap-2">
        {/* Left side: Search and filters */}
        <div className="contents">
          {/* Search input */}
          <div className="relative w-full">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <input
              type="search"
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
              placeholder="Search tasks"
              aria-label="Search tasks"
              className={cn(
                "h-11 w-full rounded-full pl-10 pr-11 md:h-10 [&::-webkit-search-cancel-button]:hidden",
                "border border-border bg-card hover:border-foreground/20",
                "text-sm placeholder:text-muted-foreground",
                "focus-visible:border-ring focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-ring/40",
                "transition-[border-color,box-shadow] duration-200"
              )}
            />
            {searchQuery && (
              <button
                type="button"
                onClick={() => onSearchChange("")}
                className="absolute right-1 top-1/2 grid size-9 -translate-y-1/2 place-items-center rounded-full text-muted-foreground outline-none transition-colors hover:bg-accent hover:text-foreground focus-visible:ring-[3px] focus-visible:ring-ring/50"
                aria-label="Clear search"
              >
                <X className="size-4" aria-hidden />
              </button>
            )}
          </div>

          {/* Status tabs */}
          <div
            className={cn(
              "inline-flex rounded-full border border-border bg-card p-1",
              "gap-1 w-full sm:w-auto"
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
                  aria-pressed={isActive}
                  className={cn(
                    "inline-flex h-9 flex-1 items-center justify-center gap-1.5 rounded-full px-3 text-[13px] font-medium outline-none transition-colors duration-150 focus-visible:ring-[3px] focus-visible:ring-ring/50 active:scale-[0.97] sm:flex-initial",
                    isActive
                      ? "bg-primary text-primary-foreground"
                      : "text-muted-foreground hover:bg-accent hover:text-foreground"
                  )}
                >
                  {Icon && <Icon className="h-3 w-3 sm:h-3.5 sm:w-3.5" />}
                  <span>{tab.label}</span>
                  {count > 0 && (
                    <span
                      className={cn(
                        "flex h-5 min-w-5 items-center justify-center rounded-full px-1.5 text-xs font-semibold tabular-nums",
                        isActive
                          ? "bg-primary-foreground/15 text-primary-foreground"
                          : "bg-muted text-muted-foreground"
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
              aria-label="Filter by priority"
              className="h-11 w-0 min-w-0 flex-1 rounded-full border-border bg-card dark:bg-card sm:w-[150px] sm:flex-none md:h-10"
            >
              {/* Short label for "all" so the trigger fits beside sort at 320 px */}
              <SelectValue placeholder="Priority">
                {priorityFilter === "all" ? "Priority" : priorities.find((p) => p.value === priorityFilter)?.label}
              </SelectValue>
            </SelectTrigger>
            <SelectContent>
              {priorities.map((p) => (
                <SelectItem key={p.value} value={p.value}>
                  {"dot" in p && <span className={cn("size-2 rounded-full", p.dot)} aria-hidden />}
                  {p.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Right side: Sort controls */}
        {/* On phones the sort controls join the priority filter row as equal columns */}
        <div className="contents sm:ml-auto sm:flex sm:items-center sm:gap-2">
          {/* Sort by dropdown */}
          <Select value={sortBy} onValueChange={onSortChange}>
            <SelectTrigger
              aria-label="Sort by"
              className="h-11 w-0 min-w-0 flex-1 rounded-full border-border bg-card dark:bg-card sm:w-[150px] sm:flex-none md:h-10"
            >
              <SelectValue placeholder="Sort by">
                {sortBy === "created_at" ? (
                  <>
                    <span className="sm:hidden">Added</span>
                    <span className="hidden sm:inline">Date added</span>
                  </>
                ) : (
                  sortOptions.find((o) => o.value === sortBy)?.label
                )}
              </SelectValue>
            </SelectTrigger>
            <SelectContent align="end">
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
              "grid size-11 shrink-0 place-items-center rounded-full md:size-10",
              "border border-border bg-card outline-none",
              "text-muted-foreground transition-colors duration-150",
              "hover:bg-accent hover:text-foreground focus-visible:ring-[3px] focus-visible:ring-ring/50 active:scale-95"
            )}
            title={sortOrder === "asc" ? "Ascending" : "Descending"}
            aria-label={`Sort ${sortOrder === "asc" ? "ascending" : "descending"}. Switch direction`}
          >
            <ArrowDown
              className={cn(
                "size-4 transition-transform duration-200",
                sortOrder === "asc" ? "rotate-180" : ""
              )}
              aria-hidden
            />
          </button>
        </div>
      </div>
    </motion.div>
  )
}
