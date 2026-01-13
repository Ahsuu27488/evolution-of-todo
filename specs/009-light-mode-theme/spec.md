# Feature Specification: Light Mode Theme

**Feature Branch**: `009-light-mode-theme`
**Created**: 2025-01-13
**Status**: Complete
**Input**: User description: "Implement Light Mode Theme. Before defining requirements, analyze all files in frontend/ (excluding node_modules) to understand the current Deep Space design tokens and CSS variable structure. The spec must define a Light Mode that maps 1:1 to the existing dark mode tokens (background, foreground, card, popover, primary, secondary, etc.) ensuring visual consistency and proper contrast ratios. analyze all files mean read all of them!"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Theme Selection (Priority: P1)

A user can choose between Light, Dark, and System themes via the theme toggle in the header. The theme toggle shows three buttons (Sun, Moon, Monitor) with visual feedback indicating the active selection. The application remembers the user's theme preference across sessions.

**Why this priority**: This is the core functionality enabling light mode. Without theme selection, light mode cannot be accessed by users.

**Independent Test**: Can be fully tested by clicking each theme button and verifying the UI switches to the corresponding theme while confirming preference persistence on page reload.

**Acceptance Scenarios**:

1. **Given** a user viewing the application in dark mode, **When** they click the Sun icon in the theme toggle, **Then** the application switches to light mode and all colors invert appropriately
2. **Given** a user with a saved light mode preference, **When** they reload the application or return after closing the browser, **Then** the application loads in light mode automatically
3. **Given** a user with system theme selected, **When** their operating system theme changes between light and dark, **Then** the application automatically switches to match the system preference

---

### User Story 2 - Light Mode Visual Consistency (Priority: P2)

When light mode is active, all UI elements maintain the same visual hierarchy and brand identity as dark mode, but with inverted brightness values. Text remains readable with proper contrast ratios (WCAG AA minimum 4.5:1). The signature cyan and purple neon accent colors remain consistent across both themes.

**Why this priority**: Ensures the light mode delivers a cohesive experience that feels like part of the same application, maintaining brand recognition while providing visual comfort in bright environments.

**Independent Test**: Can be fully tested by activating light mode and comparing each UI component (buttons, cards, inputs, modals, badges) against the dark mode version to verify semantic color mapping.

**Acceptance Scenarios**:

1. **Given** a user in light mode viewing the dashboard, **When** they look at task cards, **Then** cards have white/light backgrounds with subtle shadows and dark text instead of dark semi-transparent backgrounds
2. **Given** a user in light mode, **When** they view primary buttons, **Then** the cyan accent color remains identical to dark mode for brand consistency
3. **Given** a user in light mode, **When** they hover over interactive elements, **Then** hover states use light-appropriate colors (darker overlays instead of lighter ones)
4. **Given** a user in light mode viewing high-priority tasks, **When** they look at priority indicators, **Then** the red border and glow effects remain visually distinct against the light background

---

### User Story 3 - Component-Specific Light Mode Adaptations (Priority: P3)

Glassmorphism effects adapt appropriately for light mode. The deep space gradient background inverts to a complementary light gradient. Glass cards use light-appropriate backdrop blur with subtle borders. Glow effects on interactive elements use darker, more visible shadows instead of light emission.

**Why this priority**: These polish elements ensure the sophisticated "Deep Space" aesthetic translates elegantly to light mode rather than appearing as a simple color inversion.

**Independent Test**: Can be fully tested by examining each component type (modal, dropdown, toolbar, hero section) in light mode and verifying glass effects remain visually coherent.

**Acceptance Scenarios**:

1. **Given** a user in light mode viewing the hero section, **When** they look at the animated gradient orbs, **Then** subtle colored gradients appear against the light background instead of glowing against dark
2. **Given** a user in light mode opening a modal, **When** the modal appears, **Then** the glass effect uses a light semi-transparent background with darker border instead of dark semi-transparent with light border
3. **Given** a user in light mode completing a task, **When** the completion animation plays, **Then** the cyan glow effect adapts to use a darker cyan shadow for visibility against the light background

