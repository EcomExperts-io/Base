# CartNotification Component 🔔

Meet `<cart-notification>`, a lightweight Web Component defined in `assets/component-cart-notification.js` that keeps shoppers informed after an AJAX add-to-cart. It listens for Liquid Ajax Cart events, swaps in the latest product details, and controls the cart notification drawer UI.

---

## Overview
- Registers a custom element so multiple notifications can coexist safely.
- Listens for `liquid-ajax-cart:request-end` events to detect successful add-to-cart actions.
- Injects product title, media, and option values into the notification panel.
- Provides helper methods to show and hide the drawer via CSS classes.
- Cleans up event listeners when removed from the DOM to prevent leaks.

---

## Dependencies
- **Liquid Ajax Cart** `liquid-ajax-cart:request-end` custom event (emitted when cart requests finish).
- Notification markup containing:
  - `.cart-notification-continue_shopping`
  - `.cart-notification__close`
  - `#cart-notification-product`
  - `#cart-notification`

---

## Usage
Wrap the notification markup with the custom element and include the script:

```liquid
<cart-notification>
  <div id="cart-notification">
    <button class="cart-notification__close" type="button" aria-label="Close"></button>
    <div id="cart-notification-product"></div>
    <button class="cart-notification-continue_shopping">{% t 'general.continue_shopping' %}</button>
  </div>
</cart-notification>

<script src="{{ 'component-cart-notification.js' | asset_url }}" type="module"></script>
```

Ensure your add-to-cart logic (e.g., [Liquid Ajax Cart](https://shopify.dev/docs/api/ajax/reference/cart)) dispatches the `liquid-ajax-cart:request-end` event with `requestState` details.

---

## Method Summary 📋

| Method / Property             | Purpose                                                                 |
|------------------------------|-------------------------------------------------------------------------|
| `constructor()`              | Binds UI event handlers and subscribes to cart events.                  |
| `disconnectedCallback()`     | Removes all listeners when the element leaves the DOM.                  |
| `onCartUpdate(event)`        | Checks cart responses for successful add requests.                      |
| `updateNotification(cart)`   | Builds HTML for the product image, title, and options.                  |
| `showNotification()`         | Adds the CSS class that reveals the drawer.                             |
| `hideNotification()`         | Removes the CSS class to hide the drawer.                               |

---

## Detailed API

### constructor()
Initializes the component and wires up events:

```js
constructor() {
  super();
  this.hideNotification = this.hideNotification.bind(this);
  this.querySelector('.cart-notification-continue_shopping').addEventListener('click', () => this.hideNotification());
  this.querySelector('.cart-notification__close').addEventListener('click', () => this.hideNotification());
  document.addEventListener(
    'liquid-ajax-cart:request-end',
    this.onCartUpdate.bind(this)
  );
}
```

- Binds `hideNotification` once to reuse across handlers.
- Hooks into both “continue shopping” and “close” buttons.
- Subscribes to the global cart event stream.

### disconnectedCallback()

```js
disconnectedCallback() {
  this.querySelector('.cart-notification-continue_shopping')
    .removeEventListener('click', this.hideNotification);
  this.querySelector('.cart-notification__close')
    .removeEventListener('click', this.hideNotification);
  document.removeEventListener(
    'liquid-ajax-cart:request-end',
    this.onCartUpdate.bind(this)
  );
}
```

- Ensures listeners are removed when the node is detached (e.g., during re-renders).
- Prevents duplicate bindings and possible memory leaks.

### onCartUpdate(event)

```js
onCartUpdate(event) {
  const { requestState } = event.detail;
  if (requestState?.requestType === 'add' && requestState.responseData?.ok) {
    this.updateNotification(requestState.responseData.body);
  }
}
```

- Guard clauses ensure the notification updates only after a successful add request.
- Passes the response body to `updateNotification`.

### updateNotification(updatedCartNotification)

```js
updateNotification(updatedCartNotification) {
  const productElement = this.querySelector('#cart-notification-product');
  const optionsHTML = updatedCartNotification.options_with_values
    .map(option => `<div class="product-option"><dt>${option.name}: </dt><dd>${option.value}</dd></div>`)
    .join('');

  const productHTML = `
    <div class="cart-notification-product__image">
      <img src="${updatedCartNotification.image}" alt="${updatedCartNotification.featured_image.alt}" width="70" height="70">
    </div>
    <div>
      <p class="caption-with-letter-spacing">Shopify</p>
      <h3 class="cart-notification-product__name h4">${updatedCartNotification.product_title}</h3>
      <dl>${optionsHTML}</dl>
    </div>
  `;

  productElement.innerHTML = productHTML;
  this.showNotification();
}
```

- Generates semantic HTML for the product details (image, vendor, title, options).
- Updates `#cart-notification-product` and triggers the drawer animation.

### showNotification() & hideNotification()

```js
showNotification() {
  this.querySelector('#cart-notification').classList.add('cart-notification-open');
}

hideNotification() {
  this.querySelector('#cart-notification').classList.remove('cart-notification-open');
}
```

- Toggling the `.cart-notification-open` class drives CSS transitions.
- `hideNotification` is reused by both action buttons and can be called programmatically (e.g., after a timeout).

---

## Custom Element Definition
The script guards against duplicate registrations before defining the element:

```js
if (!customElements.get('cart-notification')) {
  customElements.define('cart-notification', CartNotification);
}
```

This makes hot reloading safe and ensures the component registers only once per page load.

---

## Implementation Notes
- Requires Liquid Ajax Cart (or equivalent) to dispatch the expected event payload.
- The notification HTML structure must include the referenced selectors.
- You can augment `updateNotification` to display prices, quantities, or badges by extending the markup template.

With this component in place, shoppers receive instant confirmation after adding to cart—no full page reloads required. 🎉

