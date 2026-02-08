/**
 * useVisualViewport - Hook for tracking the visual viewport on mobile devices.
 *
 * The Visual Viewport API is critical for proper mobile keyboard handling:
 * - window.innerHeight = layout viewport (stable, includes keyboard area)
 * - visualViewport.height = visual viewport (shrinks when keyboard opens)
 *
 * On iOS Safari:
 * - Without interactive-widget=resizes-content: keyboard overlays content
 * - With interactive-widget=resizes-content: viewport resizes but needs manual handling
 *
 * This hook provides:
 * - Current visual viewport dimensions
 * - Keyboard state (open/closed based on height change)
 * - Safe area insets for home indicator
 *
 * @see https://developer.mozilla.org/en-US/docs/Web/API/Visual_Viewport_API
 */

import { useState, useEffect } from "react";

export interface VisualViewportState {
  /** Current visual viewport height (excludes keyboard on mobile) */
  height: number;
  /** Current visual viewport width */
  width: number;
  /** Scale factor from pinch-zoom */
  scale: number;
  /** Whether the virtual keyboard is likely open */
  isKeyboardOpen: boolean;
  /** Safe area inset for bottom (home indicator on iPhone X+) */
  safeAreaBottom: number;
}

// Safe area inset fallback for browsers that don't support env()
const DEFAULT_SAFE_AREA_BOTTOM = 0;

// Safe area inset detection
function getSafeAreaBottom(): number {
  if (typeof window === "undefined") return DEFAULT_SAFE_AREA_BOTTOM;

  const computedStyle = getComputedStyle(document.documentElement);
  const inset = computedStyle.getPropertyValue("safe-area-inset-bottom");

  if (!inset || inset === "none") {
    return DEFAULT_SAFE_AREA_BOTTOM;
  }

  const parsed = parseInt(inset, 10);
  return isNaN(parsed) ? DEFAULT_SAFE_AREA_BOTTOM : parsed;
}

export function useVisualViewport(): VisualViewportState {
  const [viewport, setViewport] = useState<VisualViewportState>({
    height: typeof window !== "undefined" ? window.innerHeight : 0,
    width: typeof window !== "undefined" ? window.innerWidth : 0,
    scale: 1,
    isKeyboardOpen: false,
    safeAreaBottom: DEFAULT_SAFE_AREA_BOTTOM,
  });

  useEffect(() => {
    // Skip if running on server
    if (typeof window === "undefined") {
      return;
    }

    // Check if Visual Viewport API is supported
    const visualViewport = window.visualViewport;

    // Update viewport state
    const updateViewport = () => {
      const height = visualViewport?.height ?? window.innerHeight;
      const width = visualViewport?.width ?? window.innerWidth;
      const scale = visualViewport?.scale ?? 1;

      // Detect keyboard: if visual viewport is significantly smaller than window
      // Threshold of 150px is commonly used for keyboard detection
      const isKeyboardOpen = window.innerHeight - height > 150;

      setViewport({
        height,
        width,
        scale,
        isKeyboardOpen,
        safeAreaBottom: getSafeAreaBottom(),
      });
    };

    // Set initial state immediately
    updateViewport();

    if (visualViewport) {
      // Listen to visual viewport changes (keyboard open/close, rotation, zoom)
      visualViewport.addEventListener("resize", updateViewport);
      visualViewport.addEventListener("scroll", updateViewport);

      return () => {
        visualViewport.removeEventListener("resize", updateViewport);
        visualViewport.removeEventListener("scroll", updateViewport);
      };
    }

    // Fallback: listen to window resize if Visual Viewport API is not supported
    window.addEventListener("resize", updateViewport);
    return () => {
      window.removeEventListener("resize", updateViewport);
    };
  }, []);

  return viewport;
}
