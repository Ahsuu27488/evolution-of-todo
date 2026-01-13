# CSS Variable Contract: Light Mode Theme

**Feature**: 009-light-mode-theme
**Version**: 1.0
**Date**: 2025-01-13

## Contract Overview

This contract defines the complete set of CSS variables for light mode theme. All variables defined here must have corresponding values in the `.light` selector in `frontend/app/globals.css`.

## Variable Specifications

### Base Colors

| Variable Name | Light Mode Value | Dark Mode Value | Type | Description |
|----------------|------------------|-----------------|------|-------------|
| `--background` | `248 248 250` | `10 10 15` | RGB (r g b) | Page background color |
| `--foreground` | `30 30 35` | `245 245 250` | RGB (r g b) | Primary text color |

### Surface Colors

| Variable Name | Light Mode Value | Dark Mode Value | Type | Description |
|----------------|------------------|-----------------|------|-------------|
| `--card` | `255 255 255 / 0.8` | `20 20 30 / 0.7` | RGB with alpha | Card background |
| `--card-foreground` | `30 30 35` | `245 245 250` | RGB (r g b) | Card text color |
| `--popover` | `255 255 255 / 0.9` | `20 20 30 / 0.8` | RGB with alpha | Popover background |
| `--popover-foreground` | `30 30 35` | `245 245 250` | RGB (r g b) | Popover text color |
| `--muted` | `240 240 245 / 0.6` | `30 30 45 / 0.5` | RGB with alpha | Muted background |
| `--muted-foreground` | `120 120 140` | `150 150 170` | RGB (r g b) | Muted text color |

### Accent Colors (Brand - UNCHANGED)

| Variable Name | Value | Type | Description |
|----------------|-------|------|-------------|
| `--primary` | `0 245 255` | RGB (r g b) | Primary accent (cyan) |
| `--primary-foreground` | `248 248 250` | RGB (r g b) | Text on primary |
| `--secondary` | `168 85 247` | RGB (r g b) | Secondary accent (purple) |
| `--secondary-foreground` | `248 248 250` | RGB (r g b) | Text on secondary |
| `--accent` | `168 85 247` | RGB (r g b) | General accent |
| `--accent-foreground` | `248 248 250` | RGB (r g b) | Text on accent |

### Status Colors

| Variable Name | Value | Type | Description |
|----------------|-------|------|-------------|
| `--destructive` | `239 68 68` | RGB (r g b) | Error/danger (red) |
| `--destructive-foreground` | `248 248 250` | RGB (r g b) | Text on destructive |

### Interactive States

| Variable Name | Light Mode Value | Dark Mode Value | Type | Description |
|----------------|------------------|-----------------|------|-------------|
| `--border` | `0 0 0 / 0.1` | `255 255 255 / 0.1` | RGB with alpha | Border color |
| `--input` | `0 0 0 / 0.08` | `255 255 255 / 0.08` | RGB with alpha | Input border |
| `--ring` | `0 245 255` | `0 245 255` | RGB (r g b) | Focus ring (cyan) |

### Chart Colors (UNCHANGED)

| Variable Name | Value | Color Name |
|----------------|-------|------------|
| `--chart-1` | `0 245 255` | Cyan |
| `--chart-2` | `168 85 247` | Purple |
| `--chart-3` | `34 197 94` | Green |
| `--chart-4` | `239 68 68` | Red |
| `--chart-5` | `251 191 36` | Amber |

### Sidebar Colors

| Variable Name | Light Mode Value | Dark Mode Value | Type | Description |
|----------------|------------------|-----------------|------|-------------|
| `--sidebar` | `245 245 250` | `15 15 25` | RGB (r g b) | Sidebar background |
| `--sidebar-foreground` | `30 30 35` | `245 245 250` | RGB (r g b) | Sidebar text |
| `--sidebar-primary` | `0 245 255` | `0 245 255` | RGB (r g b) | Sidebar primary |
| `--sidebar-primary-foreground` | `248 248 250` | `10 10 15` | RGB (r g b) | Text on sidebar primary |
| `--sidebar-accent` | `168 85 247` | `168 85 247` | RGB (r g b) | Sidebar accent |
| `--sidebar-accent-foreground` | `248 248 250` | `245 245 250` | RGB (r g b) | Text on sidebar accent |
| `--sidebar-border` | `0 0 0 / 0.1` | `255 255 255 / 0.1` | RGB with alpha | Sidebar border |
| `--sidebar-ring` | `0 245 255` | `0 245 255` | RGB (r g b) | Sidebar focus ring |

## Utility Class Contracts

### Glassmorphism Utilities

| Class | Light Mode CSS | Dark Mode CSS |
|-------|----------------|---------------|
| `.glass` | `rgba(255, 255, 255, 0.7)` | `rgba(20, 20, 30, 0.7)` |
| `.glass-strong` | `rgba(255, 255, 255, 0.9)` | `rgba(20, 20, 30, 0.8)` |
| `.glass-modal` | `rgba(255, 255, 255, 0.95)` | `rgba(20, 20, 30, 0.85)` |

### Glow Effect Utilities

| Class | Light Mode CSS | Dark Mode CSS |
|-------|----------------|---------------|
| `.glow-cyan` | `rgba(0, 245, 255, 0.15)` | `rgba(0, 245, 255, 0.3)` |
| `.glow-purple` | `rgba(168, 85, 247, 0.15)` | `rgba(168, 85, 247, 0.3)` |

### Background Gradient

| Selector | Light Mode | Dark Mode |
|----------|------------|-----------|
| `body` | Cyan orb: `0.015`, Purple orb: `0.015` | Cyan orb: `0.03`, Purple orb: `0.03` |

## Implementation Requirements

1. All variables MUST be defined within `.light` selector
2. All RGB values MUST use space-separated format for `rgb(var(--name))` syntax
3. All opacity values MUST use `/` separator
4. Brand accent colors (primary, secondary) MUST remain unchanged between themes
5. All variables MUST have corresponding values (no undefined variables)

## Validation Criteria

- [ ] All 40+ CSS variables have `.light` mode values
- [ ] Contrast ratios meet WCAG AA (4.5:1 minimum)
- [ ] Brand colors identical across themes (hex comparison)
- [ ] No CSS parsing errors in browser console
- [ ] All components render correctly in both themes
