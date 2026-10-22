# Base Theme Standards

The architecture an AI tool or a developer builds against, and the rulings
behind it. Conventions are in `.claude/rules/`; this document is what Base
*is*: how its pages are put together, which parts are the standard and which
are legacy, and what has been decided. Architecture decisions are ruled on by
the Head of Engineering; open items are at the end.

## 1. Purpose

Any Figma file or live page becomes Base Theme–standard code with minimal
human touch-up: the AI reads the design (Figma MCP) and the store (Shopify
MCP), builds against these standards and the rules, verifies against the
reference, and a developer reviews. The AI must know both what the design is
and how it is to be built, without the architecture being re-explained.

Not the goal: redesigning Base to taste, turning a build into a Base refactor,
or locking the knowledge into one tool — `.claude/` is canonical and the Cursor
and Codex copies are generated. Base is a simplified take on Shopify's Dawn;
its current code is not gospel, and where it contradicts the rules, the rules
win and the gap is logged here.

## 2. Collection and PDP

**Ownership.** A section is the unit Shopify renders and the Section Rendering
API re-fetches (`?section_id=`); it owns the schema, the layout, which assets
load, and the orchestrating custom element (`<collection-info>`,
`<product-info>`). A component snippet is a repeatable fragment with explicit
parameters and optional paired CSS/JS. The boundary is who orchestrates AJAX
and URL state: sections do; components render and handle local interaction.

| Behaviour | Lives in | Why |
|---|---|---|
| Swatch → image swap on a card | `component-product-card.js` | Needed wherever a card renders |
| Price-range slider sync | `component-filters-price-range.js` | Local widget; the form carries the params |
| Filter, sort, pagination fetch and URL | `section-collection.js` (`CollectionInfo`) | One state model updates grid, counts, badges, drawers |
| Variant change and partial PDP update | `section-product.js` (`ProductInfo`) | Coordinates price, SKU, inventory, media, forms |
| A carousel of product cards | the section's own JS | Container layout, never card internals |

Put JS with the smallest reusable owner. Card-intrinsic behaviour is component
JS; multi-region page updates are section JS. Alpine holds ephemeral UI state
(drawer open, show more); custom elements fetch, sync the URL and update
several regions.

**The data-attribute contract.**

| Attribute | Meaning |
|---|---|
| <code v-pre>data-section="{{ section.id }}"</code> | Section Rendering API target |
| `data-render-section` | Filter or sort input: serialised on change |
| `data-render-section-url` | Link (pagination, clear filter): click → AJAX with its query string |
| `data-url` | Canonical product URL for variant fetches |
| `data-update-url="false"` | Quick-add modal: suppress `history.replaceState` |
| `data-product-grid` | Infinite-scroll append target |

**The URL state pattern** for any page with filter or sort UI:

1. Real `<form>` elements, even when they do not look like forms; inputs
   `name`d after Shopify facet params and marked `data-render-section`. The
   sort `<select>` binds to its form with the `form=` attribute.
2. One section custom element listens for a debounced `change` and for clicks
   on `data-render-section-url`.
3. `FormData` → `URLSearchParams`; preserve `q`; strip default price params.
4. `fetch(pathname + '?section_id=' + id + '&' + params)`, parse the HTML,
   swap fragments by id (`product-grid-{id}`, `results-count-{id}`, the
   active-filter group, the sort controls, every `.js-filter` block).
5. `history.pushState` for filters and sort; the PDP uses `replaceState` for
   a variant change, with an `AbortController` cancelling the stale request.
6. Never a full-page navigation, never a bespoke JSON endpoint.

Infinite scroll is a separate pipeline (`<infinite-scroll>`, an
`IntersectionObserver`, appends to `[data-product-grid]`) that does not update
the URL and restarts from page 1 on a filter change — see Open.

**Anti-patterns:** a separate `component-filters.js` holding the fetch (the
filter UI is multi-surface; splitting orphans the coordination); card-internal
behaviour in a section file; duplicating product-card markup instead of
rendering `component-product-card`; `DOMContentLoaded` wiring; global
selectors with no section scope; a shared multi-page file named after one
section; a full reload for a filter change; treating a docs page as truer than
the code.

**Base-specific detail, not a rule:** the 800 ms filter debounce, three filter
snippet variants for one section, the hidden `section_id` anchor in the
infinite-scroll snippet, `$persist` on the facet "show more", the quick-add
modal's `-modal-{timestamp}` id.

