/**
 * Server-Sent Events (SSE) parsing utilities.
 *
 * Provides stream parsing for SSE responses from the backend chat API.
 * Per spec.md FR-001 through FR-010.
 */

// =============================================================================
// Types
// =============================================================================

/**
 * SSE event data from the backend.
 */
export interface SSEEvent {
  eventType: string;
  data: unknown;
}

/**
 * Tool call event from AI agent.
 *
 * Emitted when AI invokes an MCP tool during conversation.
 */
export interface ToolCallEvent {
  eventType: "tool_call"
  data: {
    tool: string
    arguments: Record<string, unknown>
  }
}

/**
 * Tool result event from AI agent.
 *
 * Emitted when MCP tool completes execution.
 * Extended for Phase 1 FR-003: Parse AI tool completion events for cache updates.
 */
export interface ToolResultEvent {
  eventType: "tool_result"
  data: {
    tool: "add_task" | "complete_task" | "update_task" | "delete_task" | "get_task" | "list_tasks" | "semantic_search"
    output: {
      success: boolean
      data?: unknown
      error?: string
    }
  }
}

/**
 * Task mutation from tool result.
 *
 * Extracted task data for TanStack Query cache updates.
 * Per plan.md - Real-Time Task Synchronization (FR-001).
 */
export interface TaskMutationFromSSE {
  type: "create" | "complete" | "update" | "delete"
  taskId: number | null
  timestamp: number
  data?: unknown
  success: boolean
  error?: string
}

/**
 * Options for handling SSE events.
 */
export interface SSEEventHandlers {
  onMessageStart?: (conversationId: string, correlationId: string) => void;
  onToken?: (content: string) => void;
  onToolCall?: (tool: string, args: Record<string, unknown>) => void;
  onToolResult?: (tool: string, output: string) => void;
  onAgentHandoff?: (from: string, to: string) => void;
  onDone?: (finalOutput: string, agent: string) => void;
  onError?: (error: string) => void;
}

/**
 * Parse an SSE stream from a ReadableStream reader.
 *
 * @param reader - The ReadableStreamDefaultReader from fetch response.body
 * @param handlers - Callback functions for each event type
 * @returns AsyncGenerator that yields parsed SSE events
 */
export async function* parseSSEStream(
  reader: ReadableStreamDefaultReader<Uint8Array>,
  handlers: SSEEventHandlers = {}
): AsyncGenerator<SSEEvent> {
  const decoder = new TextDecoder();
  let buffer = "";
  let eventType = "";
  let eventData = "";

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        if (!line.trim()) continue;

        if (line.startsWith("event: ")) {
          eventType = line.slice(7).trim();
        } else if (line.startsWith("data: ")) {
          eventData = line.slice(6).trim();

          // Parse JSON data
          let data: unknown;
          try {
            data = JSON.parse(eventData);
          } catch {
            data = eventData;
          }

          // Yield the event
          yield { eventType, data };

          // Call handler if provided
          handleSSEEvent(eventType, data, handlers);

          eventType = "";
          eventData = "";
        }
      }
    }
  } catch (error) {
    if (error instanceof Error && error.name !== "AbortError") {
      handlers.onError?.(error.message);
    }
  }
}

/**
 * Handle a single SSE event by calling the appropriate handler.
 *
 * @param eventType - The type of SSE event
 * @param data - The parsed event data
 * @param handlers - Callback functions for each event type
 */
