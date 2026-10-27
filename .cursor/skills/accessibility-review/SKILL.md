---
name: accessibility-review
description: Audit a section, snippet or page for WCAG 2.1 AA issues against the theme's accessibility standard and produce a structured fix plan with the criterion, the mechanism and one fix per finding. Use when asked for an accessibility review or audit, before a PR that adds an overlay, a form, a carousel or a custom control, and when GitBot or QA reports an accessibility finding to work through.
argument-hint: <section-or-snippet-name | page URL>
---

# accessibility-review

The one review that blocks a merge (`code-review-policy.md`); the standard is
`.claude/rules/accessibility.md`, read first. Untranslated text is
localization, unescaped output is security — neither is a finding here.

**Invocation:** `/accessibility-review <section-or-snippet-name | page URL>`

## Step 1 — Gather

1. Read the target `.liquid` file, its `assets/*.css` and `assets/*.js`, and
   any snippet it renders that carries a control.
2. Run the mechanical pass (CSS `order`, `nowrap` on controls, `outline:
   none`, no reduced-motion override, a click handler on a `div`, no `alt`):

   ```bash
   python3 .claude/scripts/check-conventions.py --files <the files>
   ```

   Its findings are the floor, not the review.
3. If the theme is running (`/run-theme`), walk the page with the keyboard:
   Tab through every control, open and close every overlay, operate every
   carousel and accordion; record what focus did. Otherwise say so.

## Step 2 — Check, in the rule's order

Work through sections 1–11 of `accessibility.md` and record only what fails:

| Area | What fails most in themes |
|---|---|
| Real controls | a `div` or `span` with a click handler; a link with `href="#"` that acts as a button |
| Accessible names | icon-only buttons with no `aria-label`; `aria-label` duplicating visible text instead of `aria-labelledby` |
| Forms | inputs with a placeholder and no `<label>`; error text not associated with its field |
| Keyboard, focus, order | focus lost when a drawer or modal opens or closes; no focus return to the trigger; Escape not closing; visual order moved with CSS `order` |
| Images, icons, media | decorative SVGs announced; informative images with empty `alt`; autoplaying video with no pause |
| Structure | heading levels skipped per section; lists built from `div`s; landmarks missing or duplicated |
| Colour, contrast, reflow | text under 4.5:1 against a scheme background; content cut off at 320px or 200% zoom |
| ARIA | `aria-expanded` not toggled by Alpine state; roles on wrapper elements instead of the semantic container |
| Motion and carousels | transitions ignoring `prefers-reduced-motion`; a carousel with no pause, no keyboard, no slide count |
| Overlays | a `<dialog>` without `aria-modal`; live region inside a region that re-renders |
| Shopify specifics | `form` attributes on product forms; `aria-live` on the whole cart drawer instead of a status node |

For Alpine-driven state, confirm the ARIA attributes are bound to the same
`x-data` state the UI uses, not set once in markup.

## Step 3 — Report

Findings only, at most eight, ordered by what a shopper cannot do first. Each:

- **File and line** (`path:line`)
- **Criterion** — the WCAG 2.1 success criterion number and name
- **What happens** — one sentence from the user's side: "focus stays on the
  page behind the drawer; Tab reaches nothing inside it"
- **Fix** — one, minimal, naming the house pattern (`accessibility.md` §10)

Then **what was not checked** — contrast or screen-reader behaviour without a
running theme — stated, never implied passed. Do **not** apply fixes; the
developer approves.

## Step 4 — Record what the rule should have caught

A finding a rule or the gate should have prevented is `/record-incident`
with `should_have_caught` at `accessibility.md` or `check-conventions.py`.
Three of the same finding across sections is a standards gap, not three findings.
