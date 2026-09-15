# Base Theme Architecture Reference — Header, Cart Engine & Search

**What this is:** a read-only recon of the Base Theme (`development` at
`a24204b`, 15 Sep 2026) covering the header and its navigation, the native
cart engine and its three consumers, and search — predictive and page. It is
the durable technical standard for the part of a rebuild that the v1 vision
scheduled "later" and that a real rebuild turned out to be mostly made of:
on the MiLB build, five of nine builds were a footer, a header with five
mega-menu panels, a cart drawer, a search overlay and a set of drawers, and
none of them had a reference to build against.

**Audience:** AI coding agents with no prior context on this codebase, and any
developer checking a build's compliance.

**Companion docs:** the Collection & PDP reference for the filter/URL pattern
that search reuses; the Decisions Log for open rulings. Where this file says
"current state, not the standard", it is describing Base as it is so an agent
does not copy it — the rules in `.claude/rules/` win.

---

## Files Read (Complete List)

**Layout:** `layout/theme.liquid` (full)

**Sections:** `sections/header.liquid` (full), `sections/header-group.json`,
`sections/footer.liquid` (full), `sections/footer-group.json`,
`sections/announcement-bar.liquid` (first 120 lines — styles and markup; the
rotation script at the end was not read), `sections/search.liquid` (full),
`sections/predictive-results.liquid` (full), `sections/cart.liquid` (first 60
lines)

**Snippets:** `component-nav-drawer.liquid`, `component-nav-dropdown.liquid`,
`component-nav-megamenu.liquid`, `component-cart-drawer.liquid`,
`component-cart-notification.liquid`, `component-cart-discount.liquid`
(first 12 lines), `component-predictive-search.liquid`

**JavaScript:** `assets/cart.js` (full), `assets/component-cart-drawer.js`,
`assets/component-cart-notification.js`, `assets/component-cart-page.js`,
`assets/component-quick-add.js`, `assets/component-modal-opener.js`,
`assets/component-predictive-search.js`, `assets/theme.js`

**Not read:** `assets/component-cart-discount.js`,
`assets/component-localization-form.js`, `assets/cart.css`,
`assets/section-footer.css`, `assets/section-search.css`, the announcement
bar's script. Claims below about those are limited to how they are loaded.

---

## 1. How the shell is assembled

`layout/theme.liquid` is 89 lines and delegates everything:

| Loaded in `<head>` | Condition | Why it matters to a build |
|---|---|---|
| `css-variables` snippet, `critical.css` (preloaded) | always | The token layer every section reads. Stage 1 of a rebuild. |
| Swiper CSS + JS (`defer`) | `template.name` is collection, product, index, page or search | A section using Swiper on any other template has no library. |
| Alpine + `@alpinejs/persist` (`defer`) | always | Ephemeral UI state everywhere in the shell. |
| `theme.js` (`type="module"`) | always | Exports `debounce`; the only shared utility. |
| `#cart-data` JSON script + `cart.js` (`type="module"`) | always | The cart engine seeds its state from the rendered cart object — no first fetch. |
| `component-predictive-search.css` | `settings.predictive_search_enabled` | The JS is loaded at the end of `<body>` under the same setting. |

`<body>` renders GTM and the data layer, a skip link, the optional splash
screen, then `{% sections 'header-group' %}`, `<main id="MainContent">`, and
`{% sections 'footer-group' %}`. The header group holds `announcement-bar` then
`header`; the footer group holds `footer`.

**Durable principle:** section groups are the seam. Anything that must appear
on every page is a section inside `header-group` or `footer-group`, not markup
in the layout. The cart drawer and cart notification are rendered *by the
header section* (`settings.cart_type` decides which), which is why they exist
on every page and why the cart engine finds their section id by walking up to
`.shopify-section`.

---

## 2. Header and navigation

### Structure

```
sections/header.liquid            orchestrates; owns the schema and the search panel
  component-nav-drawer            mobile/drawer menu (Alpine drawerOpen)
    component-nav-dropdown        nav_style: 'drawer'
  component-nav-dropdown          desktop, menu_type_desktop == 'dropdown'
  component-nav-megamenu          desktop, menu_type_desktop == 'mega'
  component-localization-form     country/language, header and drawer
  component-predictive-search     context: 'header' (or a plain form when disabled)
  component-cart-notification     settings.cart_type == 'notification'
  component-cart-drawer           settings.cart_type == 'drawer'
```

The header `<header id="main-header">` carries `x-data="{ searchOpen, searchTerm }"`
and `@click.outside` to close search. Each nav `<li>` carries its own Alpine
scope (`menuOpen`, and for dropdowns `activeSubMenu`) with `x-show`, `x-cloak`
and `x-transition`. The drawer carries `drawerOpen`. **This is Alpine's job by
the rules — ephemeral open/closed state — and it is what a rebuild should reuse
for the same job.**

