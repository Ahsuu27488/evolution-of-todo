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
import { getTextDirection } from "@/lib/utils/text-direction";
import { VoiceRecorder } from "./voice-recorder";

interface ChatInputProps {
  onSend: () => void;
  disabled?: boolean;
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
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const handleTranscript = (text: string, _language?: string) => {
    // Append transcript to current input value
    setInputValue(inputValue ? `${inputValue} ${text}` : text);
  };

  return (
    <div
      className="flex items-end gap-2 px-4 py-3 rounded-xl"
      style={{
        // T048: Glassmorphism styling matching dashboard input fields
        background: "rgba(255, 255, 255, 0.05)",
        backdropFilter: "blur(12px)",
        border: "1px solid rgba(255, 255, 255, 0.1)",
        boxShadow: "0 4px 20px rgba(0, 0, 0, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.05)",
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
          // T048: Focus state styling
          transition: "all 0.2s ease",
        }}
        onFocus={(e) => {
          // Add focus ring effect
          e.currentTarget.parentElement!.style.borderColor = "rgba(0, 245, 255, 0.3)";
          e.currentTarget.parentElement!.style.boxShadow = "0 0 0 2px rgba(0, 245, 255, 0.1), 0 4px 20px rgba(0, 0, 0, 0.15)";
        }}
        onBlur={(e) => {
          // Reset focus state
          e.currentTarget.parentElement!.style.borderColor = "rgba(255, 255, 255, 0.1)";
          e.currentTarget.parentElement!.style.boxShadow = "0 4px 20px rgba(0, 0, 0, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.05)";
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
          // T050: Cyan primary color matching dashboard
          background:
            inputValue.trim() && !disabled && !isStreaming
              ? "linear-gradient(135deg, rgba(0, 245, 255, 0.8) 0%, rgba(0, 180, 216, 0.8) 100%)"
              : "rgba(255,255,255,0.1)",
          border: inputValue.trim() && !disabled && !isStreaming
            ? "1px solid rgba(0, 245, 255, 0.3)"
            : "1px solid rgba(255, 255, 255, 0.1)",
          boxShadow: inputValue.trim() && !disabled && !isStreaming
            ? "0 0 15px rgba(0, 245, 255, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.1)"
            : "none",
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
