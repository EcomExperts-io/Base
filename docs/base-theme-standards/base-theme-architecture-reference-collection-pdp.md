# Base Theme Architecture Reference — Collection & PDP
 
**What this is:** a read-only recon of the Base Theme (`native-cart`
branch), covering `sections/collection.liquid`, `sections/product.liquid`,
and their traced dependencies. This is the durable technical standard —
the rulebook any AI coding tool (Claude Code, Cursor, Codex) should be
pointed at when building or auditing a Collection or PDP page.
 
**Audience:** AI coding agents with no prior context on this codebase,
and any developer checking a build's compliance.
 
**Companion doc:** open questions and rulings from Moemen live in
*Base Theme Decisions Log* — not here. This file states the architecture
as understood; that file tracks what's still being confirmed.
 
---
 
## Files Read (Complete List)
 
**Templates:** `templates/collection.json`, `templates/product.json`
 
**Sections:** `sections/collection.liquid` (full), `sections/product.liquid` (full), `sections/search.liquid` (partial — shared filter pattern), `sections/related-products.liquid` (partial — PDP dependency), `sections/featured-products.liquid` (partial — carousel comparison), `sections/featured-collections-v2.liquid` (partial — carousel + product-card usage)
 
**Snippets:** `component-product-card.liquid`, `component-filters-sidebar.liquid`, `component-filters-horizontal.liquid`, `component-filters-drawer.liquid`, `component-filters-price-range.liquid`, `component-pagination.liquid`, `component-product-media-gallery.liquid`
 
**JavaScript:** `section-collection.js`, `section-product.js`, `component-product-card.js`, `component-filters-price-range.js`, `component-infinite-scroll.js`, `component-quick-add.js` (partial), `component-modal-opener.js` (partial), `component-selling-plans.js` (partial), `product-recommendations.js`, `section-related-products.js`, `section-featured-products.js`, `section-featured-collections-v2.js`, `theme.js`
 
**CSS / Config / Docs:** `.cursor/rules/naming-conventions.mdc`, `layout/theme.liquid` (partial), `docs/sections/collection.md`, `docs/assets/section-collection.md`, `docs/snippets/component-product-card.md`, `docs/assets/section-product.md`
 
**Not read (out of scope or conditional):** `sections/collections.liquid` (list-collections page, different from the collection grid page), `sections/product-highlights.liquid`, `sections/shop-the-look.liquid`, `component-product-media-modal.js`, `component-product-media-magnify.js`, `component-pickup-availability.js` (loaded conditionally, behavior inferred from load conditions only), `assets/cart.js`
 
---
 
## 1. File Organization
 
| Layer | Location | Owns | Does not own |
|---|---|---|---|
| Section | `sections/[name].liquid` | Page/template slice; schema settings; layout; which assets to load; orchestration custom element (`<collection-info>`, `<product-info>`) | Reusable card/filter markup duplicated across pages |
| Snippet ("component") | `snippets/component-[name].liquid` | Repeatable UI fragment; explicit parameters; optional paired `.css`/`.js` | Section settings schema; page-level AJAX orchestration |
| Section assets | `assets/section-[name].{css,js}` | Layout/behavior scoped to one section type | Behavior intrinsic to a card/widget used across many sections |
 
**Durable principle:** A section is the unit Shopify renders on a template
and the unit the Section Rendering API re-fetches (`?section_id=`). A
component snippet is anything repeated across sections with the same
markup and optional self-contained JS. The boundary is *who orchestrates
AJAX and URL state*: sections do; components render and handle local
interactions.
 
**Naming:** `section-*` = tied to a section file and usually its schema,
and should not be reused across unrelated pages under that name.
`component-*` = portable, loaded by any section that renders it, and
should be named for what it does, not for the page it first appeared on.
Sections are named by function (`collection`, `product`), not
`main-collection` — `main-` is reserved for template main sections per
project rules.
 
**When behavior lives in a component vs. a section:**
 
| Behavior | Where in Base | Why |
|---|---|---|
| Color swatch → image swap on a card | `component-product-card.js` | Same behavior needed on collection grid, related products, complementary block |
| Price range slider UI sync | `component-filters-price-range.js` | Local widget; delegates serialization to the section via `data-render-section` + form |
| Filter/sort URL + AJAX re-render | `section-collection.js` (`CollectionInfo`) | Coordinates forms, grid, badges, counts, drawers, history |
| Variant change + partial PDP update | `section-product.js` (`ProductInfo`) | Coordinates price, SKU, inventory, media, forms |
| Infinite scroll next page | `component-infinite-scroll.js` | Tentative — only one consumer observed |
| Swiper around a product list | `section-featured-products.js`, `section-featured-collections-v2.js`, `section-related-products.js` | Container layout, not card internals |
 
