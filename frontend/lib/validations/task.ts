/**
 * Zod validation schemas for task forms.
 * Matches backend validation in backend/app/models.py
 */

import { z } from "zod"

// =============================================================================
// Enums
// =============================================================================

export const priorityEnum = z.enum(["HIGH", "MEDIUM", "LOW"])

export const recurrencePatternEnum = z.enum(["DAILY", "WEEKLY", "MONTHLY"])

export const tagSchema = z.object({
  name: z
    .string()
    .min(1, "Tag name is required")
    .max(30, "Tag name must be 30 characters or less")
    .trim(),
  color: z
    .string()
    .regex(/^#[0-9A-Fa-f]{6}$/, "Color must be a valid hex color (e.g., #00f5ff)"),
})

// =============================================================================
// Create Schema
// =============================================================================

export const taskCreateSchema = z.object({
  title: z
    .string()
    .min(1, "Title is required")
    .max(200, "Title must be 200 characters or less")
    .transform((val) => val.trim()),
  description: z
    .string()
    .max(1000, "Description must be 1000 characters or less")
    .optional(),
  priority: priorityEnum.optional(),
  tags: z
    .array(tagSchema)
    .max(10, "Maximum 10 tags allowed")
    .optional(),
  due_date: z
    .string()
    .regex(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})?$/, "Due date must be a valid ISO 8601 datetime")
    .optional(),
  recurrence_pattern: recurrencePatternEnum.optional(),
})

// =============================================================================
// Update Schema
// =============================================================================

export const taskUpdateSchema = z.object({
  title: z
    .string()
    .min(1, "Title is required")
    .max(200, "Title must be 200 characters or less")
    .transform((val) => val.trim())
    .optional(),
  description: z
    .string()
    .max(1000, "Description must be 1000 characters or less")
    .transform((val) => val?.trim() || undefined)
    .optional(),
  priority: priorityEnum.optional(),
  tags: z
    .array(tagSchema)
    .max(10, "Maximum 10 tags allowed")
    .optional(),
  due_date: z
    .string()
    .regex(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})?$/, "Due date must be a valid ISO 8601 datetime")
    .nullable()
    .optional(),
  recurrence_pattern: recurrencePatternEnum.nullable().optional(),
  completed: z.boolean().optional(),
})

// =============================================================================
// Types
// =============================================================================

export type TaskCreateInput = z.infer<typeof taskCreateSchema>
export type TaskUpdateInput = z.infer<typeof taskUpdateSchema>
export type Priority = z.infer<typeof priorityEnum>
export type RecurrencePattern = z.infer<typeof recurrencePatternEnum>
export type Tag = z.infer<typeof tagSchema>