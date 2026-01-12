/**
 * useTaskFilters Hook
 *
 * Composes filter and sort logic with TanStack Query for task management.
 * Integrates with ui-store for persistent filter state.
 *
 * This hook provides:
 * - Filtered and sorted task list
 * - Task counts by status
 * - Search functionality with debouncing
 * - Integration with ui-store for persistence
 */

"use client"

import { useMemo, useEffect, useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { api } from "@/lib/api-client"
import { useUIStore, type FilterState } from "@/lib/stores/ui-store"
import { useDebounce } from "./use-debounce"
import type { Task } from "@/types/task"

// =============================================================================
// Sort Configuration
// =============================================================================

interface SortConfig {
  field: FilterState["sortBy"]
  order: FilterState["sortOrder"]
}

/** Priority values for sorting (HIGH=3, MEDIUM=2, LOW=1) */
const PRIORITY_VALUE: Record<string, number> = {
  HIGH: 3,
  MEDIUM: 2,
  LOW: 1,
}

// =============================================================================
// Sorting Functions
// =============================================================================

/**
 * Sort tasks by the configured field and order.
 *
 * @param tasks - Tasks to sort
 * @param config - Sort configuration
 * @returns Sorted tasks array
 */
function sortTasks(tasks: Task[], config: SortConfig): Task[] {
  const { field, order } = config
  const direction = order === "asc" ? 1 : -1

  return [...tasks].sort((a, b) => {
    switch (field) {
      case "created_at":
        return (new Date(a.created_at).getTime() - new Date(b.created_at).getTime()) * direction

      case "due_date": {
        // Tasks without due dates sort to the end
        const aDate = a.due_date ? new Date(a.due_date).getTime() : 0
        const bDate = b.due_date ? new Date(b.due_date).getTime() : 0

        // If both have dates or both don't, sort normally
        // If only one has a date, the one with date comes first (for asc)
        if (a.due_date && b.due_date) return (aDate - bDate) * direction
        if (a.due_date) return -1 * direction
        if (b.due_date) return 1 * direction
        return 0
      }

      case "priority":
        // Higher priority comes first for desc order
        return (PRIORITY_VALUE[a.priority] - PRIORITY_VALUE[b.priority]) * direction

      case "title":
        return a.title.localeCompare(b.title) * direction

      default:
        return 0
    }
  })
}

// =============================================================================
// Filter Functions
// =============================================================================

/**
 * Filter tasks by status, priority, and search query.
 *
 * @param tasks - Tasks to filter
 * @param filters - Filter state from ui-store
 * @param searchQuery - Optional search query for text filtering
 * @returns Filtered tasks array
 */
function filterTasks(tasks: Task[], filters: FilterState, searchQuery?: string): Task[] {
  return tasks.filter((task) => {
    // Status filter
    if (filters.status === "pending" && task.completed) return false
    if (filters.status === "completed" && !task.completed) return false

    // Priority filter
    if (filters.priority !== "all" && task.priority !== filters.priority) return false

    // Tag filter
    if (filters.tag && !task.tags.some((t) => t.name === filters.tag)) return false

    // Search query (searches title and description)
    if (searchQuery && searchQuery.trim()) {
      const query = searchQuery.toLowerCase()
      const matchesTitle = task.title.toLowerCase().includes(query)
      const matchesDescription = task.description?.toLowerCase().includes(query)
      const matchesTags = task.tags.some((t) => t.name.toLowerCase().includes(query))

      if (!matchesTitle && !matchesDescription && !matchesTags) return false
    }

    return true
  })
}

// =============================================================================
// Hook Return Type
// =============================================================================

interface UseTaskFiltersResult {
  /** All filtered and sorted tasks */
  filteredTasks: Task[]
  /** Tasks currently displayed (after pagination if added) */
  displayTasks: Task[]
  /** Total number of tasks */
  totalCount: number
  /** Number of pending tasks */
  pendingCount: number
  /** Number of completed tasks */
  completedCount: number
  /** Current search query */
  searchQuery: string
  /** Set the search query */
  setSearchQuery: (query: string) => void
  /** Current filter state from store */
  filters: FilterState
  /** Update status filter */
  setStatusFilter: (status: FilterState["status"]) => void
  /** Update priority filter */
  setPriorityFilter: (priority: FilterState["priority"]) => void
  /** Update sort field */
  setSortBy: (sortBy: FilterState["sortBy"]) => void
  /** Update sort order (toggles asc/desc) */
  toggleSortOrder: () => void
  /** Reset all filters to default */
  resetFilters: () => void
  /** Loading state */
  isLoading: boolean
  /** Error state */
  error: Error | null
}

// =============================================================================
// Main Hook
// =============================================================================

/**
 * Hook for managing task filters, sorting, and search.
 *
 * Integrates with ui-store for persistent filter state and
 * uses TanStack Query for data fetching.
 *
 * @returns Task filter state and actions
 */
export function useTaskFilters(): UseTaskFiltersResult {
  // Filter state from ui-store
  const filters = useUIStore((state) => state.filters)
  const setStatusFilter = useUIStore((state) => state.setFilterStatus)
  const setPriorityFilter = useUIStore((state) => state.setFilterPriority)
  const setSortBy = useUIStore((state) => state.setSortBy)
  const setSortOrder = useUIStore((state) => state.setSortOrder)
  const resetFilters = useUIStore((state) => state.resetFilters)

  // Local search query state (not persisted)
  const [searchQuery, setSearchQueryState] = useState("")

  // Debounced search for API calls
  const debouncedSearch = useDebounce(searchQuery, 300)

  // Fetch tasks from backend
  const {
    data: tasksResult,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["tasks", filters.status, filters.priority],
    queryFn: () =>
      api.getTasks({
        status: filters.status,
        priority: filters.priority === "all" ? undefined : filters.priority,
      }),
    })

  // Extract tasks from Result<TaskList> type
  const allTasks = useMemo(() => {
    return tasksResult?.success ? tasksResult.data.tasks ?? [] : []
  }, [tasksResult])

  // Calculate counts
  const totalCount = allTasks.length
  const pendingCount = allTasks.filter((t) => !t.completed).length
  const completedCount = allTasks.filter((t) => t.completed).length

  // Apply client-side filtering and sorting
  const filteredTasks = useMemo(() => {
    let result = allTasks

    // Apply filters (status, priority, tag, search)
    result = filterTasks(result, filters, debouncedSearch)

    // Apply sorting
    result = sortTasks(result, {
      field: filters.sortBy,
      order: filters.sortOrder,
    })

    return result
  }, [allTasks, filters, debouncedSearch])

  // Use API search when search query is present
  const [searchResults, setSearchResults] = useState<Task[]>([])
  const [isSearching, setIsSearching] = useState(false)

  // Search via API when debounced query changes
  useEffect(() => {
    if (debouncedSearch.trim()) {
      setIsSearching(true)
      api.searchTasks(debouncedSearch).then((result) => {
        if (result.success) {
          setSearchResults(result.data.tasks)
        }
        setIsSearching(false)
      })
    } else {
      setSearchResults([])
    }
  }, [debouncedSearch])

  // Determine which tasks to display
  const displayTasks = useMemo(() => {
    if (debouncedSearch.trim() && searchResults.length > 0) {
      // Apply local filters to search results
      const filtered = filterTasks(searchResults, filters)
      // Apply sorting
      return sortTasks(filtered, {
        field: filters.sortBy,
        order: filters.sortOrder,
      })
    }
    return filteredTasks
  }, [filteredTasks, searchResults, debouncedSearch, filters])

  // Wrapper for setting search query
  const setSearchQuery = (query: string) => {
    setSearchQueryState(query)
  }

  // Wrapper for toggling sort order
  const toggleSortOrder = () => {
    setSortOrder(filters.sortOrder === "asc" ? "desc" : "asc")
  }

  return {
    filteredTasks,
    displayTasks,
    totalCount,
    pendingCount,
    completedCount,
    searchQuery,
    setSearchQuery,
    filters,
    setStatusFilter,
    setPriorityFilter,
    setSortBy,
    toggleSortOrder,
    resetFilters,
    isLoading: isLoading || isSearching,
    error,
  }
}
