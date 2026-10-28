/**
 * Tag Input Component
 *
 * Type a tag and press Enter (or comma) to add it; Backspace on an empty field removes the last.
 * Chips match the task card: neutral fill, the tag's colour as a dot. Up to 10 tags, no duplicates.
 */

"use client"

import { useId, useState, KeyboardEvent } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { X } from "lucide-react"
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
  placeholder = "Type a tag, then Enter",
  maxTags = DEFAULT_MAX_TAGS,
  disabled = false,
  id,
  className,
}: TagInputProps) {
  const [inputValue, setInputValue] = useState("")
  const [hint, setHint] = useState<string | null>(null)
  const hintId = useId()

  const canAddMore = value.length < maxTags

  function handleKeyDown(e: KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault()
      addTag()
    } else if (e.key === "Backspace" && !inputValue && value.length > 0) {
      removeTag(value.length - 1)
    }
  }

  function addTag() {
    const trimmed = inputValue.trim()
    if (!trimmed || !canAddMore) return
    if (!isValidTagName(trimmed)) {
      setHint("Keep tags under 30 characters, without < > { } [ ] | ^ or quotes")
      return
    }
    if (tagExists(trimmed, value)) {
      setHint(`"${trimmed}" is already added`)
      return
    }
    onChange([...value, { name: trimmed, color: getTagColor(trimmed) }])
    setInputValue("")
    setHint(null)
  }

  function removeTag(index: number) {
    onChange(value.filter((_, i) => i !== index))
  }

  return (
    <div className="grid gap-1.5">
      <div
        className={cn(
          "flex min-h-11 flex-wrap items-center gap-1.5 rounded-[var(--radius-md)] border border-input bg-transparent px-2 py-1.5 md:min-h-10 dark:bg-input/30",
          "transition-[border-color,box-shadow] hover:border-foreground/25 focus-within:border-ring focus-within:ring-[3px] focus-within:ring-ring/50",
          disabled && "pointer-events-none opacity-50",
          className
        )}
      >
        <AnimatePresence mode="popLayout" initial={false}>
          {value.map((tag, index) => (
            <motion.span
              key={tag.name}
              layout
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              transition={{ duration: 0.15 }}
              className="inline-flex h-7 items-center gap-1.5 rounded-full bg-muted pr-0.5 pl-2.5 text-xs font-medium"
            >
              <span className="size-1.5 rounded-full" style={{ backgroundColor: tag.color }} aria-hidden />
              {tag.name}
              {!disabled && (
                <button
                  type="button"
                  onClick={() => removeTag(index)}
                  aria-label={`Remove tag ${tag.name}`}
                  className="relative grid size-6 place-items-center rounded-full text-muted-foreground outline-none transition-colors after:absolute after:-inset-2 hover:bg-accent hover:text-foreground focus-visible:ring-2 focus-visible:ring-ring/60"
                >
                  <X className="size-3" aria-hidden />
                </button>
              )}
            </motion.span>
          ))}
        </AnimatePresence>

        {canAddMore ? (
          <input
            id={id}
            type="text"
            value={inputValue}
            onChange={(e) => {
              setInputValue(e.target.value)
              setHint(null)
            }}
            onKeyDown={handleKeyDown}
            onBlur={addTag}
            placeholder={value.length === 0 ? placeholder : "Add another"}
            disabled={disabled}
            aria-describedby={hintId}
            enterKeyHint="done"
            className="h-7 min-w-28 flex-1 bg-transparent px-1.5 text-sm outline-none placeholder:text-muted-foreground"
          />
        ) : (
          <span className="px-1.5 text-xs text-muted-foreground">That&apos;s the limit of {maxTags} tags</span>
        )}
      </div>
      <p id={hintId} aria-live="polite" className={cn("text-[13px]", hint ? "text-warning" : "sr-only")}>
        {hint ?? `${value.length} of ${maxTags} tags`}
      </p>
    </div>
  )
}
