# Base Theme

A developer-first Shopify theme that prioritizes clean code, maintainability, and straightforward customization. Built with the modern developer workflow in mind, this theme serves as an ideal starting point for your Shopify projects.

## Introduction

StarterTheme is crafted for developers who appreciate clean, well-structured code and minimal complexity. This theme strips away the bloat commonly found in marketplace themes to provide a solid foundation that you can build upon. The theme leverages custom web components for 90% of its JavaScript functionality, providing a modern, encapsulated, and maintainable approach to component development.

🔗 **Demo Store**: [View the theme in action](https://blackmamba4.myshopify.com/)

### Developer Benefits

- **Clean Architecture**: Organized, logical file structure with clear separation of concerns
- **Minimal Dependencies**: Only essential libraries and tools included
- **Modern Development**: Built using Shopify CLI 3.0 and Online Store 2.0 features
- **Simplified Customization**: Well-documented sections and blocks for easy modifications
- **Performance First**: Lightweight base with no unnecessary JavaScript or CSS
- **Developer Experience**: Quick setup, clear naming conventions, and intuitive component structure
- **Zero Build Tools**: No complex build process or tooling required - just pure JavaScript and CSS

The theme follows KISS (Keep It Simple, Stupid) principles, making it an excellent choice for both rapid development and teaching/learning Shopify theme development.

### Third-Party Libraries

The theme uses a carefully selected set of third-party libraries to provide essential functionality while maintaining performance:

- **Alpine.js** ([Documentation](https://alpinejs.dev/))
  - Lightweight JavaScript framework for component behavior
  - Used for UI state management and interactivity
  - Perfect for declarative DOM manipulation

- **Liquid AJAX Cart** ([Documentation](https://liquid-ajax-cart.js.org/))
  - Cart functionality without custom JavaScript
  - Real-time cart updates and synchronization
  - Built specifically for Shopify themes

- **Swiper** ([Documentation](https://swiperjs.com/))
  - Modern mobile touch slider
  - Used for product image galleries
  - Supports touch gestures and various navigation options

These libraries were chosen for their minimal footprint, excellent documentation, and specific utility in solving common Shopify theme challenges.

## Theme Components

This theme is a work in progress, built with a focus on creating clean, efficient components. We've built several key components from scratch while temporarily leveraging some components from Dawn theme as we continue development.

### Built From Scratch
- Header
- Cart drawer
- Cart notification
- Cart page
- Collection page
- Product page
- Search page
- Predictive search

### Currently Using Dawn Components
- Blog and article pages
- Footer
- Customer account pages

Note: Our roadmap includes gradually replacing the Dawn-based components with our own implementations to maintain our minimalist, developer-friendly approach throughout the entire theme.

## Component Code Walkthrough

### Header Implementation

The header combines Alpine.js for UI state management and Liquid AJAX Cart for cart functionality. Here's how these libraries are used:

#### Alpine.js Implementation
The header uses Alpine.js for managing search functionality:

File: `sections/header.liquid`
```liquid
<header
  x-data="{ searchOpen: false, searchTerm: '' }"
  @click.outside="searchOpen = false"
  @input="searchTerm = $event.target.value"
>
```

The search toggle uses Alpine's `$nextTick` for focus management:

File: `sections/header.liquid`
```liquid
<div id="header-actions_search" 
  @click="searchOpen = !searchOpen; $nextTick(() => { if (searchOpen) $refs.searchInput.focus() })">
  {{ 'icon-search.svg' | inline_asset_content }}
</div>
```

The search form uses Alpine's x-model and x-ref for input handling:

File: `sections/header.liquid`
```liquid
<input
  type="search"
  name="q"
  x-model="searchTerm"
  x-ref="searchInput"
  x-show="searchOpen"
  @focus="$event.target.select()"
>
```
The cart toggle behavior changes based on the cart type setting:

File: `sections/header.liquid`
```liquid
<a
  id="header-cart-bubble"
  {%- if settings.cart_type == 'drawer' -%}
    @click.prevent="toggleCartDrawer"
  {%- else -%}
    href="{{ routes.cart_url }}"
  {%- endif -%}
>
```

#### Liquid AJAX Cart Integration
The cart count in the header automatically updates through Liquid AJAX Cart bindings:

File: `sections/header.liquid`
```liquid
<div data-cart-count data-ajax-cart-bind="item_count">
  {{ cart.item_count }}
</div>
```

### Product Page Implementation

The product page tells an interesting story of how variant selection works. Let's follow the flow:

#### The Variant Selection Journey

It starts with the `<variant-selector>` element, which can be rendered in two ways:

File: `sections/main-product.liquid`
```liquid
<variant-selector data-picker-type="{{ block.settings.picker_type }}">
  {% if block.settings.picker_type == 'dropdown' %}
    <!-- Dropdown lists for each option -->
  {% else %}
    <!-- Radio buttons for each option -->
  {% endif %}
</variant-selector>
```

When a user interacts with either the dropdowns or radio buttons, it triggers our variant change flow:

File: `assets/component-product-info.js`
```js
class ProductInfo extends HTMLElement {
  constructor() {
    super();
    // Listen for any variant changes
    this.variantSelector?.addEventListener('change', this.onVariantChange.bind(this));
  }

  onVariantChange(e) {
    // Kick off the section render process
    this.renderSection();
  }
}
```

The `renderSection` method is where the magic happens. It:
1. Collects the currently selected options
2. Makes a request to Shopify's Section Rendering API
3. Updates specific parts of the page with the response:

File: `assets/component-product-info.js`
```js
renderSection() {
  // Request the section with current variant selections
  fetch(`${this.dataset.url}?option_values=${this.selectedOptionValues}&section_id=${this.dataset.section}`)
    .then((response) => response.text())
    .then((responseText) => {
      // Parse the returned HTML
      const html = new DOMParser().parseFromString(responseText, 'text/html');
      
      // Get the new variant data
      const variant = this.getSelectedVariant(html);

      // Update various parts of the page
      this.updateMedia(variant?.featured_media?.id);        // Update gallery
      this.updateURL(variant?.id);                         // Update URL
      this.updateVariantInputs(variant?.id);              // Update form inputs
      
      // Update specific sections using the new HTML
      this.updateSourceFromDestination(html, `price-${this.dataset.section}`);
      this.updateSourceFromDestination(html, `sku-${this.dataset.section}`);
      this.updateSourceFromDestination(html, `inventory-${this.dataset.section}`);
      this.updateSourceFromDestination(html, `add-to-cart-container-${this.dataset.section}`);
    });
}
```

This creates a seamless experience where selecting a new variant:
1. Triggers the change event
2. Fetches fresh HTML for the new variant
3. Updates multiple parts of the page (price, SKU, inventory, etc.)
4. All without a full page reload

The beauty of this approach is that it leverages Shopify's section rendering while maintaining a smooth user experience. Each part of the page updates independently, and the URL updates to reflect the selected variant, making it shareable and maintaining browser history.

#### Cart Event item-added-to-cart

The product page also handles cart interactions through a custom event. When an item is added to the cart, we need to notify other components (like the cart drawer) about this change:

File: `assets/component-product-info.js`
```js
class ProductInfo extends HTMLElement {
  
  onCartUpdate(e) {
    const { requestState } = e.detail;
    
    // Only handle successful "add to cart" requests
    if (requestState.requestType === 'add' && requestState.responseData?.ok) {
      // Show cart drawer
      document.body.classList.add('js-show-ajax-cart');
      
      // Dispatch event for other components
      document.dispatchEvent(
        new CustomEvent('item-added-to-cart', {
          detail: requestState?.responseData?.body
        })
      );
    }
  }
}
```

This event allows for:
1. Automatic cart drawer opening when items are added
2. Other components to react to cart changes
3. Passing cart data to interested components

#### Liquid AJAX Cart Integration

The product page leverages [Liquid AJAX Cart](https://liquid-ajax-cart.js.org/v2/product-forms/):

File: `sections/main-product.liquid`
```liquid
<ajax-cart-product-form>
  {% form 'product', product, id: product_form_id, novalidate: 'novalidate' %}
    <input type="hidden" name="id" value="{{ selected_variant.id }}">
    <div id="add-to-cart-container-{{ section.id }}">
      <button
        id="AddToCart-{{ section.id }}"
        type="submit"
        name="add"
        {% if selected_variant.available == false %}disabled{% endif %}
      >
        {% if selected_variant.available == false %}
          Sold out
        {% else %}
          Add to cart
        {% endif %}
      </button>
    </div>
  {% endform %}
</ajax-cart-product-form>
```

The integration provides:
1. Automatic form submission handling
2. Real-time cart updates without page reloads
3. Cart state synchronization across components

When a product is added:
1. Liquid AJAX Cart intercepts the form submission
2. Handles the cart addition via AJAX
3. Triggers the `liquid-ajax-cart:request-end` event
4. Our code then handles the UI updates and notifications

This creates a seamless cart experience where:
- The cart updates instantly
- The UI responds immediately
- All components stay in sync
- The user gets immediate feedback

### Collection Page Implementation

The collection page tells an interesting story of how filtering, sorting, and pagination work together through two main event handlers. Let's follow the flow:

#### Event Handling Flow

The `<collection-info>` element manages two primary events:

File: `assets/component-collection-info.js`
```js
class CollectionInfo extends HTMLElement {
  constructor() {
    super();
    this.debounceOnChange = debounce((event) => this.onChangeHandler(event), 800);
    this.addEventListener('change', this.debounceOnChange.bind(this));
    this.addEventListener('click', this.onClickHandler.bind(this));
  }
}
```

1. **Filter Changes (`onChangeHandler`)**
   - Triggered by filter form changes (checkboxes, price range, etc.)
   - Debounced to prevent rapid consecutive updates
   File: `assets/component-collection-info.js`
```js
onChangeHandler = (event) => {
  if (!event.target.matches('[data-render-section]')) return;

  const form = event.target.closest('form') || document.querySelector('#filters-form') || document.querySelector('#filters-form-drawer');
  const formData = new FormData(form);
  let searchParams = new URLSearchParams(formData).toString();

  // Preserve search query if it exists
  if (window.location.search.includes('?q=')) {
    const existingParams = new URLSearchParams(window.location.search);
    const qValue = existingParams.get('q');
    searchParams = `q=${qValue}&${searchParams}`;
  }

  this.fetchSection(searchParams);
};
```
   This handler:
   - Checks if the changed element is meant to trigger a section update
   - Finds the closest filter form (supports multiple form locations)
   - Collects all filter values and converts to URL parameters
   - Preserves search query if present
   - Triggers section update with new parameters

2. **Navigation Changes (`onClickHandler`)**
   - Handles sorting and pagination and active filters badges clicks through data attributes
   File: `assets/component-collection-info.js`
```js
onClickHandler = (event) => {
  if (event.target.matches('[data-render-section-url]')) {
    event.preventDefault();
    const searchParams = new URLSearchParams(event.target.dataset.renderSectionUrl.split('?')[1]).toString()
    
    this.fetchSection(searchParams);
  }
};
```
   This handler:
   - Checks for elements with `data-render-section-url` attribute
   - Extracts search parameters from the URL in the data attribute
   - Prevents default link behavior
   - Triggers section update with the extracted parameters

   Used by elements like active filters and pagination:
   File: `sections/main-collection.liquid`
```liquid
<!-- Active filter removal -->
<div class="filter active-filter-item"
  data-render-section-url="{{ v.url_to_remove }}"
>
  <span>{{ f.label }}: {{ v.label }}</span>
  <div class="filter-close">
    {{- 'icon-close.svg' | inline_asset_content -}}
  </div>
</div>

<!-- Clear all filters -->
<div class="filter active-filter-item active-filter-clear-all"
  data-render-section-url="{{ collection.url }}"
>
  <span>Clear all filters</span>
</div>
```

Both events ultimately call `fetchSection`, which updates the page:

File: `assets/component-collection-info.js`
```js
fetchSection(searchParams) {
  // Show loading state
  this.showLoadingOverlay();
  
  // Fetch updated section content
  fetch(`${window.location.pathname}?section_id=${this.dataset.section}&${searchParams}`)
    .then((response) => response.text())
    .then((responseText) => {
      const html = new DOMParser().parseFromString(responseText, 'text/html');
      this.updateURL(searchParams);
      // Update multiple sections of the page
      this.updateSourceFromDestination(html, `product-grid-${this.dataset.section}`);
      this.updateSourceFromDestination(html, `results-count-${this.dataset.section}`);
      this.updateSourceFromDestination(html, `active-filter-group-${this.dataset.section}`);
      // ... update other sections
      this.hideLoadingOverlay();
    });
}
```

#### Filter UI with Alpine.js

The theme offers three filter layouts, each powered by Alpine.js for state management:

1. **Drawer Filters**
File: `snippets/component-filters-drawer.liquid`
```liquid
<div
  x-data="{ open: false }"
  class="drawer-main-wrapper"
  :class="{ 'drawer-active': open }"
>
  <button type="button" @click="open = !open" class="drawer__facet-button-trigger">
    <div class="svg-wrapper">
      {{ 'icon-filter.svg' | inline_asset_content }}
    </div>
  </button>
  <div class="drawer__facets-wrapper" x-data="{ openFilter: $persist(true).as('openFilter') }">
    <!-- Filter groups -->
  </div>
</div>
```

2. **Sidebar Filters**
File: `snippets/component-filters-sidebar.liquid`
```liquid
<div
  class="filter-section facets__disclosure-vertical js-filter"
  x-data="{ open: {{ open }} }"
>
  <details
    x-bind:open="open"
    @toggle="open = $event.target.open"
  >
    <summary>
      <span>{{ f.label }}</span>
      {{ 'icon-caret.svg' | inline_asset_content }}
    </summary>
    <div
      class="facets__display-vertical"
      x-data="{ showMore : $persist(false).as('sm-{{ f.param_name }}') }"
    >
      <!-- Filter values -->
    </div>
  </details>
</div>
```

3. **Horizontal Filters**
File: `snippets/component-filters-horizontal.liquid`
```liquid
<div
  class="facets__wrapper"
  x-data="{ open: false }"
>
  <button type="button" x-on:click="open = !open" class="filter-button">
    {{ f.label }}
    {{ 'icon-caret.svg' | inline_asset_content }}
  </button>
  <div
    x-cloak
    x-show="open"
    @click.away="open = false"
    x-transition
    class="filter-content js-filter"
  >
    <!-- Filter content -->
  </div>
</div>
```

Alpine.js provides:
- Persistent filter group state (`$persist`)
- Show/hide filter values
- Smooth transitions
- Click-outside handling
- Mobile-friendly drawer interactions

This implementation creates a seamless filtering experience where:
1. Filter changes immediately trigger section updates
2. The URL reflects the current filter state
3. The UI stays responsive with loading states
4. Filter preferences persist between page loads

### Cart Page Implementation

The cart page combines Liquid AJAX Cart with a clean, responsive layout to provide a seamless cart management experience.

#### Core Structure

The cart page is wrapped in a section that handles both empty and filled states:

File: `sections/main-cart-items.liquid`
```liquid
<div
  id="cart-main"
  class="page-width color-{{ section.settings.color_scheme }} gradient"
>
  {%- if cart.item_count > 0 -%}
    <div class="cart__wrapper" data-ajax-cart-section>
      <div class="cart-header">
        <h2>Your cart ({{ cart.item_count }})</h2>
        <a href="{{ routes.all_products_collection_url }}" class="underlined-link"> Continue shopping </a>
      </div>
      <!-- Cart items -->
    </div>
  {%- else -%}
    <div class="cart__warnings">
      <h1 class="cart__empty-text">Your cart is empty</h1>
      <a href="/collections/all" class="button"> Continue shopping </a>
      <h2 class="cart__login-title">Have an account?</h2>
      <p class="cart__login-paragraph">
        <a href="/account/login" class="link underlined-link">Log in</a> to check out faster.
      </p>
    </div>
  {% endif %}
</div>
```

#### Liquid AJAX Cart Integration

The cart page uses the `data-ajax-cart-section` attribute to mark sections that should be automatically updated when cart changes occur:

File: `sections/main-cart-items.liquid`
```liquid
<div class="cart__wrapper" data-ajax-cart-section>
  <div class="cart-header">
    <h2>Your cart ({{ cart.item_count }})</h2>
    <a href="{{ routes.all_products_collection_url }}" class="underlined-link"> Continue shopping </a>
  </div>
  <!-- Cart items -->
</div>
```

Each cart item uses Liquid AJAX Cart's quantity controls for real-time updates:

File: `sections/main-cart-items.liquid`
```liquid
<ajax-cart-quantity>
  <a
    data-ajax-cart-quantity-minus
    href="{{ routes.cart_change_url }}?line={{ line_item_index }}&quantity={{ line_item.quantity | minus: 1 }}"
  >
    {{- 'icon-minus.svg' | inline_asset_content -}}
  </a>

  <input
    data-ajax-cart-quantity-input="{{ line_item_index }}"
    name="updates[]"
    value="{{ line_item.quantity }}"
    type="number"
    form="my-ajax-cart-form"
  >

  <a
    data-ajax-cart-quantity-plus
    href="{{ routes.cart_change_url }}?line={{ line_item_index }}&quantity={{ line_item.quantity | plus: 1 }}"
  >
    {{- 'icon-plus.svg' | inline_asset_content -}}
  </a>
</ajax-cart-quantity>
```

The cart page also handles line item properties and discounts:

File: `sections/main-cart-items.liquid`
```liquid
{%- if line_item.product.has_only_default_variant == false
  or line_item.properties.size != 0
  or line_item.selling_plan_allocation != null
-%}
  <dl class="cart-item__options">
    {%- if line_item.product.has_only_default_variant == false -%}
      {%- for option in line_item.options_with_values -%}
        <div class="cart-item__option">
          <dt>{{ option.name }}:</dt>
          <dd>{{ option.value }}</dd>
        </div>
      {%- endfor -%}
    {%- endif -%}

    {%- for property in line_item.properties -%}
      {%- if property.last != blank and property_first_char != '_' -%}
        <div class="cart-item__option">
          <dt>{{ property.first }}:</dt>
          <dd>{{ property.last }}</dd>
        </div>
      {%- endif -%}
    {%- endfor -%}
  </dl>
{% endif %}
```

#### Error Handling

The cart page includes error handling for each line item:

File: `sections/main-cart-items.liquid`
```liquid
<div class="cart-item__errors">
  <div data-ajax-cart-errors="{{ line_item.key }}"></div>
  {{- 'icon-info.svg' | inline_asset_content -}}
</div>
```

This creates a robust cart experience where:
1. Quantity updates happen instantly through AJAX
2. Line item properties and variants are clearly displayed
3. Errors are handled gracefully at the line item level
4. The cart total and discounts update automatically
5. All changes sync across all cart instances (page, drawer, notifications)

### Cart Drawer Implementation

The cart drawer demonstrates how Alpine.js can be used to manage state across multiple components. Here's how the header and drawer work together:

#### Alpine.js State Management

The header initializes the cart drawer state when cart type is set to drawer:

File: `sections/header.liquid`
```liquid
<div
  class="color-{{ section.settings.color_scheme }} gradient"
  {% if settings.cart_type == 'drawer' %}
    x-data="cartDrawer"
  {% endif %}
>
```

The cart bubble in the header uses this state to toggle the drawer:

File: `sections/header.liquid`
```liquid
<a
  id="header-cart-bubble"
  {%- if settings.cart_type == 'drawer' -%}
    @click.prevent="toggleCartDrawer"
  {%- else -%}
    href="{{ routes.cart_url }}"
  {%- endif -%}
>
```

The drawer component defines its Alpine.js behavior:

File: `snippets/component-cart-drawer.liquid`
```js
document.addEventListener('alpine:init', () => {
  Alpine.data('cartDrawer', () => ({
    cartOpen: false,

    toggleCartDrawer() {
      this.cartOpen = !this.cartOpen;
    },

    init() {
      document.addEventListener('item-added-to-cart', () => {
        this.toggleCartDrawer();
      });
    },
  }));
});
```

The drawer's visibility is controlled by the `cartOpen` state:

File: `snippets/component-cart-drawer.liquid`
```liquid
<div
  id="cart-drawer"
  class="color-{{ settings.cart_color_scheme }} gradient"
  :class="{ 'cart-open': cartOpen }"
>
```

This creates a seamless interaction where:
1. The header and drawer share the same Alpine.js data store (`cartDrawer`)
2. Clicking the cart bubble toggles the drawer state
3. Adding items to cart automatically opens the drawer through event listening
4. The drawer's visibility is reactively updated based on the shared state




