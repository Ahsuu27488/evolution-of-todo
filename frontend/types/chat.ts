/**
 * Chat types for Phase III AI Chatbot.
 *
 * Defines TypeScript interfaces for:
 * - Messages and conversations
 * - SSE streaming events
 * - Chat state management
 *
 * Per spec.md FR-001 through FR-010.
 */

// =============================================================================
// Message Types
// =============================================================================

export type MessageRole = "user" | "assistant" | "system" | "tool";

export interface Message {
  id: string;
  conversationId: string;
  correlationId?: string;
  role: MessageRole;
  content: string;
  messageType?: "text" | "voice";  // Distinguish voice from text messages
  toolCalls?: ToolCall[];
  createdAt?: string | null;
}

export interface ToolCall {
  tool: string;
  arguments: Record<string, unknown>;
  output?: string;
}

// =============================================================================
// Conversation Types
// =============================================================================

export type LanguagePreference = "auto" | "en" | "ur";

export interface Conversation {
  id: string;
  userId: string;
  title: string;
  languagePreference: LanguagePreference;
  messageCount: number;
  createdAt: string;
  updatedAt: string;
}

// =============================================================================
// SSE Event Types
// =============================================================================

export type StreamEventType =
  | "message_start"
  | "token"
  | "tool_call"
  | "tool_result"
  | "agent_handoff"
  | "message_done"
  | "error";

export interface StreamEvent {
  event: StreamEventType;
  data: StreamEventData;
}

export type StreamEventData =
  | MessageStartData
  | TokenData
  | ToolCallData
  | ToolResultData
  | AgentHandoffData
  | MessageDoneData
  | ErrorData;

export interface MessageStartData {
  conversationId: string;
  messageId?: string;
  correlationId: string;
  timestamp?: string;
}

export interface TokenData {
  content: string;
}

export interface ToolCallData {
  tool: string;
  arguments: Record<string, unknown>;
}

export interface ToolResultData {
  tool: string;
  output: string;
}

export interface AgentHandoffData {
  fromAgent: string;
  toAgent: string;
  timestamp: string;
}

export interface MessageDoneData {
  finalOutput: string;
  agent: string;
  durationMs: number;
}

export interface ErrorData {
  conversationId?: string;  // Include conversation_id so frontend can track conversation even on error
  error: string;
  message: string;
}

// =============================================================================
// Chat State Types
// =============================================================================

export interface ChatState {
  // Current conversation
  conversationId: string | null;
  messages: Message[];

  // Streaming state
  isStreaming: boolean;
  streamedContent: string;
  currentAgent: string | null;

  // UI state
  isOpen: boolean;
  isMinimized: boolean;
  inputMode: "text" | "voice";

  // Error state
  error: string | null;

  // Conversations list
  conversations: Conversation[];
  conversationsLoaded: boolean;
}

export interface ChatActions {
  // Conversation management
  newConversation: () => Promise<void>;
  loadConversation: (id: string) => Promise<void>;
  deleteConversation: (id: string) => Promise<void>;
  loadConversations: () => Promise<void>;

  // Messaging
  sendMessage: (message: string, conversationId?: string) => Promise<void>;
  stopStreaming: () => void;

  // UI state
  setOpen: (open: boolean) => void;
  setMinimized: (minimized: boolean) => void;
  setInputMode: (mode: "text" | "voice") => void;
  clearError: () => void;
}

// =============================================================================
// API Request/Response Types
// =============================================================================

export interface ChatRequest {
  message: string;
  conversationId?: string;
}

export interface TranscriptionRequest {
  file: File;
  language?: string;
}

export interface TranscriptionResponse {
  text: string;
  language: string;
  duration?: number;
}

export interface ConversationsResponse {
  conversations: Conversation[];
  total: number;
}

export interface ConversationWithMessages {
  conversation: Conversation;
  messages: Message[];
}

// =============================================================================
// Voice Input Types
// =============================================================================

export interface VoiceState {
  isRecording: boolean;
  isProcessing: boolean;
  transcript: string;
  error: string | null;
}

// =============================================================================
// Utility Types
// =============================================================================

export type Result<T> =
  | { success: true; data: T }
  | { success: false; error: ApiError };

export interface ApiError {
  message: string;
  code?: string;
  statusCode?: number;
}
