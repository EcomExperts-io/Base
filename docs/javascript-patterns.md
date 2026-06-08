# JavaScript Patterns

How JavaScript is organized in the Base theme, and a decision framework for choosing the right tool:
**Alpine.js**, a **custom element**, or **Liquid AJAX Cart attributes**.

The theme has **zero build step** for JS and **zero JS dependencies of its own** — it uses native
browser APIs plus three vendored libraries (Alpine.js, Liquid AJAX Cart, Swiper). See
`.cursor/rules/javascript-standards.mdc` for the rules and
`.cursor/references/javascript-reference.md` for full worked examples.

---

## Decision tree: which tool?

| Use… | When | How it shows up |
|------|------|-----------------|
| **Alpine.js** (`x-data`, `@event`, `x-show`, `x-transition`, `$persist`, `x-cloak`) | State is declarative, local to a chunk of HTML, and mostly about toggling UI (open/closed, show more, transitions) | Attributes directly in Liquid markup |
| **Custom element** (`class … extends HTMLElement`) | Behavior is encapsulated, reusable, involves fetch/section-rendering, or coordinates multiple child elements | `assets/section-*.js` / `assets/component-*.js`, registered with `customElements.define` |
| **Liquid AJAX Cart attributes** (`data-ajax-cart-*`, `<ajax-cart-*>`) | Anything that mutates or reflects the cart | Attributes in Liquid; no custom fetch code |

Rules of thumb:

- Don't write a custom element to toggle a class — use Alpine.
- Don't write fetch logic for cart add/change/remove — use Liquid AJAX Cart.
- Do write a custom element when you need the Section Rendering API, request cancellation, or
  lifecycle cleanup.

---

## Custom element anatomy

All component/section JS must be a vanilla Web Component. The non-negotiables (see
`javascript-standards.mdc`):

```javascript
if (!customElements.get('product-info')) {     // guard: define only once
  customElements.define(
    'product-info',
    class ProductInfo extends HTMLElement {
      abortController = undefined;              // property declarations

      constructor() {
        super();
        // keep minimal — defer setup to connectedCallback
      }

      connectedCallback() {
        // runs when added to the DOM: set up listeners, init libraries
        this.setupEventListeners();
      }

      disconnectedCallback() {
        // runs when removed: clean up
        this.abortController?.abort();
        this.swiper?.destroy();
      }
    }
  );
}
```

- **Guard** every registration with `if (!customElements.get('name'))`.
- **`connectedCallback`** initializes; **`disconnectedCallback`** cleans up (abort fetches, destroy
  library instances, remove listeners).
- Load the script with `type="module"` (see the scripts note below).

The full annotated example (getters for child elements, async `renderSection` with the Section
Rendering API, `AbortController`, JSON parsing, `updateSourceFromDestination`) is in
`.cursor/references/javascript-reference.md`.

---

## Alpine.js ↔ custom element communication

Alpine and custom elements coordinate through DOM **custom events** rather than shared globals. The
real cart-open flow in this repo:

1. A custom element finishes work and dispatches an event on `document`. From
   `assets/component-product-info.js`, on a successful add-to-cart:

   ```javascript
   document.body.classList.add('js-show-ajax-cart');
   document.dispatchEvent(
     new CustomEvent('item-added-to-cart', { detail: requestState?.responseData?.body })
   );
   ```

2. An Alpine store listens for it. From `snippets/component-cart-drawer.liquid`:

   ```javascript
   document.addEventListener('alpine:init', () => {
     Alpine.data('cartDrawer', () => ({
       cartOpen: false,
       toggleCartDrawer() { this.cartOpen = !this.cartOpen; },
       init() {
         document.addEventListener('item-added-to-cart', () => this.toggleCartDrawer());
       },
     }));
   });
   ```

3. The header opts an element into that store with `x-data="cartDrawer"` (only when
   `settings.cart_type == 'drawer'`), and the drawer toggles `:class="{ 'cart-open': cartOpen }"`.

This is the canonical pattern: **custom element → `document.dispatchEvent` → Alpine `init()`
listener → reactive UI**.

---

## Consuming Liquid AJAX Cart events

After any cart request, Liquid AJAX Cart fires `liquid-ajax-cart:request-end` on `document`.
Components subscribe to react:

```javascript
setupEventListeners() {
  document.addEventListener('liquid-ajax-cart:request-end', this.onCartUpdate.bind(this));
}

onCartUpdate(e) {
  const { requestState } = e.detail;
  if (requestState.requestType === 'add' && requestState.responseData?.ok) {
    // …react to a successful add
  }
}
```

See `integrations.md` for the full Liquid AJAX Cart attribute/event surface.

---

## Swiper initialization + the template whitelist

Swiper is loaded **conditionally** in `layout/theme.liquid` — only on a fixed set of templates:

```liquid
{% if template.name == 'collection' or template.name == 'product' or template.name == 'index'
   or template.name == 'page' or template.name == 'search' %}
  {{ 'swiper7.4.1.min.css' | asset_url | stylesheet_tag }}
  <script src="{{ 'swiper7.4.1.min.js' | asset_url }}" defer="defer" id="swiper-script"></script>
{% endif %}
```

Because Swiper may not be present, components **check for it before initializing** and also listen
for the script's `load` event:

```javascript
connectedCallback() {
  if (typeof Swiper !== 'undefined') this.initSwiper();
}
// and:
document.getElementById('swiper-script').addEventListener('load', this.initSwiper.bind(this));
```

> **Whitelist requirement:** if you add a Swiper-powered section to a template **not** in the list
> above (e.g. `blog`, `article`, `list-collections`, or a custom template), Swiper won't load there.
> Extend the `template.name` condition in `theme.liquid` to cover that template. The `pr-review`
> skill check P-11 exists to catch this.

---

## Shared utilities (`assets/theme.js`)

`assets/theme.js` is loaded once in `theme.liquid` (`type="module"`) and currently exports a single
utility:

```javascript
/** Delays execution until after `wait` ms of inactivity. */
export function debounce(fn, wait) { /* … */ }
```

Import it where needed, e.g. the collection page debounces filter changes:

```javascript
import { debounce } from '{{ "theme.js" | asset_url }}';
// this.debounceOnChange = debounce((e) => this.onChangeHandler(e), 800);
```

> `debounce` is the only utility exported today. If you add more shared helpers, add them here and
> document them in this section.

---

## Script loading convention

Section/component scripts should be loaded as ES modules:

```liquid
<script src="{{ 'component-<name>.js' | asset_url }}" type="module"></script>
```

`type="module"` defers execution and gives module scope (and lets you `import` from `theme.js`).
This is the standard the `pr-review` skill enforces (check P-04). A few existing vendored/global
scripts in `theme.liquid` (Alpine, Swiper) use `defer="defer"` because they attach globals rather
than being imported — that is expected for those libraries.
