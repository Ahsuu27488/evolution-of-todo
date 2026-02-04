/**
 * Chat API client for Phase III AI Chatbot.
 *
 * Handles:
 * - SSE streaming for chat responses
 * - Conversation CRUD operations
 * - Audio transcription
 *
 * Per spec.md FR-001 through FR-010, FR-052 through FR-061.
 */

import { Result } from "@/types/chat";

// =============================================================================
// Configuration
// =============================================================================

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// =============================================================================
// SSE Streaming
// =============================================================================

export interface ChatStreamOptions {
  onToken: (token: string) => void;
  onToolCall: (tool: string, args: Record<string, unknown>) => void;
  onToolResult: (tool: string, output: string) => void;
  onAgentHandoff: (from: string, to: string) => void;
  onDone: (finalOutput: string, agent: string) => void;
  onError: (error: string) => void;
}

/**
 * Send a chat message and stream the response via SSE.
 */
export async function streamChat(
  message: string,
  conversationId: string | null,
  options: ChatStreamOptions,
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

  const decoder = new TextDecoder();
  let buffer = "";

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        if (!line.trim()) continue;

        // Parse SSE format: "event: <type>\ndata: <json>\n\n"
        const eventMatch = line.match(/^event:\s*(.+)$/);
        const dataMatch = line.match(/^data:\s*(.+)$/);

        if (eventMatch && dataMatch) {
          const eventType = eventMatch[1];
          const data = JSON.parse(dataMatch[1]);

          handleSSEEvent(eventType, data, options);
        }
      }
    }
  } catch (error) {
    if (error instanceof Error && error.name !== "AbortError") {
      options.onError(error.message);
    }
  }
}

function handleSSEEvent(
  eventType: string,
  data: unknown,
  options: ChatStreamOptions,
): void {
  switch (eventType) {
    case "message_start":
      // Could be used to show conversation ID
      break;

    case "token":
      if (typeof data === "object" && data !== null && "content" in data) {
        options.onToken(String(data.content));
      }
      break;

    case "tool_call":
      if (typeof data === "object" && data !== null && "tool" in data) {
        const toolData = data as { tool?: string; arguments?: Record<string, unknown> };
        options.onToolCall(
          String(toolData.tool || ""),
          toolData.arguments || {},
        );
      }
      break;

    case "tool_result":
      if (typeof data === "object" && data !== null) {
        options.onToolResult(
          String((data as { tool: string }).tool),
          String((data as { output: string }).output),
        );
      }
      break;

    case "agent_handoff":
      if (typeof data === "object" && data !== null) {
        options.onAgentHandoff(
          String((data as { from_agent: string }).from_agent),
          String((data as { to_agent: string }).to_agent),
        );
      }
      break;

    case "message_done":
      if (typeof data === "object" && data !== null) {
        options.onDone(
          String((data as { final_output: string }).final_output),
          String((data as { agent: string }).agent),
        );
      }
      break;

    case "error":
      if (typeof data === "object" && data !== null) {
        options.onError(
          String((data as { message: string }).message || "Unknown error"),
        );
      }
      break;
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

export async function getConversation(
  id: string,
  limit = 50,
  offset = 0,
): Promise<Result<ConversationWithMessagesPaginated>> {
  const token = await getAuthToken();
  if (!token) {
    return { success: false, error: { message: "Authentication required" } };
  }

  const response = await fetch(
    `${API_URL}/api/chat/conversations/${id}?limit=${limit}&offset=${offset}`,
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
        message: "Failed to load conversation",
        statusCode: response.status,
      },
    };
  }

  const data = await response.json();
  return { success: true, data };
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

// =============================================================================
// Auth Token Helper
// =============================================================================

async function getAuthToken(): Promise<string | null> {
  try {
    const response = await fetch("/api/auth/token", {
      credentials: "include",
    });
    if (!response.ok) return null;
    const data = await response.json();
    return data.token || null;
  } catch {
    return null;
  }
}

// =============================================================================
// Type Exports
// =============================================================================

interface Conversation {
  id: string;
  userId: string;
  title: string;
  languagePreference: "auto" | "en" | "ur";
  messageCount: number;
  createdAt: string;
  updatedAt: string;
}

interface Message {
  id: string;
  conversationId: string;
  correlationId?: string;
  role: "user" | "assistant" | "system";
  content: string;
  toolCalls?: ToolCall[];
  createdAt: string;
}

interface ToolCall {
  tool: string;
  arguments: Record<string, unknown>;
}

interface ConversationList {
  conversations: Conversation[];
  total: number;
}

interface ConversationWithMessagesPaginated {
  conversation: Conversation;
  messages: Message[];
  pagination: {
    limit: number;
    offset: number;
    total: number;
    has_more: boolean;
  };
}

interface TranscriptionResult {
  text: string;
  language: string;
  duration?: number;
}
