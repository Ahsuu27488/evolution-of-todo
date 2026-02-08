/**
 * Chat Message - Single message display in chat.
 *
 * Features:
 * - User and assistant message styling
 * - Tool call indicators with task cards
 * - Streaming cursor for active generation
 * - Timestamp display
 * - RTL support for Urdu (T077)
 * - Task card rendering for AI-created tasks (T116)
 *
 * Per spec.md FR-001 through FR-010, FR-048.
 * Phase 10 (T046-T050): Glassmorphism styling matching dashboard theme.
 */

import { motion } from "framer-motion";
import { User, Bot, Wrench, Mic } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { useMemo } from "react";
import ReactMarkdown from "react-markdown";
import type { Task } from "@/types/task";
import type { Message } from "@/types/chat";
import { getTextDirection } from "@/lib/utils/text-direction";
import { InlineTaskCard } from "./task-card";

// =============================================================================
// Mixed Language Text Renderer
// =============================================================================

/**
 * Urdu/Arabic Unicode pattern for detection.
 */
const URDU_PATTERN = /[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]/;

/**
 * Split text into segments, marking which contain Urdu characters.
 * Returns array of { text, isUrdu } segments.
 */
function splitTextByLanguage(text: string): Array<{ text: string; isUrdu: boolean }> {
  const segments: Array<{ text: string; isUrdu: boolean }> = [];
  let currentSegment = "";
  let currentIsUrdu = false;

  for (let i = 0; i < text.length; i++) {
    const char = text[i];
    const isUrduChar = URDU_PATTERN.test(char);

    if (i === 0) {
      currentSegment = char;
      currentIsUrdu = isUrduChar;
    } else if (isUrduChar === currentIsUrdu) {
      currentSegment += char;
    } else {
      segments.push({ text: currentSegment, isUrdu: currentIsUrdu });
      currentSegment = char;
      currentIsUrdu = isUrduChar;
    }
  }

  if (currentSegment) {
    segments.push({ text: currentSegment, isUrdu: currentIsUrdu });
  }

  return segments;
}

/**
 * Render mixed language text with Urdu words in Nastaliq font.
 * Handles strings, arrays (from markdown elements like <br>), and React nodes.
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
function renderMixedLanguageText(content: any): React.ReactNode {
  // Handle null/undefined
  if (content == null) return content;

  // Handle string directly
  if (typeof content === "string") {
    const segments = splitTextByLanguage(content);
    return segments.map((segment, idx) => {
      if (segment.isUrdu) {
        return (
          <span
            key={idx}
            style={{
              fontFamily: "'Noto Nastaliq Urdu', serif",
              lineHeight: "2",
            }}
          >
            {segment.text}
          </span>
        );
      }
      return <span key={idx}>{segment.text}</span>;
    });
  }

  // Handle array (e.g., ["text", <br />, "more text"])
  if (Array.isArray(content)) {
    return content.map((item, idx) =>
      typeof item === "string"
        ? <span key={idx}>{renderMixedLanguageText(item)}</span>
        : <span key={idx}>{item}</span>
    );
  }

  // Handle React elements (like <br />, <strong>, etc.)
  return content;
}

// =============================================================================
// Safe Date Utilities
// =============================================================================

/**
 * Safely format a date string or return "just now" if invalid.
 */
function safeFormatDistanceToNow(dateString: string | undefined | null): string {
  if (!dateString) return "just now";

  try {
    const date = new Date(dateString);
    // Check if date is valid
    if (isNaN(date.getTime())) return "just now";
    return formatDistanceToNow(date, { addSuffix: true });
  } catch {
    return "just now";
  }
}

// =============================================================================
// Utility Functions
// =============================================================================

/**
 * Extract task data from tool call output.
 * Parses the ToolResponse format from backend MCP tools.
 */
