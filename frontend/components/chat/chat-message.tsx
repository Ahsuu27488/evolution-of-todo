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
 */

import { motion } from "framer-motion";
import { User, Bot, Wrench } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { useMemo } from "react";
import type { Task } from "@/types/task";
import { InlineTaskCard } from "./task-card";

// =============================================================================
// Urdu Detection Utilities (Per T069, T077)
// =============================================================================

/**
 * Check if text contains Urdu/Arabic characters.
 * Per FR-042: Unicode range U+0600-U+06FF for Urdu detection.
 */
function isUrduText(text: string): boolean {
  if (!text) return false;
  // Urdu/Arabic Unicode range
  const urduPattern = /[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]/;
  return urduPattern.test(text);
}

/**
 * Get text direction based on content.
 * Returns "rtl" for Urdu text, "ltr" otherwise.
 */
function getTextDirection(text: string): "rtl" | "ltr" {
  return isUrduText(text) ? "rtl" : "ltr";
}

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

interface ChatMessageProps {
  message: {
    id: string;
    role: "user" | "assistant" | "system";
    content: string;
    toolCalls?: Array<{
      tool: string;
      arguments: Record<string, unknown>;
      output?: string;
    }>;
    createdAt: string;
  };
  isStreaming?: boolean;
  onTaskAction?: (action: "complete" | "delete" | "edit", task: Task) => void;
}

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

export function ChatMessage({ message, isStreaming, onTaskAction }: ChatMessageProps) {
  const isUser = message.role === "user";
  const isSystem = message.role === "system";

  // Detect text direction for Urdu support (T077)
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
        <div
          className={`px-4 py-2.5 rounded-2xl text-sm ${
            isUser ? "rounded-tr-sm" : "rounded-tl-sm"
          }`}
          style={
            isUser
              ? {
                  background: "linear-gradient(135deg, #00f5ff 0%, #00b4d8 100%)",
                  color: "#0f172a",
                }
              : {
                  background: "rgba(255, 255, 255, 0.1)",
                  border: "1px solid rgba(255, 255, 255, 0.1)",
                  color: "rgba(255, 255, 255, 0.9)",
                }
          }
        >
          <p
            className="whitespace-pre-wrap break-words"
            dir={textDirection}
            style={{
              // Urdu-friendly font settings (T077)
              fontFamily: textDirection === "rtl" ? "'Noto Nastaliq Urdu', 'Amiri', serif" : "inherit",
              lineHeight: textDirection === "rtl" ? "2" : "1.5",
            }}
          >
            {message.content}
          </p>

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
          {formatDistanceToNow(new Date(message.createdAt), { addSuffix: true })}
        </span>
      </div>
    </motion.div>
  );
}
