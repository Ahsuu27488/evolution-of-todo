/**
 * useTaskMutations Hook
 *
 * Provides TanStack Query mutations for task CRUD operations.
 * Automatically invalidates relevant queries on success for cache consistency.
 *
 * Replaces server actions with direct API calls for proper cache invalidation.
 */

"use client"

import { useMutation, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"
import { api } from "@/lib/api-client"
import type { TaskCreate, TaskUpdate } from "@/types/task"

// =============================================================================
// Mutation Hooks
// =============================================================================

/**
 * Hook for creating new tasks with automatic cache invalidation.
 */
export function useCreateTask() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: TaskCreate) => api.createTask(data),
    onSuccess: (result) => {
      if (result.success) {
        // Invalidate all task queries to refetch with new data
        queryClient.invalidateQueries({ queryKey: ["tasks"] })
        toast.success("Task created")
      } else {
        toast.error(result.error.message || "Failed to create task")
      }
    },
    onError: () => {
      toast.error("Network error: Unable to create task")
    },
  })
}

/**
 * Hook for updating existing tasks with automatic cache invalidation.
 */
export function useUpdateTask() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ taskId, data }: { taskId: number; data: TaskUpdate }) =>
      api.updateTask(taskId, data),
    onSuccess: (result) => {
      if (result.success) {
        // Invalidate all task queries
        queryClient.invalidateQueries({ queryKey: ["tasks"] })
        toast.success("Task updated")
      } else {
        toast.error(result.error.message || "Failed to update task")
      }
    },
    onError: () => {
      toast.error("Network error: Unable to update task")
    },
  })
}

/**
 * Hook for deleting tasks with automatic cache invalidation.
 */
export function useDeleteTask() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (taskId: number) => api.deleteTask(taskId),
    onSuccess: (result) => {
      if (result.success) {
        // Invalidate all task queries
        queryClient.invalidateQueries({ queryKey: ["tasks"] })
        toast.success("Task deleted")
      } else {
        toast.error(result.error.message || "Failed to delete task")
      }
    },
    onError: () => {
      toast.error("Network error: Unable to delete task")
    },
  })
}

/**
 * Hook for toggling task completion with automatic cache invalidation.
 */
export function useToggleTaskComplete() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (taskId: number) => api.toggleTaskComplete(taskId),
    onSuccess: (result) => {
      if (result.success) {
        // Invalidate all task queries
        queryClient.invalidateQueries({ queryKey: ["tasks"] })
      } else {
        toast.error(result.error.message || "Failed to update task")
      }
    },
    onError: () => {
      toast.error("Network error: Unable to update task")
    },
  })
}
