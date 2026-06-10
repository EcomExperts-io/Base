# Native Cart — remove liquid-ajax-cart, keep everything else as-is

## The idea

One new file, `assets/cart.js` (~170 lines, no dependencies), replaces the library.
No new sections, no drawer restructuring, no `data-cart-*` attribute system.
We only **remove** library artifacts from the markup — we don't add a replacement framework.
Cart UI (drawer / cart page / notification) ends up with **zero Alpine dependency** — Alpine stays only for header search/menu, untouched.

It works because the markup already says everything we need:

- Add-to-cart forms already post to `/cart/add` → intercept `submit` with one document-level listener.
- The +/− steppers and Remove links are already anchors to `/cart/change?line=X&quantity=Y` → intercept `click`, parse the href, POST it instead. (Remove is just quantity=0 — same code path.)
- Re-rendering: the drawer sits inside the header section, so after any cart change we ask Shopify for that section's HTML (Section Rendering API, `sections` param on the same request) and each cart component swaps its own chunk. Same for the cart page section. Section IDs are read from the DOM (`closest('.shopify-section').id`) — nothing hardcoded.
- No JS → everything still works: forms post natively, links navigate natively, header bubble goes to /cart.

## Structure

### `assets/cart.js` — API core (plain module, no DOM, not a custom element)

```
window.Cart = {
  state,                 // cart JSON, seeded from an inline {{ cart | json }} script tag
  add(formData),         // POST /cart/add.js  (FormData — keeps selling plans/properties working)
  change(line, qty),     // POST /cart/change.js
  update(payload),       // POST /cart/update.js  (note, attributes)
  refresh(),             // re-fetch sections + dispatch (used by the discount form)
}
```

- Tiny promise-chain queue serializes mutations (rapid +/− can't race); `html.cart-busy` toggled while working (CSS twin of `js-ajax-cart-processing`).
- Document-level delegation (the only "wiring"):
  - `submit` on `form[action*="/cart/add"]` → `Cart.add` + button spinner/disable
  - `click` on `a[href*="/cart/change"]` inside cart UI → `Cart.change`
  - `change` on quantity inputs → `Cart.change` (line number parsed from the sibling anchor's href)
  - `change` on the note textarea → `Cart.update({ note })` — **fixes the lost-notes bug** (textarea points at a form id that doesn't exist)
- Syncs all `[data-cart-count]` badges from `cart.item_count` (attribute already exists in the header; notification count span switches to it).
- Errors (422 sold-out etc.): Shopify's `description` shown verbatim in the error `<div>` already in each `.cart-item` / product form.
- Dispatches **one success event** `cart:change` on `document` — detail `{ action, payload, response, cart, previousCart, sections }` — and `cart:error` on failure. That's the whole public contract.

### Custom elements (all vanilla, no Alpine)

- **`<cart-drawer>`** (upgrade existing element in `component-cart-drawer.js`):
  - open/close = toggling its own `cart-open` class (same class CSS already uses)
  - opens on `cart:change` with `action === 'add'`
  - delegated clicks on itself: overlay + close button (survives re-renders); document-level click intercept for `#header-cart-bubble`
  - note accordion: toggles the existing `note-open` class (replaces Alpine `noteOpen`)
  - re-renders its own `.drawer__wrapper` from `detail.sections` on every `cart:change`, preserving `.cart-items` scrollTop; root element never replaced
- **`<cart-page>`** (new, thin — wraps the cart section content in `sections/cart.liquid`): re-renders itself from `detail.sections`.
- **`<cart-notification>`** (already vanilla): event swap only — `liquid-ajax-cart:request-end` → `cart:change`, `requestState.responseData.body` → `detail.response`. Count span gets `data-cart-count`.
- **`<cart-discount-form>`** (already vanilla): `window.liquidAjaxCart.update({},{})` → `Cart.refresh()`.

## Alpine removal (cart only)

| Today (Alpine) | After (vanilla) |
| --- | --- |
| header wrapper `x-data="{ cartOpen }"` + `@cart-open.window` | deleted — drawer owns its state |
| bubble `@click.prevent="cartOpen = !cartOpen"` (drawer mode) | plain `href="{{ routes.cart_url }}"` always; `<cart-drawer>` intercepts the click when present |
| drawer root `:class="{ 'cart-open': cartOpen }"` | element toggles `cart-open` class itself |
| overlay/close `@click` | delegated listener in the element |
| note `x-data="{ noteOpen }"` + `@click`/`:class` | delegated toggle of `note-open` class |

Cart page and notification already have zero Alpine — verified.

## File changes

**New**
- `assets/cart.js`

**Edited (mechanical)**
- `layout/theme.liquid` — replace library block (52-59) with `<script type="application/json" id="cart-data">{{ cart | json }}</script>` + `<script src="cart.js" type="module">`
- `snippets/component-cart-drawer.liquid` — strip `data-ajax-cart-*` + all Alpine directives; `<ajax-cart-quantity>` → `<div class="cart-quantity">`; error div → class; note textarea drops dead `form="cart"`
- `sections/cart.liquid` — same cleanup + `<cart-page>` wrapper
- `sections/product.liquid` + `snippets/component-product-card.liquid` — delete `<ajax-cart-product-form>` wrappers; error div → class
- `sections/header.liquid` — bubble becomes a plain link (conditional Alpine attrs deleted); badge keeps `data-cart-count`, loses `data-ajax-cart-bind`; cart `x-data` wrapper attrs deleted
- `snippets/component-cart-notification.liquid` — drop `data-ajax-cart-section`; count span → `data-cart-count`
- JS event swaps: `component-cart-drawer.js` (gains the open/close/render logic), `component-cart-notification.js`, `component-quick-add.js`, `component-data-layer.js` (GTM pushes stay byte-identical; `previousCart` replaces its request-start snapshot trick; `window.liquidAjaxCart.cart` → `Cart.state`), `component-cart-discount.js`
- `assets/cart.css` — rename: `ajax-cart-quantity` → `.cart-quantity`, `html.js-ajax-cart-processing` → `html.cart-busy`, error `:empty` selector → class version

**Deleted**
- `assets/liquid-ajax-cart-v2.1.1.js`

**Docs** — README.md, docs/*.md, `.cursor/rules/javascript-standards.mdc` mention the library; update after code lands.

## Order of work

1. `assets/cart.js` + wire in `theme.liquid`, drop library import — cart runs native.
2. Markup cleanup (drawer, cart page, product forms, header, notification) incl. Alpine removal.
3. Event swap in dependent JS; `<cart-drawer>` gains its own open/close.
4. CSS renames; delete library file.
5. Verify, then docs.

## What stays the same

- Drawer stays a snippet in the header section; same classes, same animations, same CSS.
- All three cart types (drawer / page / notification) keep working.
- Same GTM dataLayer pushes.
- FormData add response shape (top-level line item) preserved — notification + data layer depend on it.

## Verify

`shopify theme dev`: add from PDP / quick-add / modal; +/−, typed qty, remove, last-item empty state (drawer + cart page); discount apply/remove; note reaches checkout; badge count; notification mode toast; GTM events identical; sold-out 422 shows message; everything with JS disabled still navigates. Then `grep -ri "ajax-cart\|liquidAjaxCart"` → zero hits in theme code. No `x-data|@click|:class` left in cart drawer/page/notification files.
