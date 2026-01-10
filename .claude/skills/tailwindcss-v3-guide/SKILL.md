---
name: tailwindcss-v3-guide
description: Fetch Tailwind CSS v3 documentation and apply utility-first CSS patterns. Use when configuring tailwind.config.js, using theme extend, plugins, or maintaining v3 projects.
location: managed
version: 1.0.0
allowed-tools:
  - mcp__context7__resolve-library-id
  - mcp__context7__query-docs
  - Read
  - Write
  - Edit
---

# Tailwind CSS v3 Mastery Guide

## Theoretical Foundation

Tailwind CSS v3 is a **utility-first CSS framework** that generates styles based on class names used in your templates. It uses a JavaScript-based configuration system (`tailwind.config.js`) and PostCSS plugins to compile utility classes into optimized CSS.

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         TAILWIND CSS v3 BUILD PIPELINE                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  Source Templates (HTML/JSX/TSX)                                            │
│       │                                                                      │
│       ▼                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐     │
│  │                     PostCSS Processing                               │     │
│  │  ┌─────────────┐    ┌──────────────┐    ┌─────────────────────────┐  │     │
│  │  │ @tailwind   │───▶│ @apply       │───▶│ @layer                  │  │     │
│  │  │ directives  │    │ (component)  │    │ (base/components/util) │  │     │
│  │  └─────────────┘    └──────┬───────┘    └─────────────────────────┘  │     │
│  └────────────────────────────┼──────────────────────────────────────┘     │
│                               ▼                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐     │
│  │                     Tailwind CLI / JIT                               │     │
│  │  ┌─────────────┐    ┌──────────────┐    ┌─────────────────────────┐  │     │
│  │  │ Class Scan  │───▶│ Config Merge │───▶│ Utility Generation      │  │     │
│  │  │ (templates) │    │ (theme extend)│    │ (CSS output)            │  │     │
│  │  └─────────────┘    └──────┬───────┘    └───────────┬─────────────┘  │     │
│  └────────────────────────────┼──────────────────────────┘                 │
│                               ▼                                            │
│  Output CSS (purged, optimized)                                            │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘
```

### Key Concepts

1. **Utility-First**: Style directly in markup with pre-defined classes
2. **JIT Mode**: Just-In-Time compiler generates styles on-demand
3. **Config-Based**: `tailwind.config.js` for theme customization
4. **Plugin System**: Extend functionality with community plugins
5. **Purging**: Removes unused styles in production builds

## Configuration Structure

### tailwind.config.js

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  // Content: Paths to scan for class names
  content: [
    './pages/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
    './app/**/*.{js,ts,jsx,tsx}',
    './src/**/*.{js,ts,jsx,tsx}',
  ],

  // Dark mode strategy
  darkMode: 'class', // or 'media' for system preference

  // Theme customization
  theme: {
    // Direct override (replaces defaults)
    screens: {
      'sm': '640px',
      'md': '768px',
      'lg': '1024px',
      'xl': '1280px',
      '2xl': '1536px',
    },

    // Extend (merges with defaults)
    extend: {
      colors: {
        primary: '#3b82f6',
        secondary: '#8b5cf6',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      spacing: {
        '128': '32rem',
      },
      borderRadius: {
        '4xl': '2rem',
      },
    },
  },

  // Plugins
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    require('tailwindcss-animate'),
  ],
}
```

### Theme Extend vs Override

```javascript
// ❌ OVERRIDE - Replaces entire color palette
theme: {
  colors: {
    blue: '#0000ff', // Only blue available
  }
}

// ✅ EXTEND - Adds to existing palette
theme: {
  extend: {
    colors: {
      brand: '#3b82f6', // Adds 'brand' while keeping defaults
    }
  }
}
```

## When to Use This Skill

Activation triggers:
- Setting up a new Tailwind v3 project
- Configuring `tailwind.config.js`
- Using `theme.extend` for customization
- Adding Tailwind plugins (`@tailwindcss/forms`, `tailwindcss-animate`)
- Using `@apply` directive in components
- Configuring dark mode with `class` strategy

## Common Patterns

