# shadcn/ui Component Catalog for Todo App

## Quick Reference: Context7 Library IDs

| Library | Context7 ID | Description |
|---------|-------------|-------------|
| shadcn/ui | `/websites/ui_shadcn` | Main component library docs |
| Lucide Icons | `/websites/lucide_dev_guide_packages` | Icon reference |
| Radix UI | `/radix-ui/primitives` | Underlying primitives |

## Phase II Required Components

### Authentication UI

```bash
# Install all auth components at once
npx shadcn@latest add button card form input label
```

**Login Form Components:**
- `Card` - Container for login form
- `CardHeader`, `CardTitle`, `CardDescription` - Form header
- `CardContent` - Form inputs
- `CardFooter` - Submit button
- `Input` - Email and password fields
- `Label` - Form labels
- `Button` - Submit and social login buttons

### Task Management UI

```bash
# Install all task components at once
npx shadcn@latest add checkbox card button dialog alert-dialog dropdown-menu textarea sonner skeleton
```

**Task Card Components:**
- `Card` - Task item container
- `Checkbox` - Completion toggle
- `Button` - Edit/Delete actions
- `DropdownMenu` - Actions menu (edit, delete)

**Task Form Components:**
- `Dialog` - Modal for add/edit task
- `DialogTrigger`, `DialogContent`, `DialogHeader`
- `Textarea` - Task description
- `Input` - Task title

**Confirmation Components:**
- `AlertDialog` - Delete confirmation
- `AlertDialogAction`, `AlertDialogCancel`

**Feedback Components:**
- `Sonner` - Toast notifications
- `Skeleton` - Loading placeholders

## Design Tokens (CSS Variables)

```css
/* Primary colors - customize in globals.css */
--primary: 222.2 47.4% 11.2%;
--primary-foreground: 210 40% 98%;

/* Success state for completed tasks */
--success: 142 76% 36%;
--success-foreground: 0 0% 100%;

/* Muted for completed task styling */
--muted: 210 40% 96.1%;
--muted-foreground: 215.4 16.3% 46.9%;
```

## Common Patterns

### Empty State
```tsx
import { ClipboardList } from "lucide-react"
import { Button } from "@/components/ui/button"

function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <ClipboardList className="h-12 w-12 text-muted-foreground mb-4" />
      <h3 className="text-lg font-medium">No tasks yet</h3>
      <p className="text-muted-foreground mb-4">
        Get started by creating your first task
      </p>
      <Button>Add Task</Button>
    </div>
  )
}
```

### Loading Skeleton
```tsx
import { Skeleton } from "@/components/ui/skeleton"
import { Card } from "@/components/ui/card"

function TaskSkeleton() {
  return (
    <Card className="p-4">
      <div className="flex items-center space-x-4">
        <Skeleton className="h-5 w-5 rounded" />
        <div className="space-y-2 flex-1">
          <Skeleton className="h-4 w-3/4" />
          <Skeleton className="h-3 w-1/2" />
        </div>
      </div>
    </Card>
  )
}
```

### Task Card with Actions
```tsx
import { Card } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { Button } from "@/components/ui/button"
import { MoreHorizontal, Pencil, Trash2 } from "lucide-react"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

function TaskCard({ task, onToggle, onEdit, onDelete }) {
  return (
    <Card className={cn("p-4", task.completed && "opacity-60")}>
      <div className="flex items-start gap-3">
        <Checkbox
          checked={task.completed}
          onCheckedChange={() => onToggle(task.id)}
          aria-label={`Mark ${task.title} as ${task.completed ? 'incomplete' : 'complete'}`}
        />
        <div className="flex-1 min-w-0">
          <h3 className={cn(
            "font-medium",
            task.completed && "line-through text-muted-foreground"
          )}>
            {task.title}
          </h3>
          {task.description && (
            <p className="text-sm text-muted-foreground truncate">
              {task.description}
            </p>
          )}
        </div>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon" aria-label="Task actions">
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={() => onEdit(task)}>
              <Pencil className="mr-2 h-4 w-4" />
              Edit
            </DropdownMenuItem>
            <DropdownMenuItem
              onClick={() => onDelete(task.id)}
              className="text-destructive"
            >
              <Trash2 className="mr-2 h-4 w-4" />
              Delete
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </Card>
  )
}
```

## Lucide Icons Reference

| Icon | Import | Use Case |
|------|--------|----------|
| `Plus` | `lucide-react` | Add task button |
| `Check` | `lucide-react` | Completion indicator |
| `Pencil` | `lucide-react` | Edit action |
| `Trash2` | `lucide-react` | Delete action |
| `MoreHorizontal` | `lucide-react` | Actions menu |
| `ClipboardList` | `lucide-react` | Empty state |
| `LogOut` | `lucide-react` | Logout button |
| `User` | `lucide-react` | User profile |
| `Loader2` | `lucide-react` | Loading spinner |
| `AlertCircle` | `lucide-react` | Error states |
