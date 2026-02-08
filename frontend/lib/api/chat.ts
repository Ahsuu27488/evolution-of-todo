/**
 * Chat API client for Phase III AI Chatbot.
 *
 * Handles:
 * - SSE streaming for chat responses
 * - Conversation CRUD operations
 * - Audio transcription
 * - Real-time task cache updates from AI actions (Phase 1 - FR-001, FR-003)
 *
 * Per spec.md FR-001 through FR-010, FR-052 through FR-061.
 * Phase 1: Real-Time Task State Synchronization
 */

import { API_URL } from "@/lib/config/api";
import { getAuthToken } from "@/lib/auth/token";
import { parseSSEStream, isTaskToolResult, parseToolResult } from "@/lib/utils/sse";
import type { Result, Conversation, Message, ToolCall } from "@/types/chat";
import type { TaskMutationFromSSE } from "@/lib/utils/sse";
import type { Task } from "@/types/task";

// Re-export commonly used types from central location
export type { Conversation, Message, ToolCall };

// =============================================================================
// Task Cache Integration
// =============================================================================

/**
 * Task query keys for TanStack Query cache operations.
 * Must match the keys used in use-task-filters.ts
 */
export const taskKeys = {
  all: ["tasks"] as const,
  lists: () => [...taskKeys.all, "list"] as const,
  list: (filters?: { status?: string; priority?: string }) =>
    [...taskKeys.lists(), filters] as const,
  detail: (id: number) => [...taskKeys.all, "detail", id] as const,
};

// =============================================================================
// Task Cache Update Utilities (Phase 1 - FR-001, FR-003)
// =============================================================================

/**
 * Update TanStack Query cache for task mutations from AI actions.
 *
 * This function provides optimistic updates when the AI performs task actions,
 * ensuring the dashboard reflects changes immediately without page refresh.
 *
 * @param queryClient - TanStack Query client instance
 * @param mutation - Task mutation from SSE tool_result event
 *
 * @example
 * ```tsx
 * import { useQueryClient } from "@tanstack/react-query";
 * import { updateTaskCache } from "@/lib/api/chat";
 *
 * const queryClient = useQueryClient();
 * updateTaskCache(queryClient, {
 *   type: "complete",
 *   taskId: 123,
 *   success: true,
 *   data: { completed: true }
 * });
 * ```
 */
export function updateTaskCache(
  queryClient: import("@tanstack/react-query").QueryClient,
  mutation: TaskMutationFromSSE
): void {
  if (!mutation.success) {
    console.warn("[TaskCache] Skipping failed mutation:", mutation);
    return;
  }

  const { type, taskId, data } = mutation;

  // Handle each mutation type
  switch (type) {
    case "create": {
      // For new tasks, invalidate all task queries to fetch the new task
      // This ensures the new task appears in all filtered views
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });
      console.debug("[TaskCache] Created new task, invalidating queries");
      break;
    }

    case "complete":
    case "update": {
      // For updates, use setQueryData for immediate optimistic update
      if (!taskId) {
        console.warn("[TaskCache] No taskId for update mutation");
        return;
      }

      // Update all list queries that might contain this task
      queryClient.setQueriesData(
        { queryKey: taskKeys.lists() },
        (old: unknown) => {
          if (!old || typeof old !== "object") return old;

          // Handle Result<TaskList> structure
          const result = old as { success?: boolean; data?: { tasks?: unknown[] } };
          if (!result.data?.tasks) return old;

          const tasks = result.data.tasks as Array<{ id: number; [key: string]: unknown }>;
          const updateData = data as Record<string, unknown> | undefined;

          return {
            ...result,
            data: {
              ...result.data,
              tasks: tasks.map((task) =>
                task.id === taskId && updateData
                  ? { ...task, ...updateData }
                  : task
              ),
            },
          };
        }
      );

      // Also update the detail query if it exists
      queryClient.setQueryData(
        taskKeys.detail(taskId),
        (old: unknown) => {
          if (!old || typeof old !== "object") return old;
          const updateData = data as Record<string, unknown> | undefined;
          return updateData ? { ...old, ...updateData } : old;
        }
      );

      // Trigger background refetch to ensure consistency
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });

      console.debug("[TaskCache] Updated task:", taskId, data);
      break;
    }

    case "delete": {
      // For deletions, remove the task from all list queries
      if (!taskId) {
        console.warn("[TaskCache] No taskId for delete mutation");
        return;
      }

      queryClient.setQueriesData(
        { queryKey: taskKeys.lists() },
        (old: unknown) => {
          if (!old || typeof old !== "object") return old;

          const result = old as { success?: boolean; data?: { tasks?: unknown[]; total?: number } };
          if (!result.data?.tasks) return old;

          const tasks = result.data.tasks as Array<{ id: number }>;
          const currentTotal = result.data.total ?? tasks.length;

          return {
            ...result,
            data: {
              ...result.data,
              tasks: tasks.filter((task) => task.id !== taskId),
              total: Math.max(0, currentTotal - 1),
            },
          };
        }
      );

      // Invalidate detail query
      queryClient.invalidateQueries({ queryKey: taskKeys.detail(taskId) });

      console.debug("[TaskCache] Deleted task:", taskId);
      break;
    }

    default:
      console.warn("[TaskCache] Unknown mutation type:", type);
  }
}

