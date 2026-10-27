---
description: Writing JavaScript inside .js files, or within the {% javascript %} or {% script %} or <script></script> tags in .liquid files
paths:
  - "**/*.js"
  - "**/*.liquid"
---

# JavaScript Standards

## General Principles

- **Zero external dependencies** — native browser APIs (Alpine and Swiper are
  the only runtime libraries, loaded from `layout/theme.liquid`)
- **`const` over `let`** unless reassignment is needed
- **`for (const item of items)`** over `items.forEach()`
- **New lines before `{` and after `}` blocks**
- **`async`/`await`** over `.then()` chaining
- **Vanilla Web Components** — extend `HTMLElement` directly

## Web Components Pattern

```javascript
if (!customElements.get('product-info')) {
  class ProductInfo extends HTMLElement {
    abortController = undefined;
    swiper = null;

    constructor() {
      super();
      // Minimal constructor — setup goes in connectedCallback
    }

    connectedCallback() {
      this.setupEventListeners();
      if (typeof Swiper !== 'undefined') {
        this.initSwiper();
      }
    }

    disconnectedCallback() {
      this.abortController?.abort();
      this.swiper?.destroy();
    }

    setupEventListeners() {
      this.variantSelector?.addEventListener('change', this.onVariantChange.bind(this));
      document.getElementById('swiper-script').addEventListener('load', this.initSwiper.bind(this));
      document.addEventListener('cart:change', this.onCartUpdate.bind(this));
    }

    // Getters for DOM access
    get variantSelector() {
      return this.querySelector('variant-selector');
    }

    // Event handlers named on<Event>
    onVariantChange(e) {
      const productUrl = e.target?.dataset?.productUrl || this.dataset.url;
      this.renderSection(productUrl !== this.dataset.url, productUrl);
    }

    // Arrow functions for helpers
    updateSourceFromDestination = (html, id) => {
      const source = html.getElementById(id);
      const destination = this.querySelector(`#${id}`);
      if (source && destination) {
        destination.innerHTML = source.innerHTML;
      }
    };
  }

  customElements.define('product-info', ProductInfo);
}
```

```liquid
<product-info
  data-url="{{ product.url }}"
  data-section="{{ section.id }}"
  class="color-{{ section.settings.color_scheme }} section-{{ section.id }}-padding"
>
  <variant-selector id="variant-selector-{{ section.id }}">…</variant-selector>
</product-info>

<script src="{{ 'component-product-info.js' | asset_url }}" type="module"></script>
```

A class on a custom-element tag needs an explicit `display`
(`rules-of-engagement.md`).

## Early Returns

```javascript
// Good
const processOrder = (order) => {
  if (!order) return;
  if (!order.items.length) return;
  if (order.status !== 'pending') return;

  updateOrderStatus(order.id, 'processing');
};

// Avoid
const processOrder = (order) => {
  if (order) {
    if (order.items.length) {
      if (order.status === 'pending') {
        updateOrderStatus(order.id, 'processing');
      }
    }
  }
};
```

One optional chain is fine (`button?.enable()`); several in a row become an
early return.

```javascript
const buttonText = isLoading ? 'Loading...' : 'Add to cart';
if (isOutOfStock) return;
return product.available && product.price > 0;
```

## Events and the cart engine

Components communicate through custom events on `document`:

```javascript
onCartUpdate(e) {
  if (!window.location.pathname.includes('/products/')) return;

  // cart:change fires only on success
  // detail: { action, payload, response, cart, previousCart, sections, source }
  if (e.detail.action === 'add') {
    document.body.classList.add('js-item-added');
    document.dispatchEvent(new CustomEvent('item-added-to-cart', { detail: e.detail.response }));
  }
}
```

**Every cart mutation goes through `window.Cart` (`assets/cart.js`):**

```javascript
Cart.add(new FormData(form), form);
Cart.change({ line: 1, quantity: 2 }, sourceElement);
Cart.update({ note: 'Gift wrap please' }, sourceElement);
Cart.refresh(); // re-fetch state and section HTML after an external change
```

- Mutations are serialised through a queue; success dispatches `cart:change`
  on `document`, failure `cart:error` with `detail.error: { status, message, description }`.
- `window.Cart.state` is the current cart.
- A `fetch` to `/cart/add`, `/cart/change` or `/cart/clear` anywhere else is an
  error the gate reports: it skips the queue, the section render and
  `cart:change`, so nothing else re-renders. The one exception is a form that
  does its own `/cart/update` and then calls `Cart.refresh()`, as the discount
  form does.
- `Cart.state` is seeded from `{{ cart | json }}` in `layout/theme.liquid` and
  replaced by a `/cart.js` response after the first mutation or `Cart.refresh()`.
  Liquid's cart JSON has no `discount_codes` and no `token`; anything that needs
  them reads `/cart.js` first.
- A test of a cart mutation awaits `cart:change`, never a fixed sleep.

Guard page-specific behaviour on the path:

```javascript
updateURL(variantId) {
  if (!window.location.pathname.includes('/products/')) return;
  window.history.replaceState({}, '', `${this.dataset.url}${variantId ? `?variant=${variantId}` : ''}`);
}
```

## External Libraries

Initialise when the library is present, listen for its script's `load`
otherwise, and destroy the instance in `disconnectedCallback`:

```javascript
connectedCallback() {
  document.getElementById('swiper-script').addEventListener('load', this.initSwiper.bind(this));
  if (typeof Swiper !== 'undefined') this.initSwiper();
}

