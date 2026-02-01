---
name: chatkit-guide
description: Guide for OpenAI ChatKit UI components with Deep Space theme styling. Use when building chatbot interfaces, conversation UIs, or AI chat components (Phase III).
version: 3.0.0
allowed-tools:
  - mcp__context7__resolve-library-id
  - mcp__context7__query-docs
  - Read
  - Write
  - Edit
---

# OpenAI ChatKit UI Development Skill

## Context7 Research Results

**Library ID**: `/openai/chatkit-js`
**Source**: https://github.com/openai/chatkit-js
**Reputation**: High
**Code Snippets**: 410+
**Latest Version**: Latest

## When to Use This Skill

Activation triggers:
- Building chat interfaces for AI chatbots
- Creating conversation UI components
- Implementing message display and streaming
- Phase III chatbot development

## Deep Space Theme Colors

| Color | Hex | RGB | Usage |
|-------|-----|-----|-------|
| Cyan (Primary) | `#00f5ff` | `0 245 255` | Primary actions, accent, user messages |
| Purple (Secondary) | `#a855f7` | `168 85 247` | Secondary actions, assistant messages |
| Background (Dark) | `#0a0a0f` | `10 10 15` | Main background |
| Surface | `#14141a` | `20 20 26` | Cards, panels |
| Elevated | `#1a1a2e` | `26 26 46` | Raised elements |
| Border | `rgba(255,255,255,0.1)` | `255 255 255 / 0.1` | Subtle borders |
| Muted | `#1e1e2d` | `30 30 45 / 0.5` | Disabled states |

## ChatKit Installation

```bash
npm install @openai/chatkit-react
```

## Deep Space Theme Configuration

```typescript
// app/chat/config.ts
import { useChatKit } from '@openai/chatkit-react'

export const DEEP_SPACE_THEME = {
  colorScheme: 'dark' as const,
  radius: 'round' as const,
  density: 'normal' as const,
  color: {
    // Cyan neon for primary accent
    accent: {
      primary: 'rgb(0 245 255)',  // #00f5ff
      level: 2,
    },
    // Background colors
    background: 'rgb(10 10 15)',   // #0a0a0f
    surface: 'rgb(20 20 26)',      // #14141a
    elevated: 'rgb(26 26 46)',     // #1a1a2e
    // Border with transparency
    border: 'rgb(255 255 255 / 0.1)',
    // Text colors
    text: {
      primary: 'rgb(245 245 250)', // #f5f5fa
      secondary: 'rgb(150 150 170)', // #9696aa
      muted: 'rgb(100 100 120)',    // #646478
    },
  },
}
```

## Chat Interface with Deep Space Theme

```typescript
// app/components/ChatInterface.tsx
"use client";

import { useState, useRef, useEffect } from "react";
import { useChatKit, ChatKit } from '@openai/chatkit-react'
import { DEEP_SPACE_THEME } from '../chat/config'

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
}

export function ChatInterface() {
  const { control, messages, input, setInput, handleSubmit, isLoading } =
    useChatKit({
      theme: DEEP_SPACE_THEME,
      header: {
        enabled: true,
        title: "AI Assistant",
      },
      startScreen: {
        greeting: "How can I help with your tasks?",
        prompts: [
          {
            label: "Add a task",
            prompt: "I need to add a new task",
            icon: "plus",
          },
          {
            label: "Show my tasks",
            prompt: "What tasks do I have pending?",
            icon: "list",
          },
          {
            label: "Plan my week",
            prompt: "Help me plan my week",
            icon: "calendar",
          },
        ],
      },
      composer: {
        placeholder: "Type a message or use /commands...",
        submitButton: {
          icon: "send",
          position: "inside",
        },
      },
    })

  return (
    <div className="flex flex-col h-screen bg-background">
      <ChatKit control={control} />
    </div>
  )
}
```

## Glassmorphism Chat Container

```typescript
// app/components/ChatContainer.tsx
"use client";

export function ChatContainer({ children }: { children: React.ReactNode }) {
  return (
    <div className="glass border border-border rounded-2xl overflow-hidden
                    shadow-2xl shadow-cyan-500/10">
      {children}
    </div>
  )
}
```

## Message Bubbles with Deep Space Styling

