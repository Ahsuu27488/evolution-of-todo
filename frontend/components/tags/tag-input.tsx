/**
 * Tag Input Component
 *
 * Allows users to add and remove colored tags for tasks.
 *
 * Per contracts/components.ts:
 * - Type tag name and press Enter to add
 * - Click × on tag chip to remove
 * - Prevents duplicate tag names
 * - Colors assigned from Deep Space palette
 * - Maximum 10 tags allowed
 *
 * "use client"
 */

import { useState, KeyboardEvent } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { X, Tag as TagIcon } from "lucide-react"
import { cn } from "@/lib/utils"
import { isValidTagName, tagExists, getTagColor } from "@/lib/utils/tag-utils"
import type { Tag } from "@/types/task"

interface TagInputProps {
  value: Tag[]
  onChange: (tags: Tag[]) => void
  placeholder?: string
  maxTags?: number
  disabled?: boolean
  id?: string
  className?: string
}

const DEFAULT_MAX_TAGS = 10

export function TagInput({
  value = [],
  onChange,
  placeholder = "Add tag... (press Enter)",
  maxTags = DEFAULT_MAX_TAGS,
  disabled = false,
  id,
  className,
}: TagInputProps) {
  const [inputValue, setInputValue] = useState("")

  const canAddMore = value.length < maxTags

  function handleKeyDown(e: KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter") {
      e.preventDefault()
      addTag()
    } else if (e.key === "Backspace" && !inputValue && value.length > 0) {
      // Remove last tag when backspacing with empty input
      removeTag(value.length - 1)
    }
  }

  function addTag() {
    const trimmed = inputValue.trim()

    if (!trimmed) return
    if (!canAddMore) return
    if (!isValidTagName(trimmed)) return
    if (tagExists(trimmed, value)) return

    // Use getTagColor for persistent colors across sessions (T030)
    const color = getTagColor(trimmed)
    const newTag: Tag = { name: trimmed, color }
    onChange([...value, newTag])
    setInputValue("")
  }

  function removeTag(index: number) {
    const newTags = value.filter((_, i) => i !== index)
    onChange(newTags)
  }

  return (
    <div
      className={cn(
        "flex flex-wrap gap-2 p-2 rounded-md border",
        "bg-background/50 border-border/50",
        "focus-within:border-primary/50 focus-within:ring-1 focus-within:ring-primary/20",
        "transition-all duration-200",
        disabled && "opacity-50 cursor-not-allowed",
        className
      )}
    >
      {/* Existing tags */}
      <AnimatePresence mode="popLayout">
        {value.map((tag, index) => (
          <motion.span
            key={tag.name}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            transition={{ duration: 0.15 }}
            className="inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full"
            style={{
              backgroundColor: `${tag.color}20`,
              color: tag.color,
              border: `1px solid ${tag.color}40`,
            }}
          >
            <TagIcon className="h-3 w-3" />
            <span>{tag.name}</span>
            {!disabled && (
              <motion.button
                type="button"
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                onClick={() => removeTag(index)}
                className="ml-0.5 hover:bg-white/10 rounded-full p-0.5 transition-colors"
              >
                <X className="h-3 w-3" />
              </motion.button>
            )}
          </motion.span>
        ))}
      </AnimatePresence>

      {/* Input field */}
      {canAddMore && (
        <input
          id={id}
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          onBlur={addTag}
          placeholder={value.length === 0 ? placeholder : ""}
          disabled={disabled}
          className="flex-1 min-w-[120px] bg-transparent border-none outline-none text-sm placeholder:text-muted-foreground"
        />
      )}

      {/* Max tags indicator */}
      {!canAddMore && (
        <span className="text-xs text-muted-foreground">
          Max {maxTags} tags
        </span>
      )}
    </div>
  )
}
