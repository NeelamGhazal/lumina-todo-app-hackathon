# Implementation Tasks: Lumina – Deep Purple Royal Theme

**Feature Branch**: `004-lumina-theme-redesign`
**Created**: 2026-01-29
**Updated**: 2026-02-03
**Status**: Implemented (Final)
**Spec Reference**: [spec.md](./spec.md)
**Plan Reference**: [plan.md](./plan.md)

---

## Task Execution Rules

1. Execute tasks in order
2. Test in BOTH themes after each task
3. Run `npm run build` at each checkpoint
4. Mark task complete only after verification
5. **Design-only tasks** - no logic or feature changes
6. **Colors MUST match spec.md exactly** - no approximations
7. **Do NOT invent new colors** - only use values from spec.md
8. **If UI deviates from spec theme, the task is FAILED and must be redone**

---

## Color Reference (Quick Lookup)

### Light Theme
| Element | Color |
|---------|-------|
| Background | `#ede7f6` gradient |
| Text | Dark purple (`#1a0033`, `#5e35b1`) |
| Buttons | `#5e35b1` bg, white text |
| Logo | `#4a148c` box, `#f3e5f5` text |

### Dark Theme
| Element | Color |
|---------|-------|
| Background | `#1a0033` gradient |
| Text | Bright lavender (`#f3e5f5`, `#ce93d8`) |
| Buttons | `#ce93d8` bg, `#1a0033` text |
| Logo | `#ede7f6` box, `#4a148c` text |

---

## PHASE 1: Define Color Tokens

### T001: Define Light Theme CSS Variables
**Type**: Design | **Priority**: P0

**File**: `frontend/src/app/globals.css`

**Variables to define**:
```css
:root {
  --background: 261 46% 94%;
  --foreground: 270 100% 10%;
  --card: 0 0% 100%;
  --card-foreground: 270 100% 10%;
  --primary: 262 78% 34%;
  --primary-foreground: 0 0% 100%;
  --muted: 261 46% 84%;
  --muted-foreground: 270 100% 20%;
}
```

