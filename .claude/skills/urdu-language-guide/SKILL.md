---
name: "urdu-language-guide"
description: "Guide implementation of Urdu language support in the chatbot. Use when adding multi-language functionality for Urdu speakers (Phase III+, Bonus +100 points)."
version: "1.0.0"
---

# Urdu Language Support Implementation Guide

## When to Use This Skill

Activation triggers (Claude auto-detects these):
- User mentions Urdu language support or multi-language
- Implementation requires internationalization (i18n)
- User asks about RTL text, Urdu script, or Pakistani users
- Bonus feature: Multi-Language Support (+100 points) implementation begins

## How This Skill Works

Step-by-step workflow:
1. **Detect Language**: Identify Urdu input from text patterns
2. **Configure Agent**: Update agent instructions for bilingual support
3. **Handle RTL**: Ensure proper right-to-left text rendering
4. **Store Unicode**: Verify UTF-8 encoding throughout stack
5. **Test Coverage**: Verify Urdu input/output scenarios

## Output Format

Provide structured output:
- **Language Detection**: How to identify Urdu vs English
- **Agent Instructions**: Bilingual agent configuration
- **UI Adjustments**: RTL text handling
- **Database**: UTF-8 storage considerations
- **Test Cases**: Urdu-specific scenarios

## Constraints and Rules

- ALWAYS use UTF-8 encoding for all text storage
- Support mixed Urdu/English (code-switching)
- Render RTL text correctly in UI
- Technical terms may remain in English
- Match response language to user input language
- This skill applies to Phase III+ bonus feature

## Urdu Script Basics

| Aspect | Details |
|--------|---------|
| Script | Arabic-based with modifications |
| Direction | Right-to-left (RTL) |
| Unicode Range | U+0600 to U+06FF (Arabic), U+0750 to U+077F (Arabic Supplement) |
| Common Fonts | Noto Nastaliq Urdu, Jameel Noori Nastaleeq |

## Example: Urdu Support Implementation

**Input**: "Add Urdu language support to the chatbot"

**Output**:

### 1. Language Detection

```python
# utils/language.py
import re

URDU_PATTERN = re.compile(r'[\u0600-\u06FF\u0750-\u077F]')

def detect_language(text: str) -> str:
    """Detect if text is primarily Urdu or English."""
    urdu_chars = len(URDU_PATTERN.findall(text))
    total_chars = len(text.replace(" ", ""))

    if total_chars == 0:
        return "en"

    urdu_ratio = urdu_chars / total_chars

    # If >30% Urdu characters, treat as Urdu (allows code-switching)
    return "ur" if urdu_ratio > 0.3 else "en"


def is_urdu(text: str) -> bool:
    """Simple check if text contains Urdu."""
    return bool(URDU_PATTERN.search(text))
```

### 2. Bilingual Agent Configuration

```python
# agents/todo_agent.py
from openai_agents import Agent

BILINGUAL_INSTRUCTIONS = """You are a helpful todo list assistant that speaks both English and Urdu.

LANGUAGE RULES:
1. If the user writes in Urdu, respond in Urdu
2. If the user writes in English, respond in English
3. If the user mixes languages, match their dominant language
4. Technical terms (task, todo, complete) can stay in English within Urdu responses

URDU RESPONSE EXAMPLES:
- Task added: "آپ کا ٹاسک شامل کر دیا گیا: [task title]"
- Task list: "آپ کے ٹاسکس:" followed by numbered list
- Task completed: "ٹاسک مکمل ہو گیا: [task title]"
- Error: "معذرت، یہ ٹاسک نہیں ملا"

NATURAL URDU PHRASES:
- "میری ٹاسک لسٹ دکھاؤ" → Show my task list
- "نیا ٹاسک: [text]" → New task
- "ٹاسک مکمل کرو" → Complete task
- "ٹاسک حذف کرو" → Delete task

When creating tasks from Urdu input, preserve the Urdu text in the task title.
Always be friendly and helpful in both languages."""

todo_agent = Agent(
    name="TodoAssistant",
    model="gpt-4o-mini",
    instructions=BILINGUAL_INSTRUCTIONS,
    tools=[add_task, list_tasks, complete_task, delete_task, update_task],
)
```

