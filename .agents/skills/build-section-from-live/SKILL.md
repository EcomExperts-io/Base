---
name: build-section-from-live
description: Rebuild a section from the store's live theme as a clean Base Theme section — cleaned to the rules, using the theme's one slider, its font and colour tokens and its shared components, and matched to live pixel for pixel with a report. Use when the reference for a page or section is the live site rather than a Figma frame: "match live", "migrate the hero", "port the ee-* section", "rebuild what is on the store today".
---

# build-section-from-live

The purpose of a migration is **clean code**. Live's markup, CSS and JS are the
spec for what the section *does and looks like*. They are never the spec for
how it is written. A section that matches live but carries live's code has
failed the migration.

**Why this exists.** The Pique rebuild (Sep–Oct 2026) switched from Figma to
"match the live site" in its second week, and the Figma workflow had nothing
to say about it: no way to read live, no way to verify against it, and no
rule about what carries over. The build improvised one, then ran it over 21
batches of landing pages to 0% parity. This is that method, with the client's
numbers taken out. `build-page-from-figma` routes here when the reference is
live; the two share Steps 3–7 of that skill (standards, verification, Notion,
QA checklist, incidents).

## 0. Before writing anything

1. **Rules.** Read `.claude/rules/` for every file type you will touch. In a
   fork, `python3 .claude/scripts/check-tooling-drift.py` says whether the
   copy is behind Base; tell the user when it is. Pulling it down is their
   call.
2. **Source: the live theme, pulled from the store, never a repo.** Live has
   been newer than the repository every time anyone checked. Read-only:

   ```bash
   shopify theme list
   ```

   ```bash
   shopify theme pull --theme <live-theme-id> --path <scratchpad>/live-theme --nodelete
   ```

   Read the section, its assets and its entries in the live templates there.
   Do not commit it and do not build in it.
3. **What live actually serves.** The live stylesheet the page loads
   (`/cdn/shop/t/<n>/assets/<file>.css`) can differ from the pulled file, and
   the live theme's global CSS leaks into every section — utility classes,
   `p` line heights below a breakpoint, a root font size that is not ours.
   Measure computed styles and boxes on the live page at 1440 and 393
   (`live-parity.py page --live-only`, or the browser tools) rather than
   trusting the section's own CSS.
4. **Data.** Confirm every metafield, metaobject and field the live template
   references against the store (`/store-recon`), with real values on two or
   three pages. Never assume a field exists.
5. **Apps that act on the section.** `/recon-theme --live-url` lists what the
   live page loads. A subscription widget that auto-injects into the first
   product form, a review app that owns the stars, a page builder that owns
   the template name — each changes what the section must and must not do
   (`javascript-standards.md`, "Product forms").
6. **Existing pieces.** Look for what this theme already has before creating
   anything (§2). A second copy of a thing that exists is a defect.

## 1. Clean it — what never carries over

| Live has | Replace with |
|---|---|
| `{% style %}` keyed to `#shopify-section-{{ section.id }}` | Custom properties on the root's `style` attribute (`css-in-markup.md`) |
| Per-section colour pickers | `color_scheme`, then the theme's colour tokens. Per-block pickers may stay when live has them per block |
| Live's own padding ids (`padding_top_desktop` …) | `padding_top` / `padding_bottom` and the mobile pair, with a comment where live's values forced a different step |
| `font-family: '…' !important`, any `@font-face`, font files, Google Fonts links | The theme's font tokens (§2) |
| `!important`, ids in selectors, `max-width` queries, physical properties | Specificity fixes, mobile-first `min-width`, logical properties |
| Raw hex | Scheme variables, or an existing brand token. Add a token to `snippets/css-variables.liquid` only when none matches |
| The live theme's utility classes (`Heading`, `u-h6`, `FontWeight_Six` …) | Write the effect they had — measured — into the section's own BEM class |
| Invalid or dead declarations (`font-style: Regular`, `leading-trim`, unused classes) | Delete |
| jQuery, Flickity, Slick, Splide, Glide, Owl, hand-rolled carousels | The theme's one slider (§2) |
| Inline `<script>` or `DOMContentLoaded` | A custom element in `assets/section-<name>.js`, or no JS |
| Bare English in schema, `aria-label` or `alt` | Translation keys |
| `href="{{ url \| default: '#' }}"` fallbacks | Render the element only when its data exists |
| Promo copy, percentages or review counts as schema defaults | Neutral defaults. The template holds the real values |
| Vendor or page prefixes (`ee-`, a page name) | Name by function: `ee-hero-section` → `hero-section` |

