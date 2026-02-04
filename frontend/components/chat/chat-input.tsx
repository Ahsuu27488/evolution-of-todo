/* eslint-disable @typescript-eslint/no-unused-vars */
/**
 * Chat Input - Input component with voice recording.
 *
 * Features:
 * - Auto-expanding textarea
 * - Voice recording with Whisper API (T086-T091)
 * - Send button
 * - Character counter
 * - RTL support for Urdu (T078)
 *
 * Per spec.md FR-001 through FR-010, FR-052 through FR-061, FR-048.
 */

"use client";

import { useRef, useEffect, useMemo } from "react";
import { motion } from "framer-motion";
import { Send, Loader2 } from "lucide-react";

import { useChatInput } from "@/lib/stores/chat-store";
import { useChatStreaming } from "@/lib/stores/chat-store";
import { VoiceRecorder } from "./voice-recorder";

interface ChatInputProps {
  onSend: () => void;
  disabled?: boolean;
}

// =============================================================================
// Urdu Detection Utilities (Per T069, T078)
// =============================================================================

/**
 * Check if text contains Urdu/Arabic characters.
 */
function isUrduText(text: string): boolean {
  if (!text) return false;
  const urduPattern = /[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]/;
  return urduPattern.test(text);
}

/**
 * Get text direction based on content.
 */
function getTextDirection(text: string): "rtl" | "ltr" {
  return isUrduText(text) ? "rtl" : "ltr";
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const { inputValue, setInputValue } = useChatInput();
  const { isStreaming } = useChatStreaming();

  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Detect text direction for Urdu support (T078)
  const textDirection = useMemo(() => getTextDirection(inputValue), [inputValue]);

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    textarea.style.height = "auto";
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + "px";
  }, [inputValue]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  };

  // Handle transcript from voice recording (T090, T091)
  const handleTranscript = (text: string, _language?: string) => {
    // Append transcript to current input value
    setInputValue(inputValue ? `${inputValue} ${text}` : text);
  };

  return (
    <div
      className="flex items-end gap-2 px-4 py-3 rounded-xl"
      style={{
        background: "rgba(255, 255, 255, 0.05)",
        border: "1px solid rgba(255, 255, 255, 0.1)",
      }}
    >
      {/* Voice Input Button with Whisper API (T086-T091) */}
      <VoiceRecorder
        onTranscript={handleTranscript}
        disabled={disabled || isStreaming}
      />

      {/* Text Input */}
      <textarea
        ref={textareaRef}
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={
          textDirection === "rtl"
            ? "پوچھیں کے لیے ٹاسک شامل کریں..."  // Urdu placeholder
            : "Ask me to add tasks, plan your week..."
        }
        disabled={disabled || isStreaming}
        dir={textDirection}
        className="flex-1 min-h-[44px] max-h-[120px] bg-transparent text-white placeholder-white/40 text-sm resize-none outline-none py-3"
        style={{
          fieldSizing: "content",
          // Urdu-friendly font settings (T078)
          fontFamily: textDirection === "rtl" ? "'Noto Nastaliq Urdu', 'Amiri', serif" : "inherit",
          lineHeight: textDirection === "rtl" ? "2" : "1.5",
        }}
      />

      {/* Send Button */}
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={onSend}
        disabled={!inputValue.trim() || disabled || isStreaming}
        className="flex-shrink-0 p-2.5 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        style={{
          background:
            inputValue.trim() && !disabled && !isStreaming
              ? "linear-gradient(135deg, #00f5ff 0%, #a855f7 100%)"
              : "rgba(255,255,255,0.1)",
        }}
      >
        {isStreaming ? (
          <Loader2 className="w-5 h-5 text-white/70 animate-spin" />
        ) : (
          <Send className="w-5 h-5 text-white/70" />
        )}
      </motion.button>

      {/* Character Counter */}
      {inputValue.length > 0 && (
        <span className="text-xs text-white/30 absolute bottom-2 right-2 pointer-events-none">
          {inputValue.length}/5000
        </span>
      )}
    </div>
  );
}
