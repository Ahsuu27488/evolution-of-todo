/** Dashboard Content Component with Toolbar Integration.
 *
 * Per spec.md US2: Filter tasks by status and priority, search through tasks in real-time.
 * Per spec.md US3: Sort tasks by created date, due date, priority, or title with ascending/descending toggle.
 * Per spec.md US4: Glassmorphism visual design matching hero page aesthetic.
 *
 * [T021-T026] Enhanced with dual-ring loading states and error handling.
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

import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import Link from "next/link"
import { fadeInUp } from "@/lib/animations"
import { TaskForm } from "@/components/tasks/task-form"
import { TaskList } from "@/components/tasks/task-list"
import { DashboardToolbar } from "@/components/dashboard/dashboard-toolbar"
import { DualRingSpinner } from "@/components/ui/dual-ring-spinner"
import { LoadingErrorCard } from "@/components/dashboard/loading-error-card"
import { OrbitPanel } from "@/components/dashboard/orbit-panel"
import { useUIStore } from "@/lib/stores/ui-store"
import { useTaskFilters } from "@/lib/hooks/use-task-filters"
import { Button } from "@/components/ui/button"

interface DashboardContentProps {
  isAuthenticated?: boolean
}

export function DashboardContent({
  isAuthenticated = false
}: DashboardContentProps) {
  // Local state for search query (not persisted to store)
  const [searchQuery, setSearchQuery] = useState("")

  // Get filter state from ui-store (stable reference)
  const filters = useUIStore((state) => state.filters)

  // Get actions from ui-store using useCallback for stable references
  const setStatusFilter = useUIStore((state) => state.setFilterStatus)
  const setPriorityFilter = useUIStore((state) => state.setFilterPriority)
  const setSortBy = useUIStore((state) => state.setSortBy)

  // [T021] Use the useTaskFilters hook with loading and error states
  const {
    displayTasks: filteredTasks,
    totalCount,
    pendingCount,
    completedCount,
    setSearchQuery: setDebouncedSearch,
    toggleSortOrder,
    isLoading,  // [T021] Loading state for spinner
    error,      // [T021] Error state for error card
    refetch,    // [T021] Refetch function for retry
  } = useTaskFilters()

  // Update debounced search when local query changes
  useEffect(() => {
    setDebouncedSearch(searchQuery)
  }, [searchQuery, setDebouncedSearch])

  // Show login prompt if not authenticated
  if (!isAuthenticated) {
    return (
      <motion.div
        variants={fadeInUp}
        initial="hidden"
        animate="visible"
        className="mx-auto max-w-md text-center py-12"
      >
        <h2 className="text-2xl font-semibold mb-4">Sign in to see your tasks</h2>
        <p className="text-muted-foreground mb-6">
          Your session ended or you are not signed in yet.
        </p>
        <div className="flex gap-4 justify-center">
          <Button asChild>
            <Link href="/login">Sign in</Link>
          </Button>
          <Button asChild variant="outline">
            <Link href="/signup">Create account</Link>
          </Button>
        </div>
      </motion.div>
    )
  }

  const todayLabel = new Intl.DateTimeFormat(undefined, {
    weekday: "long",
    day: "numeric",
    month: "long",
  }).format(new Date())

  return (
    <motion.div
      variants={fadeInUp}
      initial="hidden"
      animate="visible"
      className="mx-auto grid w-full max-w-6xl gap-6 lg:grid-cols-[minmax(0,17.5rem)_minmax(0,1fr)] lg:gap-10"
    >
      <OrbitPanel className="lg:sticky lg:top-24 lg:self-start" />

      <section aria-labelledby="tasks-title" className="min-w-0">
        {/* Heading with the add button */}
        <div className="mb-5 flex items-end justify-between gap-3">
          <div>
            {/* Locale and time zone differ between server and browser; the browser's value wins */}
            <p className="text-sm text-muted-foreground" suppressHydrationWarning>{todayLabel}</p>
            <h1 id="tasks-title" className="text-[length:var(--step-h1)] font-semibold leading-tight">
              My tasks
            </h1>
          </div>
          <div className="shrink-0">
            <TaskForm />
          </div>
        </div>

        {/* Search, filters and sort */}
        <DashboardToolbar
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          statusFilter={filters.status}
          onStatusChange={setStatusFilter}
          priorityFilter={filters.priority}
          onPriorityChange={setPriorityFilter}
          sortBy={filters.sortBy}
          onSortChange={setSortBy}
          sortOrder={filters.sortOrder}
          onSortOrderToggle={toggleSortOrder}
          totalCount={totalCount}
          pendingCount={pendingCount}
          completedCount={completedCount}
        />

        {/* Task list with loading and error states */}
        <div className="relative min-h-[300px]">
          {isLoading ? (
            <div className="flex h-full min-h-[250px] items-center justify-center sm:min-h-[300px]">
              <DualRingSpinner show={true} />
            </div>
          ) : error ? (
            <LoadingErrorCard
              message="Unable to load tasks. Please check your connection and try again."
              onRetry={() => refetch()}
              isRetrying={isLoading}
            />
          ) : (
            <TaskList tasks={filteredTasks} />
          )}
        </div>
      </section>
    </motion.div>
  )
}
