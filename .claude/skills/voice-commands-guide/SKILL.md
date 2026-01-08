---
name: "voice-commands-guide"
description: "Guide implementation of voice input for chatbot using Web Speech API. Use when adding voice command functionality to the todo chatbot (Phase III+, Bonus +200 points)."
version: "1.0.0"
---

# Voice Commands Implementation Guide

## When to Use This Skill

Activation triggers (Claude auto-detects these):
- User mentions voice input, speech recognition, or voice commands
- Implementation requires microphone integration
- User asks about hands-free task management
- Bonus feature: Voice Commands (+200 points) implementation begins

## How This Skill Works

Step-by-step workflow:
1. **Check Browser Support**: Verify Web Speech API availability
2. **Request Permissions**: Get microphone access
3. **Configure Recognition**: Set up speech recognition parameters
4. **Handle Results**: Process transcription and confidence scores
5. **Integrate with Chat**: Send transcribed text to chat endpoint
6. **Provide Feedback**: Visual and audio confirmation

## Output Format

Provide structured output:
- **Browser Support**: Supported browsers and fallbacks
- **Permission Flow**: Microphone access request pattern
- **Recognition Config**: Language, continuous mode, confidence
- **UI Components**: Mic button, transcript display, status indicator
- **Error Handling**: Common issues and solutions

## Constraints and Rules

- ALWAYS check browser support before initialization
- ALWAYS request microphone permission explicitly
- Show visual feedback during listening state
- Display transcribed text before sending
- Handle low-confidence transcriptions appropriately
- Provide fallback to text input if voice unavailable
- This skill applies to Phase III+ bonus feature

## Browser Support

| Browser | Support | Notes |
|---------|---------|-------|
| Chrome | Full | Best support, recommended |
| Edge | Full | Chromium-based, works well |
| Safari | Partial | iOS and macOS support |
| Firefox | None | Use text fallback |

## Example: Voice Input Implementation

**Input**: "Add voice command support to the chatbot"

**Output**:

### 1. Voice Input Hook

```typescript
// hooks/useVoiceInput.ts
"use client";

import { useState, useEffect, useCallback } from "react";

interface VoiceInputResult {
  isSupported: boolean;
  isListening: boolean;
  transcript: string;
  confidence: number;
  error: string | null;
  startListening: () => void;
  stopListening: () => void;
  resetTranscript: () => void;
}

export function useVoiceInput(): VoiceInputResult {
  const [isSupported, setIsSupported] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [confidence, setConfidence] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [recognition, setRecognition] = useState<SpeechRecognition | null>(null);

  useEffect(() => {
    // Check browser support
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (SpeechRecognition) {
      setIsSupported(true);
      const recognizer = new SpeechRecognition();

      // Configuration
      recognizer.continuous = false;  // Single utterance mode
      recognizer.interimResults = true;  // Show partial results
      recognizer.lang = "en-US";  // Default language

      // Event handlers
      recognizer.onstart = () => {
        setIsListening(true);
        setError(null);
      };

      recognizer.onresult = (event) => {
        const last = event.results.length - 1;
        const result = event.results[last];

        setTranscript(result[0].transcript);
        setConfidence(result[0].confidence);
      };

      recognizer.onerror = (event) => {
        setError(event.error);
        setIsListening(false);
      };

      recognizer.onend = () => {
        setIsListening(false);
      };

      setRecognition(recognizer);
    }

    return () => {
      recognition?.abort();
    };
  }, []);

  const startListening = useCallback(() => {
    if (recognition && !isListening) {
      setTranscript("");
      setConfidence(0);
      recognition.start();
    }
  }, [recognition, isListening]);

  const stopListening = useCallback(() => {
    if (recognition && isListening) {
      recognition.stop();
    }
  }, [recognition, isListening]);

  const resetTranscript = useCallback(() => {
    setTranscript("");
    setConfidence(0);
  }, []);

  return {
    isSupported,
    isListening,
    transcript,
    confidence,
    error,
    startListening,
    stopListening,
    resetTranscript,
  };
}
```

