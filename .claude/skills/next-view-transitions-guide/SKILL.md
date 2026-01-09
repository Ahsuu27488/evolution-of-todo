---
name: next-view-transitions-guide
description: Fetch Next.js View Transitions API documentation and apply smooth page transition patterns. Use when implementing SPA-like navigation transitions, shared element transitions, or seamless route changes in Next.js App Router. (project)
location: managed
allowed-tools:
  - mcp__context7__resolve-library-id
  - mcp__context7__query-docs
  - Read
  - Write
  - Edit
---

# Next.js View Transitions Mastery Guide

## Theoretical Foundation

View Transitions API is a **browser-native API** that enables smooth transitions between page states. Next.js 14+ integrates this API for seamless route transitions in the App Router without requiring JavaScript animation libraries.

### How It Works

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        VIEW TRANSITION LIFECYCLE                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. START: User clicks link                                                  │
│       ↓                                                                      │
│  2. CAPTURE: Browser takes snapshot of current page (::view-transition-old) │
│       ↓                                                                      │
│  3. TRANSITION: Browser applies CSS transition                               │
│       ↓                                                                      │
│  4. NEW PAGE: Next.js renders new route (hidden initially)                   │
│       ↓                                                                      │
│  5. REVEAL: Browser fades in new page (::view-transition-new)               │
│       ↓                                                                      │
│  6. END: Transition complete, new page interactive                           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Browser Support

View Transitions API is supported in:
- Chrome 111+
- Edge 111+
- Safari 18+ (with flag)
- Firefox: Behind flag

**Always provide a fallback** for unsupported browsers.

## Core Setup

### 1. Enable View Transitions in Next.js

```typescript
// next.config.js
const nextConfig = {
  experimental: {
    viewTransition: true, // Enable view transitions
  },
}

module.exports = nextConfig
```

### 2. Basic Usage in App Router

```typescript
// app/layout.tsx
export default function RootLayout({ children }) {
  return (
    <html>
      <body>{children}</body>
    </html>
  )
}

// app/page1/page.tsx
'use client'

import Link from 'next/link'

export default function Page1() {
  return (
    <div>
      <h1>Page 1</h1>
      {/* Opt-in to view transition for this link */}
      <Link href="/page2" style={{ viewTransitionName: 'page-transition' }}>
        Go to Page 2
      </Link>
    </div>
  )
}
```

### 3. Programmatic Navigation with Transitions

```typescript
'use client'

import { useRouter } from 'next/navigation'

export function NavigationButton() {
  const router = useRouter()

  const navigateWithTransition = () => {
    // Enable view transition for this navigation
    document.startViewTransition(() => {
      router.push('/destination')
    })
  }

  return <button onClick={navigateWithTransition}>Go</button>
}
```

## Transition Patterns

### 1. Fade Transition (Default)

The simplest transition - cross-fade between pages:

```css
/* app/globals.css */
::view-transition-old(root) {
  animation: fade-out 0.3s ease-out;
}

::view-transition-new(root) {
  animation: fade-in 0.3s ease-in;
}

@keyframes fade-out {
  from { opacity: 1; }
  to { opacity: 0; }
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}
```

### 2. Slide Transition

Pages slide in from the right (forward) or left (back):

```css
/* Forward transition */
::view-transition-old(root) {
  animation: slide-out-right 0.3s ease-out;
}

::view-transition-new(root) {
  animation: slide-in-right 0.3s ease-out;
}

@keyframes slide-out-right {
  from { transform: translateX(0); opacity: 1; }
  to { transform: translateX(-20px); opacity: 0; }
}

@keyframes slide-in-right {
  from { transform: translateX(20px); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}
```

### 3. Shared Element Transition

Transition specific elements smoothly between pages:

```typescript
// app/products/page.tsx
export default function Products() {
  return (
    <div>
      {products.map((product) => (
        <Link
          key={product.id}
          href={`/products/${product.id}`}
          style={{ viewTransitionName: `product-${product.id}` }}
        >
          <ProductCard product={product} />
        </Link>
      ))}
    </div>
  )
}

// app/products/[id]/page.tsx
export default function ProductDetail({ params }) {
  return (
    <div style={{ viewTransitionName: `product-${params.id}` }}>
      <h1>{product.name}</h1>
      <img src={product.image} alt={product.name} />
    </div>
  )
}
```

### 4. Direction-Aware Transitions

