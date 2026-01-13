# Implementation Plan: Light Mode Theme

**Branch**: `009-light-mode-theme` | **Date**: 2025-01-13 | **Spec**: [spec.md](./spec.md)

## Summary

Add light mode theme support to the Chronos Todo application by extending the existing Deep Space dark mode CSS variable system. The implementation requires CSS-only changes - no component code modifications are needed because all colors use CSS variables. The existing `next-themes` library and ThemeProvider configuration already support the required functionality.

**Technical Approach**: Add a `.light` CSS selector with inverted brightness values (near-white backgrounds, dark text) while preserving brand accent colors (cyan, purple) unchanged for visual consistency.

## Technical Context

**Language/Version**: TypeScript (frontend), CSS (globals.css)
**Primary Dependencies**: next-themes ^0.4.6, Tailwind CSS v4, Next.js 16
**Storage**: localStorage (client-side only, via next-themes)
**Testing**: Visual testing, contrast ratio validation (WCAG AA)
**Target Platform**: Web browsers (modern browsers with CSS custom properties support)
**Project Type**: Web application (frontend + backend)
**Performance Goals**: Theme switch < 1 second, no layout shifts, no hydration flash
**Constraints**: No component code changes, must maintain brand identity, must meet WCAG AA
**Scale/Scope**: 1 file modified, 40+ CSS variables defined for light mode

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase Compliance
- ✅ **Phase II Scope**: This feature extends the existing Phase II frontend with UI theming
- ✅ **No Future Features**: No Phase III+ features (AI, Kubernetes) introduced
- ✅ **Spec-Driven Development**: Feature follows full SDD pipeline (spec → plan → tasks → implement)

### Technology Compliance
- ✅ **Core Stack**: Uses approved Phase II stack (Next.js 16+, Tailwind CSS v4)
- ✅ **No New Dependencies**: Uses existing `next-themes` installation
- ✅ **Single Repository**: Follows monorepo structure in `/specs/` and `/frontend/`

### Architecture Standards
- ✅ **Clean Architecture**: CSS-only change maintains separation of concerns
- ✅ **Stateless Services**: Theme state managed client-side via next-themes
- ✅ **Smallest Viable Diff**: Only 1 file modified (`globals.css`)

### Agent Behavior Rules
- ✅ **No Manual Coding**: Implementation will be done via `/sp.tasks` → `/sp.implement`
- ✅ **No Feature Invention**: Scope limited to light mode CSS variables
- ✅ **Task ID References**: Code will reference spec and plan sections

### Quality Principles
- ✅ **WCAG AA Compliance**: All light mode colors meet 4.5:1 contrast minimum
- ✅ **Brand Consistency**: Cyan/purple accents unchanged between themes
- ✅ **No Hardcoded Values**: All colors use CSS variables

**Result**: ✅ **ALL GATES PASSED** - No violations, no justifications needed

## Project Structure

### Documentation (this feature)

```text
specs/009-light-mode-theme/
├── spec.md              # Feature specification (requirements)
├── plan.md              # This file (architecture & implementation plan)
├── research.md          # Tailwind CSS v4 theming research findings
├── data-model.md        # Theme preference entity, CSS variable structure
├── quickstart.md        # Step-by-step implementation guide
├── contracts/           # CSS variable contracts
│   └── css-variables.md # Complete CSS variable specifications
└── checklists/          # Quality validation
    └── requirements.md  # Spec quality checklist (all PASS)
```

### Source Code (repository root)

```text
frontend/
├── app/
│   └── globals.css      # ONLY FILE TO MODIFY - add .light selector
├── components/
│   ├── layout/
│   │   └── theme-toggle.tsx  # NO CHANGES - already supports light/dark/system
│   └── ui/              # NO CHANGES - all use CSS variables
└── lib/
    └── stores/          # NO CHANGES - theme state via next-themes
```

**Structure Decision**: Web application structure with frontend/backend directories. This is a pure frontend theming feature with no backend or database changes required.

## Implementation Phases

### Phase 0: Research ✅ COMPLETE

**Output**: `research.md`

