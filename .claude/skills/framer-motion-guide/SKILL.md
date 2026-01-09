---
name: framer-motion-guide
description: Fetch Framer Motion documentation and apply production-grade animation patterns. Use when implementing layout animations, gesture handling, AnimatePresence exit animations, variants, or performance-optimized motion design. (project)
location: managed
allowed-tools:
  - mcp__context7__resolve-library-id
  - mcp__context7__query-docs
  - Read
  - Write
  - Edit
---

# Framer Motion Mastery Guide

## Theoretical Foundation

Framer Motion is a **React animation library** built on the Web Animations API with a sophisticated architecture:

1. **Motion Components**: Wrapper components (`motion.div`, `motion.svg`) that extend React elements with animation props
2. **Motion Values**: Reactive values (`MotionValue`) that track animation state outside React's render cycle
3. **Gesture Recognizers**: Built-in handlers for drag, hover, tap, pan, and pinch gestures
4. **Projection System**: Automatic layout animations using FLIP (First, Last, Invert, Play) technique
5. **AnimatePresence**: Specialized component for exit animations (unmounting with animation)

### Animation Lifecycle

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   initial    │───►│   animate    │───►│   while*     │───►│    exit      │
│  (mount)     │    │   (target)   │    │  (interaction)│   │  (unmount)   │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
       │                                        │
       ▼                                        ▼
   One-time                              Interactive states
   transition                           (whileHover, whileTap,
   (optional)                           whileDrag, whileFocus,
                                             whileInView)
```

## Core Patterns

### 1. Layout Animations (Automatic)

The `layout` prop enables automatic FLIP animations when element position changes:

```tsx
import { motion, AnimatePresence } from 'framer-motion'

function ReorderableList({ items, onReorder }) {
  return (
    <div>
      <AnimatePresence>
        {items.map((item) => (
          <motion.div
            key={item.id}
            layout
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            drag="y"
            dragConstraints={{ top: 0, bottom: 0 }}
            onDragEnd={(e, info) => {
              // Calculate new position and reorder
              const offset = Math.round(info.offset.y / 60)
              onReorder(item.id, offset)
            }}
          >
            {item.content}
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  )
}
```

### 2. AnimatePresence for Exit Animations

**CRITICAL:** Components must have a unique `key` prop for exit animations to work:

```tsx
import { motion, AnimatePresence } from 'framer-motion'

function TabPanel({ activeTab }) {
  return (
    <AnimatePresence mode="wait">
      {activeTab === 'profile' && (
        <motion.div
          key="profile"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: 20 }}
          transition={{ duration: 0.2 }}
        >
          <ProfileContent />
        </motion.div>
      )}
      {activeTab === 'settings' && (
        <motion.div
          key="settings"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          transition={{ duration: 0.2 }}
        >
          <SettingsContent />
        </motion.div>
      )}
    </AnimatePresence>
  )
}
```

### 3. Variant-Based Animations

Variants define animation states that can be propagated to children:

```tsx
const listVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1, // Animate children sequentially
      delayChildren: 0.2,
    },
  },
}

const itemVariants = {
  hidden: { opacity: 0, x: -20 },
  visible: { opacity: 1, x: 0 },
}

function AnimatedList({ items }) {
  return (
    <motion.ul
      variants={listVariants}
      initial="hidden"
      animate="visible"
    >
      {items.map((item) => (
        <motion.li key={item.id} variants={itemVariants}>
          {item.text}
        </motion.li>
      ))}
    </motion.ul>
  )
}
```

### 4. Gesture Handling

Comprehensive gesture support for interactive elements:

```tsx
function DraggableCard() {
  const [isDragging, setIsDragging] = useState(false)

  return (
    <motion.div
      drag
      dragConstraints={{ left: 0, right: 300, top: 0, bottom: 200 }}
      dragElastic={0.2}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95, cursor: 'grabbing' }}
      onDragStart={() => setIsDragging(true)}
      onDragEnd={() => setIsDragging(false)}
      onTap={() => console.log('Tapped!')}
      onPan={(event, info) => console.log('Pan:', info.point)}
      style={{ cursor: isDragging ? 'grabbing' : 'grab' }}
    >
      Drag me around!
    </motion.div>
  )
}
```

### 5. Imperative Animation with useAnimate

For complex, sequenced animations:

```tsx
import { useAnimate, stagger } from 'framer-motion'

