/**
 * TypeScript interfaces for task data.
 * Matches backend TaskPublic schema from models.py.
 */

export interface Tag {
  name: string
  color: string
}

export type Priority = 'HIGH' | 'MEDIUM' | 'LOW'
export type RecurrencePattern = 'DAILY' | 'WEEKLY' | 'MONTHLY' | null

export interface Task {
  id: number
  user_id: string
  title: string
  description: string | null
  priority: Priority
  completed: boolean
  tags: Tag[]
  due_date: string | null // ISO 8601
  recurrence_pattern: RecurrencePattern
  transcription_text: string | null // Phase III AI-ready field
  ai_summary: string | null // Phase III AI-ready field
  embedding_id: string | null // Phase III AI-ready field
  created_at: string // ISO 8601
  updated_at: string // ISO 8601
}

export interface TaskCreate {
  title: string
  description?: string
  priority?: Priority
  tags?: Tag[]
  due_date?: string
  recurrence_pattern?: RecurrencePattern
}

export interface TaskUpdate {
  title?: string
  description?: string
  priority?: Priority
  tags?: Tag[]
  due_date?: string
  recurrence_pattern?: RecurrencePattern
  completed?: boolean
}

export interface TaskList {
  tasks: Task[]
  total: number
  page: number
  per_page: number
}

export interface TaskActionResponse {
  success: boolean
  data?: Task
  error?: {
    message: string
    code?: string
  }
}
