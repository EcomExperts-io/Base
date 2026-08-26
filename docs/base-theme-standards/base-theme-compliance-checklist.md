# Base Theme Compliance Checklist
 
**What this is:** a scannable, pass/fail checklist derived from the Base
Theme Architecture Reference. Use it two ways:
 
- **Before building** a Collection/PDP-style page: attach this alongside
  the Architecture Reference when prompting Claude Code/Cursor/Codex, so
  the AI is checking its own output against these items as it goes.
- **After building** (or when auditing existing code): go item by item
  against the actual files. This is what "does the code follow the Base
  Theme standard" should mean in practice — not a vague impression.
This checklist is durable and cross-project — it should work the same
way on Bites Vitamins as on any future client store.
 
---
 
## A. File Organization & Naming
 
- [ ] Section-level orchestration logic (fetch, URL state, cross-region
      DOM updates) lives inside that section's own `section-[name].js` —
      not split into a separate file.
- [ ] `section-*` naming is used only for logic tied to one specific
      section. `component-*` naming is used only for genuinely reusable,
      self-contained fragments.
- [ ] No `section-*` file is loaded by more than one unrelated
      section/page. A `section-*` name asserts single-section scope; if
      the file is genuinely shared, it is renamed `component-*` in the
      same change that widens its scope.
- [ ] Where behavior is needed on several pages, the **decision test**
      has been applied (see `.claude/rules/naming-conventions.md`):
      *is the behavior and appearance the same thing everywhere, differing
      only in configuration values?*
      - **Yes** → one shared `component-*`, built so consumers configure
        it via data attributes and CSS custom properties. This is the
        "genuine atomic UI primitive" case.
      - **No** → separate `section-*` files. Base's three product
        carousels (Featured Products / Related Products / Featured
        Collections v2) are this case — each wraps Swiper with genuinely
        different configuration, so they are three carousels that share a
        library, not one carousel duplicated.
- [ ] Reusable card/widget markup uses the existing shared snippet
      (e.g. `component-product-card`) rather than being duplicated
      inline in a new section.
- [ ] Any internal doc (e.g. `.cursor/references/*`) claiming to
      document an "intentional" architecture decision has been checked
      against the Architecture Reference and Decisions Log — a doc
      written by an AI model during a build is not automatically valid
      precedent.
## B. JS Responsibility Boundaries
 
- [ ] Card-intrinsic behavior (swatches, quick-add triggers, and if ever
      built, single-product photo swipe) lives only in the card's own
      component JS.
- [ ] Container/list-level behavior — carousel or Swiper orchestration
      for a list of *different* products, grid-vs-carousel layout mode,
      breakpoints, slides-per-view — lives in that section's own JS, not
      centralized in a shared cross-page utility, and never leaked into
      the card JS.
- [ ] All filter/sort/pagination fetching and URL sync lives in one
      section-level custom element — not split into a second fetch
      pipeline.
- [ ] Ephemeral UI state that doesn't need to be shareable or persisted
      (drawer open/closed, accordion expand, "show more") uses Alpine.js
      rather than a dedicated custom element/JS class.
- [ ] Custom elements are registered once with a guard
      (`if (!customElements.get(...))`), initialize in
      `connectedCallback`, and clean up in `disconnectedCallback`.
## C. URL / Filter State Pattern
 
- [ ] Filters render as real `<form>` elements (even if they don't look
      like a form), with `name` attributes matching Shopify facet
      params.
- [ ] Filter/sort inputs use `data-render-section`; pagination,
      clear-filter, and similar links use `data-render-section-url`.
- [ ] High-frequency inputs (e.g. price range) are debounced before
      triggering a fetch.
- [ ] Fetches use the Section Rendering API (`?section_id=`) and swap
      fragments by ID — never a bespoke JSON endpoint, never a full
      page reload.
- [ ] Filter/sort changes use `history.pushState`; PDP variant changes
      use `history.replaceState`.
- [ ] If infinite scroll is enabled, confirm it's a deliberate, known
      pipeline (separate from the filter fetch) rather than an
      unnoticed gap — and if paired with a carousel presentation, that
      any per-item indicators (dots, etc.) update for newly appended
      items.
## D. Responsive / Layout-Mode Handling (new territory — judgment call, no direct Base precedent)
 
- [ ] If a page's layout mode changes by breakpoint (e.g. grid on
      desktop, carousel on mobile), it's single markup + CSS-driven
      where possible — not two duplicated render paths — unless there's
      a specific, documented reason duplication is safer here.
- [ ] If carousel JS would otherwise keep running at breakpoints where
      the carousel isn't visually active, that's either guarded off
      (e.g. `matchMedia`) or explicitly accepted as a negligible
      tradeoff — not an oversight.
## E. Schema & Merchant Controls

The section that did not exist when the Bites Vitamins audits were run,
which is part of why they missed this. A page can pass every item in
A–E and still ship sections a merchant cannot edit at all.

- [ ] Every **new merchant-addable section** exposes `padding_top` and
      `padding_bottom` (`range`, 0–100, step 4, default 40). No
      exceptions.
- [ ] Every new merchant-addable section exposes `color_scheme`, **or**
      hardcodes the surface with a Liquid comment stating why (a design
      that fixes the background on purpose).
- [ ] Every new merchant-addable section has a `presets` entry — without
      one the merchant cannot add it in the theme editor.
- [ ] A section that is deliberately *not* merchant-addable (a template
      main section, a section-group member) says so in a Liquid comment
      mentioning `presets`. The contract is about merchant editability,
      so a section nobody can place is out of scope for it.
- [ ] The `{%- style -%}` block computes
      <code v-pre>.section-{{ section.id }}-padding</code>, with mobile at 0.75× the
      desktop value, and the wrapper carries both
      <code v-pre>color-{{ section.settings.color_scheme }}</code> and that padding class.
- [ ] Schema `label`, `content`, `info`, preset `name` and block `name`
      all use `t:` keys resolving in `locales/en.default.schema.json` —
      no bare English. Note that older Base sections use bare labels;
      that pattern does not carry forward.
- [ ] Every setting declared in the schema is actually read by the
      markup, and every setting the markup reads is declared.
- [ ] CSS is loaded with `stylesheet_tag` and JS as `type="module"`,
      matching the theme rather than older scaffolding examples.

**Why this section is weighted heavily on design-driven work:** a Figma
frame carries exactly one spacing value and one background colour, so a
pass that matches the design has no reason to invent a merchant control.
On Bites Vitamins, 30 of 31 new sections shipped without any of the
above while looking entirely finished. The pre-commit gate
(`.claude/scripts/check-section-contract.py`) checks the mechanical
subset of this list; passing the gate is not the same as passing the list.

## F. Sign-off
 
- [ ] Every unchecked or partial item above has either a fix applied,
      or a logged decision in the Decisions Log explaining why it's
      being left as-is.
- [ ] Any item that required a new judgment call (no Base precedent
      either way) is logged in the Decisions Log so it doesn't get
      re-litigated from scratch on the next project.
 