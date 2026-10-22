---
name: accessibility-review
description: Audit a section, snippet or page for WCAG 2.1 AA issues against the theme's accessibility standard and produce a structured fix plan with the criterion, the mechanism and one fix per finding. Use when asked for an accessibility review or audit, before a PR that adds an overlay, a form, a carousel or a custom control, and when GitBot or QA reports an accessibility finding to work through.
argument-hint: <section-or-snippet-name | page URL>
---

# accessibility-review

Accessibility is the one review that blocks a merge (`code-review-policy.md`).
This skill produces the findings a lead can act on: each names the control,
the WCAG criterion, what a keyboard or screen-reader user actually experiences,
and one fix.

**Invocation:** `/accessibility-review <section-or-snippet-name | page URL>`
Example: `/accessibility-review component-filters-sidebar`

The standard is `.claude/rules/accessibility.md`. Read it first; this skill is
the procedure, that file is the bar. Untranslated text is localization and
unescaped output is security — neither is an accessibility finding.

## Step 1 — Gather

1. Read the target `.liquid` file, its `assets/*.css` and `assets/*.js`, and
   any snippet it renders that carries a control (buttons, links, inputs,
   dialogs, menus, sliders).
2. Run the mechanical pass. The gate already greps for the six patterns that
   recur most — CSS `order`, `white-space: nowrap` on controls,
   `outline: none` on focus, motion with no reduced-motion override, a click
   handler on a `div`, an `<img>` with no `alt`:

   ```bash
   python3 .claude/scripts/check-conventions.py --files <the files>
   ```

   Its findings are the floor, not the review.
3. If the theme is running (`/run-theme`), open the page in the browser tools
   and walk it with the keyboard: Tab through every control, open and close
   every overlay, operate every carousel and accordion. Record what focus did,
   not what the code says it should do. Without a running theme, say so in
   the report and judge from the code only.

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

For Alpine-driven state, read the `x-data` and confirm the ARIA attributes
(`aria-expanded`, `aria-controls`, `aria-selected`, `aria-hidden`) are bound to
the same state the UI uses, not set once in markup.

## Step 3 — Report

Findings only, at most eight, ordered by consequence (what a shopper cannot do
first). Each one:

- **File and line** (`path:line`)
- **Criterion** — the WCAG 2.1 success criterion number and name
- **What happens** — in a sentence, from the user's side: "focus stays on the
  page behind the drawer; Tab reaches nothing inside it"
- **Fix** — one, specific and minimal, naming the house pattern to copy
  (`accessibility.md` §10 lists the recurring ones)

Then **what was not checked** — contrast without a running theme, screen
reader behaviour without one at hand — stated plainly, never implied passed.

Do **not** apply fixes. The developer reviews and approves; if asked to fix,
the rules apply in full (a new string is a translation key, a new control is
a real control).

## Step 4 — Record what the rule should have caught

A finding that a rule or the gate should have prevented is an incident:
`/record-incident` with `should_have_caught` pointing at `accessibility.md`
or `check-conventions.py`. Three of the same finding across sections is a
standards gap, not three findings — say so.
