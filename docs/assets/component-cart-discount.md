# component-cart-discount.js

`assets/component-cart-discount.js` defines the `<cart-discount-form>` custom element that handles discount code application and removal in the cart.

**Source:** [`assets/component-cart-discount.js`](../../assets/component-cart-discount.js)

---

## What It Does

- Applies discount codes to the cart via Shopify's `/cart/update.js` endpoint
- Removes discount codes while preserving other active codes
- Updates discount pills dynamically without page reload
- Shows loading states during API calls
- Integrates with Liquid Ajax Cart for seamless cart updates

---

## CartDiscountForm API Overview

| Method / Property        | Purpose                                                         |
|--------------------------|-----------------------------------------------------------------|
| `connectedCallback()`    | Initializes DOM references and attaches event listeners        |
| `disconnectedCallback()` | Removes event listeners when component is detached              |
| `showError(msg)`         | Displays error message to the user                              |
| `hideError()`            | Hides error message                                             |
| `setLoading(loading)`    | Sets loading state on button and input during API calls         |
| `applyDiscount(codes)`   | POSTs discount codes to `/cart/update.js`                       |
| `getExistingCodes()`     | Returns array of currently applied discount codes               |
| `createPill(code)`       | Creates a new discount pill element with remove button          |
| `updatePills(cart)`     | Syncs pill display with cart discount applications              |
| `handleSubmit(event)`    | Handles form submission for applying new discount codes         |
| `handleRemoveClick(event)` | Handles remove button clicks for removing discount codes      |

---

## Detailed Methods

### connectedCallback()

Initializes the component by:
- Caching DOM references (form, input, error element, codes list, submit button)
- Storing original button text for loading state restoration
- Attaching submit handler to the form
- Attaching click handler to the codes list (event delegation for remove buttons)

```js
connectedCallback() {
  this.form = this.querySelector('#cart-discount-form');
  this.input = this.querySelector('#discount-code-input');
  this.errorEl = this.querySelector('.cart-discount__error');
  this.codesList = this.querySelector('.cart-discount__codes');
  this.submitBtn = this.form?.querySelector('button[type="submit"]');
  this.originalButtonText = this.submitBtn?.textContent.trim();

  if (!this.form) return;

  this.form.addEventListener('submit', this.handleSubmit.bind(this));
  this.codesList?.addEventListener('click', this.handleRemoveClick.bind(this));
}
```

### disconnectedCallback()

Removes all event listeners to prevent memory leaks.

### showError(msg)

Displays an error message by:
- Finding the error text element
- Setting the message content
- Showing the error container with `display: flex`

### hideError()

Hides the error message by:
- Hiding the error container
- Clearing the error text content

### setLoading(loading)

Manages loading state during API calls:
- Disables/enables the submit button
- Changes button text to "Applying..." when loading
- Disables/enables the input field

### applyDiscount(codes)

Sends discount codes to Shopify's cart update endpoint.

```js
async applyDiscount(codes) {
  const res = await fetch(`${window.Shopify.routes.root}cart/update.js`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ discount: codes })
  });

  if (!res.ok) throw new Error(`Discount update failed: ${res.status}`);
  return res.json();
}
```

**Parameters:**
- `codes` (string): Comma-separated discount codes, or empty string to remove all

**Returns:** Promise resolving to cart JSON response

### getExistingCodes()

Extracts currently applied discount codes from the DOM.

```js
getExistingCodes() {
  return Array.from(this.querySelectorAll('.cart-discount__pill'))
    .map(pill => pill.dataset.discountCode)
    .filter(Boolean);
}
```

**Returns:** Array of discount code strings

### createPill(code)

Creates a new discount pill element with:
- List item with `cart-discount__pill` class
- Paragraph displaying the code
- Remove button with close icon
- Proper ARIA labels

**Parameters:**
- `code` (string): Discount code to display

**Returns:** HTMLLIElement

### updatePills(cart)

Synchronizes the pill display with the cart's discount applications:
- Removes pills for codes no longer in the cart
- Adds pills for new discount codes
- Preserves existing pills that are still valid

**Parameters:**
- `cart` (object): Cart JSON object from Shopify API

### handleSubmit(event)

Handles form submission for applying discount codes:

1. Prevents default form submission
2. Validates input (non-empty)
3. Checks for duplicate codes
4. Sets loading state
5. Combines existing codes with new code
6. Applies discount via API
7. Fetches updated cart
8. Updates pill display
9. Triggers Liquid Ajax Cart update
10. Clears input and resets loading state

**Error Handling:**
- Shows error message if discount code is invalid
- Always resets loading state in `finally` block

### handleRemoveClick(event)

Handles remove button clicks using event delegation:

1. Finds the clicked remove button and its pill
2. Extracts the discount code to remove
3. Adds loading class to pill (opacity animation)
4. Disables remove button
5. Filters out the removed code from existing codes
6. Applies remaining codes (or empty string if none)
7. Fetches updated cart
8. Updates pill display
9. Triggers Liquid Ajax Cart update

**Error Handling:**
- Removes loading class and re-enables button on error
- Restores pill state by fetching cart and updating display

---


## Custom Element Definition

```js
if (!customElements.get('cart-discount-form')) {
  customElements.define(
    'cart-discount-form',
    class CartDiscountForm extends HTMLElement {
      // ... implementation
    }
  );
}
```

The element is wrapped in a guard to prevent re-registration during hot reloading or multiple bundle loads.

---

## Integration with Liquid Ajax Cart

The component integrates with Liquid Ajax Cart for seamless cart updates:

```js
if (window.liquidAjaxCart?.update) {
  window.liquidAjaxCart.update({}, {});
}
```

This triggers Liquid Ajax Cart to update all sections marked with `data-ajax-cart-section`, ensuring cart totals and other cart-related UI elements stay in sync.

---

## Loading States

### Button Loading State

During discount application:
- Button text changes to "Applying..."
- Button is disabled
- Input field is disabled
- Button opacity reduces to 60% (via CSS)

### Pill Removal State

During discount removal:
- Pill opacity reduces to 50% (via CSS class `cart-discount__pill--removing`)
- Remove button is disabled
- Pointer events are disabled on the pill

---

## Error Handling

Errors are displayed in a dedicated error container:
- Shows error icon and message text
- Uses `role="alert"` for screen reader announcements
- Automatically hidden when new actions are attempted

Common error scenarios:
- Invalid discount code
- Network errors
- API failures

---

## Usage Checklist

1. Ensure the form has `id="cart-discount-form"`
2. Input must have `id="discount-code-input"`
3. Error container must have class `cart-discount__error`
4. Codes list must have class `cart-discount__codes`
5. Pills must have `data-discount-code` attribute
6. Remove buttons must have class `cart-discount__pill-remove`
7. Load `component-cart-discount.js` as a module
8. Ensure Liquid Ajax Cart is loaded for cart updates

---

## CSS Dependencies

The component relies on these CSS classes:
- `.cart-discount`
- `.cart-discount__form`
- `.cart-discount__input`
- `.cart-discount__button`
- `.cart-discount__button:disabled`
- `.cart-discount__codes`
- `.cart-discount__pill`
- `.cart-discount__pill--removing`
- `.cart-discount__pill-code`
- `.cart-discount__pill-remove`
- `.cart-discount__error`
- `.cart-discount__error-text`
- `.svg-wrapper`

---

## Accessibility Features

- Proper ARIA labels on remove buttons
- Error messages use `role="alert"`
- Button states properly disabled during loading
- Keyboard navigation support
- Screen reader friendly error announcements
