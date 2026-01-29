/**
 * Notification types for Chronos Todo App.
 *
 * [Task]: T018-T019
 * [From]: spec.md FR-004, contracts/api.yaml
 */

// =============================================================================
// Enums
// =============================================================================

export enum NotificationType {
  TASK_DUE = "task_due",
  TASK_OVERDUE = "task_overdue",
  TASK_ASSIGNED = "task_assigned",
  TASK_COMPLETED = "task_completed",
  TASK_REMINDER = "task_reminder",
  SYSTEM_UPDATE = "system_update",
}

export enum NotificationChannel {
  IN_APP = "in_app",
  PUSH = "push",
  EMAIL = "email",
}

export enum EmailFrequency {
  IMMEDIATE = "immediate",
  DAILY = "daily",
  WEEKLY = "weekly",
  NONE = "none",
}

// =============================================================================
// Notification Models
// =============================================================================

export interface Notification {
  id: number
  user_id: string
  type: NotificationType
  title: string
  message: string
  data: NotificationData
  related_task_id: number | null
  read_status: boolean
  created_at: string
  sent_channels: string[]
}

export interface NotificationData {
  task_id?: number
  due_at?: string
  [key: string]: unknown
}

export interface NotificationList {
  items: Notification[]
  total: number
  unread_count: number
  limit: number
  offset: number
}

export interface NotificationPreference {
  notification_type: NotificationType
  in_app_enabled: boolean
  push_enabled: boolean
  email_enabled: boolean
  frequency: EmailFrequency
  dnd_start: string | null
  dnd_end: string | null
}

export interface NotificationSettings {
  channels: {
    in_app: { enabled: boolean }
    push: { enabled: boolean; status: "granted" | "denied" | "not_requested" }
    email: { enabled: boolean; address: string | null }
  }
  types: Record<
    string,
    { in_app: boolean; push: boolean; email: string }
  >
  do_not_disturb: {
    enabled: boolean
    start: string
    end: string
  }
}

export interface PushSubscription {
  endpoint: string
  keys: {
    p256dh: string
    auth: string
  }
}

export interface PushDeviceInfo {
  user_agent?: string
  platform?: string
}
