/**
 * Text direction utilities for multilingual support.
 *
 * Provides Urdu/Arabic text detection and RTL/LTR direction determination.
 * Per spec.md T069, T077, T078.
 */

/**
 * Check if text contains Urdu/Arabic characters.
 *
 * Per FR-042: Unicode range U+0600-U+06FF for Urdu detection.
 * Also includes additional Urdu-specific Unicode ranges.
 *
 * @param text - The text to check
 * @returns true if the text contains Urdu/Arabic characters
 */
export function isUrduText(text: string): boolean {
  if (!text) return false;
  // Urdu/Arabic Unicode range
  const urduPattern = /[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]/;
  return urduPattern.test(text);
}

/**
 * Get text direction based on content.
 *
 * Returns "rtl" for Urdu/Arabic text, "ltr" otherwise.
 *
 * @param text - The text to analyze
 * @returns "rtl" for Urdu/Arabic text, "ltr" otherwise
 */
export function getTextDirection(text: string): "rtl" | "ltr" {
  return isUrduText(text) ? "rtl" : "ltr";
}

/**
 * Get CSS dir attribute value for a given text.
 *
 * @param text - The text to analyze
 * @returns The CSS dir value ("rtl" or "ltr")
 */
export function getCssDir(text: string): "rtl" | "ltr" | undefined {
  const direction = getTextDirection(text);
  return direction === "rtl" ? "rtl" : undefined;
}