Different animations for forward vs back navigation:

```typescript
'use client'

import { useRouter, usePathname } from 'next/navigation'
import { useEffect, useRef } from 'react'

// Track navigation direction
const navigationHistory = ['']

export function useViewTransition() {
  const router = useRouter()
  const pathname = usePathname()
  const isBackRef = useRef(false)

  const push = (href: string) => {
    isBackRef.current = false
    if (document.startViewTransition) {
      document.startViewTransition(() => router.push(href))
    } else {
      router.push(href)
    }
  }

  const back = () => {
    isBackRef.current = true
    if (document.startViewTransition) {
      document.startViewTransition(() => router.back())
    } else {
      router.back()
    }
  }

  // Update CSS class based on direction
  useEffect(() => {
    document.documentElement.dataset.navigationDirection =
      isBackRef.current ? 'back' : 'forward'
  }, [pathname])

  return { push, back }
}
```

```css
/* Apply different animations based on direction */
html[data-navigation-direction='forward']::view-transition-old(root) {
  animation: slide-left 0.3s ease-out;
}

html[data-navigation-direction='forward']::view-transition-new(root) {
  animation: slide-in-right 0.3s ease-out;
}

html[data-navigation-direction='back']::view-transition-old(root) {
  animation: slide-right 0.3s ease-out;
}

html[data-navigation-direction='back']::view-transition-new(root) {
  animation: slide-in-left 0.3s ease-out;
}
```

## Advanced Patterns

### 1. Progressive Enhancement

Provide fallback for browsers without View Transitions:

```typescript
'use client'

import { useRouter } from 'next/navigation'

export function TransitionLink({
  href,
  children,
  ...props
}: React.ComponentProps<typeof Link>) {
  const router = useRouter()

  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault()

    const supportsViewTransitions = 'startViewTransition' in document

    if (supportsViewTransitions) {
      document.startViewTransition(() => router.push(href))
    } else {
      router.push(href)
    }
  }

  return (
    <a href={href} onClick={handleClick} {...props}>
      {children}
    </a>
  )
}
```

### 2. Custom Transition Duration

Control transition timing:

```typescript
function navigateWithDuration() {
  document.startViewTransition(
    () => router.push('/destination'),
    { duration: 500 } // 500ms transition
  )
}
```

### 3. Skip Transition for Certain Routes

```typescript
function navigateWithoutTransition() {
  // Skip view transition for quick navigation
  router.push('/destination', { skipViewTransition: true })
}
```

## Code Standards

### CSS Organization

```css
/* Separate view transition styles */
/* app/view-transitions.css */

/* Root group - entire page transition */
::view-transition-old(root),
::view-transition-new(root) {
  animation-duration: 0.3s;
  animation-timing-function: ease-in-out;
}

/* Named groups - specific element transitions */
::view-transition-old(hero-image),
::view-transition-new(hero-image) {
  animation-duration: 0.5s;
}

/* Default fallback */
@supports not (view-transition-name: none) {
  /* Regular page styles for browsers without support */
}
```

### TypeScript Types

```typescript
interface ViewTransitionOptions {
  duration?: number
  skipTransition?: boolean
}

declare global {
  interface Document {
    startViewTransition(
      callback: () => void | Promise<void>,
      options?: ViewTransitionOptions
    ): ViewTransition | undefined
  }

  interface CSSStyleDeclaration {
    viewTransitionName: string
  }
}
```

## Common Pitfalls

### Pitfall 1: Not Setting viewTransitionName

**Symptom:** Elements don't transition smoothly, just fade.

**Solution:** Set `viewTransitionName` on elements you want to transition individually.

### Pitfall 2: Conflicting viewTransitionName Values

**Symptom:** Only one element transitions, others are ignored.

**Solution:** Each element on a page must have a unique `viewTransitionName`.

### Pitfall 3: Forgetting Browser Support

**Symptom:** No transitions in Safari/Firefox.

**Solution:** Always check for `'startViewTransition' in document` and provide fallback.

### Pitfall 4: Large Layout Shifts

**Symptom:** Jarring transitions due to layout changes.

**Solution:** Keep page layouts consistent or use shared element transitions for major elements.

---

**Activation Trigger:** Use this skill when:
- Implementing smooth page transitions in App Router
- Creating SPA-like navigation experiences
- Building shared element transitions
- Optimizing perceived performance during route changes
