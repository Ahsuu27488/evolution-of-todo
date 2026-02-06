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

import { API_URL } from "@/lib/config/api";
import { getAuthToken } from "@/lib/auth/token";
import { parseSSEStream } from "@/lib/utils/sse";
import type { Result, Conversation, Message, ToolCall } from "@/types/chat";

// Re-export commonly used types from central location
export type { Conversation, Message, ToolCall };

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

  // Use shared SSE parsing utility
  for await (const { eventType, data } of parseSSEStream(reader, {
    onMessageStart: options.onMessageStart,
    onToken: options.onToken,
    onToolCall: options.onToolCall,
    onToolResult: options.onToolResult,
    onAgentHandoff: options.onAgentHandoff,
    onDone: options.onDone,
    onError: options.onError,
  })) {
    // Events are handled by the parseSSEStream handlers
    // This loop can be used for additional logging if needed
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

  try {
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
    console.log("[DEBUG] getConversation raw response:", JSON.stringify(data, null, 2));
    return { success: true, data };
  } catch (error) {
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
