---
name: shadcn-ui-guide
description: Fetch shadcn/ui documentation and apply accessible component best practices. Use when building UI components, forms, or implementing design system (Phase II+).
version: 2.0.0
---

# shadcn/ui Component Mastery Skill

## Theoretical Foundation

shadcn/ui is NOT a component library—it's a **collection of re-usable components**:
- **Copy-Paste**: Components are copied into your project (you own the code)
- **Radix UI Primitives**: Headless, accessible foundation
- **Tailwind CSS**: Utility-first styling with CSS variables
- **Radix Themes**: Consistent design tokens
- **TypeScript**: Full type safety

### Component Architecture

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                        SHADCN/UI COMPONENT LAYER                             │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  Your Application                                                             │
│       │                                                                      │
│       ▼                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐     │
│  │                    Component (Your Code)                             │     │
│  │  ├── button.tsx    ├── dialog.tsx    ├── form.tsx                   │     │
│  │  └── ... (copied from shadcn/ui, fully customizable)               │     │
│  └─────────────────────────────────────────────────────────────────────┘     │
│       │                                                                      │
│       ▼                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐     │
│  │                    Radix UI Primitives                              │     │
│  │  ├── @radix-ui/react-dialog (headless, accessible)                │     │
│  │  ├── @radix-ui/react-dropdown-menu (keyboard nav, ARIA)           │     │
│  │  └── ... (foundation primitives)                                   │     │
│  └─────────────────────────────────────────────────────────────────────┘     │
│       │                                                                      │
│       ▼                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐     │
│  │                    Tailwind CSS + CSS Variables                     │     │
│  │  ├── utility classes (flex, p-4, rounded-md)                       │     │
│  │  ├── CSS variables (--primary, --radius, --muted)                  │     │
│  │  └── responsive variants (sm:, md:, lg:)                           │     │
│  └─────────────────────────────────────────────────────────────────────┘     │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘
```

### Key Concepts

1. **Radix Primitives**: Headless components with full accessibility
2. **CVA (class-variance-authority)**: Type-safe variant props
3. **React Hook Form + Zod**: Form validation with `@hookform/resolvers`
4. **Sonner**: Toast notifications with rich colors
5. **Lucide React**: Icon library

## When to Use This Skill

Activation triggers:
- Adding UI components (buttons, forms, dialogs, cards)
- Implementing form validation
- Creating toast notifications
- Building accessible modals and dropdowns
- Setting up design system with CSS variables

## Installation & Setup

### Initial Setup

```bash
# Initialize shadcn/ui (interactive)
npx shadcn@latest init

# Or with defaults
npx shadcn@latest init -y -d
```

### Add Components

```bash
# Add a single component
npx shadcn@latest add button

# Add multiple components
npx shadcn@latest add button card input label form dialog sonner

# Add all at once
npx shadcn@latest add --all
```

## Component Patterns

### 1. Button with Variants

```typescript
// components/ui/button.tsx
import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md font-medium transition-colors",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
        outline: "border border-input bg-background hover:bg-accent",
        secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        link: "text-primary underline-offset-4 hover:underline",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3",
        lg: "h-11 rounded-md px-8",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button"
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

export { Button, buttonVariants }
```

### 2. Form with Zod Validation

```typescript
// components/task-form.tsx
"use client"

import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { toast } from "sonner"

const taskSchema = z.object({
  title: z.string().min(1, "Title is required").max(200),
  description: z.string().max(1000).optional(),
  priority: z.enum(["HIGH", "MEDIUM", "LOW"]).default("MEDIUM"),
  completed: z.boolean().default(false),
})

type TaskFormValues = z.infer<typeof taskSchema>

interface TaskFormProps {
  onSubmit: (data: TaskFormValues) => Promise<void>
  defaultValues?: TaskFormValues
}

