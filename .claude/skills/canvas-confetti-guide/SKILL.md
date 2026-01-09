---
name: canvas-confetti-guide
description: Fetch canvas-confetti documentation and apply celebration effects. Use when implementing confetti animations for achievements, completions, or celebratory moments in React/Next.js apps. (project)
location: managed
allowed-tools:
  - mcp__context7__resolve-library-id
  - mcp__context7__query-docs
  - Read
  - Write
  - Edit
---

# canvas-confetti Mastery Guide

## Theoretical Foundation

canvas-confetti is a **lightweight JavaScript confetti library** that performs physics-based particle animation using HTML5 Canvas. It's primarily a single function API with extensive configuration options.

### Core Concepts

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CONFETTI PHYSICS                               │
├─────────────────────────────────────────────────────────────────────────────┤
│  • Particles: Individual confetti pieces with color, size, shape            │
│  • Velocity: Initial spread speed (x, y vectors)                            │
│  • Gravity: Pulls particles downward                                       │
│  • Drag: Air resistance slowing particles                                  │
│  • Decay: How quickly velocity decreases                                   │
│  • Tilt: 3D rotation effect for depth                                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Installation

```bash
npm install canvas-confetti
# or
yarn add canvas-confetti
# or
pnpm add canvas-confetti
```

## Core Patterns

### 1. Basic Usage

The simplest confetti burst:

```typescript
import confetti from 'canvas-confetti'

function celebrate() {
  confetti({
    particleCount: 100,
    spread: 70,
    origin: { y: 0.6 }, // Start from 60% down the screen
  })
}

// In a component
<button onClick={celebrate}>Celebrate!</button>
```

### 2. Side Cannon Effect

Confetti bursts from the sides inward:

```typescript
function sideCannon() {
  const count = 200
  const defaults = {
    origin: { y: 0.7 },
  }

  function fire(particleRatio: number, opts: confetti.Options) {
    confetti({
      ...defaults,
      ...opts,
      particleCount: Math.floor(count * particleRatio),
    })
  }

  fire(0.25, {
    spread: 26,
    startVelocity: 55,
    origin: { x: 0 }, // Left side
  })

  fire(0.2, {
    spread: 60,
    origin: { x: 0 }, // Left side
  })

  fire(0.35, {
    spread: 100,
    decay: 0.91,
    scalar: 0.8,
    origin: { x: 1 }, // Right side
  })

  fire(0.1, {
    spread: 120,
    startVelocity: 25,
    decay: 0.92,
    scalar: 1.2,
    origin: { x: 1 }, // Right side
  })

  fire(0.1, {
    spread: 120,
    startVelocity: 45,
    origin: { x: 1 }, // Right side
  })
}
```

### 3. Continuous Confetti (Realistic Falling)

```typescript
let animationId: number | null = null

function continuousConfetti() {
  const duration = 3000
  const animationEnd = Date.now() + duration
  const defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 0 }

  const randomInRange = (min: number, max: number) =>
    Math.random() * (max - min) + min

  const interval = setInterval(function () {
    const timeLeft = animationEnd - Date.now()

    if (timeLeft <= 0) {
      clearInterval(interval)
      if (animationId) cancelAnimationFrame(animationId)
      return
    }

    const particleCount = 50 * (timeLeft / duration)

    // Burst from random positions
    confetti({
      ...defaults,
      particleCount,
      origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 },
    })
    confetti({
      ...defaults,
      particleCount,
      origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 },
    })
  }, 250)
}
```

### 4. Fireworks Effect

```typescript
function fireworksEffect() {
  const duration = 3000
  const end = Date.now() + duration

  ;(function frame() {
    confetti({
      particleCount: 5,
      angle: 60,
      spread: 55,
      origin: { x: 0 },
      colors: ['#bb0000', '#ffffff'],
    })
    confetti({
      particleCount: 5,
      angle: 120,
      spread: 55,
      origin: { x: 1 },
      colors: ['#bb0000', '#ffffff'],
    })

    if (Date.now() < end) {
      requestAnimationFrame(frame)
    }
  }())
}
```

### 5. React Hook Wrapper

