/**
 * Server-Sent Events (SSE) parsing utilities.
 *
 * Provides stream parsing for SSE responses from the backend chat API.
 * Per spec.md FR-001 through FR-010.
 */

/**
 * SSE event data from the backend.
 */
export interface SSEEvent {
  eventType: string;
  data: unknown;
}

/**
 * Options for handling SSE events.
 */
export interface SSEEventHandlers {
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
      // Could be used to show conversation ID
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
