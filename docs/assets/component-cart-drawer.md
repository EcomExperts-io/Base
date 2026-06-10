# CartDrawer Web Component

`assets/component-cart-drawer.js` registers `<cart-drawer>`, the element that owns the cart drawer's open/close state (no Alpine.js) and re-renders its contents from the section HTML that `cart.js` bundles into every cart mutation.

**Source:** [`assets/component-cart-drawer.js`](../../assets/component-cart-drawer.js)

---

## What It Does

- Extends `HTMLElement` to define `<cart-drawer>`.
- Owns open/close state by toggling its own `cart-open` class — no external state manager required.
- Intercepts clicks on `#header-cart-bubble` (a plain link to `/cart`, kept as a no-JS fallback) and toggles the drawer instead.
- Closes when `.drawer-overlay` or `.cart-drawer__close` is clicked; toggles the `note-open` class on the cart note label.
- Subscribes to `cart:change` on `document` and re-renders its `.drawer__wrapper` from `event.detail.sections`.
- Opens automatically when the event's `action` is `'add'`.

---

## API Overview

| Method / Lifecycle       | Purpose                                                                  |
|-------------------------|---------------------------------------------------------------------------|
| `constructor()`         | Binds `onCartChange` and `onDocumentClick` to the instance.               |
| `connectedCallback()`   | Adds the `cart:change` and document `click` listeners plus inner clicks.  |
| `disconnectedCallback()`| Removes the document-level listeners to avoid leaks when detached.        |
| `sectionId` (getter)    | Reads the section id from the closest `.shopify-section` ancestor.        |
| `open()` / `close()` / `toggle()` | Add / remove / toggle the `cart-open` class on the element.     |
| `onDocumentClick(e)`    | Toggles the drawer when `#header-cart-bubble` is clicked.                 |
| `onInnerClick(e)`       | Handles overlay/close clicks and the cart note label toggle.              |
| `onCartChange(e)`       | Re-renders from section HTML; opens the drawer after adds.                |
| `render(html, action)`  | Swaps `.drawer__wrapper` content, preserving scroll position.             |

---

## Detailed Methods

### sectionId

```js
get sectionId() {
  return this.closest('.shopify-section')?.id.replace('shopify-section-', '');
}
```

- Nothing is hardcoded — `cart.js` uses the same lookup to know which sections to request from the Section Rendering API.

### onDocumentClick(event)

```js
onDocumentClick(event) {
  const bubble = event.target.closest('#header-cart-bubble');
  if (bubble) {
    event.preventDefault();
    this.toggle();
  }
}
```

- The header cart bubble is a plain `<a href="{{ routes.cart_url }}">`; with JS active the drawer intercepts it, without JS the link still navigates to the cart page.

### onInnerClick(event)

```js
onInnerClick(event) {
  if (event.target.closest('.drawer-overlay, .cart-drawer__close')) {
    this.close();
    return;
  }

  const noteLabel = event.target.closest('.cart-note label');
  if (noteLabel) noteLabel.classList.toggle('note-open');
}
```

- One delegated listener covers the overlay, the close button, and the cart note label — all of which are re-rendered DOM, so delegation keeps them working after updates.

### onCartChange(event)

```js
onCartChange(event) {
  const html = event.detail.sections?.[this.sectionId];
  if (html) this.render(html, event.detail.action);
  if (event.detail.action === 'add') this.open();
}
```

- `event.detail.sections` is the Section Rendering API HTML bundled by `cart.js` into every mutation (`add`, `change`, `update`, `refresh`).
- After a successful add-to-cart the drawer opens automatically.

### render(html, action)

```js
render(html, action) {
  const next = new DOMParser().parseFromString(html, 'text/html').querySelector('#cart-drawer .drawer__wrapper');
  const current = this.querySelector('.drawer__wrapper');
  if (!next || !current) return;

  const scrollTop = current.querySelector('.cart-items')?.scrollTop || 0;
  current.innerHTML = next.innerHTML;

  const items = current.querySelector('.cart-items');
  if (items) items.scrollTop = action === 'add' ? 0 : scrollTop;
}
```

- Preserves the `.cart-items` scroll position across quantity changes; scrolls back to the top after an add so the shopper sees the new item.

---

## Registration

```js
if (!customElements.get('cart-drawer')) {
  customElements.define('cart-drawer', CartDrawer);
}
```

- The guard prevents redefinition during hot reloads or multiple imports.

---

## Integration with the Cart Engine

The drawer is a consumer of `assets/cart.js` (loaded globally from `layout/theme.liquid`):

```js
document.addEventListener('cart:change', this.onCartChange);
```

- `cart:change` detail: `{ action, payload, response, cart, previousCart, sections, source }`.
- Quantity steppers, remove links, and the cart note inside the drawer need no wiring here — `cart.js` handles them via document-level event delegation (`a[href*="/cart/change"]`, `.cart-quantity input`, `textarea[name="note"]`).
- While requests are in flight, `cart.js` sets `html.cart-busy` and `cart.css` dims `.cart-items`.

---

## Implementation Notes

1. Only one `<cart-drawer>` should exist per page; multiple instances could open conflicting UI states.
2. The drawer must live inside a `.shopify-section` wrapper so `sectionId` (and therefore section re-rendering) works.
3. To open or close the drawer programmatically, call the element's methods directly, e.g. `document.querySelector('cart-drawer')?.open()`.
4. Wrapper uses `color-\{\{ settings.cart_color_scheme \}\}` for theme integration.
