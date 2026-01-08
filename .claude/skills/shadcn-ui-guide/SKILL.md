---
name: "shadcn-ui-guide"
description: "Fetch shadcn/ui documentation and apply accessible component best practices. Use when building UI components, forms, or implementing design system (Phase II+)."
version: "1.0.0"
---

# shadcn/ui Component Guide Skill

## When to Use This Skill

Activation triggers (Claude auto-detects these):
- User mentions shadcn, shadcn/ui, or accessible components
- Implementation requires buttons, forms, cards, dialogs, or toasts
- User asks about UI components or design system setup
- Phase II frontend component development begins

## How This Skill Works

Step-by-step workflow:
1. **Identify Component Need**: Detect which UI component is required
2. **Fetch Docs**: Call Context7 for `/websites/ui_shadcn` with specific component topic
3. **Apply Patterns**: Use official shadcn/ui patterns with React Hook Form + Zod
4. **Validate Accessibility**: Ensure ARIA labels and keyboard navigation

## Output Format

Provide structured output:
- **Context7 Source**: `/websites/ui_shadcn`
- **Components Used**: List of shadcn components needed
- **Installation**: CLI commands to add components
- **Pattern Applied**: Form validation, toast notifications, etc.
- **Accessibility**: ARIA and keyboard considerations

## Constraints and Rules

- ALWAYS use `npx shadcn@latest add <component>` for installation
- Use React Hook Form with Zod for form validation
- Implement proper form feedback with FormMessage
- Use Sonner for toast notifications
- Apply consistent theming via CSS variables
- Ensure all interactive elements have focus states
- This skill applies to Phase II and later only

## Example

**Input**: "Create a task creation form with validation"

**Output**:
```
Context7 Source: /websites/ui_shadcn (topic: form)

Components Used:
- Form (react-hook-form wrapper)
- Input
- Textarea
- Button
- Label
- Card (for container)

Installation:
npx shadcn@latest add form input textarea button label card

Pattern Applied:
- Zod schema for title (min 1, max 200) and description (max 1000)
- FormField with FormControl, FormLabel, FormMessage
- Submit button with loading state
- Toast notification on success

Accessibility:
- Labels properly associated with inputs via htmlFor
- Error messages announced via aria-invalid
- Focus trapped in modal (if applicable)
- Submit button disabled during loading
```

## Reference: Core Components for Todo App

| Component | Use Case | Installation |
|-----------|----------|--------------|
| `button` | Actions, submit | `npx shadcn@latest add button` |
| `card` | Task container | `npx shadcn@latest add card` |
| `checkbox` | Completion toggle | `npx shadcn@latest add checkbox` |
| `dialog` | Modals, confirmations | `npx shadcn@latest add dialog` |
| `form` | Validated forms | `npx shadcn@latest add form` |
| `input` | Text input fields | `npx shadcn@latest add input` |
| `label` | Form labels | `npx shadcn@latest add label` |
| `sonner` | Toast notifications | `npx shadcn@latest add sonner` |
| `textarea` | Description fields | `npx shadcn@latest add textarea` |
| `alert-dialog` | Delete confirmation | `npx shadcn@latest add alert-dialog` |
| `skeleton` | Loading states | `npx shadcn@latest add skeleton` |
| `dropdown-menu` | Task actions menu | `npx shadcn@latest add dropdown-menu` |

## Reference: Form Validation Pattern

```typescript
// Zod schema for task
const taskSchema = z.object({
  title: z.string().min(1, "Title is required").max(200, "Title too long"),
  description: z.string().max(1000, "Description too long").optional(),
})

// React Hook Form setup
const form = useForm<z.infer<typeof taskSchema>>({
  resolver: zodResolver(taskSchema),
  defaultValues: { title: "", description: "" },
})
```

## Reference: Toast Notifications Pattern

```typescript
import { toast } from "sonner"

// Success toast
toast.success("Task created", {
  description: "Your task has been added successfully",
})

// Error toast
toast.error("Failed to create task", {
  description: "Please try again",
})
```