## 3. Shell, cart engine and search

**The shell.** `layout/theme.liquid` delegates everything: the token layer
(`css-variables` snippet, preloaded `critical.css`), Swiper only on
collection, product, index, page and search templates, Alpine with `persist`,
`theme.js` (exports `debounce`), the `#cart-data` seed and `cart.js`, then
`{% sections 'header-group' %}`, `<main id="MainContent">`,
`{% sections 'footer-group' %}`. Anything on every page is a section in a
section group, never markup in the layout. The header section renders the
cart drawer or notification (`settings.cart_type`), which is why they exist
everywhere and why their section id is the header's.

**Header and navigation.** `sections/header.liquid` orchestrates
`component-nav-drawer`, `component-nav-dropdown` or `component-nav-megamenu`
(by `menu_type_desktop`), the localization form, predictive search and the
cart surface. Open and closed state is Alpine (`searchOpen`, `menuOpen`,
`drawerOpen`) — the rules' job for ephemeral state, and what a rebuild reuses.
Layout is a CSS grid driven by `logo_position` and `menu_position`; sticky
behaviour is `position: sticky` plus two classes. The header exposes
`color_scheme`, `menu_color_scheme`, a padding pair (0–36, deliberately
narrower) and no `presets`, which is correct for a section-group member.

**The cart engine.** `assets/cart.js` is a plain module, not a custom element,
and owns every cart request:

```
window.Cart = {
  state,                                   // seeded from #cart-data, refreshed after every mutation
  add(formData, source),                   // POST /cart/add.js — FormData, so plans and properties work
  change({ line | id, quantity }, source), // POST /cart/change.js
  update({ note | attributes }, source, { withSections }),
  refresh(),                               // GET /cart.js + section HTML, no mutation
}
```

One promise queue, so rapid clicks cannot race; `cart-busy` on `<html>` while
anything is pending; `cart:change` on `document` with `{ action, payload,
response, cart, previousCart, sections, source }` on success and `cart:error`
on failure. Before each mutation it collects the `.shopify-section` ids of
every `cart-drawer` and `cart-page` and sends them as `sections=`, so the
response carries their re-rendered HTML and each consumer extracts its own
fragment. `add` returns the line item, not the cart, so the engine fetches
`/cart.js` afterwards.

Wiring is delegation on markup that works without JS: `submit` on
`form[action*="/cart/add"]`, `click` on `a[href*="/cart/change"]` and
`.cart-item__remove` (quantity steps read the input's current value, debounced
250 ms per line), `change` on `.cart-quantity input` and the note textarea.
The markup is the API; inventing `data-cart-*` attributes adds a second
contract for no gain.

| Consumer | Owns | Re-render |
|---|---|---|
| `<cart-drawer>` | open state, overlay, bubble toggle | swaps `.drawer__wrapper` from the section HTML; keeps scroll except after `add` |
| `<cart-page>` | nothing | replaces its own innerHTML |
| `<cart-notification>` | show, hide, buttons | builds the summary from the `add` response |

All three subscribe to `cart:change` in `connectedCallback` and unsubscribe in
`disconnectedCallback`; `[data-cart-count]` anywhere is updated by the engine.
A component that must talk to the cart outside the engine does its request and
then calls `Cart.refresh()`. Quick add fetches the product page, extracts
`product-info`, gives it a unique section id with `data-update-url="false"`,
and closes on the `add` action.

**Search.** `<predictive-search>` wraps a real GET form, debounces input 700 ms
and fetches `/search/suggest?q=…&section_id=predictive-results`; the results
are a section (`sections/predictive-results.liquid`) rendered by Shopify, so
states are Liquid conditions, not a JS template. The search page is the
collection pattern with `results: search`: `<collection-info>`,
`section-collection.js`, the same filter snippets and sort binding. A new
faceted listing page does the same.

**Overlays.** Dialog role, focus moved in on open and returned on close,
Escape closes, `aria-expanded` on every toggle, and a small `aria-live`
status node placed inside the dialog but outside any region that is swapped,
so the announcement survives the innerHTML replace.