export function TaskForm({ onSubmit, defaultValues }: TaskFormProps) {
  const form = useForm<TaskFormValues>({
    resolver: zodResolver(taskSchema),
    defaultValues: defaultValues || {
      title: "",
      description: "",
      priority: "MEDIUM",
      completed: false,
    },
  })

  async function handleSubmit(data: TaskFormValues) {
    try {
      await onSubmit(data)
      toast.success("Task saved successfully")
      form.reset()
    } catch (error) {
      toast.error("Failed to save task")
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Create Task</CardTitle>
        <CardDescription>Add a new task to your list</CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="title"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Title</FormLabel>
                  <FormControl>
                    <Input placeholder="Enter task title" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="description"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Description</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Optional description"
                      className="resize-none"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="priority"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Priority</FormLabel>
                  <Select onValueChange={field.onChange} defaultValue={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select priority" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value="HIGH">High</SelectItem>
                      <SelectItem value="MEDIUM">Medium</SelectItem>
                      <SelectItem value="LOW">Low</SelectItem>
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="completed"
              render={({ field }) => (
                <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                  <FormControl>
                    <Checkbox
                      checked={field.value}
                      onCheckedChange={field.onChange}
                    />
                  </FormControl>
                  <div className="space-y-1 leading-none">
                    <FormLabel>Mark as completed</FormLabel>
                  </div>
                </FormItem>
              )}
            />

            <Button type="submit" className="w-full">
              Save Task
            </Button>
          </form>
        </Form>
      </CardContent>
    </Card>
  )
}
```

### 3. Dialog with Confirmation

```typescript
// components/delete-dialog.tsx
"use client"

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"
import { Button } from "@/components/ui/button"
import { Trash2 } from "lucide-react"

interface DeleteDialogProps {
  onConfirm: () => Promise<void>
  title?: string
  description?: string
}

export function DeleteDialog({
  onConfirm,
  title = "Delete this item?",
  description = "This action cannot be undone.",
}: DeleteDialogProps) {
  return (
    <AlertDialog>
      <AlertDialogTrigger asChild>
        <Button variant="ghost" size="icon">
          <Trash2 className="h-4 w-4" />
        </Button>
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>{title}</AlertDialogTitle>
          <AlertDialogDescription>{description}</AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Cancel</AlertDialogCancel>
          <AlertDialogAction onClick={onConfirm}>
            Delete
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}
```

### 4. Toast Notifications

```typescript
// app/providers.tsx
import { Toaster } from "@/components/ui/sonner"

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <>
      {children}
      <Toaster
        position="bottom-right"
        richColors
        closeButton
        expand={false}
      />
    </>
  )
}

// Usage in components
import { toast } from "sonner"

toast.success("Task created", {
  description: "Your task has been added to the list",
})

toast.error("Failed to create task", {
  description: error.message,
})

toast.promise(createTask(data), {
  loading: "Creating task...",
  success: "Task created successfully",
  error: "Failed to create task",
})
```

## Essential Components List

| Component | Installation Command | Use Case |
|-----------|---------------------|----------|
| Button | `npx shadcn@latest add button` | Actions, submits |
| Card | `npx shadcn@latest add card` | Content containers |
| Input | `npx shadcn@latest add input` | Text input fields |
| Textarea | `npx shadcn@latest add textarea` | Multi-line input |
| Form | `npx shadcn@latest add form` | Form wrapper for RHF |
| Label | `npx shadcn@latest add label` | Form labels |
| Dialog | `npx shadcn@latest add dialog` | Modals, popovers |
| AlertDialog | `npx shadcn@latest add alert-dialog` | Confirmations |
| Select | `npx shadcn@latest add select` | Dropdowns |
| Checkbox | `npx shadcn@latest add checkbox` | Boolean inputs |
| Sonner | `npx shadcn@latest add sonner` | Toast notifications |
| Skeleton | `npx shadcn@latest add skeleton` | Loading states |
| Dropdown Menu | `npx shadcn@latest add dropdown-menu` | Action menus |

## CSS Variables for Theming

```css
/* app/globals.css */
@layer base {
  :root {
    /* Base colors */
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;

    /* Card */
    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;

    /* Primary */
    --primary: 222.2 47.4% 11.2%;
    --primary-foreground: 210 40% 98%;

    /* Secondary */
    --secondary: 210 40% 96.1%;
    --secondary-foreground: 222.2 47.4% 11.2%;

    /* Muted */
    --muted: 210 40% 96.1%;
    --muted-foreground: 215.4 16.3% 46.9%;

    /* Accent */
    --accent: 210 40% 96.1%;
    --accent-foreground: 222.2 47.4% 11.2%;

    /* Destructive */
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 210 40% 98%;

    /* Borders & Inputs */
    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 222.2 84% 4.9%;

    /* Radius */
    --radius: 0.5rem;
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    /* ... other dark mode colors */
  }
}
```

## Code Standards

| Rule | Description |
|------|-------------|
| **Client Components** | All UI components need `"use client"` |
| **Compound Components** | Use sub-components (Card.Header, Card.Content) |
| **Form Validation** | Always use Zod schemas with react-hook-form |
| **Accessibility** | Ensure all interactive elements have focus states |
| **Responsive** | Use Tailwind responsive prefixes (md:, lg:) |

## Common Pitfalls

### 1. Missing `"use client"` Directive
**Symptom**: "use client" directive required error
**Fix**: Add `"use client"` at top of interactive components

### 2. Not Using `cn()` Utility
**Symptom**: Inconsistent class merging, Tailwind conflicts
**Fix**: Always use `cn()` for conditional classes

### 3. Forgetting Form Validation
**Symptom**: No validation feedback on forms
**Fix**: Always use Zod + react-hook-form with FormField

## References

- **Documentation**: https://ui.shadcn.com
- **Components**: https://ui.shadcn.com/docs/components
- **Themes**: https://ui.shadcn.com/docs/theming