```typescript
// app/components/MessageBubble.tsx
"use client";

interface MessageProps {
  role: "user" | "assistant";
  content: string;
  timestamp?: Date;
}

export function MessageBubble({ role, content, timestamp }: MessageProps) {
  const isUser = role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div
        className={`
          max-w-[80%] rounded-2xl px-4 py-3
          backdrop-blur-md border
          ${isUser
            ? "bg-cyan-500/20 border-cyan-500/30 text-cyan-50 glow-cyan"
            : "bg-purple-500/20 border-purple-500/30 text-purple-50"
          }
        `}
      >
        <p className="text-sm leading-relaxed whitespace-pre-wrap">
          {content}
        </p>
        {timestamp && (
          <span className="text-xs opacity-60 mt-2 block">
            {timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
        )}
      </div>
    </div>
  );
}
```

## Task Card in Chat

```typescript
// app/components/TaskCard.tsx
"use client";

interface Task {
  id: number;
  title: string;
  completed: boolean;
  priority: "HIGH" | "MEDIUM" | "LOW";
  due_date?: string;
}

interface TaskCardProps {
  task: Task;
  onComplete?: (id: number) => void;
  onDelete?: (id: number) => void;
}

export function TaskCard({ task, onComplete, onDelete }: TaskCardProps) {
  const priorityColors = {
    HIGH: "bg-red-500/20 border-red-500/40 text-red-300",
    MEDIUM: "bg-yellow-500/20 border-yellow-500/40 text-yellow-300",
    LOW: "bg-green-500/20 border-green-500/40 text-green-300",
  };

  return (
    <div className="glass border border-border rounded-xl p-4 mb-2
                    hover:border-cyan-500/50 transition-colors">
      <div className="flex items-start gap-3">
        {/* Checkbox */}
        <button
          onClick={() => onComplete?.(task.id)}
          className={`
            w-5 h-5 rounded border-2 flex items-center justify-center
            transition-all
            ${task.completed
              ? "bg-cyan-500 border-cyan-500"
              : "border-cyan-500/50 hover:border-cyan-500"
            }
          `}
        >
          {task.completed && (
            <svg className="w-3 h-3 text-background" fill="currentColor" viewBox="0 0 20 20">
              <path d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" />
            </svg>
          )}
        </button>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <p className={`text-sm ${task.completed ? "line-through opacity-60" : ""}`}>
            {task.title}
          </p>
          <div className="flex gap-2 mt-2">
            <span className={`text-xs px-2 py-0.5 rounded ${priorityColors[task.priority]}`}>
              {task.priority}
            </span>
            {task.due_date && (
              <span className="text-xs text-muted-foreground">
                {new Date(task.due_date).toLocaleDateString()}
              </span>
            )}
          </div>
        </div>

        {/* Actions */}
        <button
          onClick={() => onDelete?.(task.id)}
          className="p-1 hover:bg-red-500/20 rounded text-muted-foreground hover:text-red-400"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  );
}
```

## Voice Input Button

```typescript
// app/components/VoiceInputButton.tsx
"use client";

import { useState } from "react";

export function VoiceInputButton({ onTranscript }: { onTranscript: (text: string) => void }) {
  const [isRecording, setIsRecording] = useState(false);

  const toggleRecording = () => {
    setIsRecording(!isRecording);
    // Whisper API integration here
  };

  return (
    <button
      onClick={toggleRecording}
      className={`
        p-3 rounded-full transition-all
        ${isRecording
          ? "bg-red-500/20 border-2 border-red-500 animate-pulse glow-red"
          : "bg-cyan-500/20 border border-cyan-500/50 hover:bg-cyan-500/30"
        }
      `}
      title="Voice input (Whisper)"
    >
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
      </svg>
    </button>
  );
}
```

## Streaming Response Handler

