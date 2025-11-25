# CartDrawer Web Component

`assets/component-cart-drawer.js` registers `<cart-drawer>`, a tiny helper element that listens for Liquid Ajax Cart events and tells Alpine.js to open the cart drawer whenever an item is added.

**Source:** [`assets/component-cart-drawer.js`](../../assets/component-cart-drawer.js)

---

## What It Does

- Extends `HTMLElement` to define `<cart-drawer>`.
- Subscribes to `liquid-ajax-cart:request-end` on `document`.
- When an add-to-cart request succeeds, dispatches a global `cart-open` event.
- Relies on the header/layout Alpine instance to listen for `cart-open` and toggle `cartOpen = true`.

---

## API Overview

| Method / Lifecycle       | Purpose                                                     |
|-------------------------|-------------------------------------------------------------|
| `constructor()`         | Binds `onCartRequestEnd` to the instance.                   |
| `connectedCallback()`   | Adds the document-level event listener.                     |
| `disconnectedCallback()`| Removes the listener to avoid leaks when detached.          |
| `onCartRequestEnd(e)`   | Checks request metadata and fires the `cart-open` event     |

---

## Detailed Methods

### constructor()
- Calls `super()`.
- Binds `this.onCartRequestEnd = this.onCartRequestEnd.bind(this);` so the handler can be added/removed cleanly.

### connectedCallback()
```js
connectedCallback() {
  document.addEventListener('liquid-ajax-cart:request-end', this.onCartRequestEnd);
}
```
- Runs when the element enters the DOM (usually when the snippet renders).
- Enables global listening without polluting other parts of the app.

### disconnectedCallback()
```js
disconnectedCallback() {
  document.removeEventListener('liquid-ajax-cart:request-end', this.onCartRequestEnd);
}
```
- Cleans up when the element is removed (e.g., snippet unmounted).

### onCartRequestEnd(event)
```js
onCartRequestEnd(event) {
  const { requestState } = event.detail || {};
  if (requestState?.requestType === 'add' && requestState?.responseData?.ok) {
    window.dispatchEvent(new CustomEvent('cart-open'));
  }
}
```
- Guard clauses ensure only successful `add` requests trigger the drawer.
- `cart-open` is a simple `CustomEvent` that other scripts (Alpine, theme JS) can listen for.

---

## Registration

```js
if (!customElements.get('cart-drawer')) {
  customElements.define('cart-drawer', CartDrawer);
}
```

- The guard prevents redefinition during hot reloads or multiple imports.

---

## Integration with Alpine / Theme

In `component-cart-drawer.liquid`, the `<cart-drawer>` element typically sits inside an Alpine component that defines `cartOpen`:

```html
<div x-data="{ cartOpen: false }" x-on:cart-open.window="cartOpen = true">
  {% render 'component-cart-drawer' %}
</div>
```

- When `component-cart-drawer.js` dispatches `cart-open`, Alpine updates `cartOpen` and the drawer slides in.
- The same Alpine scope usually toggles the drawer overlay buttons via `@click="cartOpen = !cartOpen"`.

---

## Implementation Notes

1. Ensure Liquid Ajax Cart is enabled so `liquid-ajax-cart:request-end` fires; otherwise the component does nothing.
2. Only one `<cart-drawer>` should exist per page; multiple instances could open conflicting UI states.
3. If you need to close the drawer programmatically after checkout, dispatch a parallel event (e.g., `window.dispatchEvent(new CustomEvent('cart-close'))`) and handle it in Alpine.
4. Wrapper uses `color-\{\{ settings.cart_color_scheme \}\}` for theme integration.