/**
 * Create a task mutation handler for use with SSE streaming.
 *
 * This factory function creates an onTaskMutation callback that automatically
 * updates the TanStack Query cache when AI actions occur.
 *
 * @param queryClient - TanStack Query client instance
 * @returns Callback function for onTaskMutation option
 *
 * @example
 * ```tsx
 * import { useQueryClient } from "@tanstack/react-query";
 * import { createTaskMutationHandler, streamChat } from "@/lib/api/chat";
 *
 * const queryClient = useQueryClient();
 * const handleTaskMutation = createTaskMutationHandler(queryClient);
 *
 * await streamChat(message, conversationId, {
 *   onTaskMutation: handleTaskMutation,
 *   // ... other options
 * });
 * ```
 */
export function createTaskMutationHandler(
  queryClient: import("@tanstack/react-query").QueryClient
): (mutation: TaskMutationFromSSE) => void {
  return (mutation) => {
    updateTaskCache(queryClient, mutation);
  };
}

/**
 * Create a comprehensive task mutation handler with store integration.
 *
 * This factory function creates an onTaskMutation callback that:
 * 1. Updates TanStack Query cache for immediate UI updates
 * 2. Updates TaskEventStore for cross-component state coordination
 * 3. Shows themed toast notifications for AI actions (T014)
 *
 * Phase 1 - T012, T014: Wire task event store + toast notifications
 *
 * @param queryClient - TanStack Query client instance
 * @param setTaskMutation - Optional TaskEventStore setTaskMutation action
 * @param showToast - Optional function to show toast notifications
 * @returns Callback function for onTaskMutation option
 *
 * @example
 * ```tsx
 * import { useQueryClient } from "@tanstack/react-query";
 * import { useTaskEventStore } from "@/lib/stores/task-events";
 * import { createTaskMutationHandlerWithStore, showToastForAIMutation } from "@/lib/api/chat";
 *
 * const queryClient = useQueryClient();
 * const setTaskMutation = useTaskEventStore((s) => s.setTaskMutation);
 *
 * const handleTaskMutation = createTaskMutationHandlerWithStore(
 *   queryClient,
 *   setTaskMutation,
 *   showToastForAIMutation
 * );
 * ```
 */
export function createTaskMutationHandlerWithStore(
  queryClient: import("@tanstack/react-query").QueryClient,
  setTaskMutation?: (mutation: {
    type: import("../stores/task-events").TaskMutationType;
    taskId: number | null;
    timestamp: number;
    data?: Partial<Task>;
    success?: boolean;
    error?: string;
  }) => void,
  showToast?: (mutation: {
    type: string
    taskId: number | null
    success?: boolean
    error?: string
  }) => void
): (mutation: TaskMutationFromSSE) => void {
  return (mutation) => {
    // Update TanStack Query cache for immediate UI updates
    updateTaskCache(queryClient, mutation);

    // Update TaskEventStore for cross-component coordination
    if (setTaskMutation) {
      setTaskMutation({
        type: mutation.type,
        taskId: mutation.taskId,
        timestamp: mutation.timestamp,
        data: mutation.data as Partial<Task> | undefined,
        success: mutation.success,
        error: mutation.error,
      });
    }

    // Show toast notification for AI actions
    if (showToast) {
      showToast({
        type: mutation.type,
        taskId: mutation.taskId,
        success: mutation.success,
        error: mutation.error,
      });
    }
  };
}

// =============================================================================
// Type Aliases for API Responses
// =============================================================================

export interface ConversationList {
  conversations: Conversation[];
  total: number;
}

export interface ConversationWithMessagesPaginated {
  conversation: Conversation;
  messages: Message[];
  pagination: {
    limit: number;
    offset: number;
    total: number;
    has_more: boolean;
  };
}

export interface TranscriptionResult {
  text: string;
  language: string;
  duration?: number;
}

// =============================================================================
// SSE Streaming Options
// =============================================================================

export interface ChatStreamOptions {
  onMessageStart?: (conversationId: string, correlationId: string) => void;
  onToken: (token: string) => void;
  onToolCall: (tool: string, args: Record<string, unknown>) => void;
  onToolResult: (tool: string, output: string) => void;
  /**
   * Called when AI performs a task action via tool result.
   * Provides parsed task mutation data for cache updates (Phase 1 - FR-003).
   */
  onTaskMutation?: (mutation: TaskMutationFromSSE) => void;
  onAgentHandoff: (from: string, to: string) => void;
  onDone: (finalOutput: string, agent: string) => void;
  onError: (error: string) => void;
}

// =============================================================================
// Chat Streaming API
// =============================================================================

