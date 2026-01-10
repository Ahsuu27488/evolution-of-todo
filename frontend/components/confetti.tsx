/** Canvas Confetti Wrapper Component.
 *
 * This component wraps canvas-confetti for task completion celebrations.
 * Per spec.md FR-040: confetti particle effect on task completion.
 * Per research.md: Custom colors cyan (#00f5ff) and purple (#a855f7).
 *
 * Usage:
 *   <Confetti trigger={showConfetti} />
 */

'use client';

import { useEffect, useRef } from 'react';
import confetti from 'canvas-confetti';

// Use inline types since canvas-confetti types are limited
interface ConfettiOrigin {
  x: number;
  y: number;
}

export interface ConfettiProps {
  /** Trigger confetti animation when true */
  trigger?: boolean;
  /** Position to fire confetti from */
  origin?: ConfettiOrigin;
  /** Custom particle count */
  particleCount?: number;
  /** Spread of particles */
  spread?: number;
  /** Custom colors (default: cyan and purple theme) */
  colors?: string[];
  /** Disable for testing */
  disabled?: boolean;
}

/** Default confetti colors matching Deep Space theme */
const DEFAULT_COLORS = ['#00f5ff', '#a855f7', '#22c55e', '#fbbf24'];

/**
 * Confetti component that triggers animation when trigger prop changes to true.
 * Auto-stops after animation completes to save resources.
 */
export function Confetti({
  trigger,
  origin = { x: 0.5, y: 0.5 },
  particleCount = 100,
  spread = 70,
  colors = DEFAULT_COLORS,
  disabled = false,
}: ConfettiProps) {
  const previousTrigger = useRef(false);

  useEffect(() => {
    // Only trigger when value changes from false to true
    if (trigger && !previousTrigger.current && !disabled) {
      // Fire confetti burst
      confetti({
        particleCount,
        spread,
        origin,
        colors,
        disableForReducedMotion: true,
        zIndex: 9999,
      });

      // Optional: Second wave for more celebration
      setTimeout(() => {
        confetti({
          particleCount: particleCount / 2,
          angle: 60,
          spread: 55,
          origin: { x: 0, y: 0.6 },
          colors,
          disableForReducedMotion: true,
          zIndex: 9999,
        });
        confetti({
          particleCount: particleCount / 2,
          angle: 120,
          spread: 55,
          origin: { x: 1, y: 0.6 },
          colors,
          disableForReducedMotion: true,
          zIndex: 9999,
        });
      }, 200);
    }

    previousTrigger.current = trigger ?? false;
  }, [trigger, particleCount, spread, origin, colors, disabled]);

  return null; // This component renders nothing itself
}

/** Hook to trigger confetti from anywhere in the component.
 *
 * Usage:
 *   const triggerConfetti = useConfetti();
 *   triggerConfetti();
 */
export function useConfetti() {
  return (options?: Partial<ConfettiProps>) => {
    const {
      origin = { x: 0.5, y: 0.5 },
      particleCount = 100,
      spread = 70,
      colors = DEFAULT_COLORS,
    } = options || {};

    confetti({
      particleCount,
      spread,
      origin,
      colors,
      disableForReducedMotion: true,
      zIndex: 9999,
    });
  };
}

/** Task completion confetti preset - fires from center with celebration colors */
export function taskCompletionConfetti() {
  // Main burst
  confetti({
    particleCount: 80,
    spread: 80,
    origin: { x: 0.5, y: 0.5 },
    colors: DEFAULT_COLORS,
    disableForReducedMotion: true,
    zIndex: 9999,
  });

  // Side bursts
  setTimeout(() => {
    confetti({
      particleCount: 40,
      angle: 60,
      spread: 50,
      origin: { x: 0.3, y: 0.6 },
      colors: DEFAULT_COLORS,
      disableForReducedMotion: true,
      zIndex: 9999,
    });
    confetti({
      particleCount: 40,
      angle: 120,
      spread: 50,
      origin: { x: 0.7, y: 0.6 },
      colors: DEFAULT_COLORS,
      disableForReducedMotion: true,
      zIndex: 9999,
    });
  }, 150);
}