### 3. RTL Text Rendering (Frontend)

```typescript
// components/Message.tsx
interface MessageProps {
  content: string;
  role: "user" | "assistant";
}

function isUrdu(text: string): boolean {
  const urduPattern = /[\u0600-\u06FF\u0750-\u077F]/;
  return urduPattern.test(text);
}

export function Message({ content, role }: MessageProps) {
  const isRtl = isUrdu(content);

  return (
    <div
      className={`max-w-[80%] rounded-lg p-3 ${
        role === "user" ? "bg-blue-500 text-white" : "bg-gray-100"
      }`}
      dir={isRtl ? "rtl" : "ltr"}
      style={{
        fontFamily: isRtl ? "'Noto Nastaliq Urdu', serif" : "inherit",
        textAlign: isRtl ? "right" : "left",
      }}
    >
      {content}
    </div>
  );
}
```

### 4. Font Configuration

```css
/* globals.css */
@import url('https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu&display=swap');

/* Urdu text styling */
[dir="rtl"] {
  font-family: 'Noto Nastaliq Urdu', 'Jameel Noori Nastaleeq', serif;
  line-height: 2;  /* Urdu script needs more line height */
}

/* Input field RTL support */
input[dir="rtl"] {
  text-align: right;
  direction: rtl;
}
```

### 5. Auto-Detect Input Direction

```typescript
// components/ChatInput.tsx
"use client";

import { useState } from "react";

export function ChatInput({ onSend }: { onSend: (text: string) => void }) {
  const [input, setInput] = useState("");

  const isRtl = /[\u0600-\u06FF]/.test(input);

  return (
    <input
      type="text"
      value={input}
      onChange={(e) => setInput(e.target.value)}
      dir={isRtl ? "rtl" : "ltr"}
      placeholder={isRtl ? "...پیغام لکھیں" : "Type a message..."}
      className="flex-1 border rounded-lg px-4 py-2"
    />
  );
}
```

### 6. Database UTF-8 Verification

```python
# Ensure Neon PostgreSQL uses UTF-8 (default, but verify)
# In your SQLModel models:

from sqlmodel import SQLModel, Field

class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: str
    title: str  # UTF-8 automatically supported
    description: str | None = None
    completed: bool = False

    # No special configuration needed - PostgreSQL handles UTF-8 natively
```

## Common Urdu Phrases for Testing

| Urdu | Transliteration | English |
|------|-----------------|---------|
| نیا ٹاسک شامل کرو | Naya task shamil karo | Add a new task |
| میرے ٹاسک دکھاؤ | Mere task dikhao | Show my tasks |
| ٹاسک مکمل کرو | Task mukammal karo | Complete task |
| ٹاسک حذف کرو | Task hazf karo | Delete task |
| دودھ خریدنا | Doodh khareedna | Buy milk |
| میٹنگ کی یاددہانی | Meeting ki yaaddhani | Meeting reminder |

## Code-Switching Examples

Users may mix languages naturally:
- "Add کرو task: buy groceries" → Create task "buy groceries"
- "Show کرو میرے pending tasks" → List pending tasks
- "Complete task نمبر 3" → Complete task #3

The agent should handle these gracefully.

## Voice Input with Urdu

```typescript
// Update voice recognition for Urdu
recognizer.lang = "ur-PK";  // Urdu (Pakistan)

// Or support both:
recognizer.lang = "en-US";  // Default English
// User can switch language in settings
```

## Test Cases

1. **Pure Urdu**: "نیا ٹاسک: کتاب پڑھنا" → Creates task with Urdu title
2. **Pure English**: "Add task: read book" → Creates task with English title
3. **Mixed**: "Add کرو: groceries" → Creates task, responds in English
4. **RTL Display**: Urdu text aligns right, numbers display correctly
5. **Unicode Storage**: Urdu characters preserved in database round-trip

## Reference: Unicode Resources

| Resource | Use Case |
|----------|----------|
| Unicode CLDR | Locale data |
| ICU | Text segmentation |
| Noto Fonts | Free Urdu fonts |
