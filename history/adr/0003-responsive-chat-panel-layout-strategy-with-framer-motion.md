# ADR-0003: Responsive Chat Panel Layout Strategy with Framer Motion

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-02-07
- **Feature:** 013-ai-chat-ui-redesign
- **Context:** Phase III AI Chatbot requires mobile-first responsive design for chat panel across all screen sizes (320px to 1920px+)

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Establishes responsive pattern for all floating panels/modals in the application
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - CSS media queries, separate components, CSS container queries evaluated
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects all responsive UI components, establishes breakpoint strategy
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

Use **Framer Motion with breakpoint-specific variants and AnimatePresence** for smooth, responsive chat panel layouts that adapt to three screen sizes.

**Components of this decision cluster:**
- **Breakpoint Strategy**: Mobile (<640px), Tablet (640px-1024px), Desktop (>1024px)
- **Framer Motion Variants**: Separate layout definitions per breakpoint (mobile/tablet/desktop)
- **AnimatePresence**: Smooth transitions between layouts during resize
- **Layout States**: Full-screen (mobile), centered modal (tablet), floating panel (desktop)
- **Custom Hook**: `useResponsive()` to track current breakpoint and trigger layout changes

**Implementation Pattern:**
```typescript
const variants = {
  mobile: {
    width: '100vw',
    height: '100vh',
    borderRadius: 0,
    position: 'fixed',
    inset: 0
  },
  tablet: {
    width: '600px',
    height: '80vh',
    x: '-50%',
    left: '50%',
    top: '10vh',
    borderRadius: '16px'
  },
  desktop: {
    width: '400px',
    height: '600px',
    bottom: 24,
    right: 24,
    borderRadius: '16px',
    position: 'fixed'
  }
}
```

## Consequences

### Positive

1. **Smooth Transitions**: Framer Motion's AnimatePresence prevents flicker during resize
2. **Mobile-First**: Progressive enhancement from mobile baseline to desktop
3. **Performance**: Hardware-accelerated animations via Framer Motion's GPU utilization
4. **Maintainability**: Variants defined once, reused across all responsive states
5. **Accessibility**: Semantic HTML preserved; screen readers announce layout changes
6. **Consistent Breakpoints**: Establishes standard breakpoints for other components

### Negative

1. **Bundle Size**: Framer Motion adds ~40KB gzipped (already in use, but confirms continued need)
2. **Animation Complexity**: Requires careful variant definitions to avoid layout bugs
3. **Resize Performance**: Rapid window resizing may trigger animation jank (debouncing needed)
4. **Testing Overhead**: Three layouts require testing at each breakpoint
5. **Edge Cases**: Device rotation and intermediate widths need careful handling
6. **Animation Overrides**: Custom timing functions may be needed for different breakpoints

## Alternatives Considered

### Alternative A: CSS Media Queries + Conditional Rendering
**Description:** Use standard CSS media queries with conditional component rendering for each breakpoint.

**Why Rejected:**
- **Flicker During Resize**: Component unmount/remount causes visual disruption
- **State Loss**: Conditional rendering resets component state on breakpoint change
- **More Code**: Separate components or complex ternaries for each layout
- **Loss of Position**: Floating panel loses position during resize transition

### Alternative B: Single Responsive Variant with CSS calc()
**Description:** Use one variant with CSS calc() and media queries within styles.

**Why Rejected:**
- **Complex Styles**: Nested ternaries and calc() expressions become unreadable
- **Difficult to Maintain**: Changes require editing complex style strings
- **Limited Flexibility**: Hard to animate position changes smoothly
- **Animation Jank**: CSS transitions may be less smooth than Framer Motion

### Alternative C: Separate Components per Breakpoint
**Description:** Create ChatPanelMobile, ChatPanelTablet, ChatPanelDesktop components.

**Why Rejected:**
- **Code Duplication**: Three components with similar logic increase maintenance burden
- **State Sharing Complex**: State must be lifted up or duplicated across components
- **Testing Overhead**: Each component needs full test coverage
- **Inconsistent UX**: Behavior differences between components likely

### Alternative D: CSS Container Queries
**Description:** Use CSS container queries for responsive behavior based on container size.

**Why Rejected:**
- **Browser Support**: Container queries have limited support in older browsers
- **Nested Container Requirements**: Requires wrapper elements for container context
- **Team Unfamiliarity**: Team has less experience with container queries vs media queries
- **Debugging Difficulty**: Container query debugging is less straightforward

### Alternative E: Responsive Grid with Tailwind Classes
**Description:** Use Tailwind's responsive prefixes (sm:, md:, lg:) with CSS Grid layout.

**Why Rejected:**
- **Positional Challenges**: Floating panel positioning difficult with grid-based approaches
- **Limited Animation**: CSS Grid animations are less smooth than Framer Motion
- **Fixed Structure**: Grid assumes 2D layout; chat panel needs fixed positioning
- **Breakpoint Limitation**: Tailwind's default breakpoints may not match our needs

## References

- Feature Spec: `/specs/013-ai-chat-ui-redesign/spec.md` (User Story 3: Mobile-First Responsive Design)
- Implementation Plan: `/specs/013-ai-chat-ui-redesign/plan.md` (Research: Framer Motion Responsive Layouts)
- Quickstart: `/specs/013-ai-chat-ui-redesign/quickstart.md` (Responsive Testing Procedures)
- Contracts: `/specs/013-ai-chat-ui-redesign/contracts/frontend.ts` (ChatPanel Props)
- Evaluator Evidence: `/history/prompts/013-ai-chat-ui-redesign/0003-ui-redesign-implementation-plan.plan.prompt.md`

## Implementation Checklist

- [ ] Create `lib/utils/responsive.ts` with `useResponsive()` hook
- [ ] Define mobile/tablet/desktop breakpoint constants (640px, 1024px)
- [ ] Implement Framer Motion variants for each breakpoint in chat-panel.tsx
- [ ] Add AnimatePresence wrapper for smooth transitions
- [ ] Test resize behavior across all breakpoints
- [ ] Test device rotation (mobile landscape ↔ portrait)
- [ ] Verify touch targets meet 44px minimum on mobile
- [ ] Add debouncing for rapid resize events
- [ ] Document breakpoint strategy in CLAUDE.md for future components
