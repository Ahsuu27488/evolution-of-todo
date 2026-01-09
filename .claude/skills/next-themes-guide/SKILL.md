---
name: next-themes-guide
description: Fetch next-themes documentation and apply dark mode patterns. Use when implementing ThemeProvider, useTheme hook, system theme detection, avoiding FOUC (flash of unstyled content), or integrating with shadcn/ui components. (project)
location: managed
allowed-tools:
  - mcp__context7__resolve-library-id
  - mcp__context7__query-docs
  - Read
  - Write
  - Edit
---

# next-themes Mastery Guide

## Theoretical Foundation

next-themes is a **zero-flash theme switching library** for Next.js that solves the persistent problem of FOUC (Flash of Unstyled Content) when implementing dark mode. It handles:
- System preference detection (`prefers-color-scheme`)
- Theme persistence across sessions (localStorage)
- SSR hydration mismatch prevention
- No-flash initial render (critical for UX)

### The Flash Problem

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        WITHOUT next-themes                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. Server renders: light theme (default)                                   │
│  2. Page loads: light theme visible                                        │
│  3. JS executes: reads localStorage, switches to dark                       │
│  4. Result: FLASH from light → dark (jarring UX)                           │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                        WITH next-themes                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. Inline script runs BEFORE React hydration                              │
│  2. Applies correct theme to <html> element                                │
│  3. React hydrates: matches existing theme                                 │
│  4. Result: No flash, smooth theme display                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Core Setup

### 1. Installation

```bash
npm install next-themes
# or
yarn add next-themes
# or
pnpm add next-themes
```

### 2. ThemeProvider Configuration

```typescript
// app/providers.tsx
'use client'

import { ThemeProvider } from 'next-themes'

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider
      attribute="class"           // Adds class="dark" to <html>
      defaultTheme="system"       // Respects system preference
      enableSystem={true}         // Enable system theme detection
      disableTransitionOnChange   // Prevents transition during theme switch
    >
      {children}
    </ThemeProvider>
  )
}

// app/layout.tsx
import { Providers } from './providers'

export default function RootLayout({ children }) {
  return (
    <html suppressHydrationWarning>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
```

### 3. Critical: suppressHydrationWarning

**ALWAYS** add `suppressHydrationWarning` to the `<html>` tag:

```tsx
<html suppressHydrationWarning>
```

This suppresses the warning about the `class` attribute mismatch between server and client. The mismatch is intentional and required for the no-flash behavior.

## Usage Patterns

### 1. Theme Toggle Component

```tsx
// components/theme-toggle.tsx
'use client'

import { useTheme } from 'next-themes'
import { Moon, Sun } from 'lucide-react'

export function ThemeToggle() {
  const { theme, setTheme, resolvedTheme } = useTheme()

  // resolvedTheme accounts for 'system' theme
  const isDark = resolvedTheme === 'dark'

  return (
    <button
      onClick={() => setTheme(isDark ? 'light' : 'dark')}
      aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
      className="rounded-md p-2 hover:bg-gray-100 dark:hover:bg-gray-800"
    >
      {isDark ? <Sun size={20} /> : <Moon size={20} />}
    </button>
  )
}
```

### 2. Theme-Aware Components

```tsx
import { useTheme } from 'next-themes'

export function Card() {
  const { theme } = useTheme()

  return (
    <div className="bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100">
      Current theme: {theme}
    </div>
  )
}
```

### 3. Multiple Themes

next-themes supports any number of custom themes:

```tsx
<ThemeProvider
  themes={['light', 'dark', 'blue', 'green']}
  defaultTheme="light"
>
  {children}
</ThemeProvider>

// Usage
function ThemeSelector() {
  const { theme, setTheme } = useTheme()

  return (
    <select value={theme} onChange={(e) => setTheme(e.target.value)}>
      <option value="light">Light</option>
      <option value="dark">Dark</option>
      <option value="blue">Blue</option>
      <option value="green">Green</option>
    </select>
  )
}
```

### 4. Tailwind CSS Integration

The standard setup for shadcn/ui and Tailwind:

```javascript
// tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ['class'], // Enable class-based dark mode
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        // ... shadcn/ui color variables
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
}
```

