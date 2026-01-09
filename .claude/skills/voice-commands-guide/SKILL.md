---
name: voice-commands-guide
description: Guide implementation of voice input for chatbot using Web Speech API. Use when adding voice command functionality to the todo chatbot (Phase III+, Bonus +200 points).
version: 2.0.0
---

# Voice Commands Implementation Skill

## When to Use This Skill

Activation triggers:
- Adding voice input to chatbot
- Implementing speech recognition
- Creating microphone integration
- Phase III+ bonus feature (+200 points)

## Browser Support

| Browser | Support |
|---------|---------|
| Chrome | Full |
| Edge | Full |
| Safari | Partial |
| Firefox | None |

## Voice Input Hook

```typescript
// hooks/useVoiceInput.ts
"use client";

import { useState, useEffect, useCallback } from "react";

export function useVoiceInput() {
  const [isSupported, setIsSupported] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [recognition, setRecognition] = useState<any>(null);

  useEffect(() => {
    const SpeechRecognition = (window as any).SpeechRecognition ||
                              (window as any).webkitSpeechRecognition;

    if (SpeechRecognition) {
      setIsSupported(true);
      const recognizer = new SpeechRecognition();

      recognizer.continuous = false;
      recognizer.interimResults = true;
      recognizer.lang = "en-US";

      recognizer.onstart = () => setIsListening(true);
      recognizer.onend = () => setIsListening(false);
      recognizer.onresult = (event: any) => {
        const last = event.results.length - 1;
        setTranscript(event.results[last][0].transcript);
      };

      setRecognition(recognizer);
    }

    return () => recognition?.abort();
  }, []);

  const startListening = useCallback(() => {
    if (recognition && !isListening) {
      setTranscript("");
      recognition.start();
    }
  }, [recognition, isListening]);

  const stopListening = useCallback(() => {
    if (recognition && isListening) {
      recognition.stop();
    }
  }, [recognition, isListening]);

  return { isSupported, isListening, transcript, startListening, stopListening };
}
```

## Voice Button Component

```typescript
// components/VoiceButton.tsx
"use client";

import { useVoiceInput } from "@/hooks/useVoiceInput";

export function VoiceButton({ onTranscript }: { onTranscript: (text: string) => void }) {
  const { isSupported, isListening, transcript, startListening, stopListening } = useVoiceInput();

  // Auto-submit when listening stops and we have transcript
  useEffect(() => {
    if (!isListening && transcript) {
      onTranscript(transcript);
    }
  }, [isListening, transcript]);

  if (!isSupported) return null;

  return (
    <button
      onClick={isListening ? stopListening : startListening}
      className={`p-2 rounded-full ${isListening ? "bg-red-500 animate-pulse" : "bg-gray-200"}`}
      title={isListening ? "Stop listening" : "Start voice input"}
    >
      {isListening ? "🛑" : "🎤"}
    </button>
  );
}
```

## Best Practices

| Practice | Implementation |
|----------|----------------|
| Check support | Graceful degradation for unsupported browsers |
| Visual feedback | Show recording indicator during listening |
| Transcript preview | Display text before sending |
| Confidence threshold | Validate transcription quality |
| Permissions | Handle microphone permission denial |

## Error Handling

| Error | Handling |
|-------|----------|
| `not-allowed` | Show "Microphone access denied" message |
| `no-speech` | Timeout and restart listening |
| `network` | Show "Network error" and retry |
| `aborted` | User cancelled, clear state |

## Context7 Topics

| Topic | Query String |
|-------|--------------|
| SpeechRecognition | "SpeechRecognition webkitSpeechRecognition API" |
| Language | "SpeechRecognition lang codes ur-PK en-US" |
| Events | "onresult onend onstart SpeechRecognition" |
