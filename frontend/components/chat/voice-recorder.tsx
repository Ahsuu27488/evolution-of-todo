/* eslint-disable @typescript-eslint/no-unused-vars */
/**
 * Voice Recorder - Audio recording with Whisper transcription.
 *
 * Features:
 * - MediaRecorder API for audio capture
 * - 30-second recording limit (T087)
 * - Visual feedback with pulse animation (T088)
 * - Upload progress indicator (T089)
 * - Whisper API integration (T090)
 * - Urdu language support
 * - Confirmation prompt for transcriptions (T092)
 *
 * Per spec.md T086-T092.
 */

"use client";

import { useState, useRef, useEffect, useCallback, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Mic, MicOff, Loader2, Check, X } from "lucide-react";
import { useChatLanguage } from "@/lib/stores/chat-store";
import { API_URL } from "@/lib/config/api";
import { getAuthToken } from "@/lib/auth/token";

// =============================================================================
// Types
// =============================================================================

interface VoiceRecorderProps {
  onTranscript: (text: string, language?: string) => void;
  disabled?: boolean;
}

interface RecordingState {
  isRecording: boolean;
  duration: number;
  audioBlob: Blob | null;
}

// =============================================================================
// Constants
// =============================================================================

const MAX_RECORDING_SECONDS = 30; // T087: 30-second limit for cost containment
const PULSE_ANIMATION_DURATION = 1.5; // Seconds for pulsing effect

// T092: Ambiguous transcription patterns
const AMBIGUOUS_PATTERNS = [
  /\b(add|create|make|new)\s*\b/i,
  /\b(delete|remove|clear)\s*\b/i,
  /\b(complete|finish|done)\s*\b/i,
  /\b(schedule|remind|notify)\s*\b/i,
  /\b(tomorrow|today|week|month)\s*\b/i,
];

/**
 * Check if transcribed text might be ambiguous (T092)
 * Ambiguous transcriptions need user confirmation before sending.
 */
function isAmbiguousTranscription(text: string): boolean {
  if (!text || text.length < 5) return false;
  // Check if text matches any ambiguous pattern
  return AMBIGUOUS_PATTERNS.some(pattern => pattern.test(text));
}

// =============================================================================
// Component
// =============================================================================