```typescript
'use client'

import { useCallback, useEffect, useRef } from 'react'
import confetti from 'canvas-confetti'

export function useConfetti() {
  const confettiRef = useRef<ConfettiInstance | null>(null)

  // Fire a basic confetti burst
  const fire = useCallback((options?: confetti.Options) => {
    confetti(options)
  }, [])

  // Fire from a specific element's position
  const fireAt = useCallback((element: HTMLElement, options?: confetti.Options) => {
    const rect = element.getBoundingClientRect()
    const x = (rect.left + rect.width / 2) / window.innerWidth
    const y = (rect.top + rect.height / 2) / window.innerHeight

    confetti({
      ...options,
      origin: { x, y },
    })
  }, [])

  // Stop all confetti
  const stop = useCallback(() => {
    confetti.reset()
  }, [])

  return { fire, fireAt, stop }
}

// Usage
function CompleteButton({ onComplete }) {
  const { fire } = useConfetti()

  const handleClick = () => {
    fire({
      particleCount: 150,
      spread: 100,
      colors: ['#26ccff', '#a25afd', '#ff5e7e', '#88ff5a'],
    })
    onComplete()
  }

  return <button onClick={handleClick}>Complete Task</button>
}
```

## Configuration Options

### Common Options

```typescript
confetti({
  // Count of particles
  particleCount: 100,

  // Spread angle in degrees (0-360)
  spread: 70,

  // Starting velocity
  startVelocity: 30,

  // Gravity (default is 1)
  gravity: 1,

  // How flat the confetti will fall (0 = flat, 1 = vertical)
  flat: 0,

  // Tilt for 3D effect (-1 to 1)
  tilt: 0,

  // Origin position (0-1)
  origin: { x: 0.5, y: 0.5 },

  // Colors (hex strings)
  colors: ['#ff0000', '#00ff00', '#0000ff'],

  // Shapes: 'square' or 'circle'
  shapes: ['square', 'circle'],

  // Scalar for particle size
  scalar: 1,

  // Velocity decay (0-1, lower = longer animation)
  decay: 0.9,

  // Z-index for canvas
  zIndex: 100,

  // Disable for reduced motion preference
  disableForReducedMotion: true,

  // Use worker for better performance
  useWorker: true,
})
```

## Code Standards

### Cleanup

Always clean up confetti in useEffect:

```typescript
useEffect(() => {
  return () => {
    confetti.reset()
  }
}, [])
```

### Reduced Motion

Respect user preferences:

```typescript
function accessibleConfetti() {
  const prefersReducedMotion = window.matchMedia(
    '(prefers-reduced-motion: reduce)'
  ).matches

  if (prefersReducedMotion) {
    return // Skip confetti
  }

  confetti({ disableForReducedMotion: true })
}
```

## Common Use Cases

### Task Completion

```typescript
function onTaskComplete() {
  confetti({
    particleCount: 100,
    spread: 70,
    origin: { y: 0.6 },
    colors: ['#10b981', '#34d399'], // Green tones for success
  })
}
```

### Achievement Unlock

```typescript
function onAchievement() {
  const end = Date.now() + 1000

  // Gold colors
  const colors = ['#ffd700', '#ffb347', '#ffec8b']

  const interval = setInterval(() => {
    confetti({
      particleCount: 50,
      spread: 100,
      colors,
      origin: { x: Math.random(), y: Math.random() * 0.5 },
    })

    if (Date.now() > end) clearInterval(interval)
  }, 100)
}
```

### Victory/Win Celebration

```typescript
function victoryConfetti() {
  // Continuous celebration
  const duration = 5000
  const end = Date.now() + duration

  ;(function frame() {
    confetti({
      particleCount: 3,
      angle: 60,
      spread: 55,
      origin: { x: 0 },
    })
    confetti({
      particleCount: 3,
      angle: 120,
      spread: 55,
      origin: { x: 1 },
    })

    if (Date.now() < end) {
      requestAnimationFrame(frame)
    }
  }())
}
```

## Common Pitfalls

### Pitfall 1: Confetti Not Visible

**Symptom:** Confetti fires but nothing appears.

**Solution:** Check `zIndex` - ensure confetti canvas isn't behind other elements.

### Pitfall 2: Performance Issues

**Symptom:** App slows down during confetti.

**Solution:** Reduce `particleCount`, enable `useWorker`, or decrease duration.

### Pitfall 3: Canvas Not Cleaning Up

**Symptom:** Multiple canvases accumulate in DOM.

**Solution:** Call `confetti.reset()` on component unmount.

---

**Activation Trigger:** Use this skill when:
- Adding celebration effects for achievements
- Implementing completion animations
- Creating victory celebrations
- Adding micro-interactions for positive feedback