### 2. Voice Button Component

```typescript
// components/VoiceButton.tsx
"use client";

import { useVoiceInput } from "@/hooks/useVoiceInput";
import { MicrophoneIcon, StopIcon } from "@heroicons/react/24/solid";

interface VoiceButtonProps {
  onTranscript: (text: string) => void;
  confidenceThreshold?: number;
}

export function VoiceButton({
  onTranscript,
  confidenceThreshold = 0.7
}: VoiceButtonProps) {
  const {
    isSupported,
    isListening,
    transcript,
    confidence,
    error,
    startListening,
    stopListening,
    resetTranscript,
  } = useVoiceInput();

  const handleStop = () => {
    stopListening();

    if (transcript && confidence >= confidenceThreshold) {
      onTranscript(transcript);
      resetTranscript();
    }
  };

  if (!isSupported) {
    return null;  // Graceful degradation
  }

  return (
    <div className="relative">
      {/* Mic Button */}
      <button
        onClick={isListening ? handleStop : startListening}
        className={`p-2 rounded-full transition-colors ${
          isListening
            ? "bg-red-500 text-white animate-pulse"
            : "bg-gray-200 hover:bg-gray-300"
        }`}
        title={isListening ? "Stop listening" : "Start voice input"}
      >
        {isListening ? (
          <StopIcon className="w-5 h-5" />
        ) : (
          <MicrophoneIcon className="w-5 h-5" />
        )}
      </button>

      {/* Transcript Preview */}
      {isListening && transcript && (
        <div className="absolute bottom-full mb-2 left-0 right-0 min-w-[200px]">
          <div className="bg-white border rounded-lg p-2 shadow-lg">
            <p className="text-sm text-gray-700">{transcript}</p>
            <div className="flex items-center mt-1">
              <div
                className={`h-1 rounded ${
                  confidence >= confidenceThreshold
                    ? "bg-green-500"
                    : "bg-yellow-500"
                }`}
                style={{ width: `${confidence * 100}%` }}
              />
              <span className="text-xs text-gray-500 ml-2">
                {Math.round(confidence * 100)}%
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="absolute bottom-full mb-2 text-xs text-red-500">
          {error === "not-allowed"
            ? "Microphone access denied"
            : `Error: ${error}`}
        </div>
      )}
    </div>
  );
}
```

### 3. Integration with Chat

```typescript
// app/chat/page.tsx (updated)
import { VoiceButton } from "@/components/VoiceButton";

// In the input section:
<div className="p-4 border-t">
  <div className="flex gap-2 items-center">
    <VoiceButton
      onTranscript={(text) => {
        setInput(text);
        // Optionally auto-send
        // sendMessage();
      }}
      confidenceThreshold={0.7}
    />
    <input
      type="text"
      value={input}
      onChange={(e) => setInput(e.target.value)}
      // ... rest of input props
    />
    <button onClick={sendMessage}>Send</button>
  </div>
</div>
```

### 4. Audio Feedback (Optional)

```typescript
// utils/audio.ts
export function playConfirmationSound(action: string) {
  const utterance = new SpeechSynthesisUtterance(action);
  utterance.rate = 1.2;
  utterance.volume = 0.8;
  window.speechSynthesis.speak(utterance);
}

// Usage after successful action:
playConfirmationSound("Task added: Buy groceries");
```

## Low Confidence Handling

When confidence < threshold:
1. Display transcript with warning indicator
2. Show "Did you mean: [transcript]?" prompt
3. Offer to retry or edit manually
4. Never auto-send low-confidence input

## Accessibility Considerations

- Provide visual feedback for deaf/hard-of-hearing users
- Keep text input as primary, voice as enhancement
- Clear status indicators for screen readers
- Error messages are descriptive and actionable

## Reference: Related APIs

| API | Use Case |
|-----|----------|
| `SpeechRecognition` | Core voice-to-text |
| `MediaDevices` | Microphone access |
| `SpeechSynthesis` | Text-to-speech feedback |
| `Permissions API` | Permission state checking |
