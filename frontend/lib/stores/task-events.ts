/**
 * Task Event Store - Zustand store for task mutation events.
 *
 * Tracks task mutations initiated by AI agent (Chronos) via SSE tool results.
 * This store persists across component unmounts and coordinates cache updates
 * between chat SSE events and TanStack Query cache.
 *
 * Per plan.md Phase 1 Design & Contracts - State Management Contracts
 * Per data-model.md - Task Event Store (NEW - Zustand)
 */

import { create } from "zustand"
import type { Task } from "@/types/task"

// =============================================================================
// Types
// =============================================================================

/**
 * Task mutation types from AI agent actions.
 */
export type TaskMutationType = "create" | "complete" | "update" | "delete"

/**
 * Task mutation event from AI tool result.
 *
 * Emitted when Chronos AI performs a task action via MCP tools.
 */
export interface TaskMutation {
  /** Type of mutation performed */
  type: TaskMutationType

  /** ID of the affected task (null for create before ID known) */
  taskId: number | null

  /** Timestamp when mutation occurred */
  timestamp: number

  /** Partial task data (for create/update operations) */
  data?: Partial<Task>

  /** Whether the mutation was successful */
  success?: boolean

  /** Error message if mutation failed */
  error?: string
}

// =============================================================================
// Store State
// =============================================================================

interface TaskEventStoreState {
  /** Most recent task mutation from AI */
  lastMutation: TaskMutation | null

  /** History of mutations (for debugging/undo) */
  mutationHistory: TaskMutation[]

  /** Maximum history size */
  maxHistorySize: number
}

// =============================================================================
// Store Actions
// =============================================================================

interface TaskEventStoreActions {
  /**
   * Record a task mutation event.
   *
   * Called when SSE tool_result event indicates AI performed a task action.
   *
   * @param mutation - Task mutation data from tool result
   *
   * @example
   * ```tsx
   * // When AI completes a task via SSE
   * setTaskMutation({
   *   type: "complete",
   *   taskId: 123,
   *   timestamp: Date.now(),
   *   data: { completed: true },
   *   success: true,
   * })
   * ```
   */
  setTaskMutation: (mutation: TaskMutation) => void

  /**
   * Clear the most recent mutation.
   *
   * Called after cache update is processed to prevent stale state.
   */
  clearMutation: () => void

  /**
   * Clear all mutation history.
   *
   * Useful for testing or logout.
   */
  clearHistory: () => void

  /**
   * Get mutations for a specific task.
   *
   * @param taskId - Task ID to filter by
   * @returns Array of mutations for the task
   */
  getMutationsForTask: (taskId: number) => TaskMutation[]

  /**
   * Get the most recent mutation of a specific type.
   *
   * @param type - Mutation type to filter by
   * @returns Most recent mutation of type, or null
   */
  getLastMutationOfType: (type: TaskMutationType) => TaskMutation | null
}

// =============================================================================
// Store Definition
// =============================================================================

type TaskEventStore = TaskEventStoreState & TaskEventStoreActions

export const useTaskEventStore = create<TaskEventStore>((set, get) => ({
  // Initial state
  lastMutation: null,
  mutationHistory: [],
  maxHistorySize: 50,

  // Actions
  setTaskMutation: (mutation) =>
    set((state) => {
      // Create history entry with copy
      const historyEntry = { ...mutation }
      const newHistory = [historyEntry, ...state.mutationHistory]

      // Trim history if needed (keep most recent)
      if (newHistory.length > state.maxHistorySize) {
        newHistory.length = state.maxHistorySize
      }

      return {
        lastMutation: mutation,
        mutationHistory: newHistory,
      }
    }),

  clearMutation: () =>
    set((state) => ({
      ...state,
      lastMutation: null,
    })),

  clearHistory: () =>
    set({
      lastMutation: null,
      mutationHistory: [],
    }),

  getMutationsForTask: (taskId) => {
    const state = get()
    return state.mutationHistory.filter((m) => m.taskId === taskId)
  },

  getLastMutationOfType: (type) => {
    const state = get()
    return (
      state.mutationHistory.find((m) => m.type === type && m.success) || null
    )
  },
}))

// =============================================================================
// Selectors (for optimized reads)
// =============================================================================

/**
 * Select the last mutation from the store.
 * Prevents unnecessary re-renders when other state changes.
 */
export const selectLastMutation = (state: TaskEventStore) => state.lastMutation

/**
 * Select mutation history from the store.
 */
export const selectMutationHistory = (state: TaskEventStore) => state.mutationHistory

/**
 * Select whether there was a recent successful create mutation.
 */
export const selectHasRecentCreate = (state: TaskEventStore) => {
  if (!state.lastMutation) return false
  return (
    state.lastMutation.type === "create" &&
    state.lastMutation.success === true &&
    Date.now() - state.lastMutation.timestamp < 5000 // Within 5 seconds
  )
}

/**
 * Select whether there was a recent successful complete mutation.
 */
export const selectHasRecentComplete = (state: TaskEventStore) => {
  if (!state.lastMutation) return false
  return (
    state.lastMutation.type === "complete" &&
    state.lastMutation.success === true &&
    Date.now() - state.lastMutation.timestamp < 5000 // Within 5 seconds
  )
}
