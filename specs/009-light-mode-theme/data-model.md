# Data Model: Light Mode Theme

**Feature**: 009-light-mode-theme
**Date**: 2025-01-13
**Status**: Complete

## Overview

This feature does not introduce new data entities. It extends the existing CSS variable system to support light mode themes. All data is stored and managed by the existing `next-themes` library.

## Existing Entities

### Theme Preference

**Source**: `next-themes` library (internal implementation)

**Storage**: `localStorage` key `theme`

**Attributes**:

| Attribute | Type | Values | Description |
|-----------|------|--------|-------------|
| theme | string | `'light'` \| `'dark'` \| `'system'` | User's selected theme mode |

**Behavior**:
- When `'system'` selected, library watches `prefers-color-scheme` media query
- Theme value persisted to `localStorage` automatically
- Theme class (`.light` or `.dark`) applied to `<html>` element

**Lifecycle**:
1. On page load, read from `localStorage` (default: `'system'`)
2. If `'system'`, detect OS preference via `prefers-color-scheme`
3. Apply appropriate class to `<html>` element
4. Listen for OS theme changes when in system mode

### CSS Variable Token

**Source**: `frontend/app/globals.css`

**Structure**: Each token has two values - one for `.light` class, one for `.dark` class

**Categories**:

#### 1. Base Colors
```css
/* --background, --foreground */
```

#### 2. Surface Colors
```css
/* --card, --popover, --muted */
```

#### 3. Accent Colors
```css
/* --primary, --secondary, --accent, --destructive */
```

#### 4. Interactive States
```css
/* --border, --input, --ring */
```

#### 5. Chart Colors
```css
/* --chart-1 through --chart-5 */
```

#### 6. Sidebar Colors
```css
/* --sidebar-* variants */
```

## State Transitions

```
┌─────────────────────────────────────────────────────────────┐
│                    Theme State Machine                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────┐   select light   ┌──────────┐               │
│   │  Dark   │ ────────────────▶│  Light   │               │
│   └─────────┘                 └──────────┘               │
│        ▲                            ▲                      │
│        │                            │                      │
│        │     select system          │                      │
│        └────────────────────────────┴─────────────┐       │
│                                                     │       │
│                                              ┌──────┴──────┐│
│                                              │   System    ││
│                                              └──────┬──────┘│
│                                                     │       │
│                               OS changes (dark◀─────┘       │
│                                   ─────────────▶            │
│                               OS changes (light)           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## No Database Changes

This feature requires no database migrations, API changes, or backend modifications. All theme state is client-side only.

## Component Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Theme Data Flow                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  User clicks theme toggle                                    │
│       │                                                      │
│       ▼                                                      │
│  next-themes setTheme()                                      │
│       │                                                      │
│       ├──▶ Update localStorage                              │
│       ├──▶ Apply .light or .dark class to <html>            │
│       └──▶ Trigger re-render of ThemeProvider consumers     │
│                                                             │
│  CSS Cascade                                                 │
│       │                                                      │
│       ▼                                                      │
│  .light or .dark selector activates                          │
│       │                                                      │
│       ▼                                                      │
│  CSS variables resolve to theme-specific values              │
│       │                                                      │
│       ▼                                                      │
│  Components re-render with new colors (automatic)           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Validation Rules

No validation required - theme values are constrained by the UI (three button options).

## Persistence Strategy

| Aspect | Implementation |
|--------|----------------|
| Storage | `localStorage` via `next-themes` |
| Key | `theme` |
| Default | `'system'` |
| Duration | Until manually changed or localStorage cleared |
| Fallback | System preference via `prefers-color-scheme` |