### Custom Color Palette

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6', // DEFAULT
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
      },
    },
  },
}
```

### Custom Utilities with @apply

```css
/* globals.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer components {
  .btn-primary {
    @apply px-4 py-2 bg-primary text-white rounded-lg;
    @apply hover:bg-primary-700 active:scale-95;
    @apply transition-all duration-200;
  }

  .card {
    @apply bg-white dark:bg-gray-800 rounded-xl shadow-md p-6;
  }
}

@layer utilities {
  .text-balance {
    text-wrap: balance;
  }
}
```

### Dark Mode Configuration

```javascript
// tailwind.config.js
module.exports = {
  darkMode: 'class', // Manual control with .dark class
  // darkMode: 'media', // System preference (default)
}
```

```jsx
// Usage with next-themes
import { ThemeProvider } from 'next-themes'

export default function RootLayout({ children }) {
  return (
    <ThemeProvider attribute="class" defaultTheme="system">
      {children}
    </ThemeProvider>
  )
}
```

### Custom Animations

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      keyframes: {
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'slide-up': {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
      animation: {
        'fade-in': 'fade-in 0.5s ease-out',
        'slide-up': 'slide-up 0.5s ease-out',
      },
    },
  },
}
```

## Popular Plugins

| Plugin | Purpose | Install |
|--------|---------|---------|
| `@tailwindcss/forms` | Form reset & styling | `npm install -D @tailwindcss/forms` |
| `@tailwindcss/typography` | Prose styling for content | `npm install -D @tailwindcss/typography` |
| `tailwindcss-animate` | Animation utilities | `npm install -D tailwindcss-animate` |

### Using tailwindcss-animate

```javascript
// tailwind.config.js
module.exports = {
  plugins: [require('tailwindcss-animate')],
}
```

```jsx
// Animations available
<div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
  Content animates in
</div>
```

## Code Standards

### Configuration Standards

| Rule | Description |
|------|-------------|
| **Prefer extend** | Use `theme.extend` to preserve defaults |
| **Semantic names** | Use descriptive names (`brand-primary` vs `blue-500`) |
| **Consistent spacing** | Follow 4px base unit for spacing scale |
| **Type colors** | Define semantic colors (primary, secondary, accent) |

### Class Ordering Standards

```jsx
// ✅ GOOD - Logical grouping
<div className="
  flex items-center justify-between
  px-4 py-2
  bg-white dark:bg-gray-800
  rounded-lg shadow-md
  hover:shadow-lg
  transition-shadow
  duration-200
">

// ❌ BAD - Random order
<div className="flex bg-white hover:shadow-lg px-4 duration-200 rounded-lg">
```

### @layer Standards

```css
/* ✅ CORRECT - Proper layer usage */
@layer base {
  /* Global resets */
}

@layer components {
  /* Reusable components */
}

@layer utilities {
  /* Custom utilities */
}

/* ❌ WRONG - Everything in base */
@layer base {
  .btn { @apply px-4 py-2; }
  .card { @apply p-6 rounded-xl; }
}
```

## Common Pitfalls

### Pitfall 1: Not Configuring Content Paths

**Symptom**: Styles not applying after build

**Fix**: Ensure all template paths are in `content` array

```javascript
// ❌ WRONG - Missing paths
module.exports = {
  content: ['./src/**/*.{js,jsx}'], // Misses .ts, .tsx
}

// ✅ CORRECT - All file extensions
module.exports = {
  content: [
    './src/**/*.{js,ts,jsx,tsx}',
    './app/**/*.{js,ts,jsx,tsx}',
    './pages/**/*.{js,ts,jsx,tsx}',
  ],
}
```

### Pitfall 2: Overriding Instead of Extending

**Symptom**: Default utilities disappear

**Fix**: Always use `theme.extend` for additions

```javascript
// ❌ WRONG - Loses all default colors
theme: {
  colors: {
    blue: '#0000ff',
  }
}

// ✅ CORRECT - Keeps defaults
theme: {
  extend: {
    colors: {
      blue: {
        custom: '#0000ff',
      },
    }
  }
}
```

### Pitfall 3: Using @apply for Everything

**Symptom**: Larger CSS bundle, harder to maintain

**Fix**: Use utilities directly in HTML, @apply only for repeated patterns

```jsx
/* ❌ WRONG - @apply for one-off styles */
.my-div {
  @apply flex items-center justify-between px-4 py-2 bg-white;
}

/* ✅ CORRECT - Direct utilities for one-off */
<div className="flex items-center justify-between px-4 py-2 bg-white">

/* ✅ CORRECT - @apply for repeated component */
@layer components {
  .btn {
    @apply px-4 py-2 bg-primary text-white rounded-lg;
  }
}
```

## Context7 Query Patterns

| Topic | Query String |
|-------|--------------|
| Configuration | "tailwind.config.js theme extend colors screens spacing" |
| Dark Mode | "darkMode class media configuration next-themes" |
| Plugins | "@tailwindcss/forms typography tailwindcss-animate plugins" |
| @apply | "@apply directive @layer components utilities CSS" |
| JIT | "JIT mode purge content configuration production build" |

## Quick Reference

| Concept | v3 Syntax |
|---------|-----------|
| Config | `tailwind.config.js` (JavaScript) |
| Import | `@tailwind base/components/utilities;` |
| Theme values | `theme('colors.blue.500')` |
| Custom utility | `@layer utilities { .class { @apply ... } }` |
| Extend | `theme: { extend: { ... } }` |
| Plugins | `plugins: [require('plugin-name')]` |

## Migration from v2

```javascript
// v2 → v3 changes

// ❌ v2 - purge option
module.exports = {
  purge: ['./src/**/*.{html,js}'],
}

// ✅ v3 - content option (auto JIT)
module.exports = {
  content: ['./src/**/*.{html,js}'],
}
```

```javascript
// ❌ v2 - variants in theme
module.exports = {
  theme: {
    extend: {
      variants: {
        display: ['hover'],
      },
    },
  },
}

// ✅ v3 - variants no longer needed (all variants enabled by default)
```

## References

- **Documentation**: https://tailwindcss.com/docs
- **v3 Reference**: https://v3.tailwindcss.com
- **Plugins**: https://tailwindcss.com/docs/plugins
- **Context7 ID**: `/websites/v3_tailwindcss`