function handleSSEEvent(
  eventType: string,
  data: unknown,
  handlers: SSEEventHandlers
): void {
  switch (eventType) {
    case "message_start":
      if (typeof data === "object" && data !== null) {
        const startData = data as { conversation_id?: string; correlation_id?: string };
        if (startData.conversation_id) {
          handlers.onMessageStart?.(
            String(startData.conversation_id),
            String(startData.correlation_id || "")
          );
        }
      }
      break;

    case "token":
      if (typeof data === "object" && data !== null && "content" in data) {
        handlers.onToken?.(String(data.content));
      }
      break;

    case "tool_call":
      if (typeof data === "object" && data !== null && "tool" in data) {
        const toolData = data as { tool?: string; arguments?: Record<string, unknown> };
        handlers.onToolCall?.(
          String(toolData.tool || ""),
          toolData.arguments || {}
        );
      }
      break;

    case "tool_result":
      if (typeof data === "object" && data !== null) {
        handlers.onToolResult?.(
          String((data as { tool: string }).tool || ""),
          String((data as { output: string }).output || "")
        );
      }
      break;

    case "agent_handoff":
      if (typeof data === "object" && data !== null) {
        handlers.onAgentHandoff?.(
          String((data as { from_agent: string }).from_agent || ""),
          String((data as { to_agent: string }).to_agent || "")
        );
      }
      break;

    case "message_done":
      if (typeof data === "object" && data !== null) {
        handlers.onDone?.(
          String((data as { final_output: string }).final_output || ""),
          String((data as { agent: string }).agent || "TodoAgent")
        );
      }
      break;

    case "error":
      if (typeof data === "object" && data !== null) {
        handlers.onError?.(
          String((data as { message: string }).message || "Unknown error")
        );
      }
      break;
  }
}

/**
 * Parse tool result event into task mutation for cache updates.
 *
 * Extracts task mutation data from tool_result SSE events for real-time
 * TanStack Query cache synchronization (FR-001, FR-003).
 *
 * @param tool - Name of the tool that was called
 * @param output - Tool output data
 * @returns TaskMutationFromSSE or null if not a task-related mutation
 *
 * @example
 * ```tsx
 * const mutation = parseToolResult("complete_task", {
 *   success: true,
 *   data: { id: 123, completed: true }
 * })
 * // Returns: { type: "complete", taskId: 123, success: true, ... }
 * ```
 */
export function parseToolResult(
  tool: string,
  output: ToolResultEvent["data"]["output"]
): TaskMutationFromSSE | null {
  // Map tool names to mutation types
  const toolToMutationMap: Record<string, TaskMutationFromSSE["type"]> = {
    add_task: "create",
    complete_task: "complete",
    update_task: "update",
    delete_task: "delete",
  }

  const mutationType = toolToMutationMap[tool]
  if (!mutationType) {
    // Not a task-related tool (e.g., get_task, list_tasks, semantic_search)
    return null
  }

  // Extract task ID from output data
  let taskId: number | null = null
  let taskData: unknown = undefined

  if (output.success && output.data) {
    const data = output.data as { id?: number; [key: string]: unknown }
    taskId = data.id ?? null
    taskData = data
  }

  return {
    type: mutationType,
    taskId,
    timestamp: Date.now(),
    data: taskData,
    success: output.success,
    error: output.error,
  }
}

/**
 * Check if SSE event is a task-related tool result.
 *
 * Utility for filtering SSE events to only task mutations.
 *
 * @param eventType - SSE event type
 * @param data - SSE event data
 * @returns true if event is a task tool result
 */
export function isTaskToolResult(
  eventType: string,
  data: unknown
): data is ToolResultEvent["data"] {
  if (eventType !== "tool_result") return false
  if (typeof data !== "object" || data === null) return false

  const tool = (data as { tool?: string }).tool
  const taskTools = ["add_task", "complete_task", "update_task", "delete_task"]

  return typeof tool === "string" && taskTools.includes(tool)
}

/**
 * Parse SSE format line-by-line (legacy interface for backward compatibility).
 *
 * @param line - A single line from an SSE stream
 * @returns Object with event and data if found, null otherwise
 */
export function parseSSELine(line: string): { event?: string; data?: unknown } | null {
  if (!line.trim()) return null;

  const eventMatch = line.match(/^event:\s*(.+)$/);
  const dataMatch = line.match(/^data:\s*(.+)$/);

  if (eventMatch && dataMatch) {
    return {
      event: eventMatch[1],
      data: JSON.parse(dataMatch[1]),
    };
  }

  if (dataMatch) {
    try {
      return { data: JSON.parse(dataMatch[1]) };
    } catch {
      return { data: dataMatch[1] };
    }
  }

  return null;
}
