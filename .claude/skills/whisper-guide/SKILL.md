---
name: whisper-guide
description: Guide for implementing OpenAI Whisper API speech-to-text with FastAPI backend and Next.js 15.2 frontend. Use when implementing audio transcription endpoints, voice input features, multi-language speech recognition (including Urdu), or real-time audio processing.
version: 2.0.0
---

# OpenAI Whisper API Guide

Server-side speech-to-text using OpenAI's hosted Whisper API with FastAPI + Next.js 15.2 stack.

## Quick Start

**Python (FastAPI) with OpenAI API:**
```python
from openai import AsyncOpenAI
from pathlib import Path

client = AsyncOpenAI()

audio_file = Path("speech.mp3")
transcription = await client.audio.transcriptions.create(
    model="whisper-1",
    file=audio_file,
)
print(transcription.text)
```

**Next.js 15.2 (Server Action):**
```tsx
'use server'
async function transcribeAudio(formData: FormData) {
  const file = formData.get('audio') as File
  // Send to FastAPI backend
}
```

## API Overview

### POST /audio/transcriptions

Transcribes audio into text using the Whisper model. Automatically detects language and supports various audio formats.

**Endpoint**: `POST /audio/transcriptions`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | file | ✅ | Audio file to transcribe |
| `model` | string | ✅ | Must be `"whisper-1"` |
| `language` | string | ❌ | ISO-639-1 code (e.g., `"en"`, `"ur"` for Urdu). Auto-detect if omitted |
| `prompt` | string | ❌ | Optional text to guide the model |
| `response_format` | string | ❌ | `"json"`, `"text"`, `"srt"`, `"vtt"` |
| `temperature` | number | ❌ | Sampling temperature (0-1, default: 0) |

**Response:**
```json
{
  "text": "The quick brown fox jumped over the lazy dogs."
}
```

## Constraints

| Constraint | Value |
|------------|-------|
| **Max file size** | 25 MB |
| **Supported formats** | mp3, mp4, mpeg, mpga, m4a, wav, webm |
| **Languages** | 99+ languages (auto-detected) |
| **Cost** | $0.006 per minute (~$0.003 per 30-second command) |

## FastAPI Backend

### Transcription Service (OpenAI API)

```python
# app/services/whisper_service.py
from openai import AsyncOpenAI
import tempfile
import os
from pathlib import Path

class WhisperService:
    def __init__(self, api_key: str | None = None):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = "whisper-1"

    async def transcribe(
        self,
        audio_path: str,
        language: str | None = None,  # Auto-detect if None
        prompt: str | None = None,
        temperature: float = 0.0,
    ) -> dict:
        """Transcribe audio file using OpenAI Whisper API."""
        with open(audio_path, "rb") as audio_file:
            transcription = await self.client.audio.transcriptions.create(
                model=self.model,
                file=audio_file,
                language=language,
                prompt=prompt,
                temperature=temperature,
            )

        return {
            "text": transcription.text,
        }

# Singleton instance
_whisper_service = None

def get_whisper_service() -> WhisperService:
    global _whisper_service
    if _whisper_service is None:
        _whisper_service = WhisperService()
    return _whisper_service
```

### Transcription Endpoint

```python
# app/routes/chat.py (or app/api/endpoints/transcription.py)
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.services.whisper_service import get_whisper_service
from app.simple_auth import get_current_user_id

router = APIRouter()

@router.post("/api/chat/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    language: str | None = None,  # Auto-detect if None
    user_id: str = Depends(get_current_user_id),
):
    """
    Transcribe audio file using OpenAI Whisper API.

    - **file**: Audio file (max 25 MB)
    - **language**: Optional ISO-639-1 code (auto-detect if omitted)
    """
    # Validate file type
    allowed_types = ["audio/mpeg", "audio/mp4", "audio/mp3",
                     "audio/mpga", "audio/mp4a", "audio/wav", "audio/webm"]

    if file.content_type not in allowed_types:
        raise HTTPException(
            415,
            f"Unsupported audio type. Supported: {', '.join(allowed_types)}"
        )

    # Validate file size (25 MB limit from OpenAI)
    MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            413,
            f"File too large. Maximum size is 25 MB."
        )

    # Save to temp file for API upload
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        service = get_whisper_service()
        result = await service.transcribe(
            tmp_path,
            language=language,  # None = auto-detect
        )
        return {"text": result["text"]}
    except Exception as e:
        raise HTTPException(500, f"Transcription failed: {str(e)}")
    finally:
        os.unlink(tmp_path)
```

### With Language Detection (Urdu Support)

```python
# Auto-detect language (supports Urdu)
result = await service.transcribe(
    tmp_path,
    language=None,  # Auto-detect (works for Urdu too)
)

# Explicit Urdu (ISO 639-1 code)
result = await service.transcribe(
    tmp_path,
    language="ur",  # Urdu
)

# Explicit English
result = await service.transcribe(
    tmp_path,
    language="en",  # English
)
```

### With Prompt for Context

```python
# Optional prompt to improve accuracy for specific vocabulary
result = await service.transcribe(
    tmp_path,
    prompt="This is a todo list management app with tasks, priorities, due dates.",
)
```

## Next.js 15.2 Frontend

### Audio Recording Component

