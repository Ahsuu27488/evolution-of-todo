/**
 * useDebounce Hook
 *
 * Debounces a value with a specified delay.
 * Used primarily for search input to prevent excessive API calls.
 *
 * Per research.md: Custom debounce hook using React's setTimeout and useEffect
 * for full control over delay duration without additional dependencies.
 *
 * @template T - The type of value to debounce
 * @param value - The value to debounce
 * @param delay - The debounce delay in milliseconds (default: 300ms)
 * @returns The debounced value
 */

"use client"

import { useEffect, useState } from "react"

export function useDebounce<T>(value: T, delay = 300): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value)

  useEffect(() => {
    // Set up timer to update debounced value after delay
    const handler = setTimeout(() => {
      setDebouncedValue(value)
    }, delay)

    // Clean up timer if value changes before delay expires
    return () => {
      clearTimeout(handler)
    }
  }, [value, delay])

  return debouncedValue
}