**Durable principle:** put JS with the smallest reusable owner.
Card-intrinsic behavior → component JS. Multi-region page updates
(grid + filters + URL) → section JS.
 
---
 
## 2. JS Architecture
 
**Custom elements as the connection layer.** Every significant module
registers a custom element with a guard:
 
```js
if (!customElements.get('collection-info')) {
  customElements.define('collection-info', CollectionInfo);
}
```
 
The guard itself is universal (confirmed in all eight modules examined:
`CollectionInfo`, `ProductInfo`, `ProductCard`, `PriceRange`,
`InfiniteScroll`, `FeaturedProducts`, `RelatedProductsCarousel`,
`FeaturedCollectionsV2`). **Correction (verified against code):**
"initialize in `connectedCallback`" is the majority pattern, not a
universal one — `ProductInfo`, `ProductCard`, `PriceRange`,
`FeaturedProducts`, `RelatedProductsCarousel`, and
`FeaturedCollectionsV2` wire up there, but `CollectionInfo` (the
`collection-info` example above) and `InfiniteScroll` both wire up their
listeners/observer directly in the `constructor` instead
(`assets/section-collection.js`, `assets/component-infinite-scroll.js`)
— check the specific file rather than assuming `connectedCallback`.
Cleanup in `disconnectedCallback` is even less consistent: only the
three carousel classes (`FeaturedProducts`, `RelatedProductsCarousel`,
`FeaturedCollectionsV2`) define one; `CollectionInfo`, `ProductInfo`,
`ProductCard`, `PriceRange`, and `InfiniteScroll` don't. Note:
`variant-selector` and `quantity-selector` on the PDP are semantic tags
only — no `customElements.define` found for them (confirmed via
repo-wide grep); don't assume every custom tag has a JS class behind it.
 
**Data-attribute contract (markup ↔ JS):**
 
| Attribute | Used by | Meaning |
|---|---|---|
| <code v-pre>data-section="{{ section.id }}"</code> | `CollectionInfo`, `ProductInfo` | Section Rendering API target |
| `data-render-section` | Filter/sort inputs | Participates in form serialization on change |
| `data-render-section-url` | Links, clear buttons, pagination | Pre-built URL query string; click → AJAX |
| `data-url` | `ProductInfo` | Canonical product URL for variant fetches |
| `data-update-url="false"` | Quick-add modal (cloned PDP) | Suppress `history.replaceState` in modal context |
| `data-product-grid` | Infinite scroll | Marker for grid container to append/inject |
 
**Durable principle:** sections expose a declarative contract via
attributes; JS listens at the orchestrator root rather than wiring every
input individually.
 
**Product grid carousel vs. product-card JS:** `component-product-card.js`
only handles swatch clicks (swap featured image) — it does not implement
swipe/carousel. Carousel behavior for grids of product cards lives in
section-level files (`section-featured-products.js`,
`section-featured-collections-v2.js`, `section-related-products.js`),
which wrap the card markup in Swiper and init it in the section custom
element. Reasoning: Swiper needs a container (wrapper, slides, nav,
breakpoints) — that structure belongs to the section layout, and card JS
shouldn't assume it's always inside a carousel.
 
**Filtering lives in `section-collection.js`, not a separate file.** All
filter/sort/pagination AJAX is in `CollectionInfo`. Reasoning: multiple
filter UIs (sidebar, horizontal, drawer) share one state model (the URL
query string); one fetch must update many DOM targets (grid, counts,
badges, facet counts, sort controls); filter snippets are markup-only and
emit events upward via `data-render-section`.
 
**Alpine.js vs. custom elements:** Alpine for ephemeral UI state (drawer
open/closed, show-more, filter accordion). Custom elements for data
fetching, URL sync, and cross-region DOM updates.
 
**Shared utilities:** `theme.js` exports `debounce`, used by
`CollectionInfo` (800ms on filter change). Swiper is loaded globally from
`layout/theme.liquid` on collection, product, index, page, and search
templates — not bundled per section.
 
---
 
## 3. URL / Query String State Pattern (Filters)
 
**Reusable pattern, when a page has filter/sort UI that persists in the URL:**
 
1. Render real `<form>` elements, even if they don't look like forms visually.
2. Give filter inputs `name` matching Shopify facet param names, marked with `data-render-section`.
3. Wrap the page in a section custom element listening for debounced `change` and `click` on `data-render-section-url`.
4. Serialize with `new FormData(form) → URLSearchParams`.
5. `fetch(pathname + ?section_id=SECTION_ID + & + params)`, parse HTML, swap targeted fragments, `history.pushState`.
6. Never full-page navigate for filter/sort/pagination when JS is active.
**Corrected — filtering is form-based, but there are only two form IDs,
not three:** `#filters-form` (shared by both `component-filters-sidebar.liquid`
and `component-filters-horizontal.liquid` — they render the same ID, not
distinct variants) and `#filters-form-drawer` (`component-filters-drawer.liquid`).
The sort `<select>` sits outside both and associates via the HTML `form=`
attribute, set dynamically per `section.settings.filter_type`:
`form="filters-form-drawer"` when `filter_type == 'drawer'`, otherwise
`form="filters-form"` (`sections/collection.liquid`). Checkboxes use
Shopify-generated `name`/`value` pairs.
 
