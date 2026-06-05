---
name: accessibility-review
description: Audit a component or section for WCAG 2.1 AA accessibility issues and produce a structured fix plan. Use when the user asks for an accessibility review/audit of a component or section.
---

# accessibility-review

**Purpose:** Audit a component or section for WCAG 2.1 AA accessibility issues and produce a
structured fix plan.

**Invocation:** `/accessibility-review <component-or-section-name>`
Example: `/accessibility-review component-filters-sidebar`

> Converted from the orphaned `.cursor/prompts/fix-accessibility-issue.md` prompt, which referenced
> a non-existent `fetch_rules` tool. This skill replaces those tool calls with direct reads.

## Steps

1. Read the target `.liquid` file and its corresponding `.js` file (if any).
2. Check against these categories. Instead of any `fetch_rules` call, read the relevant
   `.cursor/rules/*.mdc` directly and read the component file to discover its existing ARIA
   patterns:
   - **ARIA roles:** the role must be on the element that directly contains the items; no role on
     wrapper divs above the semantic container.
   - **Keyboard navigation:** all interactive elements reachable by Tab; custom elements handle
     `keydown` for Enter/Space/Escape where appropriate.
   - **Focus management:** focus is not lost on open/close of drawers, modals, dropdowns; use
     `focus()` or the `inert` attribute.
   - **Screen reader text:** icon-only buttons must have an `aria-label`; use `aria-labelledby` to
     reference existing visible text rather than duplicating with `aria-label`.
   - **Contrast:** flag any hardcoded colors that may fail the 4.5:1 ratio; recommend
     `var(--color-*)` tokens instead.
   - **Motion:** verify CSS animations respect `prefers-reduced-motion`.
   - **Alpine.js components:** `x-data` components should have correct `aria-expanded`,
     `aria-controls`, and `aria-selected` attributes reflecting Alpine state.
3. Output a structured issue list: issue description, current code snippet, recommended fix, and
   the WCAG criterion.
4. Do **not** auto-apply fixes — the developer reviews and approves.

## Key differences from the original prompt

- Removes all `fetch_rules` tool calls.
- Removes references to `accordion-accessibility`, `carousel-accessibility`, etc. as separate fetch
  targets — the relevant patterns are read directly from the component file and the relevant
  `.mdc` rule.
- Adds Alpine.js-specific ARIA guidance (relevant given the many `x-data` declarations in this
  codebase).
