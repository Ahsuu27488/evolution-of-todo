---
name: "chatkit-guide"
description: "Fetch OpenAI ChatKit documentation and apply chat UI best practices. Use when building chatbot interfaces or conversation UIs (Phase III)."
version: "1.0.0"
---

# OpenAI ChatKit UI Development Guide

## When to Use This Skill

Activation triggers (Claude auto-detects these):
- User mentions ChatKit, chat UI, or conversation interface
- Implementation requires chatbot frontend components
- User asks about message display, input handling, or streaming
- Phase III frontend development begins
- Need to configure domain allowlist for deployment

## How This Skill Works

Step-by-step workflow:
1. **Identify UI Need**: Detect chat interface requirement from context
2. **Fetch ChatKit Docs**: Call Context7 for ChatKit component patterns
3. **Design UI**: Plan message display, input, and state management
4. **Configure Deployment**: Set up domain allowlist and environment
5. **Integrate Backend**: Connect to FastAPI chat endpoint

## Output Format

Provide structured output:
- **Context7 Source**: ChatKit documentation source
- **Components Used**: ChatKit components implemented
- **Configuration**: Domain allowlist and environment setup
- **State Management**: How conversation state is handled
- **Backend Integration**: API client setup

## Constraints and Rules

- ALWAYS configure domain allowlist before deployment
- Use proper environment variables for domain key
- Implement proper loading and error states
- Support message streaming for better UX
- Handle connection errors gracefully
- This skill applies to Phase III only

## Domain Allowlist Configuration

**CRITICAL**: ChatKit requires domain allowlist configuration for production.

### Setup Steps:

1. **Deploy frontend** to get production URL:
   - Vercel: `https://your-app.vercel.app`
   - Custom domain: `https://yourdomain.com`

2. **Add domain to OpenAI allowlist**:
   - Navigate to: https://platform.openai.com/settings/organization/security/domain-allowlist
   - Click "Add domain"
   - Enter your frontend URL (no trailing slash)
   - Save changes

3. **Get domain key** from OpenAI after adding domain

4. **Configure environment**:
   ```bash
   NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-domain-key-here
   ```

## Example: ChatKit Integration

**Input**: "Create a chat interface for the Todo chatbot"

**Output**:

### 1. ChatKit Setup

```typescript
// app/chat/page.tsx
"use client";

import { useState, useRef, useEffect } from "react";
import { fetchWithAuth } from "@/lib/api";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<number | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: input,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetchWithAuth("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          conversation_id: conversationId,
          message: input,
        }),
      });

      const data = await response.json();

      if (!conversationId) {
        setConversationId(data.conversation_id);
      }

      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: data.response,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Failed to send message:", error);
      // Show error toast or message
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-3xl mx-auto">
      {/* Header */}
      <header className="p-4 border-b">
        <h1 className="text-xl font-semibold">Todo Assistant</h1>
        <p className="text-sm text-gray-500">
          Manage your tasks with natural language
        </p>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 mt-8">
            <p>Start a conversation!</p>
            <p className="text-sm mt-2">Try: "Show me my tasks" or "Add a task to buy groceries"</p>
          </div>
        )}
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[80%] rounded-lg p-3 ${
                message.role === "user"
                  ? "bg-blue-500 text-white"
                  : "bg-gray-100 text-gray-900"
              }`}
            >
              {message.content}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg p-3">
              <span className="animate-pulse">Thinking...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            placeholder="Type a message..."
            className="flex-1 border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            disabled={isLoading || !input.trim()}
            className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 disabled:opacity-50"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
```

### 2. Environment Configuration

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-domain-key-here  # For hosted ChatKit
```

### 3. API Client

```typescript
// lib/api.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetchWithAuth(path: string, options: RequestInit = {}) {
  const session = await getSession();

  return fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      ...options.headers,
      Authorization: `Bearer ${session?.token}`,
    },
  });
}
```

## UI Components Checklist

- [ ] Message list with user/assistant distinction
- [ ] Input field with send button
- [ ] Loading state indicator
- [ ] Error handling and display
- [ ] Auto-scroll to latest message
- [ ] Empty state with suggestions
- [ ] Responsive design for mobile

## Reference: Context7 Topics

| Topic | Use Case |
|-------|----------|
| `installation` | ChatKit setup |
| `components` | UI component usage |
| `configuration` | Domain and API config |
| `streaming` | Real-time message display |
| `styling` | Custom theme and appearance |
