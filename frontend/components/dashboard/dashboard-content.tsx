/** Dashboard Content Component with Toolbar Integration.
 *
 * Per spec.md US2: Filter tasks by status and priority, search through tasks in real-time.
 * Per spec.md US3: Sort tasks by created date, due date, priority, or title with ascending/descending toggle.
 * Per spec.md US4: Glassmorphism visual design matching hero page aesthetic.
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

  // Use the useTaskFilters hook for filtered/sorted tasks and stable actions
  const {
    displayTasks: filteredTasks,
    totalCount,
    pendingCount,
    completedCount,
    setSearchQuery: setDebouncedSearch,
    toggleSortOrder,
    isLoading,
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
        <h2 className="text-2xl font-bold mb-4">Welcome to Todo App</h2>
        <p className="text-muted-foreground mb-6">
          Please sign in to manage your tasks.
        </p>
        <div className="flex gap-4 justify-center">
          <Link href="/login">
            <Button>Sign In</Button>
          </Link>
          <Link href="/signup">
            <Button variant="outline">Sign Up</Button>
          </Link>
        </div>
      </motion.div>
    )
  }

  return (
    <motion.div
      variants={fadeInUp}
      initial="hidden"
      animate="visible"
      className="mx-auto max-w-3xl"
    >
      {/* Dashboard Toolbar - integrates search, filters, and sort */}
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

      {/* Section header with title and add button */}
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-3xl font-bold bg-linear-to-r from-primary via-secondary to-primary bg-clip-text text-transparent animate-gradient bg-[length:200%_auto]">
          My Tasks
        </h1>

        {/* Floating Action Button */}
        <motion.div
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="shrink-0"
        >
          <TaskForm />
        </motion.div>
      </div>

      {/* Task count or empty state message */}
      {!isLoading && filteredTasks.length === 0 ? (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center py-12"
        >
          {searchQuery || filters.status !== "all" || filters.priority !== "all" ? (
            <>
              <p className="text-muted-foreground text-lg mb-2">
                No tasks match your filters
              </p>
              <p className="text-muted-foreground text-sm">
                Try adjusting your search or filters
              </p>
            </>
          ) : (
            <>
              <p className="text-muted-foreground text-lg mb-2">
                No tasks yet
              </p>
              <p className="text-muted-foreground text-sm">
                Create your first task to get started!
              </p>
            </>
          )}
        </motion.div>
      ) : null}

      {/* Task List */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <TaskList tasks={filteredTasks} />
      </motion.div>
    </motion.div>
  )
}
