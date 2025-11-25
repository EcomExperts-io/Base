# component-cart-drawer Snippet

`snippets/component-cart-drawer.liquid` renders the slide-out cart drawer with line items, totals, cart note, and checkout actions. It pairs Alpine.js state (`cartOpen`) with the `<cart-drawer>` custom element and wires Liquid Ajax Cart bindings for real-time updates.

---

## What It Does

- Defines a documented snippet (`{% doc %}`) that merchants can include anywhere (usually the header/layout).
- Loads `cart.css` for drawer styling and outputs the `<cart-drawer>` wrapper with Alpine classes/attributes.
- Handles both empty and populated cart states, including localized messaging and optional featured collection.
- Iterates `cart.items` to render media, pricing, options, custom properties, discounts, and quantity controls.
- Includes footer content: cart note, cart discounts, estimated totals, and the checkout form.
- Imports `component-cart-drawer.js` and `cart-discount.js` modules for interactivity and discount handling.

---

## Dependencies & Assets

| Type   | Files / Components                                                                 |
|--------|-------------------------------------------------------------------------------------|
| CSS    | `cart.css`                                                                          |
| JS     | `component-cart-drawer.js`, `cart-discount.js`                                      |
| Snips  | `cart-discount`, inline SVG icons (checkmark, minus, plus, discount, etc.)          |
| Data   | Requires global `cart`, `settings.cart_color_scheme`, `settings.cart_drawer_collection`, `settings.show_cart_note` |

- Alpine.js powers `cartOpen`/`noteOpen` state toggles (expects surrounding layout to define Alpine component).
- AJAX bindings (`data-ajax-cart-*`) rely on Liquid Ajax Cart to keep contents in sync.

---

## Markup Overview

```liquid
<cart-drawer
  id="cart-drawer"
  class="color-{{ settings.cart_color_scheme }}"
  :class="{ 'cart-open': cartOpen }"
>
  <button class="drawer-overlay" @click="cartOpen = !cartOpen">…</button>
  <div class="drawer__wrapper" data-ajax-cart-section>
    {% if cart == empty %}
      <!-- Empty cart content -->
    {% else %}
      <!-- Cart header, items, footer -->
    {% endif %}
  </div>
</cart-drawer>
<script src="{{ 'component-cart-drawer.js' | asset_url }}" type="module"></script>
<script src="{{ 'cart-discount.js' | asset_url }}" type="module"></script>
```

- Wrapper uses `color-\{\{ settings.cart_color_scheme \}\}` for theme integration.
- Overlay button closes the drawer and is accessible via visually hidden text.
- `data-ajax-cart-section` ensures the drawer updates after AJAX actions.

---

## Empty State

- Shows a close icon button, “cart empty” heading (`sections.cart.empty`), `Continue shopping` link, and optional login prompt/statements for guests.
- If `settings.cart_drawer_collection` is set, displays the featured collection image/title as cross-sell content.

---

## Populated Cart

### Header
- Title uses `cart.title` translation and outputs `cart.item_count`.
- Close button toggles Alpine state.

### Items
- Loop over `cart.items`:
  - Media: product image or placeholder.
  - Details: title link, original/final price, options/properties/selling plan, line-level discounts with icons.
  - Quantity controls inside `<ajax-cart-quantity>` with `data-ajax-cart-quantity-*` bindings.
  - Remove link uses `line_item.url_to_remove` plus an inline close icon.
  - Totals show compare vs final line price.
  - Each item includes an `errors` block with `data-ajax-cart-errors`.

### Footer
- Optional cart note textarea toggled by Alpine `noteOpen`.
- Renders `cart-discount` snippet (discount code input/pills).
- Summary shows cart-level discounts, estimated total, and shipping/tax disclaimer.
- Checkout form posts via `form 'cart'`.

---

## Events & Behavior

- `<cart-drawer>` listens for custom events via `component-cart-drawer.js` (see asset doc) to open automatically after AJAX add-to-cart.
- `data-ajax-cart-section-scroll` on `.cart-items` enables automatic scroll-to-top when contents update.
- `data-ajax-cart-request-button` ensures remove links trigger AJAX refreshes.

---

## Usage Tips

1. Mount the snippet once (typically in `snippets/header.liquid` or `layout/theme.liquid`) so IDs remain unique.
2. Ensure Alpine component defines `cartOpen` state and listens for the global `cart-open` event (dispatched by the JS module).
3. Provide translations for all referenced keys (`cart.title`, `cart.remove`, `cart.checkout`, etc.).
4. Keep icon assets (`icon-close.svg`, `icon-discount.svg`, etc.) available in `assets/`.
5. When customizing layout, maintain `data-ajax-cart-` attributes so Liquid Ajax Cart keeps working.

