/** Framer Motion Animation Configurations.
 *
 * This module provides reusable animation variants and utilities
 * for the Deep Space Glassmorphism UI.
 *
 * Per spec.md FR-039: micro-animations for state transitions (slide-in, glow, fade)
 * Per research.md: framer-motion for complex UI animations
 */

import { Variants } from 'framer-motion';

// =============================================================================
// Animation Timing
// =============================================================================

/** Default spring physics for smooth, natural motion */
export const spring = {
  type: 'spring',
  stiffness: 300,
  damping: 30,
};

/** Default transition config */
export const transition = {
  duration: 0.3,
  ease: [0.4, 0, 0.2, 1] as const, // Cubic bezier
};

// =============================================================================
// Variants
// =============================================================================

/** Fade in animation */
export const fadeIn: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { ...transition, duration: 0.2 },
  },
};

/** Fade in with upward slide */
export const fadeInUp: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition,
  },
};

/** Fade in with downward slide (for modals) */
export const fadeInDown: Variants = {
  hidden: { opacity: 0, y: -20 },
  visible: {
    opacity: 1,
    y: 0,
    transition,
  },
};

/** Scale in from center */
export const scaleIn: Variants = {
  hidden: { opacity: 0, scale: 0.9 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: { ...transition, duration: 0.2 },
  },
};

/** Slide in from bottom (for mobile bottom sheets) */
export const slideInBottom: Variants = {
  hidden: { y: '100%', opacity: 0 },
  visible: {
    y: 0,
    opacity: 1,
    transition: { type: 'spring', stiffness: 300, damping: 30 },
  },
};

/** Slide out to bottom */
export const slideOutBottom: Variants = {
  visible: { y: 0, opacity: 1 },
  hidden: {
    y: '100%',
    opacity: 0,
    transition: { type: 'spring', stiffness: 300, damping: 30 },
  },
};

/** Stagger children animation */
export const staggerContainer: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.1,
    },
  },
};

/** Task card variants */
export const taskCard: Variants = {
  hidden: { opacity: 0, y: 10, scale: 0.95 },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: { type: 'spring', stiffness: 400, damping: 25 },
  },
  hover: {
    scale: 1.02,
    transition: { type: 'spring', stiffness: 400, damping: 20 },
  },
};

/** Task completion glow animation */
export const taskComplete: Variants = {
  normal: {
    boxShadow: '0 0 0 rgba(0, 245, 255, 0)',
    scale: 1,
  },
  glow: {
    boxShadow: [
      '0 0 0 rgba(0, 245, 255, 0)',
      '0 0 20px rgba(0, 245, 255, 0.3)',
      '0 0 40px rgba(0, 245, 255, 0.1)',
      '0 0 0 rgba(0, 245, 255, 0)',
    ],
    scale: [1, 1.02, 1],
    transition: { duration: 0.6 },
  },
};

/** Strike through animation for completed tasks */
export const strikeThrough: Variants = {
  hidden: { width: 0 },
  visible: {
    width: '100%',
    transition: { duration: 0.3, ease: 'easeOut' },
  },
};

/** Modal backdrop blur animation */
export const backdrop: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { duration: 0.2 },
  },
};

/** Modal content slide in */
export const modalContent: Variants = {
  hidden: {
    opacity: 0,
    scale: 0.95,
    y: 20,
  },
  visible: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: {
      type: 'spring',
      stiffness: 300,
      damping: 30,
    },
  },
  exit: {
    opacity: 0,
    scale: 0.95,
    y: 20,
    transition: { duration: 0.15 },
  },
};

/** Disintegration animation for delete */
export const disintegrate: Variants = {
  visible: {
    opacity: 1,
    scale: 1,
    filter: 'blur(0px)',
  },
  hidden: {
    opacity: 0,
    scale: 0.8,
    filter: 'blur(10px)',
    transition: { duration: 0.4, ease: 'easeIn' },
  },
};

/** Floating action button pulse */
export const fabPulse: Variants = {
  idle: {
    scale: 1,
    boxShadow: '0 4px 20px rgba(0, 245, 255, 0.3)',
  },
  hover: {
    scale: 1.1,
    boxShadow: '0 6px 30px rgba(0, 245, 255, 0.5)',
    transition: { type: 'spring', stiffness: 400, damping: 15 },
  },
  tap: {
    scale: 0.95,
    transition: { type: 'spring', stiffness: 600, damping: 20 },
  },
};

/** Command Center slide down */
export const commandSlide: Variants = {
  hidden: {
    opacity: 0,
    y: -20,
    scaleY: 0.95,
  },
  visible: {
    opacity: 1,
    y: 0,
    scaleY: 1,
    transition: {
      type: 'spring',
      stiffness: 400,
      damping: 25,
    },
  },
};

/** Priority indicator glow */
export const priorityGlow = {
  high: {
    boxShadow: '0 0 20px rgba(239, 68, 68, 0.4)',
    borderColor: 'rgb(239 68 68)',
  },
  medium: {
    boxShadow: '0 0 15px rgba(168, 85, 247, 0.3)',
    borderColor: 'rgb(168 85 247)',
  },
  low: {
    boxShadow: '0 0 10px rgba(150, 150, 170, 0.2)',
    borderColor: 'rgb(150 150 170)',
  },
};

// =============================================================================
// Layout Animations
// =============================================================================

/** Auto-animate layout for list reordering */
export const layoutAnimation = {
  layout: 'position' as const,
  transition: { type: 'spring', stiffness: 350, damping: 35 },
};

// =============================================================================
// Preset Combinations
// =============================================================================

/** Modal animation preset */
export const modalAnimation = {
  backdrop,
  content: modalContent,
};

/** Task list animation preset */
export const taskListAnimation = {
  container: staggerContainer,
  item: taskCard,
};

/** Form animation preset */
export const formAnimation = {
  container: fadeIn,
  item: fadeInUp,
};