Layout is a CSS grid: `auto 1fr auto` or `1fr auto 1fr` depending on
`logo_position`; `menu_position` left/center/right; mobile flips the columns
under `mobile_logo_position`. Sticky behaviour is a `sticky_header_type`
select — `none`, `on-scroll-up`, `always`, `reduce-logo-size` — implemented
with `position: sticky` and two classes the inline script toggles.

### The inline script, and the CSS variable it owns

The header ends with an inline `<script>` that sets `--header-height` on the
root from `offsetHeight` (on `load` and `resize`) and toggles
`.scrolled-header` and `.header-sticky` on scroll. `--header-height` (and
`--announcement-bar-height`, which nothing in the files read sets) is consumed
by the drawer and dropdown heights: `calc(100vh - var(--header-height) - var(--announcement-bar-height, 0px))`.

**Current state, not the standard:** this is a plain inline script, not a
custom element, and it binds `window` listeners it never removes. A rebuild
should put the same logic in a `<header-shell>` custom element with
`connectedCallback`/`disconnectedCallback` — the MiLB build did exactly this
and fixed `--header-height` reporting 80 when the header was 110.

### Settings contract

`color_scheme` and `menu_color_scheme` (both `color_scheme`), `padding_top` /
`padding_bottom` (`range` 0–36 step 4, default 20 — a narrower range than the
0–100 contract, deliberately), `margin_bottom`, `show_line_separator`,
`enable_country_selector`, `enable_language_selector`, `enable_customer_avatar`,
one `@app` block type with `max_blocks: 3`. No `presets` — correct for a
section-group member.

**Current state, not the standard:** `menu_position` and its options carry bare
English labels; the section uses a `{% style %}` block rather than a
`section-header.css`; the header's own breakpoint is **1024/1025px**, not the
750/769 the rest of the theme uses — a client build must pick one and the recon
must measure it, not assume it.

### Accessibility — what the frames cannot show

The dropdown's toggles are `<div class="menu-toggle">` (the megamenu's are
`<button>`); nothing sets `aria-expanded`; there is no Escape handling and no
focus management on open or close; the `#header-search` panel is shown by class
with no focus move into it. The MiLB parity audit's three high-severity findings
were all in this layer (a silent cart count, a drawer that announced nothing, a
failed variant switch). **For a rebuild these are requirements, not
inheritances** — see the build skill's overlay checklist: focus moved in on
open, returned to the trigger on close, Escape closes, `aria-expanded` on every
toggle, a small `aria-live="polite"` node for asynchronous status.

### Announcement bar

A section-group member with `announcement` blocks (text, link, emoji) and
`auto_rotate_interval`. **Current state, not the standard:** its colours are
`background_color`/`text_color` hex settings rather than a `color_scheme`, its
styles live in a `{% style %}` block in `rem` units where the theme is `px`,
and its breakpoint is a `max-width: 768px` query. Its script was not read.

### Footer

`sections/footer.liquid` loads `section-footer.css` with `stylesheet_tag`,
then a small inline `<style>` that hardcodes the section background to
`rgb(243, 243, 243)` beside the `color_scheme` setting it also exposes. Blocks:
`link_list`, `text`, `social_icons`, `brand_information`, `@app`. Renders the
localization form, payment icons (`shop.enabled_payment_types`), policies and
copyright. Spacing is a `margin_top` range, not the padding pair — the
compliance report scores it "padding present, top control only". Presets exist
(the footer group seeds one). **Current state:** "Follow Us" is a bare string.

---

## 3. The cart engine

### One module, one queue, one event

`assets/cart.js` replaced the `liquid-ajax-cart` library. It is a plain module
— **not a custom element** — that owns every Cart AJAX call:

```
window.Cart = {
  state,                       // seeded from #cart-data, refreshed after every mutation
  add(formData, source),       // POST /cart/add.js  (FormData, so selling plans and properties work)
  change({line|id, quantity}, source),   // POST /cart/change.js
  update({note|attributes}, source, { withSections }),  // POST /cart/update.js
  refresh(),                   // GET /cart.js + section HTML, no mutation
}
```

Every mutation runs through **one promise queue**, so rapid clicks cannot
race, and toggles `cart-busy` on `<html>` while anything is pending. On success
it dispatches `cart:change` on `document` with
`{ action, payload, response, cart, previousCart, sections, source }`; on
failure `cart:error` with `{ action, payload, error: { status, message,
description }, source }`.

### Section Rendering API, from the DOM