function extractTaskFromToolCall(toolCall: {
  tool: string;
  arguments: Record<string, unknown>;
  output?: string;
}): Task | null {
  if (toolCall.tool !== "add_task") return null;

  // Try to parse task from output
  if (toolCall.output) {
    try {
      const parsed = JSON.parse(toolCall.output);
      if (parsed.data && parsed.data.id) {
        return parsed.data as Task;
      }
    } catch {
      // Output might be plain text
    }
  }

  // Try to construct task from arguments
  const args = toolCall.arguments;
  if (args.title && typeof args.title === "string") {
    // Create a minimal task object for display
    return {
      id: (args.id as number) || 0,
      user_id: "",
      title: args.title,
      description: (args.description as string | null) || null,
      priority: (args.priority as Task["priority"]) || "MEDIUM",
      completed: false,
      tags: (args.tags as Task["tags"]) || [],
      due_date: (args.due_date as string | null) || null,
      recurrence_pattern: null,
      transcription_text: null,
      ai_summary: null,
      embedding_id: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
  }

  return null;
}

// =============================================================================
// Props
// =============================================================================

interface ChatMessageProps {
  message: Message;
  isStreaming?: boolean;
  onTaskAction?: (action: "complete" | "delete" | "edit", task: Task) => void;
}

// =============================================================================
// Animation Variants - T049: Spring physics matching dashboard components
// =============================================================================

const messageVariants = {
  hidden: {
    opacity: 0,
    y: 10,
    scale: 0.95,
  },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
  },
};

// =============================================================================
// Component
// =============================================================================

