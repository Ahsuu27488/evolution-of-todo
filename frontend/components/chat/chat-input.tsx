/**
 * Chat Input - Input component with voice recording.
 *
 * Features:
 * - Auto-expanding textarea
 * - Voice recording with Whisper API (T086-T091)
 * - Send button
 * - Character counter
 * - RTL support for Urdu (T078)
 * - Responsive design across all screen sizes
 *
 * Per spec.md FR-001 through FR-010, FR-052 through FR-061, FR-048.
 */

"use client";

import { useRef, useEffect, useMemo, useState, useCallback } from "react";
import { motion } from "framer-motion";
import { Send, Loader2, Mic } from "lucide-react";

import { useChatInput } from "@/lib/stores/chat-store";
import { useChatStreaming } from "@/lib/stores/chat-store";
import { getTextDirection } from "@/lib/utils/text-direction";
import { useResponsive, type Breakpoint } from "@/lib/utils/responsive";
import { VoiceRecorder, type VoiceRecorderRef } from "./voice-recorder";

interface ChatInputProps {
  onSend: () => void;
  disabled?: boolean;
}

// Responsive configuration
const getResponsiveConfig = (breakpoint: Breakpoint) => {
  if (breakpoint === "mobile") {
    return {
      containerGap: "gap-1",
      containerPx: "px-3",
      containerPy: "py-2",
      textareaMinH: "min-h-[40px]",
      textareaMaxH: 100,
      textSize: "text-xs",
      iconSize: "w-4 h-4",
      sendButtonPadding: "p-2",
    };
  }
  if (breakpoint === "tablet") {
    return {
      containerGap: "gap-2",
      containerPx: "px-4",
      containerPy: "py-3",
      textareaMinH: "min-h-[44px]",
      textareaMaxH: 120,
      textSize: "text-sm",
      iconSize: "w-5 h-5",
      sendButtonPadding: "p-2.5",
    };
  }
  // Desktop
  return {
    containerGap: "gap-2",
    containerPx: "px-4",
    containerPy: "py-3",
    textareaMinH: "min-h-[44px]",
    textareaMaxH: 120,
    textSize: "text-sm",
    iconSize: "w-5 h-5",
    sendButtonPadding: "p-2.5",
  };
};

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const { inputValue, setInputValue } = useChatInput();
  const { isStreaming } = useChatStreaming();
  const { breakpoint } = useResponsive();

  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const voiceRecorderRef = useRef<VoiceRecorderRef>(null);
  const [isRecording, setIsRecording] = useState(false);

  // Get responsive configuration
  const responsive = getResponsiveConfig(breakpoint);

  // Detect text direction for Urdu support (T078)
  const textDirection = useMemo(() => getTextDirection(inputValue), [inputValue]);

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    textarea.style.height = "auto";
    textarea.style.height = Math.min(textarea.scrollHeight, responsive.textareaMaxH) + "px";
  }, [inputValue, responsive.textareaMaxH]);

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

  // Handle button click based on state
  const handleButtonClick = useCallback(() => {
    if (isRecording) {
      // Stop recording
      if (voiceRecorderRef.current) {
        voiceRecorderRef.current.stopRecording();
      }
    } else if (inputValue.trim()) {
      // Has text - send message
      onSend();
    } else {
      // No text - start voice recording
      if (voiceRecorderRef.current) {
        voiceRecorderRef.current.startRecording();
      }
    }
  }, [isRecording, inputValue, onSend]);

  // Responsive placeholder text
  const placeholderText = useMemo(() => {
    if (isRecording) {
      return "Recording...";  // Show during recording
    }
    if (textDirection === "rtl") {
      return breakpoint === "mobile"
        ? "پوچھیں کے لیے..."  // Shorter Urdu for mobile
        : "پوچھیں کے لیے ٹاسک شامل کریں...";
    }
    return breakpoint === "mobile"
      ? "Ask me anything..."  // Shorter for mobile
      : "Ask me to add tasks, plan your week...";
  }, [textDirection, breakpoint, isRecording]);

  return (
    <div
      className={`flex items-end ${responsive.containerGap} ${responsive.containerPx} ${responsive.containerPy} rounded-xl relative`}
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
        ref={voiceRecorderRef}
        onTranscript={handleTranscript}
        disabled={disabled || isStreaming}
        onRecordingStateChange={setIsRecording}
        hideMainButtonDuringRecording={true}
      />

      {/* Text Input */}
      <textarea
        ref={textareaRef}
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholderText}
        disabled={disabled || isStreaming}
        dir={textDirection}
        className={`flex-1 ${responsive.textareaMinH} bg-transparent text-white placeholder-white/40 resize-none outline-none`}
        style={{
          fieldSizing: "content",
          // Urdu-friendly font settings (T078)
          fontFamily: textDirection === "rtl" ? "'Noto Nastaliq Urdu', 'Amiri', serif" : "inherit",
          lineHeight: textDirection === "rtl" ? "1.8" : "1.5",
          // T048: Focus state styling
          transition: "all 0.2s ease",
          padding: breakpoint === "mobile" ? "0.5rem 0" : "0.75rem 0",
          // Prevents iOS auto-zoom on focus - always use 16px on mobile
          fontSize: breakpoint === "mobile" ? "16px" : undefined,
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

      {/* Send Button - doubles as voice start/stop button */}
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={handleButtonClick}
        disabled={(!inputValue.trim() && !isRecording) || disabled || isStreaming}
        className={`flex-shrink-0 ${responsive.sendButtonPadding} rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed min-h-[40px] min-w-[40px] flex items-center justify-center`}
        style={{
          // T050: Cyan primary color matching dashboard
          // Button is active (cyan) when: has text OR is recording
          background:
            (inputValue.trim() || isRecording) && !disabled && !isStreaming
              ? "linear-gradient(135deg, rgba(0, 245, 255, 0.8) 0%, rgba(0, 180, 216, 0.8) 100%)"
              : "rgba(255,255,255,0.1)",
          border: (inputValue.trim() || isRecording) && !disabled && !isStreaming
            ? "1px solid rgba(0, 245, 255, 0.3)"
            : "1px solid rgba(255, 255, 255, 0.1)",
          boxShadow: (inputValue.trim() || isRecording) && !disabled && !isStreaming
            ? "0 0 15px rgba(0, 245, 255, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.1)"
            : "none",
        }}
        title={isRecording ? "Stop recording" : inputValue.trim() ? "Send message" : "Start voice recording"}
      >
        {isStreaming ? (
          <Loader2 className={responsive.iconSize + " text-white/70 animate-spin"} />
        ) : isRecording ? (
          // Square/Stop icon during recording (white square)
          <div className="w-3.5 h-3.5 rounded-sm bg-white" />
        ) : inputValue.trim() ? (
          // Send icon when there's text to send
          <Send className={responsive.iconSize + " text-white/70"} />
        ) : (
          // Mic icon when idle (no text, not recording) - indicates this button can start voice
          <Mic className={responsive.iconSize + " text-white/70"} />
        )}
      </motion.button>

      {/* Character Counter - Responsive positioning */}
      {inputValue.length > 0 && breakpoint !== "mobile" && (
        <span className="text-xs text-white/30 absolute bottom-2 right-2 pointer-events-none">
          {inputValue.length}/5000
        </span>
      )}
      {/* Mobile: Show character count above input when text is present */}
      {inputValue.length > 0 && breakpoint === "mobile" && inputValue.length > 100 && (
        <span className="text-[10px] text-white/30 absolute -top-4 left-0 pointer-events-none">
          {inputValue.length}/5000
        </span>
      )}
    </div>
  );
}