Before each mutation `sectionIds()` collects the `.shopify-section` ids of
every `cart-drawer` and `cart-page` on the page and sends them as
`sections=` plus `sections_url=` on the same request. Shopify returns the
re-rendered HTML of those sections in the response, and each component picks
its own fragment out of `event.detail.sections[sectionId]`. **Nothing is
hardcoded**: because the drawer is rendered inside the header section, its
section id is the header's, and the drawer extracts `#cart-drawer .drawer__wrapper`
from the header's HTML.

`add` is the one asymmetric call: `/cart/add.js` with FormData returns the
added line item, not the cart, so the engine fetches `/cart.js` afterwards for
state. `component-cart-notification.js` and `component-data-layer.js` rely on
that line-item shape in `response`.

### Wiring is delegation on markup that already works without JS

Three `document`-level listeners, no per-element binding:

| Event | Matches | Behaviour |
|---|---|---|
| `submit` | `form[action*="/cart/add"]` | prevent default, disable the button, show `.loading__spinner`, `Cart.add(FormData)`; on error write `error.description` into `.form-error` and `Cart.refresh()` (a 422 can still partially add) |
| `click` | `a[href*="/cart/change"]`, or anywhere in `.cart-item__remove` | read `line=` or `id=` and `quantity=` from the href; inside `.cart-quantity` step from the input's **current** value (so quick clicks accumulate) and debounce 250 ms per line; outside it, remove |
| `change` | `.cart-quantity input`; `textarea[name="note"]` inside `cart-drawer`/`cart-page` | typed quantity → same debounced path; note → `Cart.update({ note }, …, { withSections: false })` |

**Durable principle:** the markup is the API. Steppers are real links to
`/cart/change?line=N&quantity=M`, remove is `line_item.url_to_remove`,
add-to-cart is a real `<form action="/cart/add">`. With JS disabled every one
of them still works. A rebuild that invents `data-cart-action` attributes has
added a second contract for no gain.

### The three consumers

| Element | File | Owns | Re-render |
|---|---|---|---|
| `<cart-drawer>` | `component-cart-drawer.{liquid,js}` | open/close state (`.cart-open` class, no Alpine), overlay and close clicks, toggling on `#header-cart-bubble` clicks, note label toggle | swaps `.drawer__wrapper` innerHTML from the section HTML; preserves `.cart-items` scroll except after `add`, which opens the drawer and scrolls to top |
| `<cart-page>` | `sections/cart.liquid` + `component-cart-page.js` | nothing but re-rendering | replaces its own innerHTML from the section HTML |
| `<cart-notification>` | `component-cart-notification.{liquid,js}` | show/hide, close and continue buttons | builds the product summary from the `add` **response** (line item JSON), not from section HTML |

All three register behind `if (!customElements.get(...))`, bind
`onCartChange` in `connectedCallback` (the notification in its constructor)
and remove it in `disconnectedCallback`. `[data-cart-count]` anywhere on the
page is updated by the engine, which is how the header bubble stays current
without knowing the header exists.

`component-cart-discount.liquid` renders `<cart-discount-form>`; its script
"does its own requests" and then calls `Cart.refresh()` (per the engine's
comment) — the pattern for any component that talks to the cart outside the
engine: do the request, then `refresh()` so every consumer re-renders.

### Quick add

`<modal-opener data-modal="#…">` shows a spinner and calls `modal.show(button)`.
`<quick-add-modal>` fetches the product URL, extracts `product-info`, gives it
a unique section id (`${id}-modal-${Date.now()}`), sets `data-update-url="false"`
so the variant picker does not `replaceState`, strips pickup availability, the
media modal and recommendations, re-injects the scripts, and closes itself on
the `add` action of `cart:change`. **Current state:** it appends itself to
`document.body` in `connectedCallback` and wires most listeners in the
constructor.

### Accessibility

**Current state, not the standard:** the drawer has no `role="dialog"`, no
focus trap, no Escape handling and no live region; the notification has
`role="dialog" aria-modal="true"`. The MiLB build added a live region *inside
the dialog but outside the swapped region* so the announcement survives the
innerHTML swap — that placement is the pattern.

---

## 4. Search

### Predictive search

`component-predictive-search.liquid` renders `<predictive-search>` around a
real GET form to `routes.search_url` (`q`, `options[prefix]=last`), a reset
button, the empty `#predictive-search` results container, and — when
`context == 'header'` — an overlay wired to the header's Alpine `searchOpen`.
The input shares the header's Alpine scope through `x-model="searchTerm"`.

`component-predictive-search.js` is a custom element that debounces `input`
by 700 ms (the shared `debounce` from `theme.js`), then fetches
`/search/suggest?q=…&section_id=predictive-results` and injects the innerHTML
of `#shopify-section-predictive-results` from the response. **The results
markup is a section**, `sections/predictive-results.liquid`, rendered by the
Section Rendering API with the `predictive_search` object — no JSON endpoint,
no client-side templating. It has no schema and is not merchant-addable.

