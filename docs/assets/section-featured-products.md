# FeaturedProducts Web Component

`assets/section-featured-products.js` exports the `FeaturedProducts` class, which extends `HTMLElement` and is registered as the custom element `<featured-products>`. This component initializes and manages a Swiper.js carousel for displaying featured products with responsive breakpoints.

**Source:** [`assets/section-featured-products.js`](../../assets/section-featured-products.js)

## Overview

The `FeaturedProducts` component:
- Initializes a Swiper.js carousel for featured products display
- Handles responsive breakpoints for different screen sizes
- Listens to Shopify section load/unload events for theme editor compatibility
- Prevents duplicate Swiper initialization
- Properly cleans up Swiper instances when sections are unloaded

## Class Structure

```javascript
export class FeaturedProducts extends HTMLElement {
  constructor()
  connectedCallback()
  disconnectedCallback()
  init()
  destroy()
  onSectionLoad(e)
  onSectionUnload(e)
}
```

## API Reference

| Method | Description |
|--------|-------------|
| `constructor()` | Initializes the component, stores section ID, and binds event handlers |
| `connectedCallback()` | Lifecycle hook that initializes Swiper and sets up Shopify section event listeners |
| `disconnectedCallback()` | Lifecycle hook that destroys Swiper and removes event listeners |
| `init()` | Initializes Swiper.js carousel with responsive configuration |
| `destroy()` | Destroys the Swiper instance and cleans up resources |
| `onSectionLoad(e)` | Handles Shopify section load events in theme editor |
| `onSectionUnload(e)` | Handles Shopify section unload events in theme editor |

## Method Details

### constructor()

```javascript
export class FeaturedProducts extends HTMLElement {
  constructor() {
    super();
    this.swiper = null;
    this.sectionId = this.getAttribute('data-section-id');

    // Store bound methods so add/removeEventListener match
    this.onSectionLoad = this.onSectionLoad.bind(this);
    this.onSectionUnload = this.onSectionUnload.bind(this);
  }
}
```

**Initialization:**
- Sets `swiper` to `null` initially
- Retrieves section ID from `data-section-id` attribute
- Binds event handler methods for proper event listener management

### connectedCallback()

```javascript
  connectedCallback() {
    this.init();
    document.addEventListener('shopify:section:load', this.onSectionLoad);
    document.addEventListener('shopify:section:unload', this.onSectionUnload);
  }
```

**Behavior:**
1. Initializes the Swiper carousel
2. Listens for Shopify section load events (theme editor)
3. Listens for Shopify section unload events (theme editor)

### disconnectedCallback()

```javascript
  disconnectedCallback() {
    this.destroy();
    document.removeEventListener('shopify:section:load', this.onSectionLoad);
    document.removeEventListener('shopify:section:unload', this.onSectionUnload);
  }
```

**Behavior:**
- Destroys Swiper instance to prevent memory leaks
- Removes all event listeners for proper cleanup

### init()

```javascript
  init() {
    if (window.Swiper && this.sectionId) {
      const selector = `#featured-products-${this.sectionId}`;
      const swiperEl = document.querySelector(selector);

      // Prevent duplicate swiper initialization
      if (!swiperEl || swiperEl.classList.contains('swiper-initialized')) return;

      this.swiper = new Swiper(selector, {
        slidesPerView: 1.8,
        spaceBetween: 16,
        autoHeight: true,
        navigation: {
          nextEl: `${selector} .featured-products__swiper-next`,
          prevEl: `${selector} .featured-products__swiper-prev`,
        },
        breakpoints: {
          750: { slidesPerView: 2, centeredSlides: false },
          990: { slidesPerView: 4, centeredSlides: false },
        },
        loop: false,
        watchOverflow: true,
      });
    }
  }
```

**Configuration:**
- **Mobile (< 750px)**: 1.8 slides per view with 16px spacing
- **Tablet (750px+)**: 2 slides per view
- **Desktop (990px+)**: 4 slides per view
- **Features**: Auto-height, navigation buttons, no loop, overflow detection

**Safety Checks:**
- Only initializes if Swiper.js is loaded and section ID exists
- Prevents duplicate initialization by checking for `swiper-initialized` class

### destroy()

```javascript
  destroy() {
    if (this.swiper) {
      this.swiper.destroy(true, true);
      this.swiper = null;
    }
  }
```

**Behavior:**
- Destroys Swiper instance with full cleanup (removes all listeners and DOM modifications)
- Resets swiper reference to null

### onSectionLoad(e)

```javascript
  onSectionLoad(e) {
    if (e.detail && e.detail.sectionId === this.sectionId) {
      this.destroy();
      this.init();
    }
  }
```

**Behavior:**
- Triggered when Shopify theme editor loads a section
- Destroys existing Swiper and re-initializes to ensure fresh state

### onSectionUnload(e)

```javascript
  onSectionUnload(e) {
    if (e.detail && e.detail.sectionId === this.sectionId) {
      this.destroy();
    }
  }
```

**Behavior:**
- Triggered when Shopify theme editor unloads a section
- Destroys Swiper instance to prevent memory leaks

## Custom Element Definition

```javascript
if (!customElements.get('featured-products')) {
  customElements.define('featured-products', FeaturedProducts);
}
```

Ensures the element is registered only once across bundles or hot reload sessions.

## Integration with Shopify Liquid

```liquid
<featured-products data-section-id="{{ section.id }}">
  <div id="featured-products-{{ section.id }}" class="swiper">
    <div class="swiper-wrapper">
      {% for product in collections.featured.products %}
        <div class="swiper-slide">
          {% render 'component-product-card', product: product %}
        </div>
      {% endfor %}
    </div>
    
    <button class="featured-products__swiper-prev">Previous</button>
    <button class="featured-products__swiper-next">Next</button>
  </div>
</featured-products>

<script src="{{ 'section-featured-products.js' | asset_url }}" type="module"></script>
```

## Implementation Notes

- The component requires a `data-section-id` attribute matching the Shopify section ID
- The Swiper container must have an ID matching `#featured-products-{sectionId}`
- Navigation buttons must have classes `.featured-products__swiper-prev` and `.featured-products__swiper-next`
- Swiper.js must be loaded before this component initializes
- The component automatically handles theme editor section load/unload events
- Duplicate initialization is prevented by checking for `swiper-initialized` class
- The component properly cleans up resources when removed from DOM

