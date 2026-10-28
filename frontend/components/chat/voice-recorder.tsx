/**
 * Voice Recorder - Audio recording with Whisper transcription.
 *
 * Features:
 * - MediaRecorder API for audio capture
 * - 30-second recording limit (T087)
 * - Visual feedback with pulse animation (T088, T026)
 * - Upload progress indicator (T089)
 * - Whisper API integration (T090)
 * - Urdu language support
 * - Direct send to agent (T028) - no confirmation prompts
 * - Recording duration display (T025) - MM:SS format
 * - Stop/cancel button (T027) - allows cancel during recording
 * - Error handling with retry (T030)
 *
 * Per spec.md T086-T092.
 * Per User Story 4 (FR-015 through FR-019): Streamlined voice recording.
 */

"use client";

import { useState, useRef, useEffect, useCallback, useImperativeHandle, forwardRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";
import { Mic, Loader2, Send } from "lucide-react";
import { useChatLanguage } from "@/lib/stores/chat-store";
import { API_URL } from "@/lib/config/api";
import { getAuthToken } from "@/lib/auth/token";

// =============================================================================
// Types
// =============================================================================

export interface VoiceRecorderRef {
  /** Stop the current recording (if recording) */
  stopRecording: () => void;
  /** Start recording (if not already recording) */
  startRecording: () => void;
  /** Check if currently recording */
  isRecording: () => boolean;
}

interface VoiceRecorderProps {
  onTranscript: (text: string, language?: string) => void;
  onVoiceMessageSend?: (text: string, language?: string) => void;  // Auto-send callback
  disabled?: boolean;
  onRecordingStateChange?: (isRecording: boolean) => void;  // Expose recording state to parent
  hideMainButtonDuringRecording?: boolean;  // Hide the main Record/Stop/Send button when recording (parent takes over)
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

// =============================================================================
// Component
// =============================================================================

export const VoiceRecorder = forwardRef<VoiceRecorderRef, VoiceRecorderProps>(
  ({ onTranscript, onVoiceMessageSend, disabled, onRecordingStateChange, hideMainButtonDuringRecording }, ref) => {
    const { languagePreference } = useChatLanguage();

    const [state, setState] = useState<RecordingState>({
      isRecording: false,
      duration: 0,
      audioBlob: null,
    });

    const [isTranscribing, setIsTranscribing] = useState(false);
    const [uploadProgress, setUploadProgress] = useState(0);
    const [error, setError] = useState<string | null>(null);

    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const chunksRef = useRef<BlobPart[]>([]);
    const timerRef = useRef<NodeJS.Timeout | null>(null);
    const streamRef = useRef<MediaStream | null>(null);
    const isCancellingRef = useRef(false); // Flag to track cancellation intent

    // Clear error after 3 seconds
    useEffect(() => {
      if (error) {
        const timeout = setTimeout(() => setError(null), 3000);
        return () => clearTimeout(timeout);
      }
    }, [error]);

    // Notify parent when recording state changes
    useEffect(() => {
      onRecordingStateChange?.(state.isRecording);
    }, [state.isRecording, onRecordingStateChange]);

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
        // If user cancelled, don't create the audio blob, but still release microphone
        if (isCancellingRef.current) {
          isCancellingRef.current = false;
          chunksRef.current = [];
          // CRITICAL: Release microphone tracks even when cancelling
          if (streamRef.current) {
            streamRef.current.getTracks().forEach((track) => track.stop());
            streamRef.current = null;
          }
          return;
        }

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

  // Expose methods to parent via ref (must be after stopRecording is defined)
  useImperativeHandle(ref, () => ({
    stopRecording: () => {
      if (state.isRecording) {
        stopRecording();
      }
    },
    startRecording: () => {
      if (!state.isRecording) {
        startRecording();
      }
    },
    isRecording: () => state.isRecording,
  }), [state.isRecording, stopRecording, startRecording]);

  // Transcribe audio using Whisper API
  // Per T028: Sends directly to agent without confirmation prompt
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

      // Transcription is independent of language mode
      // - Auto mode: Let Whisper auto-detect (no language param)
      // - EN mode: Force English transcription
      // - UR mode: Force Urdu transcription
      // This ensures transcription captures what was actually spoken
      const language = languagePreference === "auto" ? undefined : languagePreference;
      if (language) {
        formData.append("language", language);
      }

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

      // T028: Send voice message directly to agent without confirmation
      const transcript = {
        text: result.text,
        language: result.language,
      };

      if (onVoiceMessageSend) {
        // Auto-send voice message directly to chat (streamlined UX)
        onVoiceMessageSend(transcript.text, transcript.language);
      } else {
        // Fallback: put in input field (original behavior)
        onTranscript(transcript.text, transcript.language);
      }

      // Clear audio blob after successful transcription
      setState((prev) => ({ ...prev, audioBlob: null }));

    } catch (err) {
      console.error("Transcription error:", err);
      // T030: Inline error message with retry option
      setError("Transcription failed. Please try again or use text input.");
    } finally {
      setIsTranscribing(false);
      setUploadProgress(0);
    }
  }, [state.audioBlob, languagePreference, onTranscript, onVoiceMessageSend]);

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

  // Retry button on error (T030)
  const handleRetry = useCallback(() => {
    setError(null);
    if (state.audioBlob) {
      transcribeAudio();
    }
  }, [state.audioBlob, transcribeAudio]);

  // Cancel button during recording (T027)
  const handleCancelRecording = useCallback(() => {
    isCancellingRef.current = true; // Set flag BEFORE stopping
    stopRecording();
    setState({ isRecording: false, duration: 0, audioBlob: null });
    // Error removed - cancellation is a user action, not an error
  }, [stopRecording]);

  // Don't render if disabled and no interaction possible
  if (disabled && !state.isRecording && !state.audioBlob && !isTranscribing) {
    return null;
  }

  return (
    <div className="relative flex items-center gap-2">
      {/* Error message with retry button (T030) */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            className="flex items-center gap-2 whitespace-nowrap text-xs text-destructive"
            role="alert"
          >
            <span>{error}</span>
            <button
              type="button"
              onClick={handleRetry}
              className="rounded-full px-1.5 font-medium underline underline-offset-2 outline-none hover:text-foreground focus-visible:ring-[3px] focus-visible:ring-ring/50"
            >
              Retry
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Recording duration indicator (T025) */}
      <AnimatePresence>
        {state.isRecording && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="font-mono text-xs text-muted-foreground tabular-nums"
            aria-live="off"
          >
            {formatDuration(state.duration)} / {MAX_RECORDING_SECONDS}s
          </motion.div>
        )}
      </AnimatePresence>

      {/* Cancel button during recording (T027) */}
      <AnimatePresence>
        {state.isRecording && (
          <motion.button
            type="button"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            onClick={handleCancelRecording}
            className="flex h-11 items-center justify-center rounded-full border border-border px-3.5 text-xs font-medium text-muted-foreground outline-none transition-colors hover:bg-accent hover:text-foreground focus-visible:ring-[3px] focus-visible:ring-ring/50"
          >
            Cancel
          </motion.button>
        )}
      </AnimatePresence>

      {/* Record/Stop/Send button */}
      {/* Hide during recording if parent component takes over stop button */}
      {!(hideMainButtonDuringRecording && state.isRecording) && (() => {
        const readyToSend = Boolean(state.audioBlob || (state.isRecording && chunksRef.current.length > 0))
        const label = isTranscribing
          ? "Transcribing"
          : readyToSend
            ? "Send voice message"
            : state.isRecording
              ? "Stop recording"
              : "Record a voice message"
        return (
          <button
            type="button"
            onClick={handleRecordClick}
            disabled={disabled || isTranscribing}
            aria-label={label}
            title={label}
            className={cn(
              "relative grid size-11 shrink-0 place-items-center rounded-full outline-none transition-[background-color,color,transform] duration-150",
              "focus-visible:ring-[3px] focus-visible:ring-ring/50 active:scale-95 disabled:opacity-50",
              isTranscribing
                ? "bg-primary/15 text-primary"
                : readyToSend
                  ? "bg-primary text-primary-foreground"
                  : state.isRecording
                    ? "bg-destructive/15 text-destructive"
                    : "text-muted-foreground hover:bg-accent hover:text-foreground"
            )}
          >
            {/* Recording indicator: a soft ring that breathes (T026, T088) */}
            {state.isRecording && !state.audioBlob && (
              <motion.span
                aria-hidden
                className="absolute inset-0 rounded-full border-2 border-destructive/50 motion-reduce:hidden"
                animate={{ scale: [1, 1.18, 1], opacity: [0.7, 0, 0.7] }}
                transition={{ duration: PULSE_ANIMATION_DURATION, repeat: Infinity, ease: "easeInOut" }}
              />
            )}

            {isTranscribing ? (
              <Loader2 className="size-5 animate-spin" aria-hidden />
            ) : readyToSend ? (
              <Send className="size-[18px]" aria-hidden />
            ) : state.isRecording ? (
              <span className="size-3.5 rounded-[3px] bg-current" aria-hidden />
            ) : (
              <Mic className="size-5" aria-hidden />
            )}
          </button>
        )
      })()}

      {/* Upload progress indicator (T089) */}
      {isTranscribing && (
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${uploadProgress}%` }}
          className="h-1 max-w-[60px] rounded-full bg-primary"
        />
      )}
    </div>
  );
});

VoiceRecorder.displayName = "VoiceRecorder";