```css
/* app/globals.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    /* ... light theme values */
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    /* ... dark theme values */
  }
}
```

## Advanced Patterns

### 1. System Theme Detection with Fallback

```tsx
'use client'

import { useTheme } from 'next-themes'
import { useEffect, useState } from 'react'

export function SystemThemeAwareComponent() {
  const { theme, systemTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  // Prevent hydration mismatch
  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return null // or a loading skeleton
  }

  // systemTheme is the actual system preference
  const actualTheme = theme === 'system' ? systemTheme : theme

  return <div>Current theme: {actualTheme}</div>
}
```

### 2. Theme-Specific Styles with CSS Variables

```tsx
// Define theme-specific variables
const themes = {
  light: {
    primary: '#3b82f6',
    background: '#ffffff',
  },
  dark: {
    primary: '#60a5fa',
    background: '#0f172a',
  },
}

// Apply them in your CSS
// globals.css
:root {
  --primary: 59 130% 246%; /* blue-500 in HSL */
}

.dark {
  --primary: 217 91% 60%; /* blue-400 in HSL */
}
```

### 3. Conditional Rendering Based on Theme

```tsx
import { useTheme } from 'next-themes'

export function ThemeConditionalComponent() {
  const { resolvedTheme } = useTheme()

  return (
    <div>
      {resolvedTheme === 'dark' ? (
        <DarkThemeIllustration />
      ) : (
        <LightThemeIllustration />
      )}
    </div>
  )
}
```

## Code Standards

### Naming Conventions

```tsx
// ✅ Use descriptive component names
<ThemeToggle />
<ThemeSwitcher />
<ThemeProvider />

// ✅ Use descriptive hook variables
const { theme, setTheme, resolvedTheme } = useTheme()
```

### Type Safety

```tsx
import type { Theme } from 'next-themes'

const themes: Theme[] = ['light', 'dark', 'system']

function setCustomTheme(theme: Theme) {
  setTheme(theme)
}
```

## Common Pitfalls

### Pitfall 1: Missing 'use client' Directive

**Symptom:** "useTheme must be used within a ThemeProvider" or hydration errors.

**Solution:** Any component using `useTheme` must be a Client Component with `'use client'`.

### Pitfall 2: Not Waiting for Mounted State

**Symptom:** Hydration mismatch warnings, inconsistent theme on first render.

**Solution:** Always check `mounted` state before rendering theme-dependent UI.

```tsx
const [mounted, setMounted] = useState(false)
useEffect(() => setMounted(true), [])
if (!mounted) return null
```

### Pitfall 3: Forgetting suppressHydrationWarning

**Symptom:** "Text content did not match" hydration warning in console.

**Solution:** Add `suppressHydrationWarning` to `<html>` tag in layout.

### Pitfall 4: Dark Mode Not Working with Tailwind

**Symptom:** Dark classes not applying or taking effect.

**Solution:** Ensure `darkMode: ['class']` is in tailwind.config.js.

### Pitfall 5: Using Theme During SSR

**Symptom:** Theme is undefined or incorrect during server-side rendering.

**Solution:** Use `resolvedTheme` or wait for `mounted` state for client-only rendering.

## shadcn/ui Integration

next-themes works seamlessly with shadcn/ui components:

```tsx
// components/theme-provider.tsx
'use client'

import * as React from 'react'
import { ThemeProvider as NextThemesProvider } from 'next-themes'

export function ThemeProvider({
  children,
  ...props
}: React.ComponentProps<typeof NextThemesProvider>) {
  return <NextThemesProvider {...props}>{children}</NextThemesProvider>
}

// app/layout.tsx
import { ThemeProvider } from '@/components/theme-provider'

export default function RootLayout({ children }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          {children}
        </ThemeProvider>
      </body>
    </html>
  )
}
```

## When to Use Context7

For advanced scenarios:
- Custom theme storage adapters
- Theme transition animations
- Multiple theme domains (sections with different themes)

Query `/pacocoursey/next-themes` for official documentation.

---

**Activation Trigger:** Use this skill when:
- Implementing dark mode in Next.js
- Setting up ThemeProvider
- Using useTheme hook
- Avoiding FOUC in theme switching
- Integrating with shadcn/ui or Tailwind dark mode