**Serialization flow:** triggered on debounced (800ms) `change` of
`[data-render-section]`. Handler (`CollectionInfo.onChangeHandler`) finds
the form (`closest('form')` or fallback IDs), builds
`FormData → URLSearchParams`, preserves an existing `q` search param,
strips default price params via `removeDefaultPriceFilters()`, then calls
`fetchSection(finalParams)`. **Corrected — precise attribute split in the
price-range widget** (`snippets/component-filters-price-range.liquid`):
the range inputs (`.min-range`/`.max-range`) carry both `name` (the
Shopify facet param) and `data-render-section`, so they're what actually
reaches `FormData`; the paired number inputs (`.min-number`/`.max-number`)
carry `data-render-section` but no `name`, so they never serialize
directly — `PriceRange` (`assets/component-filters-price-range.js`) keeps
them visually in sync via its own `input`-event listener, but only the
range inputs' `change` event (which fires once, on release) reaches
`CollectionInfo`'s `change` listener — hence fetch fires on range
release, not every tick.
 
**Click path:** elements with `data-render-section-url` (pagination,
remove filter, clear all) — handler takes
`dataset.renderSectionUrl.split('?')[1]` as the query string. Uses
`event.target.matches(...)` only, so clicks on child nodes (e.g. an SVG
inside a close button) may not fire — tracked as an open item in the
Decisions Log.
 
**Navigation model:** Section Rendering API + fragment swap +
`history.pushState` — not a full reload, not a bespoke JSON API:
 
```js
fetch(`${window.location.pathname}?section_id=${this.dataset.section}&${searchParams}`)
// ...
history.pushState({}, '', `${window.location.pathname}?${searchParams}`);
```
 
**Corrected — list was missing two fragments.** Updated fragments by ID
(per `CollectionInfo.fetchSection` in `assets/section-collection.js`):
`product-grid-{id}`, `results-count-{id}`, `drawer-results-count-{id}`,
`active-filters-count-{id}`, `active-filter-group-{id}`, `sort-by-{id}` /
`sort-by-drawer-{id}`, `filters-drawer-buttons-wrapper-id`, plus all
`.js-filter` blocks.
 
**Pagination:** standard pagination uses `data-render-section-url` on
links, handled by the same click pipeline. **Infinite scroll** (when
enabled) is a separate pipeline — an `<infinite-scroll>` custom element
using `IntersectionObserver`, fetching the next page and appending to
`[data-product-grid]`. It does **not** update the browser URL, does not
route through `CollectionInfo`, and resets from page 1 whenever a filter
change replaces the grid — tracked as an open item in the Decisions Log.
 
---
 
## 4. State & Data Flow
 
Section settings flow into markup via schema + inline `{%- style -%}` +
explicit snippet arguments — JS reads `this.dataset.section`, not
`section.settings` directly, since re-fetched HTML re-applies settings
server-side.
 
**PDP variant flow:** changing a variant input bubbles to `ProductInfo`,
which fetches
`` `${productUrl}?option_values=${selectedOptionValues}&section_id=${sectionId}` ``,
parses the returned `[data-selected-variant]` JSON, and patches price,
SKU, inventory, add-to-cart, and variant-selector fragments by ID — using
`history.replaceState` (variant is shareable but not a new history
entry). Combined-listing product URL changes replace the entire
`<product-info>`. An `AbortController` cancels stale requests.
 
**Durable principle:** PDP uses `replaceState` for variant changes;
Collection uses `pushState` for filters (so the back button traverses
filter history, unlike variant changes).
 
---
 
## 5. Patterns to Follow
 
- Wrap the interactive page region in one section custom element (`collection-info`, `product-info`) that owns fetch + URL + fragment updates.
- Use the Shopify Section Rendering API for AJAX — not bespoke JSON endpoints.
- Mark interactive controls declaratively (`data-render-section`, `data-render-section-url`).
- Debounce high-frequency filter changes (~800ms observed) before fetch.
- Make surgical DOM updates by matching IDs — don't replace a whole section unless necessary.
- Load component assets from the section that renders them.
- Keep card-intrinsic UX (swatches, modal openers) in component JS.
- Register custom elements once with `if (!customElements.get(...))`.
- Pass `section_id` into snippets that generate unique form/modal IDs.
- Prefer native elements (`<details>` for accordions, real forms for facets).
- Load scripts conditionally — only when the relevant setting/feature is enabled.
- Lazy-load recommendation blocks via `IntersectionObserver`; init carousels after content arrives.
---
 