## 2. One of each — reuse, never duplicate

- **Slider:** the one `layout/theme.liquid` already loads (Swiper in Base).
  Every live carousel, whatever library it used, becomes that slider inside a
  custom element, with translated `a11y` labels and reduced motion. Never add
  a slider library, a second copy, or a CSS-only scroll carousel as a
  substitute unless the theme already settled on one.
- **Fonts:** only the tokens in `snippets/css-variables.liquid`. Check which
  faces are loaded before using a weight — `font_modify` emits nothing for a
  face the library lacks and the browser synthesises
  (`.claude/references/layout-pitfalls.md`). If live fakes bold on a single
  face, keep the weight live has rather than loading a face live never had.
- **Colours:** `color_scheme`, then the theme's tokens. Grep
  `css-variables.liquid` for the value first.
- **Icons:** `assets/icon-*.svg` through `inline_asset_content`. Grep for an
  existing icon before adding one.
- **Cart:** `window.Cart` and the product form's events (`assets/cart.js`).
  Never fetch `/cart/add` directly.
- **Shared UI:** if a piece already exists in another migrated section, apply
  the decision test in `naming-conventions.md` before copying it — a button,
  the stars plus review line, a numbered step. Same behaviour, differing only
  in values, means one `component-*` snippet and stylesheet that each section
  configures through custom properties; moving it there, and renaming it, is
  part of the change that adds the second user.
- **Translations:** reuse an existing key rather than adding the same English
  under a new name — and count the schema locale first near the cap
  (`locales.md`).

## 3. Reusable by construction

- Section code reads **no page metafields**. The template connects them
  through dynamic sources, including repeating blocks, so the section works
  on any page with any data. A dynamic source's metafield type must match the
  setting type (`schemas.md`, "Limits the upload enforces").
- **Product data** comes from the section's product:
  `section.settings.product | default: product`, so it works on a product
  template without a pick and a pick overrides it. One `product` setting in a
  section's own settings; a second goes on a block.
- **Keep live's block types and content setting ids**, so the template JSON
  copies across. The only renames are the ones the settings contract forces.
- **Anything that varies between live's uses is a setting**, not a branch on
  a page handle or template name.
- **A page assigned to a page builder's template** (`page.replo.<id>`,
  `page.shogun…`) keeps rendering that template until admin is changed. Build
  the new template under the function name and a copy under live's name, and
  say in the handoff which admin switch retires the copy. Read
  `product.template_suffix` before editing a product template
  (`templates.md`).
- **Every section** exposes the settings contract and has a
  `docs/sections/<name>.md` page.

## 4. Verify against live — the report is the evidence

`/verify-against-reference`, the live half: `live-parity.py section` per
section at `1440,393` while iterating and the full width list once at the end;
`states` for anything that opens, slides or toggles; `hoverstyles` for the
interactive elements; `page` when the page below a section drifts. Compare
**spans**, not heights — the live theme may move bands with negative and
collapsing margins that leave a height equal and everything below shifted.

**Target 0%.** Explain every remaining pixel by locating it. Write the report
to `.claude/verify/<slug>/` and, for a page handoff, copy it to
`docs/ai-workflow/verify/<slug>/`.

Then the gates, as for any build: `check-conventions.py --changed`,
`check-section-contract.py --files`, `check-theme-staged.py --files`, and
after `theme dev` uploads, confirm the dev theme accepted the file — one
rejected schema 500s every route and names a file you were not editing
(`/run-theme`). A template can race ahead of a new section's schema; restart
the server before believing the page (`templates.md`).

## 5. Hand off

`build-page-from-figma` Steps 5–7: Notion updated, the QA checklist in plain
English with the live URL beside the preview URL for every row, and
`/record-incident` the moment a trap a rule should have named costs more than
a few minutes.