initSwiper() {
  this.swiper = new Swiper('.swiper', {
    pagination: { el: '.swiper-pagination' },
    navigation: { prevEl: '.swiper-button-prev', nextEl: '.swiper-button-next' },
  });
}

disconnectedCallback() {
  this.swiper?.destroy();
}
```

```liquid
<script src="{{ 'swiper7.4.1.min.js' | asset_url }}" defer="defer" id="swiper-script"></script>
```

## Input Validation

Clamp numeric input to its `min`/`max`:

```javascript
onQuantitySelectorEvent(e) {
  const input = this.quantitySelector.querySelector('input[type="number"]');
  const value = parseInt(input.value);
  const min = parseInt(input.getAttribute('min')) || 0;
  const max = parseInt(input.getAttribute('max')) || Infinity;

  if (e.target.name === 'minus' && value > min) input.value = value - 1;
  else if (e.target.name === 'plus' && value < max) input.value = value + 1;
  else if (e.type === 'change') input.value = Math.min(Math.max(value, min), max);
}
```

## JSON from Liquid

```liquid
<script type="application/json" data-selected-variant>
  {{ selected_variant | json }}
</script>
```

```javascript
getSelectedVariant(html) {
  const json = html.querySelector('[data-selected-variant]')?.innerHTML;
  return json ? JSON.parse(json) : null;
}
```

## URLs and Query Parameters

Build query strings with `URL` and `searchParams`; never concatenate. Product
URLs from the recommendations API already carry `?pr_prod_strat=…`, so a
concatenated `?variant=` is silently dropped:

```javascript
// Bad — /products/x?pr_prod_strat=collection?variant=123
const url = product.url + '?variant=' + variantId;

// Good — replaces the key if present, appends if not, encodes the value
const url = new URL(product.url, window.location.origin);
url.searchParams.set('variant', variantId);
```

Read with `new URL(...).searchParams.get('variant')`, not a regex. Pass
`window.location.origin` whenever the input may be relative; `new URL('/products/x')` throws.

## AbortController

Cancel the previous request before starting the next, and in `disconnectedCallback`:

```javascript
async renderSection(hasDifferentProductUrl, productUrl) {
  this.abortController?.abort();
  this.abortController = new AbortController();

  try {
    const response = await fetch(`${productUrl}?section_id=${this.dataset.section}`, {
      signal: this.abortController.signal,
    });
    const html = new DOMParser().parseFromString(await response.text(), 'text/html');
    this.updateSourceFromDestination(html, `price-${this.dataset.section}`);
  } catch (error) {
    if (error.name !== 'AbortError') console.error(error);
  }
}
```

**Whatever closes a UI state must abort the request that state started** — in
the one method every dismissal routes through, before its `isOpen` early
return, so a redundant dismissal still cancels. Otherwise a late response
reopens the panel after the shopper dismissed it (predictive search, cart
drawer, quick-add, variant re-render).

```javascript
close(returnFocus = false) {
  this.abortController?.abort();
  window.clearTimeout(this.debounceTimer);
  this.removeAttribute('data-loading');
  if (!this.isOpen) return;
  // …
}
```

## Product forms

- **Read a form's attributes with `getAttribute`.** `<input name="id">` shadows
  `form.id`, so a selector built from it matches nothing and nothing throws. The
  same holds for controls named `action`, `method`, `name` or `submit`.
- **A section that renders its own selling-plan UI must turn off the
  subscription app's auto-inject.** Recharge's legacy widget injects into the
  first `form[action*="/cart/add"]`; its switch is `window.DISABLE_RECHARGE = true`,
  set inline before window load, or the page renders two purchase UIs.

## Error Handling

```javascript
const fetchData = async (url) => {
  try {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error('Fetch error:', error);
    return null;
  }
};
```

## JSDoc

Annotate parameters, return types and complex objects:

```javascript
/**
 * @typedef {Object} ProductData
 * @property {string} id
 * @property {number} price
 * @property {boolean} [available]
 */

/**
 * @param {ProductData} product
 * @param {HTMLElement} container
 * @returns {Promise<void>}
 */
const updateProductDisplay = async (product, container) => {
  // …
};
```