function StaggeredAnimation() {
  const [scope, animate] = useAnimate()

  const playSequence = async () => {
    await animate(
      scope.current,
      { x: 100 },
      { duration: 0.5 }
    )
    await animate(
      '.item',
      { opacity: [0, 1], scale: [0.8, 1] },
      {
        duration: 0.4,
        delay: stagger(0.1),
      }
    )
  }

  return (
    <div ref={scope}>
      <button onClick={playSequence}>Animate</button>
      <div className="item">Item 1</div>
      <div className="item">Item 2</div>
      <div className="item">Item 3</div>
    </div>
  )
}
```

## Performance Optimization

### 1. GPU-Accelerated Properties

**ALWAYS** animate these properties for 60fps performance:

```tsx
// ✅ GPU-accelerated (transform, opacity)
<motion.div animate={{ x: 100, scale: 1.2, opacity: 0.5 }} />

// ⚠️ CPU-bound triggers layout (avoid for frequent animations)
<motion.div animate={{ width: 100, height: 100, color: 'red' }} />
```

### 2. useReducedMotion

Respect user's motion preferences:

```tsx
import { useReducedMotion } from 'framer-motion'

function AnimatedComponent() {
  const shouldReduceMotion = useReducedMotion()

  return (
    <motion.div
      animate={{ x: shouldReduceMotion ? 0 : 100 }}
      transition={shouldReduceMotion ? { duration: 0 } : undefined}
    >
      Content
    </motion.div>
  )
}
```

### 3. Layout Animation Optimization

Use `layout="position"` for position-only animations (excludes size):

```tsx
<motion.div layout="position" />
// Equivalent to layout but only animates x/y, not width/height
```

## Code Standards

### Component Structure

```tsx
// ✅ RECOMMENDED: Destructure motion imports
import { motion, AnimatePresence, useAnimate } from 'framer-motion'

// ❌ AVOID: Default imports
import Motion from 'framer-motion'
```

### Transition Defaults

Define consistent transitions:

```tsx
const DEFAULT_TRANSITION = {
  type: 'spring',
  stiffness: 300,
  damping: 30,
}

<motion.div animate={{ x: 100 }} transition={DEFAULT_TRANSITION} />
```

### Type Safety with Variants

```tsx
type Variants = {
  hidden: AnimationProps
  visible: AnimationProps
}

const variants: Variants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1 },
}
```

## Common Pitfalls

### Pitfall 1: Missing Key in AnimatePresence

**Symptom:** Exit animation doesn't play.

**Solution:** Every child in AnimatePresence MUST have a unique `key`.

### Pitfall 2: AnimatePresence Without mode="wait"

**Symptom:** Multiple components visible during tab transition.

**Solution:** Add `mode="wait"` for exit animation before enter animation.

### Pitfall 3: Dragging on Mobile

**Symptom:** Drag doesn't work on touch devices, page scrolls instead.

**Solution:** Add `dragControls` or ensure touch-action CSS is set.

### Pitfall 4: Animation in Server Components

**Symptom:** "use client" directive required error.

**Solution:** Framer Motion only works in Client Components. Mark with `'use client'`.

## When to Use Context7

For advanced scenarios:
- Complex gesture orchestration
- SVG path animation
- Scroll-linked animations (useScroll, useTransform)
- Physics-based springs tuning

Query `/grx7/framer-motion` or `/websites/motion-dev-docs` (Motion v10+ docs).

---

**Activation Trigger:** Use this skill when:
- Implementing animations in React/Next.js
- Creating gesture-driven interactions
- Building animated UI components (modals, toasts, transitions)
- Optimizing animation performance