```tsx
// app/components/VoiceRecorder.tsx
'use client'

import { useState, useRef } from 'react'

export function VoiceRecorder() {
  const [isRecording, setIsRecording] = useState(false)
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<BlobPart[]>([])

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const recorder = new MediaRecorder(stream)
      mediaRecorderRef.current = recorder
      chunksRef.current = []

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data)
        }
      }

      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' })
        setAudioBlob(blob)
        setIsRecording(false)
      }

      recorder.start()
      setIsRecording(true)
    } catch (err) {
      console.error('Microphone access denied:', err)
      // Show error to user
    }
  }

  const stopRecording = () => {
    mediaRecorderRef.current?.stop()
    setIsRecording(false)
  }

  return (
    <div>
      <button
        onClick={isRecording ? stopRecording : startRecording}
        className={isRecording ? 'recording animate-pulse' : ''}
        disabled={!audioBlob && !isRecording}
      >
        {isRecording ? '⏹ Stop' : '🎤 Record'}
      </button>
      {audioBlob && <TranscribeForm audioBlob={audioBlob} />}
    </div>
  )
}
```

### Transcribe Form Component

```tsx
// app/components/TranscribeForm.tsx
'use client'

import { useState } from 'react'
import { transcribeAudio } from '@/app/actions/transcribe'

export function TranscribeForm({ audioBlob }: { audioBlob: Blob }) {
  const [transcription, setTranscription] = useState('')
  const [isUploading, setIsUploading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsUploading(true)

    const formData = new FormData()
    formData.append('file', audioBlob, 'audio.webm')

    try {
      const result = await transcribeAudio(formData)
      setTranscription(result.text)
    } catch (err) {
      console.error('Transcription failed:', err)
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <button
        type="submit"
        disabled={isUploading}
        className="px-4 py-2 bg-primary rounded-lg disabled:opacity-50"
      >
        {isUploading ? 'Transcribing...' : 'Transcribe Voice'}
      </button>
      {transcription && (
        <p className="p-3 bg-muted rounded-lg">
          "{transcription}"
        </p>
      )}
    </form>
  )
}
```

### Server Action

```tsx
// app/actions/transcribe.ts
'use server'

import { API_URL } from '@/lib/config'

export async function transcribeAudio(formData: FormData) {
  const response = await fetch(`${API_URL}/api/chat/transcribe`, {
    method: 'POST',
    body: formData,
    headers: {
      // No Content-Type with FormData - browser sets it with boundary
      'Authorization': `Bearer ${await getToken()}`,
    },
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Transcription failed')
  }

  return response.json() // { text: "..." }
}
```

## Cost Calculation

### Pricing (as of 2025)

| Model | Price |
|-------|-------|
| **whisper-1** | $0.006 per minute |

### Cost Per Command

```python
# 30-second command
cost_per_30s = (30 / 60) * 0.006  # = $0.003

# 1-minute recording
cost_per_1min = 0.006

# Example: 100 voice commands per month
monthly_cost = 100 * cost_per_30s  # = $0.30
```

## Language Support

### Auto-Detection (Recommended)

```python
# Detects language automatically (supports Urdu, English, etc.)
result = await service.transcribe(tmp_path, language=None)
```

### Explicit Languages

```python
# Urdu (ISO 639-1: ur)
result = await service.transcribe(tmp_path, language="ur")

# English (ISO 639-1: en)
result = await service.transcribe(tmp_path, language="en")

# Roman Urdu (transcribe as English text)
result = await service.transcribe(tmp_path, language="en")
```

**Supported languages**: 99+ including Urdu (ur), Hindi (hi), Arabic (ar), Chinese (zh), Spanish (es), French (fr), German (de), Japanese (ja), Korean (ko), and more.

## Error Handling

```python
# app/services/whisper_service.py
async def transcribe_with_fallback(self, audio_path: str) -> dict:
    """Transcribe with graceful error handling."""
    try:
        return await self.transcribe(audio_path)
    except Exception as e:
        # Log error for monitoring
        logger.error(f"Whisper API error: {e}")

        # Return error that AI agent can explain
        return {
            "error": "transcription_failed",
            "message": "Could not transcribe audio. Please try again or use text input.",
            "text": None,
        }
```

## Best Practices

### 1. Limit Recording Duration

```tsx
// Stop recording after 30 seconds for cost containment
const MAX_RECORDING_SECONDS = 30

useEffect(() => {
  let timeout: NodeJS.Timeout
  if (isRecording) {
    timeout = setTimeout(() => {
      stopRecording()
    }, MAX_RECORDING_SECONDS * 1000)
  }
  return () => clearTimeout(timeout)
}, [isRecording])
```

### 2. Show Upload Progress

```tsx
const [uploadProgress, setUploadProgress] = useState(0)

const handleSubmit = async () => {
  const xhr = new XMLHttpRequest()
  xhr.upload.onprogress = (e) => {
    if (e.lengthComputable) {
      setUploadProgress((e.loaded / e.total) * 100)
    }
  }
  // ... send request
}
```

### 3. Handle Non-ASCII Text (Urdu, etc.)

```python
# OpenAI returns UTF-8 text - store correctly
return {
    "text": result["text"],  # May contain Urdu characters
    "language": detected_language,
}

# Frontend: Display with proper RTL support
<p dir="auto" className="whisper-text">{transcription}</p>
```

## Context7 Queries

For latest patterns and updates:

```bash
# Query OpenAI Python docs for Whisper API
context7 query /openai/openai-python "audio transcriptions whisper API file upload"

# Query OpenAI Cookbook for examples
context7 query /openai/openai-cookbook "whisper API transcription cost pricing"
```

## References

- **OpenAI API Docs**: https://platform.openai.com/docs/guides/speech-to-text
- **OpenAI Python SDK**: https://github.com/openai/openai-python
- **Audio API Specs**: Supports mp3, mp4, mpeg, mpga, m4a, wav, webm (max 25 MB)
