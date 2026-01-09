---
name: tailwindcss-v4-guide
description: Fetch Tailwind CSS v4 documentation and apply CSS-first architecture patterns. Use when implementing v4's new @import syntax, @theme directive, cascade layers, or migrating from v3. (project)
location: managed
allowed-tools:
  - mcp__context7__resolve-library-id
  - mcp__context7__query-docs
  - Read
  - Write
  - Edit
---

# Tailwind CSS v4 Mastery Guide

## Theoretical Foundation

Tailwind CSS v4 represents a **fundamental architectural shift** from JavaScript-based configuration to **CSS-first configuration**. This redesign embraces native CSS features (cascade layers, CSS custom properties, @import) while maintaining the utility-first philosophy.

### Key Architectural Changes (v3 → v4)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              TAILWIND v3                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  tailwind.config.js ──► PostCSS ──► JIT Generator ──► Output CSS            │
│  ├─ theme() function                                                        │
│  ├─ JavaScript plugins                                                      │
│  └─ Build-time class scanning                                               │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              TAILWIND v4                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  @import "tailwindcss" ──► CSS Parser ──► Vite Plugin ──► Output CSS       │
│  ├─ @theme directive (CSS variables)                                        │
│  ├─ Native cascade layers (@layer)                                          │
│  └─ Runtime-first class generation                                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

### The @theme Directive

The `@theme` directive is the heart of v4 configuration. It converts CSS custom properties into utility classes:

```css
@import "tailwindcss";

@theme {
  /* Typography */
  --font-display: "Satoshi", "sans-serif";
  --font-mono: ui-monospace, monospace;

  /* Breakpoints (use with 3xl: prefix) */
  --breakpoint-3xl: 1920px;

  /* Colors (oklch format recommended for perceptual uniformity) */
  --color-avocado-100: oklch(0.99 0 0);
  --color-avocado-500: oklch(0.84 0.18 117.33);

  /* Animation easing */
  --ease-fluid: cubic-bezier(0.3, 0, 0, 1);
  --ease-snappy: cubic-bezier(0.2, 0, 0, 1);

  /* Spacing, spacing units, border radius, etc. */
}
```

### Cascade Layers

v4 uses native CSS cascade layers for deterministic specificity:

```css
/* Layer order (lowest to highest priority): */
@layer base, components, utilities;

/* Custom utilities now use @utility instead of @layer utilities */
@utility tab-4 {
  tab-size: 4;
}
```

## Migration Guide: v3 → v4

### 1. Configuration Migration

**v3 (JavaScript):**
```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: '#3b82f6',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [require('@tailwindcss/forms')],
}
```

**v4 (CSS):**
```css
/* app/globals.css */
@import "tailwindcss";

@theme {
  --color-primary: #3b82f6;
  --font-sans: "Inter", sans-serif;
}

/* Forms plugin is now built-in - no plugin required */
```

### 2. theme() Function Migration

**v3:**
```css
.my-class {
  background-color: theme(colors.red.500);
  color: theme('colors.blue.500');
}
```

**v4:**
```css
.my-class {
  background-color: var(--color-red-500);
  color: var(--color-blue-500);
}
```

### 3. Custom Utilities Migration

**v3:**
```css
@layer utilities {
  .text-balance {
    text-wrap: balance;
  }
}
```

**v4:**
```css
@utility text-balance {
  text-wrap: balance;
}
```

## Code Standards

### Color Format Preference

**Always prefer OKLCH over hex/rgb** for perceptual uniformity:

```css
/* ✅ RECOMMENDED: Perceptually uniform */
--color-primary-500: oklch(0.6 0.2 250);

/* ⚠️ ACCEPTABLE: Traditional formats */
--color-accent: #3b82f6;
--color-warning: rgb(251 191 36);
```

### Variable Naming Convention

Follow the kebab-case convention for theme variables:

```css
/* ✅ CORRECT */
--color-blue-500: ...
--font-display: ...
--breakpoint-3xl: ...

/* ❌ INCORRECT */
--blue500: ...
--displayFont: ...
--3xl-breakpoint: ...
```

### @theme Organization

Structure your @theme block logically:

```css
@theme {
  /* 1. Typography */
  --font-*: ...

  /* 2. Colors (lightest to darkest) */
  --color-*-100: ...
  --color-*-900: ...

  /* 3. Spacing */
  --spacing-*: ...

  /* 4. Breakpoints */
  --breakpoint-*: ...

  /* 5. Animation */
  --ease-*: ...
  --duration-*: ...
}
```

## Common Pitfalls

### Pitfall 1: Missing @import

**Symptom:** Utilities not generating, no styles applied.

**Solution:** Always start with `@import "tailwindcss";` before @theme.

### Pitfall 2: Using Old tailwind.config.js

**Symptom:** Configuration not being applied, confusing build errors.

**Solution:** Remove `tailwind.config.js` entirely and migrate to @theme in CSS. v4 ignores JS config files.

### Pitfall 3: Hybrid darkMode Configuration

**Symptom:** Dark mode not working after migration.

**Solution:** In v4, use the class strategy with `class="dark"` on html element. The dark mode configuration is automatic with next-themes.

## When to Use Context7

For edge cases not covered in this guide:
- Migration of complex plugins to v4 equivalents
- Advanced @theme nested configurations
- CSS-first strategies for third-party integrations

Use the context7-lookup skill to query:
- `/tailwindlabs/tailwindcss.com` for official v4 documentation
- `/websites/v3_tailwindcss` for legacy v3 patterns (for comparison)

## Quick Reference

| Concept | v3 Syntax | v4 Syntax |
|---------|-----------|-----------|
| Config | `tailwind.config.js` | `@theme { }` in CSS |
| Import | `@tailwind base;` | `@import "tailwindcss";` |
| Theme values | `theme(colors.x)` | `var(--color-x)` |
| Custom utility | `@layer utilities` | `@utility` |
| Color format | hex/hsl() | oklch() preferred |

---

**Activation Trigger:** Use this skill when implementing Tailwind CSS, especially when:
- Setting up a new Tailwind v4 project
- Migrating from v3 to v4
- Configuring @theme, @utility, or CSS variables
- Troubleshooting v4-specific issues