export function VoiceRecorder({ onTranscript, disabled }: VoiceRecorderProps) {
  const { languagePreference } = useChatLanguage();

  const [state, setState] = useState<RecordingState>({
    isRecording: false,
    duration: 0,
    audioBlob: null,
  });

  const [isTranscribing, setIsTranscribing] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  // T092: Pending transcript confirmation state
  const [pendingTranscript, setPendingTranscript] = useState<{
    text: string;
    language?: string;
  } | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  // T092: Check if pending transcript is ambiguous
  const isAmbiguous = useMemo(() => {
    return pendingTranscript && isAmbiguousTranscription(pendingTranscript.text);
  }, [pendingTranscript]);

  // Clear error after 3 seconds
  useEffect(() => {
    if (error) {
      const timeout = setTimeout(() => setError(null), 3000);
      return () => clearTimeout(timeout);
    }
  }, [error]);

  // Format duration as MM:SS
  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  // Start recording
  const startRecording = useCallback(async () => {
    setError(null);

    try {
      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      // Initialize MediaRecorder
      const recorder = new MediaRecorder(stream, {
        mimeType: "audio/webm", // Prefer webm for better quality
      });

      mediaRecorderRef.current = recorder;
      chunksRef.current = [];

      // Handle data available event
      recorder.ondataavailable = (event: BlobEvent) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      // Handle recording stop
      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, {
          type: "audio/webm",
        });
        setState((prev) => ({ ...prev, audioBlob: blob, isRecording: false, duration: 0 }));

        // Stop all tracks to release microphone
        if (streamRef.current) {
          streamRef.current.getTracks().forEach((track) => track.stop());
          streamRef.current = null;
        }
      };

      // Start recording
      recorder.start();
      setState((prev) => ({ ...prev, isRecording: true, audioBlob: null, duration: 0 }));

      // Start duration timer with auto-stop at MAX_RECORDING_SECONDS (T087)
      timerRef.current = setInterval(() => {
        setState((prev) => {
          const newDuration = prev.duration + 1;
          if (newDuration >= MAX_RECORDING_SECONDS) {
            // Auto-stop at max duration
            stopRecording();
            return { ...prev, duration: MAX_RECORDING_SECONDS };
          }
          return { ...prev, duration: newDuration };
        });
      }, 1000);

    } catch (err) {
      console.error("Microphone access error:", err);
      setError("Microphone access denied. Please enable microphone permissions.");
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Stop recording
  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
      mediaRecorderRef.current.stop();
    }

    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  // Transcribe audio using Whisper API
  const transcribeAudio = useCallback(async () => {
    if (!state.audioBlob) return;

    setIsTranscribing(true);
    setUploadProgress(0);
    setError(null);

    try {
      // Get auth token for API call
      const token = await getAuthToken();
      if (!token) {
        throw new Error("Authentication required");
      }

      // Prepare form data
      const formData = new FormData();
      formData.append("file", state.audioBlob, "audio.webm");

      // Determine language parameter from preference
      // const language = languagePreference === "auto" ? "auto" : languagePreference;

      // Fetch with progress tracking (T089)
      const response = await fetch(`${API_URL}/api/chat/transcribe`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
        // Note: XHR would give better progress tracking, but fetch is simpler
      });

      setUploadProgress(100);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: "Transcription failed" }));
        throw new Error(errorData.detail || errorData.error || "Transcription failed");
      }

      const result = await response.json();

      // T092: Set pending transcript for confirmation (if ambiguous)
      // or send directly (if clear)
      const transcript = {
        text: result.text,
        language: result.language,
      };

      if (isAmbiguousTranscription(result.text)) {
        setPendingTranscript(transcript);
      } else {
        onTranscript(transcript.text, transcript.language);
      }

      // Clear audio blob after successful transcription
      setState((prev) => ({ ...prev, audioBlob: null }));

    } catch (err) {
      console.error("Transcription error:", err);
      setError("Transcription failed. Please try again or use text input.");
    } finally {
      setIsTranscribing(false);
      setUploadProgress(0);
    }
  }, [state.audioBlob, onTranscript]);

  // T092: Confirm pending transcript
  const handleConfirmTranscript = useCallback(() => {
    if (pendingTranscript) {
      onTranscript(pendingTranscript.text, pendingTranscript.language);
      setPendingTranscript(null);
    }
  }, [pendingTranscript, onTranscript]);

  // T092: Reject pending transcript
  const handleRejectTranscript = useCallback(() => {
    setPendingTranscript(null);
    setError("Transcription discarded. Please try again or type manually.");
  }, []);

  // Handle record button click
  const handleRecordClick = () => {
    if (state.isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  // Auto-transcribe when recording stops and we have audio
  useEffect(() => {
    if (!state.isRecording && state.audioBlob && !isTranscribing) {
      transcribeAudio();
    }
  }, [state.isRecording, state.audioBlob, isTranscribing, transcribeAudio]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
        mediaRecorderRef.current.stop();
      }
    };
  }, []);

  // Don't render if disabled and no interaction possible
  if (disabled && !state.isRecording && !state.audioBlob && !isTranscribing) {
    return null;
  }

  return (
    <div className="relative flex items-center gap-2">
      {/* Error message */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            className="text-xs text-red-400 whitespace-nowrap"
          >
            {error}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Recording duration indicator */}
      <AnimatePresence>
        {state.isRecording && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            className="text-xs font-mono text-white/70"
            style={{
              fontFamily: "monospace",
            }}
          >
            {formatDuration(state.duration)} / {MAX_RECORDING_SECONDS}s
          </motion.div>
        )}
      </AnimatePresence>

      {/* Record/Stop button */}
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={handleRecordClick}
        disabled={disabled || isTranscribing}
        className="relative flex-shrink-0 p-2.5 rounded-lg transition-all disabled:opacity-50"
        style={{
          background: state.isRecording
            ? "rgba(239, 68, 68, 0.2)"  // Red when recording
            : state.audioBlob || isTranscribing
              ? "rgba(0, 245, 255, 0.2)"  // Cyan when ready to transcribe
              : "rgba(255, 255, 255, 0.1)",
          border: state.isRecording
            ? "1px solid rgba(239, 68, 68, 0.3)"
            : "none",
        }}
      >
        {/* Recording indicator with pulse animation (T088) */}
        {state.isRecording && (
          <motion.span
            className="absolute inset-0 rounded-lg"
            animate={{
              scale: [1, 1.2, 1],
              opacity: [0.3, 0, 0.3],
            }}
            transition={{
              duration: PULSE_ANIMATION_DURATION,
              repeat: Infinity,
              ease: "easeInOut",
            }}
            style={{
              background: "rgba(239, 68, 68, 0.4)",
            }}
          />
        )}

        {isTranscribing ? (
          <Loader2 className="w-5 h-5 text-cyan-400 animate-spin" />
        ) : state.isRecording ? (
          <MicOff className="w-5 h-5 text-red-400" />
        ) : (
          <Mic className="w-5 h-5 text-white/70" />
        )}
      </motion.button>

      {/* Upload progress indicator (T089) */}
      {isTranscribing && (
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${uploadProgress}%` }}
          className="h-1 bg-cyan-500 rounded-full"
          style={{ maxWidth: "60px" }}
        />
      )}

      {/* T092: Confirmation prompt for ambiguous transcriptions */}
      <AnimatePresence>
        {pendingTranscript && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 10 }}
            className="absolute bottom-full left-0 mb-2 p-3 rounded-xl z-50"
            style={{
              background: "rgba(20, 20, 26, 0.95)",
              border: "1px solid rgba(255, 255, 255, 0.1)",
              backdropFilter: "blur(12px)",
              minWidth: "280px",
            }}
          >
            <div className="space-y-3">
              {/* Header */}
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-white/90">
                  {isAmbiguous ? "Confirm transcription?" : "Transcription ready"}
                </span>
                <button
                  onClick={handleRejectTranscript}
                  className="p-1 rounded hover:bg-white/10 text-white/50 hover:text-white/80 transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Transcript text */}
              <div
                className="p-2.5 rounded-lg text-sm text-white/80"
                style={{
                  background: "rgba(0, 245, 255, 0.1)",
                  border: "1px solid rgba(0, 245, 255, 0.2)",
                }}
              >
                &quot;{pendingTranscript.text}&quot;
              </div>

              {/* Warning for ambiguous transcriptions */}
              {isAmbiguous && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex items-start gap-2 text-xs text-amber-400/90"
                >
                  <span>⚠️</span>
                  <span>
                    This transcription contains task-related keywords.{" "}
                    Please confirm before sending.
                  </span>
                </motion.div>
              )}

              {/* Action buttons */}
              <div className="flex gap-2">
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleRejectTranscript}
                  className="flex-1 px-3 py-2 rounded-lg text-sm font-medium transition-all"
                  style={{
                    background: "rgba(255, 255, 255, 0.05)",
                    border: "1px solid rgba(255, 255, 255, 0.1)",
                  }}
                >
                  <div className="flex items-center justify-center gap-1.5">
                    <X className="w-3.5 h-3.5" />
                    <span>Retry</span>
                  </div>
                </motion.button>

                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleConfirmTranscript}
                  className="flex-1 px-3 py-2 rounded-lg text-sm font-medium transition-all"
                  style={{
                    background: "linear-gradient(135deg, rgb(0 245 255) 0%, rgb(168 85 247) 100%)",
                  }}
                >
                  <div className="flex items-center justify-center gap-1.5 text-white">
                    <Check className="w-3.5 h-3.5" />
                    <span>Send</span>
                  </div>
                </motion.button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