export function ChatMessage({ message, isStreaming, onTaskAction }: ChatMessageProps) {
  const isUser = message.role === "user";
  const isSystem = message.role === "system";
  const isVoice = message.messageType === "voice";

  // Detect text direction for alignment (40%+ Urdu = RTL)
  const textDirection = useMemo(() => getTextDirection(message.content), [message.content]);

  // System messages are styled differently
  if (isSystem) {
    return (
      <motion.div
        variants={messageVariants}
        initial="hidden"
        animate="visible"
        className="flex justify-center my-2"
      >
        <div
          className="px-3 py-1.5 rounded-full text-xs text-center"
          style={{
            background: "rgba(168, 85, 247, 0.2)",
            border: "1px solid rgba(168, 85, 247, 0.3)",
            color: "rgba(255,255,255,0.8)",
          }}
        >
          {message.content}
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      variants={messageVariants}
      initial="hidden"
      animate="visible"
      whileHover={{ scale: 1.002 }}
      whileTap={{ scale: 0.998 }}
      transition={{ type: "spring", stiffness: 400, damping: 25 }}
      className={`flex gap-3 ${isUser ? "flex-row-reverse" : "flex-row"}`}
    >
      {/* Avatar */}
      <div
        className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isUser ? "bg-gradient-to-br from-cyan-400 to-blue-500" : ""
        }`}
        style={
          !isUser
            ? {
                background: "linear-gradient(135deg, #a855f7 0%, #ec4899 100%)",
              }
            : undefined
        }
      >
        {isUser ? (
          <User className="w-4 h-4 text-white" />
        ) : (
          <Bot className="w-4 h-4 text-white" />
        )}
      </div>

      {/* Message Content */}
      <div className={`flex flex-col ${isUser ? "items-end" : "items-start"} max-w-[80%]`}>
        {isVoice && isUser ? (
          // T047: Voice Message Indicator - Glassmorphism styling
          <motion.div
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="px-4 py-3 rounded-2xl rounded-tr-sm flex items-center gap-2"
            style={{
              background: "linear-gradient(135deg, rgba(0, 245, 255, 0.2) 0%, rgba(0, 180, 216, 0.2) 100%)",
              border: "1px solid rgba(0, 245, 255, 0.3)",
              color: "#00f5ff",
              backdropFilter: "blur(12px)",
              boxShadow: "0 0 20px rgba(0, 245, 255, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.1)",
            }}
          >
            <Mic className="w-4 h-4" />
            <span className="font-medium">Voice message</span>
          </motion.div>
        ) : (
          // T046: Regular Text Message - Glassmorphism styling
          <motion.div
            whileHover={{ scale: 1.01 }}
            whileTap={{ scale: 0.99 }}
            className={`px-4 py-2.5 rounded-2xl text-sm ${
              isUser ? "rounded-tr-sm" : "rounded-tl-sm"
            }`}
            style={
              isUser
                ? {
                    // T050: User message - Cyan gradient matching dashboard
                    background: "linear-gradient(135deg, rgba(0, 245, 255, 0.2) 0%, rgba(0, 180, 216, 0.2) 100%)",
                    border: "1px solid rgba(0, 245, 255, 0.3)",
                    color: "#00f5ff",
                    backdropFilter: "blur(12px)",
                    boxShadow: "0 0 15px rgba(0, 245, 255, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.1)",
                  }
                : {
                    // T046: Assistant message - Glassmorphism with white/gray tint
                    background: "rgba(255, 255, 255, 0.05)",
                    backdropFilter: "blur(12px)",
                    border: "1px solid rgba(255, 255, 255, 0.08)",
                    color: "rgba(255, 255, 255, 0.9)",
                    boxShadow: "0 4px 20px rgba(0, 0, 0, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.05)",
                  }
            }
          >
            <div dir={textDirection}>
              <ReactMarkdown
                components={{
                  // Custom text renderer for mixed language support
                  p: ({ children }) => (
                    <p style={{ marginBottom: "0.5rem" }}>
                      {renderMixedLanguageText(children)}
                    </p>
                  ),
                  li: ({ children }) => (
                    <li style={{ marginBottom: "0.15rem" }}>
                      {renderMixedLanguageText(children)}
                    </li>
                  ),
                  strong: ({ children }) => (
                    <strong style={{ fontWeight: 700, color: isUser ? "inherit" : "#00f5ff" }}>
                      {renderMixedLanguageText(children)}
                    </strong>
                  ),
                  // Style links
                  a: ({ ...props }) => (
                    <a
                      {...props}
                      style={{
                        color: isUser ? "#0ea5e9" : "#00f5ff",
                        textDecoration: "underline",
                      }}
                      target="_blank"
                      rel="noopener noreferrer"
                    />
                  ),
                  // Style unordered lists
                  ul: ({ ...props }) => (
                    <ul
                      {...props}
                      style={{
                        listStyleType: "disc",
                        marginLeft: textDirection === "rtl" ? "0" : "1.2rem",
                        marginRight: textDirection === "rtl" ? "1.2rem" : "0",
                        paddingLeft: textDirection === "rtl" ? "0" : "0.5rem",
                        listStylePosition: "inside",
                        marginTop: "0.25rem",
                        marginBottom: "0.25rem",
                      }}
                    />
                  ),
                  // Style ordered lists
                  ol: ({ ...props }) => (
                    <ol
                      {...props}
                      style={{
                        listStyleType: "decimal",
                        marginLeft: textDirection === "rtl" ? "0" : "1.2rem",
                        marginRight: textDirection === "rtl" ? "1.2rem" : "0",
                        paddingLeft: textDirection === "rtl" ? "0" : "0.5rem",
                        listStylePosition: "inside",
                        marginTop: "0.25rem",
                        marginBottom: "0.25rem",
                      }}
                    />
                  ),
                  // Style code (inline)
                  // eslint-disable-next-line @typescript-eslint/no-explicit-any
                  code: ({ inline, ...props }: { inline?: boolean } & any) => (
                    <code
                      {...props}
                      style={{
                        background: isUser ? "rgba(0,0,0,0.1)" : "rgba(255,255,255,0.15)",
                        padding: inline ? "2px 6px" : "0.5rem",
                        borderRadius: inline ? "4px" : "8px",
                        fontSize: "0.9em",
                        fontFamily: "'JetBrains Mono', monospace",
                      }}
                    />
                  ),
                }}
              >
                {message.content}
              </ReactMarkdown>

              {/* Streaming cursor */}
              {isStreaming && (
                <motion.span
                  animate={{ opacity: [0, 1, 0] }}
                  transition={{ repeat: Infinity, duration: 1 }}
                  className="inline-block w-2 h-4 ml-1 align-middle"
                  style={{
                    background: "rgba(255,255,255,0.7)",
                  }}
                />
              )}
            </div>
          </motion.div>
        )}

        {/* Task Cards from Tool Calls (T116) */}
        {!isUser && message.toolCalls && message.toolCalls.length > 0 && (
          <div className="mt-3 space-y-2">
            {message.toolCalls.map((toolCall, idx) => {
              const task = extractTaskFromToolCall(toolCall);
              return task && (
                <motion.div
                  key={`task-${idx}`}
                  initial={{ opacity: 0, y: 5 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.1 }}
                >
                  <InlineTaskCard task={task} onAction={onTaskAction} />
                </motion.div>
              );
            })}
          </div>
        )}

        {/* Tool Calls Indicator */}
        {message.toolCalls && message.toolCalls.length > 0 && (
          <div className="flex items-center gap-2 mt-1 px-2 py-1 rounded-lg text-xs text-white/50">
            <Wrench className="w-3 h-3" />
            <span>
              Used {message.toolCalls.length} tool{message.toolCalls.length > 1 ? "s" : ""}
            </span>
          </div>
        )}

        {/* Timestamp */}
        <span className="text-xs text-white/40 mt-1 px-1">
          {safeFormatDistanceToNow(message.createdAt)}
        </span>
      </div>
    </motion.div>
  );
}