/**
 * Send a chat message and stream the response via SSE.
 */
export async function streamChat(
  message: string,
  conversationId: string | null,
  options: ChatStreamOptions,
  languagePreference?: "auto" | "en" | "ur",
  signal?: AbortSignal,
): Promise<void> {
  // Get auth token
  const token = await getAuthToken();
  if (!token) {
    options.onError("Authentication required");
    return;
  }

  const response = await fetch(`${API_URL}/api/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      message,
      conversation_id: conversationId,
      language_preference: languagePreference,
    }),
    signal,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Unknown error" }));
    options.onError(error.detail || "Failed to send message");
    return;
  }

  const reader = response.body?.getReader();
  if (!reader) {
    options.onError("No response body");
    return;
  }

  // Use shared SSE parsing utility with extended tool result handling
  for await (const { eventType, data } of parseSSEStream(reader, {
    onMessageStart: options.onMessageStart,
    onToken: options.onToken,
    onToolCall: options.onToolCall,
    onToolResult: (tool, output) => {
      // Call original handler
      options.onToolResult?.(tool, output);

      // Phase 1 FR-003: Parse task mutations from tool results
      if (isTaskToolResult(eventType, { tool, output: output as unknown })) {
        const mutation = parseToolResult(tool, { success: true, data: output });
        if (mutation) {
          options.onTaskMutation?.(mutation);
        }
      }
    },
    onAgentHandoff: options.onAgentHandoff,
    onDone: options.onDone,
    onError: options.onError,
  })) {
    // Events are handled by the parseSSEStream handlers
    // This loop can be used for additional logging if needed
    console.debug("[ChatSSE] Event:", eventType, data);
  }
}

// =============================================================================
// Conversation API
// =============================================================================

export async function getConversations(
  limit = 50,
  offset = 0,
): Promise<Result<ConversationList>> {
  const token = await getAuthToken();
  if (!token) {
    return { success: false, error: { message: "Authentication required" } };
  }

  const response = await fetch(
    `${API_URL}/api/chat/conversations?limit=${limit}&offset=${offset}`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    },
  );

  if (!response.ok) {
    return {
      success: false,
      error: {
        message: "Failed to load conversations",
        statusCode: response.status,
      },
    };
  }

  const data = await response.json();
  return { success: true, data };
}

/**
 * Get a conversation with its messages.
 * T054: Added AbortSignal support for cancelling pending requests when user switches conversations rapidly.
 */
export async function getConversation(
  id: string,
  limit = 50,
  offset = 0,
  signal?: AbortSignal,
): Promise<Result<ConversationWithMessagesPaginated>> {
  const token = await getAuthToken();
  if (!token) {
    return { success: false, error: { message: "Authentication required" } };
  }

  try {
    const response = await fetch(
      `${API_URL}/api/chat/conversations/${id}?limit=${limit}&offset=${offset}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
        signal, // T054: Pass AbortSignal to enable request cancellation
      },
    );

    if (!response.ok) {
      return {
        success: false,
        error: {
          message: "Failed to load conversation",
          statusCode: response.status,
        },
      };
    }

    const data = await response.json();
    console.log("[DEBUG] getConversation raw response:", JSON.stringify(data, null, 2));
    return { success: true, data };
  } catch (error) {
    // T054: Handle AbortError specifically (don't log as error)
    if (error instanceof Error && error.name === 'AbortError') {
      console.log("[getConversation] Request cancelled by user");
      throw error; // Re-throw AbortError for caller to handle
    }

    console.error("[getConversation] Network error:", {
      id,
      API_URL,
      error: error instanceof Error ? error.message : String(error),
      name: error instanceof Error ? error.name : "Unknown",
    });
    return {
      success: false,
      error: {
        message: `Network error: ${error instanceof Error ? error.message : "Unknown error"}`,
      },
    };
  }
}

export async function deleteConversation(id: string): Promise<Result<void>> {
  const token = await getAuthToken();
  if (!token) {
    return { success: false, error: { message: "Authentication required" } };
  }

  const response = await fetch(`${API_URL}/api/chat/conversations/${id}`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    return {
      success: false,
      error: {
        message: "Failed to delete conversation",
        statusCode: response.status,
      },
    };
  }

  return { success: true, data: undefined };
}

// =============================================================================
// Transcription API
// =============================================================================

export async function transcribeAudio(
  file: File,
  language?: string,
): Promise<Result<TranscriptionResult>> {
  const token = await getAuthToken();
  if (!token) {
    return { success: false, error: { message: "Authentication required" } };
  }

  const formData = new FormData();
  formData.append("file", file);
  if (language) {
    formData.append("language", language);
  }

  const response = await fetch(`${API_URL}/api/chat/transcribe`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: formData,
  });

  if (!response.ok) {
    return {
      success: false,
      error: {
        message: "Failed to transcribe audio",
        statusCode: response.status,
      },
    };
  }

  const data = await response.json();
  return { success: true, data };
}
