/**
 * useChat hook - React hook for chat functionality.
 *
 * Combines TanStack Query for server state with Context for UI state.
 * Handles SSE streaming for real-time AI responses.
 *
 * Per spec.md FR-001 through FR-010.
 * Phase 9 (T045): Integrates themed toast notifications for AI task actions.
 */

import { useCallback, useRef } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

import { API_URL } from "@/lib/config/api";
import { getAuthToken } from "@/lib/auth/token";
import { parseToolResult, isTaskToolResult } from "@/lib/utils/sse";
import { showToastForAIMutation } from "@/lib/utils/toast";
import type { Conversation, Message } from "@/types/chat";

// =============================================================================
// Query Keys
// =============================================================================

export const chatKeys = {
  all: ["chat"] as const,
  conversations: () => [...chatKeys.all, "conversations"] as const,
  conversation: (id: string) => [...chatKeys.all, "conversation", id] as const,
};

// =============================================================================
// Hooks
// =============================================================================

export function useConversations() {
  const queryClient = useQueryClient();

  const result = useQuery({
    queryKey: chatKeys.conversations(),
    queryFn: async () => {
      const token = await getAuthToken();
      const response = await fetch(`${API_URL}/api/chat/conversations`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (!response.ok) throw new Error("Failed to load conversations");
      return response.json() as Promise<{
        conversations: Conversation[];
        total: number;
      }>;
    },
    staleTime: 1000 * 60, // 1 minute
  });

  const invalidate = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: chatKeys.conversations() });
  }, [queryClient]);

  return {
    ...result,
    invalidate,
  };
}

export function useConversation(conversationId: string | null) {
  return useQuery({
    queryKey: chatKeys.conversation(conversationId || ""),
    queryFn: async () => {
      if (!conversationId) throw new Error("No conversation ID");
      const token = await getAuthToken();
      const response = await fetch(`${API_URL}/api/chat/conversations/${conversationId}`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (!response.ok) throw new Error("Failed to load conversation");
      return response.json() as Promise<{
        conversation: Conversation;
        messages: Message[];
      }>;
    },
    enabled: !!conversationId,
    staleTime: 1000 * 30, // 30 seconds
  });
}

export function useSendMessage() {
  const queryClient = useQueryClient();
  const abortControllerRef = useRef<AbortController | null>(null);

  const mutation = useMutation({
    mutationFn: async ({
      message,
      conversationId,
      languagePreference,
      messageType,
      onMessageStart,
      onToken,
      onToolCall,
      onToolResult,
      onAgentHandoff,
      onDone,
      onError,
    }: {
      message: string;
      conversationId: string | null;
      languagePreference?: "auto" | "en" | "ur";
      messageType?: "text" | "voice";
      onMessageStart?: (conversationId: string, correlationId: string) => void;
      onToken: (token: string) => void;
      onToolCall: (tool: string, args: Record<string, unknown>) => void;
      onToolResult?: (tool: string, output: string) => void;
      onAgentHandoff: (from: string, to: string) => void;
      onDone: (output: string, agent: string) => void;
      onError: (error: string, conversationId?: string) => void;
    }) => {
      // Cancel any existing request
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }

      abortControllerRef.current = new AbortController();

      // Get auth token before sending request
      const token = await getAuthToken();
      if (!token) {
        onError("Authentication required. Please sign in.");
        throw new Error("Authentication required");
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
          message_type: messageType,  // Include message type so backend can store it
        }),
        signal: abortControllerRef.current.signal,
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: "Failed to send message" }));
        onError(error.detail || "Unknown error");
        throw new Error(error.detail);
      }

      // Parse SSE stream
      const reader = response.body?.getReader();
      if (!reader) {
        onError("No response body");
        throw new Error("No response body");
      }

      const decoder = new TextDecoder();
      let buffer = "";
      let eventType = "";
      let eventData = "";

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
            try {
              const data = JSON.parse(eventData);

              switch (eventType) {
                case "message_start":
                  // Backend sends conversation_id (snake_case), not conversationId (camelCase)
                  if (onMessageStart && data.conversation_id) {
                    onMessageStart(data.conversation_id, data.correlation_id || "");
                  }
                  break;
                case "token":
                  onToken(data.content || "");
                  break;
                case "tool_call":
                  onToolCall(data.tool, data.arguments || {});
                  break;
                case "tool_result":
                  // T045: Handle tool_result events for AI task actions
                  onToolResult?.(data.tool, data.output);
                  // Show themed toast for task mutations
                  if (isTaskToolResult(eventType, { tool: data.tool, output: data.output })) {
                    const mutation = parseToolResult(data.tool, data.output);
                    if (mutation) {
                      showToastForAIMutation(mutation);
                    }
                  }
                  break;
                case "agent_handoff":
                  onAgentHandoff(data.from_agent, data.to_agent);
                  break;
                case "message_done":
                  onDone(data.final_output || "", data.agent || "TodoAgent");
                  break;
                case "error":
                  onError(data.message || "Unknown error", data.conversation_id);
                  break;
              }
            } catch {
              // Ignore JSON parse errors for partial data
            }
            eventType = "";
            eventData = "";
          }
        }
      }
    },
    onSuccess: (_, variables) => {
      // Invalidate queries
      queryClient.invalidateQueries({ queryKey: chatKeys.conversations() });
      if (variables.conversationId) {
        queryClient.invalidateQueries({ queryKey: chatKeys.conversation(variables.conversationId) });
      }
    },
  });

  const stop = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
  }, []);

  return {
    ...mutation,
    stop,
    isStreaming: mutation.isPending,
  };
}

export function useDeleteConversation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (conversationId: string) => {
      const token = await getAuthToken();
      const response = await fetch(`${API_URL}/api/chat/conversations/${conversationId}`, {
        method: "DELETE",
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (!response.ok) throw new Error("Failed to delete conversation");
      return conversationId;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: chatKeys.conversations() });
    },
  });
}
