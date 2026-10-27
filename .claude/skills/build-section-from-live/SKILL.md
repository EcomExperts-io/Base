---
name: build-section-from-live
description: Rebuild a section from the store's live theme as a clean Base Theme section — cleaned to the rules, using the theme's one slider, its font and colour tokens and its shared components, and matched to live pixel for pixel with a report. Use when the reference for a page or section is the live site rather than a Figma frame: "match live", "migrate the hero", "port the ee-* section", "rebuild what is on the store today".
argument-hint: <section-name> --live <live-page-url>
---

# build-section-from-live

Live's markup, CSS and JS are the spec for what the section *does and looks
like*, never for how it is written; a section that carries live's code has
failed the migration. `build-page-from-figma` routes here and shares Steps 3–7.

## 0. Before writing anything

1. **Rules.** Read `.claude/rules/` for every file type you will touch. In a
   fork, `python3 .claude/scripts/check-tooling-drift.py` says whether the
   copy is behind Base; tell the user.
2. **Source: the live theme, pulled from the store, never a repo** — live is
   newer. Read-only:

   ```bash
   shopify theme list
   ```

   ```bash
   shopify theme pull --theme <live-theme-id> --path <scratchpad>/live-theme --nodelete
   ```

   Read the section, its assets and its live template entries there; never
   commit it or build in it.
3. **What live actually serves.** The stylesheet the page loads
   (`/cdn/shop/t/<n>/assets/<file>.css`) can differ from the pulled file, and
   global CSS leaks into every section — utility classes, `p` line heights, a
   root font size. Measure computed styles and boxes on the live page at 1440
   and 393 (`live-parity.py page --live-only`, or the browser tools).
4. **Data.** Confirm every metafield, metaobject and field the live template
   references against the store (`/store-recon`), with real values on pages.
5. **Apps that act on the section.** `/recon-theme --live-url` lists what the
   live page loads: a subscription widget injecting into the first product
   form, a review app owning the stars, a page builder owning the template
   name (`javascript-standards.md`, "Product forms").
6. **Existing pieces.** Look for what this theme already has (§2) before
   creating anything.

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

- **Slider:** the one `layout/theme.liquid` already loads (Swiper in Base),
  inside a custom element with translated `a11y` labels and reduced motion.
  Never a second library or a CSS-only substitute unless the theme settled on one.
- **Fonts:** only the tokens in `snippets/css-variables.liquid`. Check which
  faces are loaded — `font_modify` emits nothing for a face the library lacks
  (`.claude/references/layout-pitfalls.md`); if live fakes bold, keep its weight.
- **Colours:** `color_scheme`, then the theme's tokens (grep `css-variables.liquid`).
- **Icons:** `assets/icon-*.svg` through `inline_asset_content`; grep first.
- **Cart:** `window.Cart` and the product form's events (`assets/cart.js`).
  Never fetch `/cart/add` directly.
- **Shared UI:** a piece that exists in another migrated section — a button,
  stars plus review line — goes through the decision test in
  `naming-conventions.md`: same behaviour differing only in values means one
  `component-*` snippet and stylesheet, moved and renamed in the same change.
- **Translations:** reuse an existing key; count the schema locale near the cap (`locales.md`).

## 3. Reusable by construction

- Section code reads **no page metafields**; the template connects them
  through dynamic sources, including repeating blocks, and the metafield type
  must match the setting type (`schemas.md`, "Limits the upload enforces").
- **Product data** comes from `section.settings.product | default: product`.
  One `product` setting per section; a second goes on a block.
- **Keep live's block types and content setting ids**, so the template JSON
  copies across. The only renames are the ones the settings contract forces.
- **Anything that varies between live's uses is a setting**, not a branch on
  a page handle or template name.
- **A page assigned to a page builder's template** (`page.replo.<id>`,
  `page.shogun…`) keeps rendering it until admin is changed: build the new
  template under the function name and a copy under live's name, and name the
  admin switch in the handoff. Read `product.template_suffix` first (`templates.md`).
- **Every section** exposes the settings contract and has a
  `docs/sections/<name>.md` page.

## 4. Verify against live — the report is the evidence

`/verify-against-reference`, the live half: `live-parity.py section` at
`1440,393` while iterating and the full width list once at the end; `states`
for anything that opens, slides or toggles; `hoverstyles` for interactive
elements; `page` when the page below a section drifts. Compare **spans**, not
heights. **Target 0%**, every remaining pixel located; report to
`.claude/verify/<slug>/`, copied to `docs/ai-workflow/verify/<slug>/` for a
page handoff.

Then the gates: `check-conventions.py --changed`,
`check-section-contract.py --files`, `check-theme-staged.py --files`, and
after `theme dev` uploads, confirm the dev theme accepted the file — one
rejected schema 500s every route (`/run-theme`). A template can race ahead of
a new section's schema; restart the server before believing the page.

## 5. Hand off

`build-page-from-figma` Steps 5–7: Notion updated, the QA checklist with the
live URL beside the preview URL for every row, `/record-incident` the moment
a trap a rule should have named costs more than a few minutes.
