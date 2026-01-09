---
name: urdu-language-guide
description: Guide implementation of Urdu language support in the chatbot. Use when adding multi-language functionality for Urdu speakers (Phase III+, Bonus +100 points).
version: 2.0.0
---

# Urdu Language Support Implementation Skill

## When to Use This Skill

Activation triggers:
- Adding Urdu language support to chatbot
- Implementing RTL (right-to-left) text rendering
- Supporting bilingual (English/Urdu) users
- Phase III+ bonus feature (+100 points)

## Urdu Detection

```python
import re

URDU_PATTERN = re.compile(r'[\u0600-\u06FF\u0750-\u077F]')

def detect_language(text: str) -> str:
    """Detect if text is primarily Urdu or English."""
    urdu_chars = len(URDU_PATTERN.findall(text))
    total_chars = len(text.replace(" ", ""))

    if total_chars == 0:
        return "en"

    # If >30% Urdu characters, treat as Urdu
    return "ur" if (urdu_chars / total_chars) > 0.3 else "en"
```

## Bilingual Agent Instructions

```python
BILINGUAL_INSTRUCTIONS = """You are a helpful todo list assistant that speaks both English and Urdu.

LANGUAGE RULES:
1. If the user writes in Urdu, respond in Urdu
2. If the user writes in English, respond in English
3. Match response language to user input language

URDU RESPONSE EXAMPLES:
- Task added: "آپ کا ٹاسک شامل کر دیا گیا"
- Task list: "آپ کے ٹاسکس:"
- Task completed: "ٹاسک مکمل ہو گیا"
- Error: "معذرت، یہ ٹاسک نہیں ملا"
"""

todo_agent = Agent(
    name="TodoAssistant",
    model="gpt-4o-mini",
    instructions=BILINGUAL_INSTRUCTIONS,
    tools=[add_task, list_tasks, complete_task],
)
```

## RTL Text Rendering

```typescript
// components/Message.tsx
function isUrdu(text: string): boolean {
  return /[\u0600-\u06FF]/.test(text);
}

export function Message({ content, role }: MessageProps) {
  const isRtl = isUrdu(content);

  return (
    <div
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

## Font Configuration

```css
/* globals.css */
@import url('https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu&display=swap');

[dir="rtl"] {
  font-family: 'Noto Nastaliq Urdu', serif;
  line-height: 2; /* Urdu script needs more height */
}
```

## Common Urdu Phrases

| Urdu | Transliteration | English |
|------|-----------------|---------|
| نیا ٹاسک شامل کرو | Naya task shamil karo | Add a new task |
| میرے ٹاسک دکھاؤ | Mere task dikhao | Show my tasks |
| ٹاسک مکمل کرو | Task mukammal karo | Complete task |
| ٹاسک حذف کرو | Task hazf karo | Delete task |
| دودھ خریدنا | Doodh khareedna | Buy milk |
| میٹنگ کی یاددہانی | Meeting ki yaaddhani | Meeting reminder |

## Test Cases

1. **Pure Urdu**: "نیا ٹاسک: کتاب پڑھنا" → Creates task with Urdu title
2. **Pure English**: "Add task: read book" → Creates task with English title
3. **Mixed**: "Add کرو: groceries" → Creates task, responds appropriately
4. **RTL Display**: Urdu text aligns right
5. **Unicode**: Urdu characters preserved in database
