# Implementation Plan: Lumina – Deep Purple Royal Theme

**Feature Branch**: `004-lumina-theme-redesign`
**Created**: 2026-01-29
**Updated**: 2026-02-03
**Status**: Implemented (Final)
**Spec Reference**: [spec.md](./spec.md)

---

## Executive Summary

This plan describes how to apply the Lumina Deep Purple Royal theme to a Todo application. The implementation focuses on:
1. Defining theme-aware CSS custom properties
2. Ensuring text/button contrast in both light and dark modes
3. Applying glassmorphism effects for dark mode
4. Styling the logo with theme-inverted colors

**No changes to application structure, architecture, or features.**

---

## Design Architecture

### Theme Strategy
- **Approach**: Class-based theme switching with `next-themes`
- **Default**: Dark mode enabled by default
- **Persistence**: localStorage
- **Transition**: Smooth CSS transitions (no flash)

### Color Token Structure
```
globals.css
├── :root (Light theme tokens)
├── .dark (Dark theme tokens)
├── Glass effect classes
├── Gradient text classes (theme-aware)
├── Button classes (theme-aware)
└── Logo classes (theme-aware)

tailwind.config.ts
├── lumina.primary scale (#f3e5f5 → #311b92)
├── lumina.dark backgrounds
├── lumina.light backgrounds
├── lumina.accent colors
└── lumina.success/warning/danger semantics
```

---

## Implementation Phases

### PHASE 1: Define Color Tokens

**Objective**: Establish CSS custom properties for both themes.

**Light Theme Variables**:
- `--background`: Light lavender base (`261 46% 94%`)
- `--foreground`: Very dark purple (`270 100% 10%`)
- `--card`: White (`0 0% 100%`)
- `--primary`: Deep purple (`262 78% 34%`)
- `--muted-foreground`: Dark enough for contrast (`270 100% 20%`)

**Dark Theme Variables**:
- `--background`: Deep purple (`270 100% 10%`)
- `--foreground`: Bright lavender (`291 47% 95%`)
- `--card`: Dark surface (`270 100% 12%`)
- `--primary`: Bright purple (`291 47% 72%`)
- `--muted-foreground`: Light for readability (`291 47% 80%`)

**Acceptance**: Build passes, themes switch correctly.

---

### PHASE 2: Apply Contrast-Safe Text Colors

**Objective**: Ensure all text is visible against its background.

**Approach**:
1. Create CSS overrides for `.text-lumina-primary-*` classes
2. Light mode: Override to darker purples (`#5e35b1`, `#512da8`)
3. Dark mode: Override to brighter lavenders (`#ce93d8`, `#e1bee7`)
4. Muted text: Ensure sufficient contrast in both themes

**CSS Pattern**:
```css
/* Light mode - darker text */
.text-lumina-primary-400 {
  color: #5e35b1 !important;
}

/* Dark mode - brighter text */
.dark .text-lumina-primary-400 {
  color: #ce93d8 !important;
}
```

**Acceptance**: All text readable in both themes.

---

### PHASE 3: Apply Theme-Aware Gradient Text

**Objective**: Make GradientText component work in both themes.

**Approach**:
1. Replace Tailwind gradient classes with custom CSS classes
2. Create `.gradient-text-primary` with theme-aware gradients
3. Light mode: Dark purple gradient (`#4a148c → #7e57c2`)
4. Dark mode: Bright lavender gradient (`#e1bee7 → #f3e5f5`)

**Component Change**:
```typescript
// GradientText uses CSS class instead of Tailwind utilities
const gradientMap = {
  primary: "gradient-text-primary", // Theme-aware via CSS
};
```

**Acceptance**: "Lumina" and "Tasks" headings visible in both themes.

---

### PHASE 4: Apply Theme-Aware Button Styling

**Objective**: Ensure buttons are visible and clickable in both themes.

**Approach**:
1. Create `.btn-gradient` class for gradient buttons
2. Create `.btn-primary` class for solid buttons
3. Light mode: Dark purple background, white text
4. Dark mode: Bright lavender background, dark text

**Button Colors**:
| Theme | Background | Hover | Text |
|-------|------------|-------|------|
| Light | `#5e35b1` gradient | `#4a148c` | White |
| Dark | `#ce93d8` gradient | `#e1bee7` | `#1a0033` |

**Acceptance**: Buttons clearly visible, text readable in both themes.

---

### PHASE 5: Apply Logo Box Styling

**Objective**: Style the "L" logo with inverted colors per theme.

**Approach**:
1. Create `.logo-box` class for background
2. Create `.logo-text` class for letter
3. Light mode: Dark box (`#4a148c`), light text (`#f3e5f5`)
4. Dark mode: Light box (`#ede7f6`), dark text (`#4a148c`)