**Durable principle:** the same pattern as collection filtering — ask Shopify
to render a section, swap the fragment. A rebuild's search overlay is this
element plus states (empty, loading, results, no results), each a
`predictive-results` rendering condition, not a JS template.

**Current state, not the standard:** an `AbortController` is created but never
used to abort, so a slow earlier response can overwrite a later one; a
`console.log` is left in `onChange`; results open/close by toggling
`style.display`; the section's headings ("Suggestions", "Articles and Pages",
"Products", "Search for") and the form's placeholder and `aria-label`s are bare
English.

### The search page

`sections/search.liquid` **is the collection page pattern with `results: search`**:
`<collection-info data-section>`, `section-collection.js`, the three filter
snippets called with `results: search` and `context: 'search'`, the sort
`<select>` bound to the right form by `form=`, `data-render-section` /
`data-render-section-url`, the active-filter group, the product grid rendering
`component-product-card` / `component-article-card` / an inline page card by
`item.object_type`, infinite scroll or pagination. It loads
`section-collection.css` plus its own `section-search.css`. The Decisions Log's
open question — "does Base consider the search page the same pattern as
collection?" — is answered by the code: yes, down to the schema name it copied
(`t:sections.main-collection-product-grid.name`).

Padding pair and `color_scheme` present; no presets (template main). Breakpoints
in its style block are 769 and 990. Bare labels on the swatch and pagination
settings.

---

## 5. Patterns to follow

- Everything on every page is a section in a section group; the layout stays
  thin.
- One engine for the cart, on `window.Cart`, with one queue and two events.
  Components subscribe to `cart:change`; nothing else calls `/cart/*.js`.
- Ask for section HTML in the mutation itself (`sections=`), and let each
  component extract its own fragment by an id it reads from the DOM.
- Markup that works without JS is the contract: real forms, real
  `/cart/change` links, real GET search forms. JS intercepts; it does not
  replace.
- Alpine for open/closed state in the shell (search panel, drawer, menus);
  custom elements for anything that fetches, re-renders or syncs.
- Predictive results are a section rendered by Shopify, not a JS template.
- The search page reuses the collection orchestrator; a new faceted listing
  page does the same.
- Register every custom element behind `if (!customElements.get(...))`,
  subscribe in `connectedCallback`, unsubscribe in `disconnectedCallback`.
- Overlay accessibility is part of the build: dialog role, focus in and back,
  Escape, `aria-expanded` on toggles, a live region placed outside any region
  that gets swapped.

## 6. Anti-patterns to avoid

| Anti-pattern | Why it fails here |
|---|---|
| A second cart client (`fetch('/cart/add.js')` in a component) | Bypasses the queue, the state, the count sync and every subscriber. Use `Cart.add` or call `Cart.refresh()` after an external request. |
| Hardcoding the drawer's section id | The drawer lives inside the header section; its id is the header's, discovered by `closest('.shopify-section')`. |
| Re-rendering the whole `<cart-drawer>` | Loses open state and scroll position. Swap `.drawer__wrapper`. |
| Inventing `data-cart-*` attributes | The `/cart/change` links and `/cart/add` forms already carry every value. |
| Inline `<script>` on `window` for header behaviour | Listeners never removed, no lifecycle; wrap it in a custom element. |
| A JS template for predictive results | Shopify renders `predictive-results.liquid`; states are Liquid conditions. |
| A live region inside the region that gets swapped | The announcement is destroyed by the innerHTML swap before it is read. |
| `<div>` toggles without `aria-expanded` | Copies the current dropdown; the megamenu already uses `<button>`. |

## 7. Principle vs. implementation detail

| Topic | Durable principle | Base-specific detail (not a universal rule) |
|---|---|---|
| Shell | Section groups, thin layout | `header-group` = announcement-bar + header |
| Cart | One engine, one queue, `cart:change`/`cart:error`, section HTML in the mutation | `window.Cart`, `#cart-data` seed, 250 ms stepper debounce, `cart-busy` class |
| Drawer | Extract own fragment from section HTML | `#cart-drawer .drawer__wrapper`; toggled by `#header-cart-bubble` |
| Notification | Build from the `add` response | line-item JSON fields `image`, `product_title`, `options_with_values` |
| Header state | Alpine for open/closed; a custom element for measured layout | inline script sets `--header-height`; 1024/1025 breakpoint |
| Predictive search | Section-rendered results, debounced input | 700 ms; `/search/suggest?…&section_id=predictive-results` |
| Search page | Reuse the collection orchestrator | `collection-info` + `section-collection.js` with `results: search` |