### Edge Cases

- What happens when a user's system theme changes while the application is open?
  - The application detects the change via the `next-themes` library and updates the UI immediately without requiring a page reload
- How does the system handle browsers that don't support `backdrop-filter` for glassmorphism?
  - The existing `@supports not (backdrop-filter: blur(1px))` fallback provides solid opaque backgrounds; this fallback works identically in light mode with appropriate background colors
- What happens when JavaScript is disabled and the theme toggle cannot function?
  - The application defaults to system theme via the `defaultTheme="system"` configuration in ThemeProvider; users cannot switch themes without JS but the application remains functional
- How do custom scrollbar styles (if any) adapt to light mode?
  - Scrollbar WebKit styles using CSS variables like `var(--background)` automatically adapt to the current theme's color values

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a theme toggle with three options: Light, Dark, and System
- **FR-002**: System MUST persist the user's theme preference in localStorage
- **FR-003**: System MUST respect the operating system's theme preference when System mode is selected
- **FR-004**: System MUST define a complete set of light mode CSS variables that map 1:1 to existing dark mode tokens
- **FR-005**: System MUST maintain the cyan (#00f5ff / oklch(0.91 0.17 195)) and purple (#a855f7 / oklch(0.65 0.26 293)) accent colors unchanged between light and dark modes
- **FR-006**: System MUST ensure all text in light mode meets WCAG AA contrast requirements (minimum 4.5:1 for normal text, 3:1 for large text)
- **FR-007**: System MUST adapt glassmorphism utilities (`.glass`, `.glass-strong`, `.glass-modal`) for light mode with appropriate backgrounds and borders
- **FR-008**: System MUST adapt the deep space background gradient to a complementary light gradient
- **FR-009**: System MUST adapt glow effects for light mode using darker shadows/overlays instead of light emission
- **FR-010**: System MUST provide seamless transitions between themes without page reload
- **FR-011**: System MUST prevent hydration mismatch errors during initial page load for server-rendered components

### Key Entities

**Theme Preference**
- Represents the user's selected theme mode
- Attributes: theme value (light | dark | system), persistence mechanism (localStorage), system preference detection (prefers-color-scheme media query)

**CSS Variable Token**
- Represents a single design token that has different values in light vs dark mode
- Attributes: variable name (e.g., `--background`, `--foreground`), light mode value, dark mode value, usage context (component, utility, global)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can switch between Light, Dark, and System themes in under 1 second without page reload
- **SC-002**: All interactive elements (buttons, links, inputs) meet or exceed WCAG AA contrast ratios (4.5:1) in light mode
- **SC-003**: The theme preference persists across sessions for 30 days or until manually changed
- **SC-004**: Light mode maintains visual consistency across all component types (cards, modals, buttons, badges, inputs)
- **SC-005**: The signature cyan and purple accent colors have identical hex values in both light and dark modes
- **SC-006**: Glassmorphism effects remain visually coherent in light mode with proper backdrop blur and border visibility
- **SC-007**: No visual "flash" of incorrect theme occurs during initial page load
- **SC-008**: All 35+ existing CSS variables defined in `globals.css` have corresponding light mode values

## Design Token Specifications

### Current Dark Mode Tokens (Deep Space)

The following tokens are defined in `frontend/app/globals.css` and MUST have corresponding light mode values:

```css
/* Base Colors (Dark Mode) */
--color-background: oklch(0.08 0.01 270);    /* Deep space black */
--color-foreground: oklch(0.98 0.005 270);  /* Light text */

/* Glass Surfaces */
--color-card: oklch(0.12 0.01 270 / 0.7);
--color-popover: oklch(0.12 0.01 270 / 0.8);

/* Primary - Neon Cyan (unchanged in light mode) */
--color-primary: oklch(0.91 0.17 195);
--color-primary-foreground: oklch(0.08 0.01 270);

/* Secondary - Neon Purple (unchanged in light mode) */
--color-secondary: oklch(0.65 0.26 293);
--color-secondary-foreground: oklch(0.98 0.005 270);

/* Muted */
--color-muted: oklch(0.16 0.01 270 / 0.5);
--color-muted-foreground: oklch(0.65 0.01 270);

/* Accent */
--color-accent: oklch(0.65 0.26 293);

/* Destructive - Red */
--color-destructive: oklch(0.60 0.25 25);

/* Border & Input */
--color-border: oklch(1 0 270 / 0.1);
--color-input: oklch(1 0 270 / 0.08);
--color-ring: oklch(0.91 0.17 195);

/* Chart Colors */
--color-chart-1: oklch(0.91 0.17 195); /* cyan */
--color-chart-2: oklch(0.65 0.26 293); /* purple */
--color-chart-3: oklch(0.75 0.20 145); /* green */
--color-chart-4: oklch(0.60 0.25 25);  /* red */
--color-chart-5: oklch(0.85 0.15 85);  /* amber */

/* Sidebar */
--color-sidebar: oklch(0.10 0.01 270);
--color-sidebar-foreground: oklch(0.98 0.005 270);
```

### Light Mode Token Specifications

The following token values MUST be defined for light mode (when `.light` class is present on `<html>`):

```css
/* Base Colors (Light Mode) */
--color-background: oklch(0.98 0.005 270);   /* Near-white */
--color-foreground: oklch(0.15 0.01 270);   /* Dark text */

/* Glass Surfaces */
--color-card: oklch(1 0 270 / 0.8);         /* White with opacity */
--color-popover: oklch(1 0 270 / 0.9);      /* White with higher opacity */

/* Primary - Same Neon Cyan */
--color-primary: oklch(0.91 0.17 195);      /* UNCHANGED */
--color-primary-foreground: oklch(0.98 0.005 270); /* Light text on cyan */

/* Secondary - Same Neon Purple */
--color-secondary: oklch(0.65 0.26 293);    /* UNCHANGED */
--color-secondary-foreground: oklch(0.98 0.005 270); /* Light text on purple */

/* Muted */
--color-muted: oklch(0.94 0.005 270 / 0.6); /* Light gray */
--color-muted-foreground: oklch(0.50 0.01 270); /* Medium gray text */

/* Accent */
--color-accent: oklch(0.65 0.26 293);       /* UNCHANGED - purple */
--color-accent-foreground: oklch(0.98 0.005 270);

/* Destructive - Same Red */
--color-destructive: oklch(0.60 0.25 25);   /* UNCHANGED */
--color-destructive-foreground: oklch(0.98 0.005 270);

/* Border & Input */
--color-border: oklch(0 0 270 / 0.1);        /* Dark with low opacity */
--color-input: oklch(0 0 270 / 0.08);       /* Dark with very low opacity */
--color-ring: oklch(0.91 0.17 195);         /* UNCHANGED - cyan */

/* Chart Colors - UNCHANGED */
--color-chart-1 through 5: Same values as dark mode

/* Sidebar */
--color-sidebar: oklch(0.96 0.005 270);     /* Light gray */
--color-sidebar-foreground: oklch(0.15 0.01 270);
--color-sidebar-primary: oklch(0.91 0.17 195); /* UNCHANGED */
--color-sidebar-accent: oklch(0.65 0.26 293);  /* UNCHANGED */
```

### RGB Format Variables

The application also uses RGB format variables (for `rgb(var(--name))` syntax). These MUST also be defined:

```css
/* Light mode RGB variables */
--background: 248 248 250;    /* #f8f8fa */
--foreground: 30 30 35;       /* #1e1e23 */
--card: 255 255 255 / 0.8;
--card-foreground: 30 30 35;
--popover: 255 255 255 / 0.9;
--popover-foreground: 30 30 35;
--primary: 0 245 255;         /* UNCHANGED */
--primary-foreground: 248 248 250;
--secondary: 168 85 247;       /* UNCHANGED */
--secondary-foreground: 248 248 250;
--muted: 240 240 245 / 0.6;
--muted-foreground: 120 120 140;
--accent: 168 85 247;          /* UNCHANGED */
--accent-foreground: 248 248 250;
--destructive: 239 68 68;      /* UNCHANGED */
--destructive-foreground: 248 248 250;
--border: 0 0 0 / 0.1;
--input: 0 0 0 / 0.08;
--ring: 0 245 255;             /* UNCHANGED */
```

### Utility Class Adaptations

The following utility classes MUST have light-mode-specific behavior:

**`.glass` class in light mode:**
- Background: `rgba(255, 255, 255, 0.7)` instead of `rgba(20, 20, 30, 0.7)`
- Border: Darker color for visibility against light backgrounds
- Backdrop filter: unchanged (blur works identically)

**`.glass-strong` class in light mode:**
- Background: `rgba(255, 255, 255, 0.9)` for stronger opacity
- Border: Slightly darker than `.glass` for hierarchy

**`.glass-modal` class in light mode:**
- Background: `rgba(255, 255, 255, 0.95)` for near-solid modal
- Shadow: Darker shadow for elevation (`0 25px 50px -12px rgba(0, 0, 0, 0.15)`)
- Inset highlight: Darker for visibility

**`.glow-cyan`, `.glow-purple` classes in light mode:**
- Use darker shadows with lower opacity for visibility
- Cyan glow: `0 0 20px rgba(0, 245, 255, 0.15), 0 0 40px rgba(0, 245, 255, 0.05)`
- Purple glow: `0 0 20px rgba(168, 85, 247, 0.15), 0 0 40px rgba(168, 85, 247, 0.05)`

**Body background gradient in light mode:**
- Radial gradients use much lower opacity for subtle effect
- Cyan orb: `rgba(0, 245, 255, 0.015)` instead of `0.03`
- Purple orb: `rgba(168, 85, 247, 0.015)` instead of `0.03`
- Base color: Near-white instead of deep space black

## Technical Implementation Notes

### Theme Provider Configuration

The existing `ThemeProvider` in `frontend/app/providers.tsx` uses:
- `attribute="class"` - adds `.dark` or `.light` class to `<html>` element
- `defaultTheme="system"` - respects OS preference by default
- `enableSystem` - enables system theme detection
- `disableTransitionOnChange` - prevents animation during theme switch

No configuration changes are required to the ThemeProvider; only CSS variable definitions need to be added.

### File Locations for Changes

1. **`frontend/app/globals.css`** - Add `.light` selector with all light mode variable definitions (parallel to existing `.dark` selector)
2. **`@layer utilities` section** - Add light-mode-specific overrides for glass and glow utilities using `.light` prefix
3. **`@layer base` body section** - Update body background gradient for light mode

### Component Considerations

All components using CSS variables for colors will automatically adapt to light mode once variables are defined. No component code changes are required because:

- `components/ui/button.tsx` uses `bg-primary`, `text-foreground`, etc.
- `components/ui/card.tsx` uses `bg-card`, `text-card-foreground`
- `components/ui/input.tsx` uses `border-input`, `bg-background/50`
- All UI components follow this pattern and will inherit light mode values

### Hero Section Background

The animated gradient orbs in `components/landing/hero-section.tsx` use inline styles with `bg-primary/20` and `bg-secondary/20`. These opacity utilities work correctly in light mode because they reference the same accent colors; only the opacity provides the appropriate subtlety.

## Assumptions

1. The `next-themes` library is already installed and configured (version `^0.4.6` in package.json)
2. The existing theme toggle UI in `components/layout/theme-toggle.tsx` requires no changes
3. Light mode should feel like a "daytime version" of the same space, not a completely different aesthetic
4. Users prefer light mode in bright environments (daylight, bright offices) for reduced eye strain
5. The glassmorphism aesthetic is equally desirable in light mode
6. No additional color palette options are needed beyond light/dark/system

## Dependencies

- **Existing**: `next-themes` library for theme management
- **Existing**: `ThemeProvider` component wrapping the application
- **Existing**: Theme toggle UI with Light/Dark/System options
- **New**: CSS variable definitions for light mode in `globals.css`
