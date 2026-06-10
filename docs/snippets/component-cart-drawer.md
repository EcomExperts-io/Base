# component-cart-drawer Snippet

`snippets/component-cart-drawer.liquid` renders the slide-out cart drawer with line items, totals, cart note, and checkout actions. The `<cart-drawer>` custom element (`component-cart-drawer.js`) owns the open/close state and re-renders the wrapper from the section HTML bundled with every `cart:change` event — no Alpine.js involved.

---

## What It Does

- Defines a documented snippet (`{% doc %}`) that merchants can include anywhere (usually the header/layout).
- Loads `cart.css` for drawer styling and outputs the `<cart-drawer>` wrapper.
- Handles both empty and populated cart states, including localized messaging and optional featured collection.
- Iterates `cart.items` to render media, pricing, options, custom properties, discounts, and quantity controls.
- Includes footer content: cart note, cart discounts, estimated totals, and the checkout form.
- Imports `component-cart-drawer.js` and `component-cart-discount.js` modules for interactivity and discount handling.

---

## Dependencies & Assets

| Type   | Files / Components                                                                 |
|--------|-------------------------------------------------------------------------------------|
| CSS    | `cart.css`                                                                          |
| JS     | `component-cart-drawer.js`, `component-cart-discount.js`                            |
| Snips  | `component-cart-discount`, inline SVG icons (checkmark, minus, plus, discount, etc.)|
| Data   | Requires global `cart`, `settings.cart_color_scheme`, `settings.cart_drawer_collection`, `settings.show_cart_note` |

- Open/close state lives on the `<cart-drawer>` element itself (a `cart-open` class) — no Alpine state or wrapper needed.
- Line items, totals, and the note stay in sync via the native cart engine (`assets/cart.js`): every mutation bundles fresh section HTML, and the drawer re-renders its `.drawer__wrapper` from it.

---

## Markup Overview

```liquid
<cart-drawer
  id="cart-drawer"
  class="color-{{ settings.cart_color_scheme }}"
>
  <button class="drawer-overlay">…</button>
  <div class="drawer__wrapper">
    {% if cart == empty %}
      <!-- Empty cart content -->
    {% else %}
      <!-- Cart header, items, footer -->
    {% endif %}
  </div>
</cart-drawer>
<script src="{{ 'component-cart-drawer.js' | asset_url }}" type="module"></script>
<script src="{{ 'component-cart-discount.js' | asset_url }}" type="module"></script>
```

- Wrapper uses `color-\{\{ settings.cart_color_scheme \}\}` for theme integration.
- Clicking `.drawer-overlay` or `.cart-drawer__close` closes the drawer (handled inside the custom element); the overlay button stays accessible via visually hidden text.
- The element re-renders `.drawer__wrapper` whenever a `cart:change` event carries section HTML for its section id.

---

## Empty State

- Shows a close icon button, “cart empty” heading (`sections.cart.empty`), `Continue shopping` link, and optional login prompt/statements for guests.
- If `settings.cart_drawer_collection` is set, displays the featured collection image/title as cross-sell content.

---

## Populated Cart

### Header
- Title uses `cart.title` translation and outputs `cart.item_count`.
- `.cart-drawer__close` click is handled by the custom element and closes the drawer.

### Items
- Loop over `cart.items`:
  - Media: product image or placeholder.
  - Details: title link, original/final price, options/properties/selling plan, line-level discounts with icons.
  - Quantity controls inside a plain `<div class="cart-quantity">` — `cart.js` intercepts the `/cart/change` stepper links and the input's `change` events via delegation (rapid clicks are debounced into one request).
  - Remove link uses `line_item.url_to_remove` plus an inline close icon (also intercepted by `cart.js`).
  - Totals show compare vs final line price.
  - Each item includes an errors block with an empty `.cart-item__error` div that `cart.js` fills on failure.

### Footer
- Optional cart note textarea; the label's `note-open` class is toggled by the custom element, and `cart.js` auto-saves the note to `/cart/update.js` on `change`.
- Renders `component-cart-discount` snippet (discount code input/pills).
- Summary shows cart-level discounts, estimated total, and shipping/tax disclaimer.
- Checkout form posts via `form 'cart'` with id `cart-checkout-form` (the quantity inputs reference it via their `form` attribute).

---

## Events & Behavior

- `<cart-drawer>` listens for `cart:change` on `document` (see asset doc): it re-renders `.drawer__wrapper` from the bundled section HTML and opens automatically when the action is `add`.
- The `.cart-items` scroll position is preserved across re-renders; after an add it scrolls back to the top.
- Clicking `#header-cart-bubble` toggles the drawer (intercepted by the element); the bubble itself is a plain link to `/cart` as a no-JS fallback.
- While a cart request is in flight, `cart.js` adds `cart-busy` to `<html>` and `cart.css` dims `.cart-items`.

---

## Usage Tips

1. Mount the snippet once (typically in `sections/header.liquid` or `layout/theme.liquid`) so IDs remain unique.
2. Keep the `.drawer__wrapper`, `.drawer-overlay`, and `.cart-drawer__close` hooks intact — the custom element relies on them for re-rendering and close behavior.
3. Provide translations for all referenced keys (`cart.title`, `cart.remove`, `cart.checkout`, etc.).
4. Keep icon assets (`icon-close.svg`, `icon-discount.svg`, etc.) available in `assets/`.
5. When customizing layout, keep `.cart-quantity` around the stepper, the `/cart/change` link hrefs, and `.cart-item__error` divs so the cart engine keeps working.

