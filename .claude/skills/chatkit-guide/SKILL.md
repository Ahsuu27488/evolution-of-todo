---
name: chatkit-guide
description: Fetch OpenAI ChatKit documentation and apply chat UI best practices. Use when building chatbot interfaces or conversation UIs (Phase III).
version: 2.0.0
---

# OpenAI ChatKit UI Development Skill

## When to Use This Skill

Activation triggers:
- Building chat interfaces for AI chatbots
- Creating conversation UI components
- Implementing message display and input
- Phase III chatbot development

## Core Chat UI Pattern

```typescript
// components/ChatInterface.tsx
"use client";

import { useState, useRef, useEffect } from "react";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
}

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function sendMessage() {
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
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          conversation_id: conversationId,
          message: input,
        }),
      });

      const data = await response.json();

      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: data.response,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="flex flex-col h-screen max-w-3xl mx-auto">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div className={`max-w-[80%] rounded-lg p-3 ${
              msg.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted"
            }`}>
              {msg.content}
            </div>
          </div>
        ))}
        {isLoading && <div className="text-muted-foreground">Thinking...</div>}
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
            className="flex-1 border rounded-lg px-4 py-2"
            disabled={isLoading}
          />
          <button onClick={sendMessage} disabled={isLoading}>
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
```

## Domain Allowlist Configuration

**CRITICAL**: ChatKit requires domain allowlist for production.

1. Deploy frontend and get URL
2. Add domain to OpenAI: https://platform.openai.com/settings/organization/security/domain-allowlist
3. Get domain key
4. Set `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` environment variable

## Best Practices

| Practice | Implementation |
|----------|----------------|
| Auto-scroll | Scroll to bottom on new messages |
| Loading states | Show indicator during API call |
| Error handling | Display errors, retry mechanism |
| Message history | Persist conversations in database |
| Streaming | Consider for better UX |

## Context7 Topics

| Topic | Query String |
|-------|--------------|
| Components | "ChatKit components installation usage" |
| Streaming | "ChatKit streaming real-time messages" |
| Configuration | "domain allowlist environment setup" |
