# Cart Engine

The cart is three JavaScript layers plus presentation components that only swap HTML.

| Layer | File | Job |
|---|---|---|
| Transport | `assets/cart-api.js` | The only file with `/cart/*.js` URLs. JSON bodies, `sections` forwarding, `CartApiError`. |
| Store | `assets/cart-store.js` | `window.Cart`: state, one request queue, events, `subscribe()`, `use()` for rules. |
| Rules | `assets/cart-rules.js` | Gift with purchase, kit integrity. Return mutations, never touch the DOM. |
| Presentation | `section-cart-drawer.js`, `section-cart.js`, `component-cart-line-item.js`, `component-cart-count.js`, `component-cart-discount.js`, `component-product-form.js` | Subscribe, swap HTML, call `Cart.*`. Never fetch. |

Loaded from `layout/theme.liquid`: `cart-store.js`, `component-cart-count.js`, `component-product-form.js` and `component-cart-rules` (config JSON plus `cart-rules.js`). The layout also renders the static sections `cart-json` and, when the cart type is drawer, `cart-drawer`.

---

## Requests

Every mutation posts JSON and includes `sections` for each element on the page carrying `data-cart-section`, plus the `cart-json` section. Shopify renders them in the same response. The store reads new state from the `cart-json` HTML, so an add is one request. Without that section on the page, an add falls back to a `GET /cart.js`.

Lines are addressed by `line_item.key`, never by index.

## Store API

```js
Cart.state                       // latest cart JSON
Cart.pending                     // jobs in flight; <html class="cart-busy"> while > 0
Cart.add(items, { source })      // items: [{ id, quantity, properties, selling_plan }]
Cart.change(key, quantity, { properties, sellingPlan, source })
Cart.update({ note, attributes, discount, updates }, { source, withSections })
Cart.clear()
Cart.refresh()                   // state + sections, no mutation, no rules
Cart.subscribe(fn)               // fn(detail); returns unsubscribe
Cart.use(rule)                   // rule(detail) → mutation[]
```

## Events on `document`

- `cart:change` — `{ action, payload, response, cart, previousCart, sections, source }`. `action` is `add | change | update | clear | refresh`. For `add`, `response` is `{ items: [...] }`.
- `cart:error` — `{ action, payload, error: { status, message, description }, source }`.
- `cart:count` — `{ count, optimistic }`. Fired immediately on add (optimistic) and again when confirmed. `<cart-count>` renders it; the header is never part of a section render.

## Rules

A rule is `(detail) => mutation[]`. Mutations are `{ type: 'add', items }`, `{ type: 'change', key, quantity }` or `{ type: 'update', ... }`. The store queues them with `source: 'rule'` and re-runs rules on the result up to depth 2, then stops. Rules must be idempotent.

Config comes from `snippets/component-cart-rules.liquid`, which renders theme settings as JSON. The gift threshold setting is in the store currency and converted to cents there.

Property vocabulary (underscore prefix hides them in cart and checkout):

| Property | Meaning |
|---|---|
| `_gwp` | gift rule id; the line is locked (no stepper, no remove) |
| `_kit_id` | shared across every line of one kit |
| `_kit_role` | `parent` or `child` |

## Markup hooks

| Hook | Read by |
|---|---|
| `data-cart-section` | store: section is re-rendered on every mutation |
| `<cart-line-item data-key>` with `[data-step]`, `[data-remove]`, `.cart-quantity input` | `component-cart-line-item.js` |
| `[data-cart-open]` | `section-cart-drawer.js` opens the drawer |
| `[data-drawer-close]` | `section-cart-drawer.js` closes it |
| `<product-form>` wrapping `form[action*="/cart/add"]` with `button[name="add"]`, `.loading__spinner`, `.form-error` | `component-product-form.js` |
| `<cart-discount-form data-codes data-error-invalid data-error-generic>` | `component-cart-discount.js` |
| `textarea[data-cart-note]` | `section-cart-drawer.js` / `section-cart.js` save the note on change |

## Liquid

- `sections/cart-drawer.liquid` and `sections/cart.liquid` both render `component-cart-line-item` and `component-cart-summary`, so a line-item change is made once.
- `component-cart-line-item` handles default lines, `item_components` (Shopify Bundles / Cart Transform), kit children and gifts. Steppers respect `variant.quantity_rule`. The `<a>` links work without JavaScript.
- `component-cart-discount` renders pills from the cart's discount applications. Nothing about discounts is built in JavaScript.

## Known gaps

- `component-cart-notification.js` still builds its product summary in JavaScript from `response.items[0]`. It should become a rendered section.
- `component-quick-add.js` still fetches the whole product page. It should request the product section by `section_id`.