**CSS**:
```css
.logo-box { background-color: #4a148c; }
.logo-text { color: #f3e5f5; }

.dark .logo-box { background-color: #ede7f6; }
.dark .logo-text { color: #4a148c; }
```

**Acceptance**: Logo clearly visible in both themes, colors invert.

---

### PHASE 6: Theme Validation

**Objective**: Verify all styling works correctly.

**Validation Steps**:
1. Toggle between light and dark themes
2. Verify hero section text visibility
3. Verify tasks page heading visibility
4. Verify all buttons are visible and clickable
5. Verify logo background box appears
6. Verify no layout changes
7. Run `npm run build` - zero errors

---

## Implementation Constraints

### DO
- Use CSS custom properties for theme tokens
- Use `!important` for critical overrides when needed
- Use class-based theme-aware styles
- Test both themes for every change

### DO NOT
- Change application structure
- Change routing or layouts
- Modify business logic
- Change API integration
- Add or remove features
- Modify component hierarchy

---

## File Modifications

| File | Changes |
|------|---------|
| `globals.css` | Theme tokens, glass effects, gradient text, button styles, logo styles |
| `tailwind.config.ts` | Lumina color palette, animations, shadows |
| `gradient-text.tsx` | Use CSS class instead of Tailwind gradients |
| `animated-button.tsx` | Use `.btn-gradient` and `.btn-primary` classes |
| `sidebar.tsx` | Apply `.logo-box` and `.logo-text` classes |
| `landing-nav.tsx` | Apply `.logo-box` and `.logo-text` classes |

---

## Verification Checklist

After implementation:
- [ ] Light theme: Text is dark and readable
- [ ] Dark theme: Text is bright and readable
- [ ] Light theme: Buttons have dark background, white text
- [ ] Dark theme: Buttons have bright background, dark text
- [ ] Hero "Lumina" text visible in both themes
- [ ] "/tasks" heading visible in both themes
- [ ] Logo has themed background box
- [ ] No layout changes
- [ ] Build passes with zero errors
- [ ] Theme toggle works smoothly

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Text blending with background | CSS overrides with `!important` |
| Button invisibility | Theme-aware CSS classes |
| Glassmorphism browser support | Fallback backgrounds in `@supports` |
| Theme flash on load | next-themes with class strategy |
| **Theme drift during implementation** | **Mandatory spec validation phase (see below)** |
| **Color invention by agent** | **Strict "no color invention" rule in spec** |

---

## PHASE 7: Theme Compliance Validation (MANDATORY)

> **This phase is required after ANY implementation run that touches UI files.**

### Step 1: Color Audit
Compare every color in the codebase against spec.md:

```bash
# Extract all hex colors from globals.css
grep -oP '#[0-9a-fA-F]{6}' frontend/src/app/globals.css | sort -u

# Compare against spec.md palette
# All colors MUST exist in spec.md
```

### Step 2: Visual Verification
For EACH page (`/`, `/login`, `/signup`, `/tasks`):
1. Load in light theme → verify text, buttons, backgrounds match spec
2. Load in dark theme → verify text, buttons, backgrounds match spec
3. Toggle between themes → verify smooth transition, no flash

### Step 3: Contrast Verification
| Check | Light Theme | Dark Theme |
|-------|-------------|------------|
| Body text on background | `#1a0033` on `#ede7f6` | `#f3e5f5` on `#1a0033` |
| Button text on button | `#FFFFFF` on `#5e35b1` | `#1a0033` on `#ce93d8` |
| Muted text | `hsl(270 60% 25%)` on light | `hsl(291 47% 80%)` on dark |
| Gradient text | Dark gradient on light bg | Bright gradient on dark bg |

### Step 4: Build Verification
```bash
cd frontend && npm run build
# MUST complete with ZERO errors and ZERO warnings related to styling
```

### Step 5: Rejection Criteria
**If ANY of the following are true, the implementation is REJECTED:**
- A color not in spec.md is introduced
- Text is unreadable in either theme
- Button contrast fails in either theme
- Gradient text is invisible in either theme
- Logo colors don't invert between themes
- Build fails
- Layout changes occurred

---

## Theme Lock Enforcement

### For All Future Changes
1. **Read spec.md FIRST** before touching any UI file
2. **Match spec exactly** — do not approximate or "improve"
3. **Verify in BOTH themes** after every change
4. **Update spec if changing theme** — code and spec must always match
5. **Never introduce new colors** without explicit user request

### Spec is Canonical
The color values in `specs/004-lumina-theme-redesign/spec.md` are the **single source of truth**. When in doubt, spec wins over code. If code differs from spec, code is the bug.

---

## Dependencies

- Existing Tailwind CSS configuration
- next-themes already configured
- Component library (shadcn/ui) in place
- No new packages required

---

*This plan enforces recreation of the EXACT Lumina theme as documented in spec.md. Any deviation is a defect.*