```typescript
// app/chat/streaming.ts
import { useChatKit } from '@openai/chatkit-react'

export function useChatStreaming() {
  const { control, appendMessage } = useChatKit()

  const sendMessage = async (message: string, conversationId?: string) => {
    // Add user message
    appendMessage({ role: 'user', content: message })

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, conversation_id: conversationId }),
      })

      if (!response.ok) throw new Error('Chat failed')

      // Handle streaming
      const reader = response.body?.getReader()
      const decoder = new TextDecoder()
      let assistantMessage = ''

      while (true) {
        const { done, value } = await reader!.read()
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6))
            assistantMessage += data.content || ''

            // Update the assistant message incrementally
            appendMessage({
              role: 'assistant',
              content: assistantMessage,
            })
          }
        }
      }
    } catch (error) {
      console.error('Chat error:', error)
      appendMessage({
        role: 'assistant',
        content: 'Sorry, something went wrong. Please try again.',
      })
    }
  }

  return { sendMessage, isLoading: control.isLoading }
}
```

## Typing Indicator with Neon Animation

```css
/* app/chat/globals.css */
@keyframes pulse-cyan {
  0%, 100% {
    opacity: 0.4;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.1);
  }
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 12px 16px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: rgb(0 245 255);
  animation: pulse-cyan 1.4s ease-in-out infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}
```

```typescript
// app/components/TypingIndicator.tsx
export function TypingIndicator() {
  return (
    <div className="typing-indicator">
      <span />
      <span />
      <span />
    </div>
  )
}
```

## Floating Chat Widget

```typescript
// app/components/FloatingChatWidget.tsx
"use client";

import { useState } from "react";
import { ChatInterface } from "./ChatInterface";

export function FloatingChatWidget() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      {/* Floating Toggle Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 z-50
                         w-14 h-14 rounded-full
                         bg-cyan-500/20 border-2 border-cyan-500
                         backdrop-blur-md
                         hover:bg-cyan-500/30
                         shadow-lg shadow-cyan-500/20
                         transition-all hover:scale-110"
          title="Open AI Assistant"
        >
          <svg className="w-6 h-6 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 z-50
                        w-96 h-[600px]
                        glass border border-border rounded-2xl
                        shadow-2xl shadow-cyan-500/10">
          <ChatInterface />
        </div>
      )}
    </>
  );
}
```

## CSS Utilities for Deep Space Theme

```css
/* app/chat/deep-space.css */

/* Glassmorphism base */
.glass {
  background: rgba(20, 20, 26, 0.6);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

/* Neon glow effects */
.glow-cyan {
  box-shadow:
    0 0 20px rgba(0, 245, 255, 0.3),
    0 0 40px rgba(0, 245, 255, 0.1);
}

.glow-purple {
  box-shadow:
    0 0 20px rgba(168, 85, 247, 0.3),
    0 0 40px rgba(168, 85, 247, 0.1);
}

.glow-red {
  box-shadow:
    0 0 20px rgba(239, 68, 68, 0.3),
    0 0 40px rgba(239, 68, 68, 0.1);
}

/* Text glow */
.text-glow-cyan {
  text-shadow:
    0 0 10px rgba(0, 245, 255, 0.5),
    0 0 20px rgba(0, 245, 255, 0.3);
}

/* Cyan utility classes */
.bg-cyan-500\/20 {
  background-color: rgba(0, 245, 255, 0.2);
}

.border-cyan-500\/30 {
  border-color: rgba(0, 245, 255, 0.3);
}

.text-cyan-50 {
  color: rgb(245 245 250);
}
```

## Best Practices

| Practice | Implementation |
|----------|----------------|
| Auto-scroll | Scroll to bottom on new messages |
| Loading states | Show typing indicator during API call |
| Error handling | Display errors with retry option |
| Message history | Persist conversations in database |
| Streaming | Use Server-Sent Events for real-time |
| Voice input | Whisper API with 30-second limit |
| Theme consistency | Use Deep Space colors throughout |

## Domain Allowlist Configuration

**CRITICAL**: ChatKit requires domain allowlist for production.

1. Deploy frontend and get URL
2. Add domain to OpenAI: https://platform.openai.com/settings/organization/security/domain-allowlist
3. Get domain key
4. Set `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` environment variable

## Context7 Topics

| Topic | Query String |
|-------|--------------|
| Installation | "ChatKit React installation setup" |
| Theme | "ChatKit theme colors customization" |
| Streaming | "ChatKit streaming real-time messages" |
| Components | "ChatKit UI components message bubble" |
| Configuration | "domain allowlist environment setup" |