**Acceptance**:
- [ ] Light theme background is lavender (#ede7f6)
- [ ] Light theme text is dark purple

---

### T002: Define Dark Theme CSS Variables
**Type**: Design | **Priority**: P0

**File**: `frontend/src/app/globals.css`

**Variables to define**:
```css
.dark {
  --background: 270 100% 10%;
  --foreground: 291 47% 95%;
  --card: 270 100% 12%;
  --card-foreground: 291 47% 95%;
  --primary: 291 47% 72%;
  --primary-foreground: 270 100% 10%;
  --muted: 270 100% 18%;
  --muted-foreground: 291 47% 80%;
}
```

**Acceptance**:
- [ ] Dark theme background is deep purple (#1a0033)
- [ ] Dark theme text is bright lavender (#f3e5f5)

---

### T003: Define Background Gradients
**Type**: Design | **Priority**: P0

**File**: `frontend/src/app/globals.css`

**CSS**:
```css
body {
  background: linear-gradient(135deg, #ede7f6 0%, #d1c4e9 100%);
}

.dark body {
  background: linear-gradient(135deg, #1a0033 0%, #2e003e 50%, #120024 100%);
}
```

**Acceptance**:
- [ ] Light mode has lavender gradient
- [ ] Dark mode has deep purple gradient

---

### CHECKPOINT 1: Color Foundation
```bash
npm run build
```
- [ ] Build passes
- [ ] Themes switch correctly
- [ ] Gradients visible

---

## PHASE 2: Apply Contrast-Safe Text Colors

### T004: Add Light Mode Text Overrides
**Type**: Design | **Priority**: P0

**File**: `frontend/src/app/globals.css`

**CSS**:
```css
.text-lumina-primary-300 { color: #7e57c2 !important; }
.text-lumina-primary-400 { color: #5e35b1 !important; }
.text-lumina-primary-500 { color: #512da8 !important; }
.text-muted-foreground { color: hsl(270 60% 25%) !important; }
```

**Acceptance**:
- [ ] Purple text is dark on light backgrounds
- [ ] Muted text is readable

---

### T005: Add Dark Mode Text Overrides
**Type**: Design | **Priority**: P0

**File**: `frontend/src/app/globals.css`

**CSS**:
```css
.dark .text-lumina-primary-300 { color: #e1bee7 !important; }
.dark .text-lumina-primary-400 { color: #ce93d8 !important; }
.dark .text-lumina-primary-500 { color: #b39ddb !important; }
.dark .text-muted-foreground { color: hsl(291 47% 80%) !important; }
```

**Acceptance**:
- [ ] Purple text is bright on dark backgrounds
- [ ] Muted text is readable

---

### CHECKPOINT 2: Text Visibility
- [ ] All text readable in light theme
- [ ] All text readable in dark theme

---

## PHASE 3: Apply Gradient Text Styling

### T006: Create Gradient Text CSS Classes
**Type**: Design | **Priority**: P0

**File**: `frontend/src/app/globals.css`

**CSS**:
```css
/* Light mode - dark gradient */
.gradient-text-primary {
  background-image: linear-gradient(to right, #4a148c, #5e35b1, #7e57c2) !important;
}

/* Dark mode - bright gradient */
.dark .gradient-text-primary {
  background-image: linear-gradient(to right, #e1bee7, #ce93d8, #f3e5f5) !important;
}
```

**Acceptance**:
- [ ] "Lumina" headline visible in light theme (dark gradient)
- [ ] "Lumina" headline visible in dark theme (bright gradient)

---

### T007: Update GradientText Component
**Type**: Design | **Priority**: P0

**File**: `frontend/src/components/ui/gradient-text.tsx`

**Change**:
```typescript
const gradientMap: Record<GradientVariant, string> = {
  primary: "gradient-text-primary", // CSS class instead of Tailwind
  accent: "gradient-text-accent",
  // ...
};
```

**Acceptance**:
- [ ] GradientText uses CSS classes
- [ ] "Tasks" heading visible in both themes

---

### CHECKPOINT 3: Gradient Text
- [ ] Hero "Lumina" text visible in both themes
- [ ] "/tasks" heading visible in both themes

---

## PHASE 4: Apply Button Styling

### T008: Create Gradient Button CSS Class
**Type**: Design | **Priority**: P0

**File**: `frontend/src/app/globals.css`

**CSS**:
```css
/* Light mode */
.btn-gradient {
  background: linear-gradient(135deg, #5e35b1 0%, #4a148c 100%) !important;
  box-shadow: 0 4px 14px rgba(94, 53, 177, 0.35);
}
.btn-gradient:hover {
  background: linear-gradient(135deg, #4a148c 0%, #311b92 100%) !important;
}

/* Dark mode */
.dark .btn-gradient {
  background: linear-gradient(135deg, #ce93d8 0%, #e1bee7 100%) !important;
  color: #1a0033 !important;
}
.dark .btn-gradient:hover {
  background: linear-gradient(135deg, #e1bee7 0%, #f3e5f5 100%) !important;
}
```

**Acceptance**:
- [ ] Gradient buttons dark purple in light theme
- [ ] Gradient buttons bright lavender in dark theme
- [ ] Text readable on both

---

### T009: Create Primary Button CSS Class
**Type**: Design | **Priority**: P0

**File**: `frontend/src/app/globals.css`

**CSS**:
```css
.btn-primary { background-color: #5e35b1 !important; }
.btn-primary:hover { background-color: #4a148c !important; }

.dark .btn-primary {
  background-color: #ce93d8 !important;
  color: #1a0033 !important;
}
.dark .btn-primary:hover { background-color: #e1bee7 !important; }
```

**Acceptance**:
- [ ] Primary buttons visible in both themes
- [ ] Hover states work

---

### T010: Update AnimatedButton Component
**Type**: Design | **Priority**: P0

**File**: `frontend/src/components/ui/animated-button.tsx`

**Change**:
```typescript
variant: {
  default: ["btn-primary", "text-white", "shadow-md hover:shadow-lg"],
  gradient: ["btn-gradient", "text-white font-semibold", "shadow-lg", "hover:shadow-xl"],
  // ...
}
```

**Acceptance**:
- [ ] AnimatedButton uses CSS classes
- [ ] All buttons visible and clickable

---

### CHECKPOINT 4: Button Visibility
```bash
npm run build
```
- [ ] Build passes
- [ ] Buttons visible in light theme (dark purple)
- [ ] Buttons visible in dark theme (bright lavender)
- [ ] Button text readable

---

## PHASE 5: Apply Logo Styling

### T011: Create Logo CSS Classes
**Type**: Design | **Priority**: P0

**File**: `frontend/src/app/globals.css`

**CSS**:
```css
/* Light mode - dark box, light text */
.logo-box { background-color: #4a148c; }
.logo-text { color: #f3e5f5; }

/* Dark mode - light box, dark text */
.dark .logo-box { background-color: #ede7f6; }
.dark .logo-text { color: #4a148c; }
```

**Acceptance**:
- [ ] Logo has background box
- [ ] Colors invert between themes

---

### T012: Update Sidebar Logo
**Type**: Design | **Priority**: P0

**File**: `frontend/src/components/layout/sidebar.tsx`

**Change**:
```tsx
<div className="w-8 h-8 rounded-lg logo-box flex items-center justify-center">
  <span className="font-bold text-lg logo-text">L</span>
</div>
```

**Acceptance**:
- [ ] Sidebar logo styled correctly
- [ ] Light theme: dark box, light "L"
- [ ] Dark theme: light box, dark "L"

---

### T013: Update Landing Nav Logo
**Type**: Design | **Priority**: P0

**File**: `frontend/src/components/landing/landing-nav.tsx`

**Change**:
```tsx
<div className="w-8 h-8 rounded-lg logo-box flex items-center justify-center">
  <span className="font-bold text-lg logo-text">L</span>
</div>
```

**Acceptance**:
- [ ] Landing nav logo styled correctly
- [ ] Matches sidebar logo behavior

---

### CHECKPOINT 5: Logo Styling
- [ ] Logo visible in light theme
- [ ] Logo visible in dark theme
- [ ] Colors properly inverted

---

## PHASE 6: Final Validation

### T014: Validate Hero Section Visibility
**Type**: Verification | **Priority**: P0

**Steps**:
1. Navigate to landing page (/)
2. Toggle to light theme
3. Verify "Lumina" text is dark purple
4. Verify badge text is readable
5. Toggle to dark theme
6. Verify "Lumina" text is bright lavender
7. Verify badge text is readable

**Acceptance**:
- [ ] Hero text visible in light theme
- [ ] Hero text visible in dark theme

---

### T015: Validate Buttons in Both Themes
**Type**: Verification | **Priority**: P0

**Steps**:
1. Check "Get Started Free" button on landing
2. Check "Sign In" button on landing
3. Check "Add Task" button on /tasks
4. Toggle between themes
5. Verify all buttons visible and clickable

**Acceptance**:
- [ ] All buttons visible in light theme
- [ ] All buttons visible in dark theme
- [ ] Button text readable

---

### T016: Validate Logo Background Box
**Type**: Verification | **Priority**: P0

**Steps**:
1. Check logo in landing nav
2. Check logo in sidebar
3. Toggle between themes
4. Verify box colors invert

**Acceptance**:
- [ ] Logo box visible in light theme (dark purple)
- [ ] Logo box visible in dark theme (light lavender)
- [ ] "L" text properly contrasts with box

---

### T017: Run Production Build
**Type**: Verification | **Priority**: P0

**Command**:
```bash
cd frontend && npm run build
```

**Acceptance**:
- [ ] Build completes with zero errors
- [ ] All routes generated successfully
- [ ] No TypeScript errors

---

### CHECKPOINT 6: Final Verification
- [ ] All text visible in both themes
- [ ] All buttons visible in both themes
- [ ] Logo styled correctly in both themes
- [ ] Build passes
- [ ] No layout changes from original

---

## Summary

| Phase | Tasks | Focus |
|-------|-------|-------|
| Phase 1 | T001-T003 | Color tokens & gradients |
| Phase 2 | T004-T005 | Text visibility overrides |
| Phase 3 | T006-T007 | Gradient text component |
| Phase 4 | T008-T010 | Button styling |
| Phase 5 | T011-T013 | Logo box styling |
| Phase 6 | T014-T017 | Validation |

**Total**: 17 design-focused tasks

---

## Constraints Reminder

**ONLY modify**:
- CSS/styling
- Color values
- Class names

**DO NOT modify**:
- Application structure
- Routing
- Features
- Business logic
- API integration

---

## PHASE 7: Theme Compliance Audit (MANDATORY)

### T018: Verify All Colors Match Spec
**Type**: Verification | **Priority**: P0

**Steps**:
1. Open `specs/004-lumina-theme-redesign/spec.md`
2. Compare EVERY color in `globals.css` against spec tables
3. Compare EVERY color in `tailwind.config.ts` against spec tables
4. Flag any color that does not appear in spec

**Acceptance**:
- [ ] Every hex color in globals.css exists in spec.md
- [ ] Every hex color in tailwind.config.ts exists in spec.md
- [ ] No undocumented colors introduced
- [ ] **If ANY mismatch is found: STOP and fix before proceeding**

---

### T019: Verify Light Theme Visual Compliance
**Type**: Verification | **Priority**: P0

**Steps**:
1. Load each page (`/`, `/login`, `/signup`, `/tasks`) in light theme
2. Verify against spec.md:
   - Page background: `#ede7f6` gradient
   - Body text: `#1a0033` (very dark purple)
   - Buttons: `#5e35b1` bg with `#FFFFFF` text
   - Gradient text: `#4a148c → #5e35b1 → #7e57c2`
   - Logo: `#4a148c` box, `#f3e5f5` text
   - Muted text: `hsl(270 60% 25%)`

**Acceptance**:
- [ ] Background is lavender gradient, NOT white, NOT grey
- [ ] All text is dark purple, NOT light, NOT invisible
- [ ] Buttons are dark purple with white text, NOT faded
- [ ] Gradient headlines are dark and readable
- [ ] Logo box is dark purple with light text

---

### T020: Verify Dark Theme Visual Compliance
**Type**: Verification | **Priority**: P0

**Steps**:
1. Load each page in dark theme
2. Verify against spec.md:
   - Page background: `#1a0033` gradient
   - Body text: `#f3e5f5` (bright lavender)
   - Buttons: `#ce93d8` bg with `#1a0033` text
   - Gradient text: `#e1bee7 → #ce93d8 → #f3e5f5`
   - Logo: `#ede7f6` box, `#4a148c` text
   - Muted text: `hsl(291 47% 80%)`

**Acceptance**:
- [ ] Background is deep purple gradient, NOT black, NOT grey
- [ ] All text is bright lavender, NOT dark, NOT invisible
- [ ] Buttons are bright lavender with dark text, NOT faded
- [ ] Gradient headlines are bright and readable
- [ ] Logo box is light with dark text

---

### T021: Verify Modal & Dialog Compliance
**Type**: Verification | **Priority**: P0

**Steps**:
1. Open Add Task modal in both themes
2. Open Delete confirmation dialog in both themes
3. Open Calendar popover in both themes
4. Open Select dropdowns in both themes

**Acceptance**:
- [ ] Add Task modal: light `#d1c3e9` bg / dark `#4e2f83` bg
- [ ] Delete dialog: light `#ffffff` bg / dark `#2e1a47` bg
- [ ] Calendar: light `#ffffff` bg / dark `#1e1e2e` bg
- [ ] All text readable in both themes
- [ ] Input fields properly styled in both themes

---

### T022: Verify Priority Badges Compliance
**Type**: Verification | **Priority**: P0

**Steps**:
1. View tasks with high, medium, and low priority in both themes

**Acceptance**:
- [ ] Light: High=`#fee2e2`/`#991b1b`, Medium=`#fef3c7`/`#92400e`, Low=`#dcfce7`/`#166534`
- [ ] Dark: High=`rgba(127,29,29,0.3)`/`#f87171`, Medium=`rgba(120,53,15,0.3)`/`#fbbf24`, Low=`rgba(20,83,45,0.3)`/`#4ade80`

---

### CHECKPOINT 7: Theme Compliance
- [ ] All colors match spec.md exactly
- [ ] Light theme fully compliant
- [ ] Dark theme fully compliant
- [ ] Modals and dialogs compliant
- [ ] Priority badges compliant
- [ ] Build passes with zero errors
- [ ] **No undocumented colors exist in the codebase**

---

## Rejection Criteria (BINDING)

A task is **FAILED** and must be redone if ANY of the following are true:

| # | Rejection Condition |
|---|---------------------|
| R1 | A color not documented in spec.md is introduced |
| R2 | Text is unreadable (fails WCAG AA) in either theme |
| R3 | Button contrast fails in either theme |
| R4 | Gradient text is invisible or blends with background |
| R5 | Logo colors don't properly invert between themes |
| R6 | Build fails with errors |
| R7 | Layout or structure is changed |
| R8 | Light/dark theme behavior is altered |
| R9 | Glassmorphism effects are removed or degraded |
| R10 | Theme toggle produces flash or visual glitch |

**Any violation = task rejected. Fix and re-verify.**

---

## Updated Summary

| Phase | Tasks | Focus |
|-------|-------|-------|
| Phase 1 | T001-T003 | Color tokens & gradients |
| Phase 2 | T004-T005 | Text visibility overrides |
| Phase 3 | T006-T007 | Gradient text component |
| Phase 4 | T008-T010 | Button styling |
| Phase 5 | T011-T013 | Logo box styling |
| Phase 6 | T014-T017 | Validation |
| **Phase 7** | **T018-T022** | **Theme compliance audit (MANDATORY)** |

**Total**: 22 tasks (17 design + 5 compliance verification)

---

*These tasks enforce EXACT recreation of the Lumina theme. spec.md is the canonical reference. Any deviation is a defect.*
