---
id: 002
title: Phase II Frontend Clarifications
stage: spec
date: 2026-01-27
surface: agent
model: claude-opus-4-5-20251101
feature: 002-phase2-todo-frontend
branch: 002-phase2-todo-frontend
user: neela
command: /sp.clarify
labels: ["clarification", "frontend", "ux", "phase2"]
links:
  spec: specs/002-phase2-todo-frontend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-phase2-todo-frontend/spec.md
tests:
  - Clarification coverage validation (5/5 questions resolved)
---

## Prompt

```
/sp.clarify

My Phase II Frontend specification is at specs/phase2-frontend/spec.md

Please analyze it for gaps and ambiguities:

1. AMBIGUOUS TERMS
   - "World-class design" - What specific design patterns? (Glassmorphism? Neumorphism? Both?)
   - "Smooth animations" - What exact FPS target? (60fps confirmed?)
   - "Beautiful modal" - Drawer from right? Center modal? Bottom sheet on mobile?
   - "Optimistic updates" - How to handle if backend fails? Rollback UI? Show error?
   - "Card design" - What exact card style? (Bordered? Shadowed? Glassmorphic?)
   - "Skeleton screens" - Pulse animation? Shimmer? Wave?

2. MISSING ASSUMPTIONS
   - Page transitions: Route change animations? (Fade? Slide? None?)
   - Form validation: Show errors on blur or on submit?
   - Toast notifications: Where positioned? (Top-right? Top-center? Bottom?)
   - Mobile gestures: Swipe to delete confirmed? Pull to refresh?
   - Error retry: Automatic or manual retry button?
   - Empty states: What illustrations to use? (Custom SVG? Lucide icons?)
   - Loading duration: Minimum spinner time to avoid flash? (300ms minimum?)
   - Image assets: Where to get illustrations? (undraw.co? Custom?)

3. INCOMPLETE REQUIREMENTS
   - Better Auth setup: Which auth provider? (Email only? Add Google OAuth?)
   - JWT refresh: When to refresh token? (On 401? Before expiry?)
   - Filter persistence: Should filters persist on page refresh? (localStorage?)
   - Sort options: Should tasks be sortable? (By date? Priority? Manual drag-drop?)
   - Task limits: Max tasks per user? Pagination needed?
   - Search: Is search feature needed in Phase II? (Spec says Phase V?)
   - Multi-select: Can user select multiple tasks for bulk delete?
   - Keyboard shortcuts: Should we add? (n for new, / for search, etc.)

4. SCOPE CONFLICTS
   - Spec says "Basic features only" but mentions filters, tags, categories (are these Basic or Intermediate?)
   - Spec mentions "Recurring tasks UI" in NOT building but also mentions due dates/times (are reminders needed?)
   - "Real-time updates" mentioned in success criteria but "Real-time collaboration" in NOT building - clarify?
   - Dark mode: Should it respect system preference or always use toggle?
   - Mobile responsive: Should there be a separate mobile-optimized layout or just responsive?

5. TECHNICAL CLARIFICATIONS
   [Additional technical questions listed...]

6. DESIGN SYSTEM GAPS
   [Additional design questions listed...]

7. DEPLOYMENT SPECIFICS
   [Additional deployment questions listed...]

List gaps in priority order:
- CRITICAL (must resolve before planning): [list]
- IMPORTANT (affects plan quality): [list]
- NICE-TO-HAVE (can decide during implementation): [list]
```

## Response snapshot

Performed structured ambiguity scan and resolved 5 high-impact clarifications:

**Questions Asked & Answered:**

1. **Optimistic Update Failure Handling**
   - Q: When an optimistic update fails, what should happen?
   - A: Revert UI silently + show error toast with retry button

2. **Modal Type for Task Forms**
   - Q: What type of modal should be used for task forms?
   - A: Center modal on desktop, bottom sheet on mobile (adaptive)

3. **Toast Notification Position**
   - Q: Where should toast notifications appear?
   - A: Top-center (high visibility, modern pattern)

4. **Form Validation Timing**
   - Q: When should form validation errors be displayed?
   - A: On blur + on submit attempt (balanced approach)

5. **Dark Mode System Preference**
   - Q: How should dark mode interact with system preferences?
   - A: Respect system preference initially, allow manual override that persists

**Sections Updated:**
- Edge Cases (optimistic failure handling)
- FR-020 (modal type clarification)
- FR-021 (validation timing)
- FR-061 (dark mode system preference)
- FR-062 (toast position)
- New Clarifications section added

## Outcome

- Impact: Resolved 5 critical UX ambiguities that would have caused implementation confusion
- Tests: All clarifications validated and integrated into spec
- Files: 1 file updated (spec.md with Clarifications section)
- Next prompts: `/sp.plan` - Proceed to implementation planning
- Reflection: User's detailed gap analysis helped prioritize the most impactful questions

## Evaluation notes (flywheel)

- Failure modes observed: None - all 5 questions answered clearly with recommended options
- Graders run and results (PASS/FAIL): Clarification integration PASS (5/5 integrated)
- Prompt variant (if applicable): User-provided gap analysis enabled targeted questioning
- Next experiment (smallest change to try): N/A - proceed to planning phase
