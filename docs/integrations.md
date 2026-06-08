# Integrations

Reference for the three third-party libraries the theme depends on and **how they're actually used
in this codebase** — directives, attributes, events, and where the bootstrap happens. Versions are
the vendored files in `assets/`.

| Library | Vendored version | Loaded in |
|---------|------------------|-----------|
| Alpine.js | 3.14.8 (`assets/alpinejs@3.14.8.min.js` + `alpinejs-persist@3.14.8.min.js`) | `layout/theme.liquid` (global, `defer`) |
| Liquid AJAX Cart | 2.1.1 (`assets/liquid-ajax-cart-v2.1.1.js`) | `layout/theme.liquid` (ES module import) |
| Swiper | 7.4.1 (`assets/swiper7.4.1.min.js` + `.css`) | `layout/theme.liquid` (conditional, `defer`) |

---

## Alpine.js 3.14

Loaded globally in `theme.liquid` (with the `-persist` plugin) via `defer`. Used for declarative,
local UI state.

### Directives used in this repo

- `x-data` — component-local state (e.g. `x-data="{ open: false }"`, `x-data="{ searchOpen: false }"`).
- `@event` / `x-on:` — event handlers (`@click`, `@input`, `@toggle`, `@click.outside`,
  `@click.away`, `@focus`).
- `x-show` — conditional visibility (e.g. filter content, search input).
- `x-transition` — enter/leave transitions on shown content.
- `x-bind` / `:class` — reactive attributes (e.g. `:class="{ 'drawer-active': open }"`,
  `x-bind:open="open"`).
- `x-model` / `x-ref` — input binding and element refs (header search uses `x-model="searchTerm"`,
  `x-ref="searchInput"`).
- `$persist` — persist state across page loads (filter groups:
  `$persist(true).as('openFilter')`, `$persist(false).as('sm-<param>')`).
- `x-cloak` — hide elements until Alpine initializes.

### The `x-cloak` + CSS pattern

`snippets/css-variables.liquid` ships the matching CSS so cloaked elements stay hidden until Alpine
boots:

```css
[x-cloak] { display: none !important; }
```

Add `x-cloak` to any element whose pre-init state would otherwise flash (e.g. a dropdown that
defaults open in markup but should start closed).

### The `$persist` filter-state pattern

Filter UIs keep their open/closed state between navigations using `$persist` with a stable key:

```liquid
<div x-data="{ openFilter: $persist(true).as('openFilter') }">…</div>
<div x-data="{ showMore: $persist(false).as('sm-{{ f.param_name }}') }">…</div>
```

### Named Alpine stores (`Alpine.data`)

For state shared across components, the theme registers a named store on `alpine:init`. The cart
drawer is the canonical example (`snippets/component-cart-drawer.liquid`):

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

An element opts in with `x-data="cartDrawer"` (the header does this when
`settings.cart_type == 'drawer'`). See `javascript-patterns.md` for how this connects to the
product custom element.

---

## Liquid AJAX Cart 2.1.1

Provides cart mutations and live cart UI **without custom fetch code**. Imported as an ES module in
`theme.liquid`.

### Bootstrap (in `layout/theme.liquid`)

```liquid
<script type="application/json" data-ajax-cart-initial-state>
  {{ cart | json }}
</script>

<script type="module">
  import '{{ "liquid-ajax-cart-v2.1.1.js" | asset_url }}';
</script>
```

`data-ajax-cart-initial-state` seeds the library with the server-rendered cart so the UI is correct
on first paint.

### Attributes & elements used in this repo

- `data-ajax-cart-section` — marks a region (cart page wrapper, drawer) that is auto re-rendered
  after any cart change.
- `data-ajax-cart-bind="item_count"` — binds an element's content to a cart property (header count).
- `<ajax-cart-product-form>` — wraps the product `{% form 'product' %}` so add-to-cart is handled
  via AJAX.
- `<ajax-cart-quantity>` with `data-ajax-cart-quantity-minus` / `-plus` /
  `data-ajax-cart-quantity-input` (keyed by line-item index) — line-item quantity controls.
- `data-ajax-cart-errors` (keyed by line-item key) — per-line-item error output.

### Events

After every cart request, the library fires `liquid-ajax-cart:request-end` on `document`. Components
listen for it; e.g. `assets/component-product-info.js` opens the drawer on a successful add and
re-dispatches `item-added-to-cart`:

```javascript
document.addEventListener('liquid-ajax-cart:request-end', this.onCartUpdate.bind(this));
```

---

## Swiper 7.4.1

Used for product image galleries / sliders. Loaded **conditionally** in `theme.liquid`.

### Conditional load + template whitelist

```liquid
{% if template.name == 'collection' or template.name == 'product' or template.name == 'index'
   or template.name == 'page' or template.name == 'search' %}
  {{ 'swiper7.4.1.min.css' | asset_url | stylesheet_tag }}
  <script src="{{ 'swiper7.4.1.min.js' | asset_url }}" defer="defer" id="swiper-script"></script>
{% endif %}
```

Swiper (CSS + JS) only loads on the **`collection`, `product`, `index`, `page`, and `search`**
templates. This keeps it off pages that don't need it.

> **Why the whitelist matters:** a Swiper-powered section placed on a template **outside** this list
> (e.g. `blog`, `article`, `list-collections`, or a custom template) will have **no Swiper available**
> and will silently fail to initialize. If you add such a section, extend the `template.name`
> condition in `layout/theme.liquid` to include that template. The `pr-review` skill check **P-11**
> is designed to catch this.

### Adding a new Swiper section — checklist

1. Confirm the target template is in the `theme.liquid` whitelist; if not, add it.
2. Initialize defensively: only call `new Swiper(...)` when `typeof Swiper !== 'undefined'`, and also
   listen for the `#swiper-script` `load` event (Swiper is deferred, so it may not be ready in
   `connectedCallback`):

   ```javascript
   connectedCallback() {
     if (typeof Swiper !== 'undefined') this.initSwiper();
   }
   // also:
   document.getElementById('swiper-script').addEventListener('load', this.initSwiper.bind(this));
   ```

3. Destroy the instance in `disconnectedCallback()` (`this.swiper?.destroy()`).

See `javascript-patterns.md` for the full initialization pattern.
