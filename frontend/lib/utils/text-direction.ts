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
 * Calculate the ratio of Urdu/Arabic characters in text.
 *
 * @param text - The text to analyze
 * @returns Number between 0 and 1 (1 = all Urdu)
 */
function getUrduRatio(text: string): number {
  if (!text) return 0;

  // Remove whitespace and punctuation for cleaner counting
  const cleanText = text.replace(/[\s\p{P}]/gu, "");
  if (cleanText.length === 0) return 0;

  // Count Urdu/Arabic characters
  const urduPattern = /[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]/g;
  const urduMatches = cleanText.match(urduPattern);
  const urduCount = urduMatches ? urduMatches.length : 0;

  return urduCount / cleanText.length;
}

/**
 * Get text direction based on DOMINANT content.
 *
 * Returns "rtl" only if Urdu/Arabic is the majority language (>40%),
 * otherwise returns "ltr". This prevents mixed English-Urdu messages
 * from being fully right-aligned.
 *
 * @param text - The text to analyze
 * @returns "rtl" for Urdu-dominant text, "ltr" otherwise
 */
export function getTextDirection(text: string): "rtl" | "ltr" {
  const urduRatio = getUrduRatio(text);
  // Use 40% threshold to account for mixed content
  return urduRatio > 0.4 ? "rtl" : "ltr";
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