## 6. Anti-Patterns to Avoid
 
| Anti-pattern | Why it fails here |
|---|---|
| Splitting filter fetch/update into a separate `component-filters.js` | Filter UI is multi-surface; one URL state must update grid, counts, badges, and all `.js-filter` nodes — splitting orphans coordination and duplicates fetch logic |
| Section-scoped carousel file for card-*internal* behavior (e.g. per-card image swipe) | Card behavior should survive regardless of grid/carousel/recommendations context |
| Duplicating product card markup instead of using `component-product-card` | Diverges from collection/related-products; breaks shared JS/CSS and quick-add patterns |
| `DOMContentLoaded` wiring | Project rules require custom elements + lifecycle hooks |
| Global selectors without section scope | Fragile if multiple grids/instances exist on one page |
| Treating docs as source of truth over code | Docs reference IDs that differ from actual Liquid — code wins |
| Expecting `component-product-card.js` to handle carousels | It doesn't — carousel init is section-level in current Base |
| Full page reload for filter changes | Breaks loading overlay, scroll restoration, and drawer UX |
| A shared, multi-page component named after one section (e.g. `section-[pagename]-carousel.js` reused on unrelated pages) | Naming should reflect actual scope; if something is genuinely shared, name it `component-*`, not `section-[origin-page]-*` |
 
---
 
## 7. Principle vs. Implementation Detail
 
| Topic | Durable principle | Base-specific detail (not a universal rule) |
|---|---|---|
| Section vs. component | Sections orchestrate; components render + local behavior | Three filter snippet variants for one section |
| Filter URL state | Form serialize → Section API → pushState → fragment swap | 800ms debounce; exact list of swapped IDs |
| Pagination | Use `data-render-section-url` for AJAX pages | Anchor `#product-grid-{id}` in pagination snippet |
| Infinite scroll | Can be a separate pipeline from the filter orchestrator | Hidden `<a href="...&section_id=">` trick |
| Product card JS | Owns behavior that travels with every card instance | Swatches only — no carousel |
| Product grid carousel | Container owns layout/interaction between cards | Implemented in `section-related-products.js`, not the card |
| PDP updates | Section API + patch by ID; `replaceState` for variant | `option_values=` query param; modal `-modal-{timestamp}` ID hack |
| Price filter | Widget syncs UI; form names carry API params | Strip default price params before fetch |
| Alpine vs. custom elements | Alpine for UI chrome; CE for fetch/URL | `$persist` for "show more" in facets |

---

## Change Log

- **Aug 5, 2026** — Independent verification pass against the actual
  Base Theme code (`native-cart` branch, last commit June 10, 2026 — no
  code changes since this doc was written, so all corrections below are
  "inaccurate as originally written," not staleness). Three corrections
  made, all in Section 2 and Section 3:
  - **Custom element lifecycle:** "Register once, initialize in
    `connectedCallback`" was stated as a universal pattern but isn't —
    `CollectionInfo` (`assets/section-collection.js`) and
    `InfiniteScroll` (`assets/component-infinite-scroll.js`) both wire
    up in the `constructor` instead, confirmed by reading all eight
    referenced modules directly. Notably, `CollectionInfo` is the same
    class used as the doc's own illustrative code sample for the guard
    pattern.
  - **Fragment ID list:** was missing two IDs that `CollectionInfo.fetchSection`
    actually updates — `drawer-results-count-{id}` and
    `active-filters-count-{id}` (both present in
    `assets/section-collection.js`, lines ~104–106).
  - **Form ID count and price-range attribute split:** "three form IDs"
    was corrected to two (`#filters-form` is shared by both the sidebar
    and horizontal filter snippets, not a distinct ID per layout); the
    sort `<select>`'s dynamic `form=` target (drawer vs. non-drawer) was
    added; and the price-range description's "no `name`" claim was
    corrected to specify that only the *number* inputs lack `name` — the
    *range* inputs carry both `name` and `data-render-section`, per
    `snippets/component-filters-price-range.liquid`.
  - Everything else checked — File Organization, the data-attribute
    contract table, the carousel-ownership claims (including
    cross-checking `component-product-card.js` never contains carousel
    logic), the PDP variant-fetch flow, Swiper's template-gated loading
    in `layout/theme.liquid`, `variant-selector`/`quantity-selector`
    having no `customElements.define`, and the Patterns/Anti-Patterns
    tables — confirmed accurate against the code as-is. See the
    Decisions Log for the carousel-ownership-specific verification
    (unchanged, no corrections needed there).
 