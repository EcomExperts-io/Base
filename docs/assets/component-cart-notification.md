# CartNotification Web Component

Meet `<cart-notification>`, a lightweight Web Component defined in `assets/component-cart-notification.js` that keeps shoppers informed after an AJAX add-to-cart. It listens for Liquid Ajax Cart events, swaps in the latest product details, and controls the cart notification drawer UI.

**Source:** [`assets/component-cart-notification.js`](../../assets/component-cart-notification.js)

---

## What It Does

- Subscribes to `liquid-ajax-cart:request-end` so it can react immediately to add-to-cart requests.
- Updates the notification drawer with product title, image, and selected options returned by the cart API.
- Provides dedicated methods for showing and hiding the drawer via a CSS class toggle.
- Removes all event listeners inside `disconnectedCallback()` to avoid duplicate bindings.

---

## API Overview

| Method / Property           | Purpose                                                                 |
|----------------------------|-------------------------------------------------------------------------|
| `constructor()`            | Binds UI handlers and registers the Liquid Ajax Cart listener.          |
| `disconnectedCallback()`   | Cleans up listeners when the element leaves the DOM.                    |
| `onCartUpdate(event)`      | Filters cart responses and triggers UI updates for successful adds.     |
| `updateNotification(cart)` | Builds notification markup (image, vendor, options) from the cart JSON. |
| `showNotification()`       | Adds `cart-notification-open` to reveal the drawer.                     |
| `hideNotification()`       | Removes the class to hide the drawer.                                   |

---

## Detailed Method Documentation

### constructor()
Initializes the component and wires up events:

```js
constructor() {
  super();
  this.hideNotification = this.hideNotification.bind(this);
  this.querySelector('.cart-notification-continue_shopping')
    .addEventListener('click', () => this.hideNotification());
  this.querySelector('.cart-notification__close')
    .addEventListener('click', () => this.hideNotification());
  document.addEventListener(
    'liquid-ajax-cart:request-end',
    this.onCartUpdate.bind(this)
  );
}
```

- Uses a single bound `hideNotification` reference for all button listeners.
- Hooks into “continue shopping” and close controls for quick dismissal.
- Subscribes to the global Liquid Ajax Cart event bus.

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

- Removes every listener that was registered in the constructor.
- Prevents double subscription when the element is re-rendered.

### onCartUpdate(event)

```js
onCartUpdate(event) {
  const { requestState } = event.detail;
  if (requestState?.requestType === 'add' && requestState.responseData?.ok) {
    this.updateNotification(requestState.responseData.body);
  }
}
```

- Checks the request type and HTTP status before updating the drawer.
- Passes the cart payload to `updateNotification`.

### updateNotification(updatedCartNotification)

```js
updateNotification(updatedCartNotification) {
  const productElement = this.querySelector('#cart-notification-product');
  const optionsHTML = updatedCartNotification.options_with_values
    .map(
      (option) =>
        `<div class="product-option"><dt>${option.name}: </dt><dd>${option.value}</dd></div>`
    )
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

- Renders semantic markup for the product image, vendor, title, and options.
- Calls `showNotification()` after updating the DOM fragment.

### showNotification() & hideNotification()

```js
showNotification() {
  this.querySelector('#cart-notification').classList.add('cart-notification-open');
}

hideNotification() {
  this.querySelector('#cart-notification').classList.remove('cart-notification-open');
}
```

- Both methods encapsulate the CSS class toggle that controls animation/visibility.
- `hideNotification` can be reused for auto-dismiss timers or external scripts.

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

## Integration with Shopify Liquid

Include the wrapper and script inside `theme.liquid` or the relevant section/snippet:

```liquid
<cart-notification>
  <div id="cart-notification">
    <button class="cart-notification__close" type="button" aria-label="Close"></button>
    <div id="cart-notification-product"></div>
    <button class="cart-notification-continue_shopping">
      {% t 'general.continue_shopping' %}
    </button>
  </div>
</cart-notification>

<script src="{{ 'component-cart-notification.js' | asset_url }}" type="module"></script>
```

Ensure your add-to-cart logic (e.g., [Liquid Ajax Cart](https://shopify.dev/docs/api/ajax/reference/cart)) dispatches `liquid-ajax-cart:request-end` with the `requestState` payload this component expects.

---

## Usage Checklist

1. Render `<cart-notification>` near the footer or header so it can overlay the page.
2. Keep the required selectors (`#cart-notification`, `#cart-notification-product`, button classes) intact.
3. Load `component-cart-notification.js` as a module on every page where AJAX add-to-cart is available.
4. Optionally extend `updateNotification` to output pricing, quantity, or upsell content.
5. Close button uses `icon-close.svg`, `aria-label="\{\{ 'accessibility.close' | t \}\}"`, and a `cart-notification__close` class that the JS controller listens for.

With this component in place, shoppers receive instant confirmation after adding to cart—no full page reloads required. 🎉
