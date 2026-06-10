# CartPage Web Component

`assets/component-cart-page.js` registers `<cart-page>`, a small wrapper element around the cart page section content (`sections/cart.liquid`) that re-renders itself from the section HTML that `cart.js` bundles into every cart mutation.

**Source:** [`assets/component-cart-page.js`](../../assets/component-cart-page.js)

---

## What It Does

- Extends `HTMLElement` to define `<cart-page>`.
- Subscribes to `cart:change` on `document`.
- Reads its own section id from the closest `.shopify-section` ancestor.
- When the event's `detail.sections` contains HTML for that section id, swaps in the freshly rendered `<cart-page>` inner HTML.

---

## API Overview

| Method / Lifecycle       | Purpose                                                        |
|-------------------------|------------------------------------------------------------------|
| `constructor()`         | Binds `onCartChange` to the instance.                            |
| `connectedCallback()`   | Adds the `cart:change` listener on `document`.                   |
| `disconnectedCallback()`| Removes the listener to avoid leaks when detached.               |
| `sectionId` (getter)    | Reads the section id from the closest `.shopify-section`.        |
| `onCartChange(e)`       | Re-renders from the bundled Section Rendering API HTML.          |

---

## Detailed Methods

### onCartChange(event)

```js
onCartChange(event) {
  const html = event.detail.sections?.[this.sectionId];
  if (!html) return;

  const next = new DOMParser().parseFromString(html, 'text/html').querySelector('cart-page');
  if (next) this.innerHTML = next.innerHTML;
}
```

- `event.detail.sections` is the Section Rendering API HTML that `cart.js` requests alongside every mutation (`add`, `change`, `update`, `refresh`).
- The element replaces its own children with the newly rendered `<cart-page>` content, so quantities, totals, discounts, and the empty state all stay in sync without a page reload.

---

## Registration

```js
if (!customElements.get('cart-page')) {
  customElements.define('cart-page', CartPage);
}
```

- The guard prevents redefinition during hot reloads or multiple imports.

---

## Integration with Shopify Liquid

`sections/cart.liquid` wraps its entire body in the element and loads the module:

```liquid
<cart-page>
  <!-- cart header, items, footer / empty state -->
</cart-page>

<script src="{{ 'component-cart-page.js' | asset_url }}" type="module"></script>
```

- Quantity steppers, remove links, and the cart note inside the section need no wiring here — `cart.js` handles them via document-level event delegation.
- The presence of `<cart-page>` on the page is also what tells `cart.js` to request this section's HTML with every mutation (it collects section ids from `<cart-drawer>` / `<cart-page>` elements).

---

## Implementation Notes

1. The element must live inside a `.shopify-section` wrapper so `sectionId` resolves and the engine can request the right section HTML.
2. Re-rendering replaces all children — avoid storing transient JS state inside the section; delegated listeners (as used by `cart.js` and `<cart-discount-form>`) survive re-renders.
3. While a cart request is in flight, `cart.js` sets `html.cart-busy` and `cart.css` dims `.cart-items` for feedback.
