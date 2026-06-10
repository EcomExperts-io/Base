# Cart Engine (`assets/cart.js`)

`assets/cart.js` is the theme's native cart engine (it replaces the third-party liquid-ajax-cart library). It owns all Cart AJAX API calls, serializes them through a queue, and asks Shopify to render the cart sections in the same request (Section Rendering API) so cart components can re-render themselves. It is loaded as an ES module from `layout/theme.liquid` on every page.

**Source:** [`assets/cart.js`](../../assets/cart.js)

---

## What It Does

- Exposes a global API: `window.Cart = { state, add, change, update, refresh }`.
- Reads initial cart state from `<script type="application/json" id="cart-data">{{ cart | json }}</script>` in `layout/theme.liquid`.
- Serializes every mutation through a promise queue so rapid clicks can't race; while requests are in flight, `<html>` gets a `cart-busy` class (`cart.css` dims `.cart-items`).
- Bundles Section Rendering API HTML into every mutation via the `sections` request param — section ids are read from the DOM (`closest('.shopify-section')`) for any `<cart-drawer>` / `<cart-page>` elements present, nothing is hardcoded.
- Dispatches `cart:change` on success and `cart:error` on failure (both on `document`).
- Syncs every `[data-cart-count]` element from `cart.item_count` on init and after every mutation.
- Wires all cart UI through document-level event delegation — no wrapper elements or data attributes needed.

---

## Public API

| Method | Purpose |
|--------|---------|
| `Cart.state` | The latest cart JSON (initialized from `#cart-data`, updated after every mutation). |
| `Cart.add(formData, source)` | POSTs FormData to `/cart/add.js`. The response is the added line item at the top level — `component-data-layer.js` and `component-cart-notification.js` rely on that shape. |
| `Cart.change(payload, source)` | POSTs `{ line, quantity }` (or `{ id, quantity }`) to `/cart/change.js`. |
| `Cart.update(payload, source, options)` | POSTs `{ note }` / `{ attributes }` to `/cart/update.js`. Pass `{ withSections: false }` to skip section rendering. |
| `Cart.refresh()` | Re-fetches `/cart.js` plus the cart section HTML without mutating — used after external cart changes (e.g. the discount form does its own requests). |

All mutation methods return a promise that resolves with the raw response and reject with an error carrying `status` and `description`.

---

## Events

### `cart:change` (success)

```js
document.addEventListener('cart:change', (event) => {
  const { action, payload, response, cart, previousCart, sections, source } = event.detail;
});
```

- `action`: `'add' | 'change' | 'update' | 'refresh'`.
- `response`: the raw endpoint response (for `add`, the added line item; otherwise the cart).
- `cart` / `previousCart`: cart state after / before the mutation.
- `sections`: Section Rendering API HTML keyed by section id (or `null`).
- `source`: the DOM element that triggered the mutation (or `null`).

### `cart:error` (failure)

```js
document.addEventListener('cart:error', (event) => {
  const { action, payload, error, source } = event.detail;
  // error: { status, message, description }
});
```

---

## Event Delegation

The engine wires existing markup via three document-level listeners:

| Listener | Target | Behavior |
|----------|--------|----------|
| `submit` | `form[action*="/cart/add"]` | Prevents default, disables the submit button, shows its `.loading__spinner`, calls `Cart.add(new FormData(form), form)`. Errors render into the form's `.form-error` div, and a `Cart.refresh()` re-syncs the UI (a 422 can still partially add the max available quantity). |
| `click` | `a[href*="/cart/change"]` | Quantity steppers inside `.cart-quantity` step from the input's current value, with a 250ms debounce that collapses rapid +/- clicks into one request; links outside a stepper are remove links (`quantity=0`). Errors render into the line's `.cart-item__error` div. |
| `change` | `.cart-quantity input` | Typed quantities go through the same debounced line change. |
| `change` | `cart-drawer textarea[name="note"]`, `cart-page textarea[name="note"]` | Auto-saves the cart note via `/cart/update.js` (this fixed a bug — the note previously pointed at a nonexistent form id and was never saved). |

---

## Integration with Liquid

`layout/theme.liquid` provides the initial state and loads the engine:

```liquid
<script type="application/json" id="cart-data">
  {{ cart | json }}
</script>
<script src="{{ 'cart.js' | asset_url }}" type="module"></script>
```

Consumers:

- `<cart-drawer>` (`component-cart-drawer.js`) — re-renders from `detail.sections`, opens on `add`.
- `<cart-page>` (`component-cart-page.js`) — re-renders the cart page section from `detail.sections`.
- `<cart-notification>` (`component-cart-notification.js`) — builds the add-to-cart toast from `detail.response`.
- `<quick-add-modal>` (`component-quick-add.js`) — closes modals and resets spinners on `add`.
- `<cart-discount-form>` (`component-cart-discount.js`) — calls `Cart.refresh()` after applying/removing codes.
- GTM data layer (`component-data-layer.js`) — derives add/remove/update events from `detail.response` and `detail.previousCart`.

---

## Implementation Notes

1. Add-to-cart posts FormData (not JSON), so `/cart/add.js` responds with the added line item at the top level — keep this in mind when consuming `detail.response` for `add` actions; after an add the engine re-fetches `/cart.js` for the full cart state.
2. Section ids are discovered from the DOM at request time, so the same code works whether the page has a drawer, a cart page, both, or neither.
3. If the `#cart-data` script is missing, the engine falls back to fetching `/cart.js` on init.
4. `cart:change` only fires on success — consumers don't need to check response status.
5. Keep the delegated-markup hooks intact when customizing templates: `form[action*="/cart/add"]`, `.form-error`, `.cart-quantity`, `a[href*="/cart/change"]`, `.cart-item__error`, and `textarea[name="note"]`.