**Key Decisions**:
- Use Tailwind CSS v4 `@theme inline` with class-based selectors
- Continue using OKLCH color space for consistency
- Zero component code changes required (CSS variable architecture)
- Glassmorphism adapts to white semi-transparent backgrounds
- Glow effects reduce opacity for light mode visibility

### Phase 1: Design ✅ COMPLETE

**Outputs**:
- `data-model.md` - Theme preference entity, CSS variable structure
- `quickstart.md` - Step-by-step implementation guide
- `contracts/css-variables.md` - Complete CSS variable specifications

**Artifacts Created**:
- 40+ CSS variable specifications for light mode
- Glassmorphism utility contracts
- WCAG AA compliance verification

### Phase 2: Implementation (PENDING - requires /sp.tasks)

**File to Modify**: `frontend/app/globals.css`

**Changes Required**:
1. Add `.light` selector after `.dark` selector (lines ~168-220)
2. Add `.light` glassmorphism utilities in `@layer utilities`
3. Add `.light` glow effect utilities in `@layer utilities`
4. Add `.light body` background gradient in `@layer base`

**No Component Changes**: All components automatically adapt via CSS variables

### Phase 3: Testing (PENDING - requires /sp.tasks)

**Test Cases**:
1. Theme toggle functionality (Light/Dark/System)
2. Theme persistence across sessions
3. System theme detection and change response
4. Visual consistency across all components
5. WCAG AA contrast ratio validation
6. Glassmorphism effects visibility
7. No hydration flash on page load

## CSS Variable Mapping

The following table shows the complete mapping from dark to light mode:

| Category | Variable | Dark Mode | Light Mode | Unchanged? |
|----------|----------|-----------|------------|------------|
| Base | `--background` | Deep space black | Near-white | No |
| Base | `--foreground` | Light text | Dark text | No |
| Surface | `--card` | Dark glass | White glass | No |
| Primary | `--primary` | Cyan #00f5ff | Cyan #00f5ff | **Yes** |
| Secondary | `--secondary` | Purple #a855f7 | Purple #a855f7 | **Yes** |
| Destructive | `--destructive` | Red #ef4444 | Red #ef4444 | **Yes** |
| Border | `--border` | Light/low-opacity | Dark/low-opacity | No |

**Brand Colors Preserved**: Cyan and purple accents remain identical hex values across both themes for brand consistency.

## Dependencies

### Existing (No Installation Required)
- `next-themes@^0.4.6` - Theme management
- `tailwindcss` v4 - CSS framework
- `@theme` directive - CSS variable system

### New
- None - this feature extends existing infrastructure

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Hydration mismatch flash | `disableTransitionOnChange` in ThemeProvider |
| Browser compatibility | CSS custom properties supported in all modern browsers |
| Contrast issues | WCAG AA verified during design (all ratios 4.5:1+) |
| Component breakage | CSS variable architecture ensures automatic adaptation |
| Visual inconsistency | Comprehensive testing checklist defined |

## Success Criteria

From spec.md - all measurable outcomes:

- [ ] SC-001: Theme switching in under 1 second without page reload
- [ ] SC-002: WCAG AA contrast ratios (4.5:1) met for all interactive elements
- [ ] SC-003: Theme preference persists across sessions
- [ ] SC-004: Visual consistency across all component types
- [ ] SC-005: Brand accent colors identical in both themes
- [ ] SC-006: Glassmorphism effects visually coherent in light mode
- [ ] SC-007: No visual flash of incorrect theme on page load
- [ ] SC-008: All 35+ CSS variables have light mode values defined

## Next Steps

1. Run `/sp.tasks` to generate actionable implementation tasks
2. Review tasks.md and approve task breakdown
3. Run `/sp.implement` to execute the implementation
4. Verify all success criteria are met
5. Create PHR documenting the implementation

## References

- [Tailwind CSS v4 Documentation](https://tailwindcss.com/docs)
- [next-themes Documentation](https://github.com/pacocoursey/next-themes)
- [WCAG AA Contrast Guidelines](https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum)
- [OKLCH Color Space](https://oklch.com)