**Legacy in Base, not the standard** — copy none of it: the header's inline
`<script>` (window listeners never removed; a rebuild uses a custom element
and measures the real height for `--header-height`); the header's 1024/1025
breakpoint against the theme's 750/769; bare English in the header's
`menu_position` labels, the announcement bar, the footer's "Follow Us" and
predictive search's headings; the announcement bar's hex colour settings and
`rem` units; the footer's hardcoded background beside its `color_scheme`; the
cart drawer without dialog role, focus trap or Escape; predictive search's
unused `AbortController`; `CollectionInfo` and `InfiniteScroll` wiring in the
constructor and several elements with no `disconnectedCallback`.

**Anti-patterns:** a second cart client (`fetch('/cart/add.js')` anywhere);
a hardcoded drawer section id; re-rendering the whole `<cart-drawer>`;
`data-cart-*` attributes; an inline window script for header behaviour; a JS
template for predictive results; a live region inside the swapped region;
`<div>` toggles without `aria-expanded`.

## 4. Rulings

| Question | Ruling |
|---|---|
| The settings contract is required; why do many of Base's own sections lack it? | Template main sections and section-group members are outside it (a `presets` entry on `cart` would be wrong). The content sections that lack it predate the rule and are not retrofitted in passing; the gate checks only sections added in a commit. |
| Shared behaviour on several pages: one `component-*` or a `section-*` each? | Apply the test in `naming-conventions.md`: same behaviour and appearance differing only in values → one shared component; otherwise separate section files. Base's three product carousels are the second case. When a file's scope widens, rename it in the same change. |
| Single-product photo swipe on a card | Card JS, if ever built. |
| A carousel of different products | Section-level, as in all three of Base's carousels; the card never knows it is in one. |
| `CollectionCarousel` and `CollectionInfo` in one file | A named exception: the carousel stays its own registered element so it survives the grid's innerHTML swap. Not a licence for multi-class section files. |
| Is the search page the collection pattern? | Yes, down to the copied schema name. |
| Keep the Cursor mirror? | Yes until the team's move to Claude Code is complete; it is generated, so it costs nothing to keep. |
| Where does a mistake get recorded? | `/record-incident`, in the repo where it happened, committed at the moment it happens. Incidents stay there; the rules they produce travel. |
| In what order is a store rebuilt? | By dependency: recon → foundations → commerce path → chrome → shared components → transactional templates → homepage and content → long tail (`rebuild-playbook.md`). |
| How does a fork receive tooling and send learnings back without shared history? | `base-link.sh` adds Base as a remote and worktree; `pull-base-tooling.py` overlays three-way against a stamp; `/harvest` pushes from the worktree and opens the Base PR. |
| Mobile padding: a multiple of desktop, or its own setting? | Its own setting. Measured ratios run from 0.43 to 1.70 and cross 1.0, so a constant is the wrong shape; a conditional defers the judgment to the worst moment. Four padding settings on every new section (ruled 2026-09-17). |

## 5. Open

- **`templates/product.json` sets `image_ratio` on shop-the-look, which its
  schema never defines.** Shopify drops the key silently. Fix with the retrofit
  below, not in tooling work.
- **Retrofit Base's own sections to the contract.** The reference
  implementation is what agents copy, and every fork inherits its compliance
  on day one (`report-compliance.py` gives the number). One additive theme PR:
  the non-compliant sections, the bare labels, the `max-width` queries,
  constructor wiring moved to `connectedCallback`. **Needs a ruling.**
- **Admin API writes from a session** (pages, metafield definitions, menus)
  would close the "inert until someone creates the page" gap. Needs a scope
  decision and confirmation per write; `/store-recon` stays read-only.
- **Collection filters, single-open on desktop.** `<collection-filters>`
  treats every group as independent, matching Base's sidebar. A row of
  dropdown chips implies opening one closes the others, but no frame states
  it; independent-per-group ships until a design says otherwise.
- **`updateFilters` scope.** `document.querySelectorAll('collection-info
  .js-filter')` could cross two `collection-info` instances on one page.
- **Infinite scroll versus the filter pipeline.** Deliberately separate, or a
  gap?
- **A layout that switches mode by breakpoint** (grid on desktop, carousel on
  mobile) has no Base precedent; prefer single markup with CSS driving the
  mode, and guard carousel JS with `matchMedia` where it is inactive.
- Minor, team's call: click delegation uses `matches()` not `closest()`, so
  an icon inside a filter badge may not register; `CollectionInfo.form` looks
  like dead code; `featured-products.liquid` duplicates card markup instead of
  rendering `component-product-card`.
