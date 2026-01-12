/**
 * Tag Utilities
 *
 * Helper functions for tag management including color generation,
 * validation, and persistence.
 *
 * Per contracts/components.ts: Predefined Deep Space color palette:
 * - Cyan: #00f5ff
 * - Purple: #a855f7
 * - Green: #22c55e
 * - Yellow: #eab308
 * - Pink: #ec4899
 * - Orange: #f97316
 */

import type { Tag } from "@/types/task"

// =============================================================================
// Color Palette
// =============================================================================

/** Deep Space theme colors for tags */
export const TAG_COLORS = [
  "#00f5ff", // Cyan
  "#a855f7", // Purple
  "#22c55e", // Green
  "#eab308", // Yellow
  "#ec4899", // Pink
  "#f97316", // Orange
] as const

/** Type for valid tag colors */
export type TagColor = (typeof TAG_COLORS)[number]

// =============================================================================
// Color Generation
// =============================================================================

/**
 * Get a random color from the Deep Space color palette.
 *
 * @returns A random hex color from the predefined palette
 */
export function getRandomColor(): TagColor {
  return TAG_COLORS[Math.floor(Math.random() * TAG_COLORS.length)]
}

/**
 * Get a consistent color for a tag name.
 * Uses localStorage to persist color assignments across sessions.
 *
 * Per T030: Tag color persistence using localStorage
 *
 * @param tagName - The tag name to get a color for
 * @returns The persisted or newly assigned color for this tag
 */
export function getTagColor(tagName: string): TagColor {
  if (typeof window === "undefined") {
    return getRandomColor()
  }

  const storageKey = "tag-colors"
  const stored = localStorage.getItem(storageKey)

  if (stored) {
    try {
      const colorMap = JSON.parse(stored) as Record<string, TagColor>
      if (colorMap[tagName]) {
        return colorMap[tagName]
      }
    } catch {
      // Invalid JSON, ignore and continue
    }
  }

  // Generate new color and store it
  const color = getRandomColor()
  setTagColor(tagName, color)
  return color
}

/**
 * Set a color for a tag name in localStorage.
 *
 * @param tagName - The tag name
 * @param color - The color to assign
 */
export function setTagColor(tagName: string, color: TagColor): void {
  if (typeof window === "undefined") return

  const storageKey = "tag-colors"
  const stored = localStorage.getItem(storageKey)
  const colorMap: Record<string, TagColor> = stored ? JSON.parse(stored) : {}

  colorMap[tagName] = color
  localStorage.setItem(storageKey, JSON.stringify(colorMap))
}

/**
 * Get all stored tag color mappings.
 *
 * @returns Record mapping tag names to their assigned colors
 */
export function getAllTagColors(): Record<string, TagColor> {
  if (typeof window === "undefined") return {}

  const storageKey = "tag-colors"
  const stored = localStorage.getItem(storageKey)

  if (!stored) return {}

  try {
    return JSON.parse(stored) as Record<string, TagColor>
  } catch {
    return {}
  }
}

// =============================================================================
// Tag Validation
// =============================================================================

/**
 * Validate a tag name according to the rules:
 * - 1-30 characters
 * - No special characters: <>{}|[]^"
 *
 * @param tagName - The tag name to validate
 * @returns true if valid, false otherwise
 */
export function isValidTagName(tagName: string): boolean {
  if (tagName.length < 1 || tagName.length > 30) return false

  // Check for forbidden characters
  const forbiddenChars = /[<>{}|[\]^"]/
  return !forbiddenChars.test(tagName)
}

/**
 * Sanitize a tag name by removing invalid characters.
 *
 * @param tagName - The tag name to sanitize
 * @returns The sanitized tag name
 */
export function sanitizeTagName(tagName: string): string {
  return tagName.replace(/[<>{}|[\]^"]/g, "").trim().slice(0, 30)
}

/**
 * Check if a tag already exists in a list of tags.
 * Comparison is case-sensitive as per data-model.md.
 *
 * @param tagName - The tag name to check
 * @param existingTags - List of existing tags
 * @returns true if the tag name already exists
 */
export function tagExists(tagName: string, existingTags: Tag[]): boolean {
  return existingTags.some((tag) => tag.name === tagName)
}

// =============================================================================
// Tag Creation
// =============================================================================

/**
 * Create a new tag with a generated or persisted color.
 *
 * @param tagName - The name for the new tag
 * @returns A new Tag object
 */
export function createTag(tagName: string): Tag {
  return {
    name: tagName,
    color: getTagColor(tagName),
  }
}

/**
 * Create multiple tags from an array of names.
 *
 * @param tagNames - Array of tag names
 * @returns Array of Tag objects
 */
export function createTags(tagNames: string[]): Tag[] {
  return tagNames.map((name) => createTag(name))
}
