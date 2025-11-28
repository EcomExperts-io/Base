# ProductInfo Web Component

`assets/section-product.js` exports the `ProductInfo` class, which extends `HTMLElement` and is registered as the custom element `<product-info>`. This component manages product variant selection, quantity controls, media gallery synchronization, and dynamic product section updates without page reload.

**Source:** [`assets/section-product.js`](../../assets/section-product.js)

## Overview

The `ProductInfo` component:
- Handles variant selection changes and updates product information dynamically
- Manages quantity selector controls (increment/decrement buttons and input validation)
- Initializes and controls Swiper.js galleries for product media (thumbnails and carousel views)
- Updates product price, SKU, inventory, and add-to-cart sections via AJAX
- Synchronizes media gallery to show the selected variant's featured image
- Updates browser URL when variant changes (can be disabled for modal contexts)

## Class Structure

```javascript
export class ProductInfo extends HTMLElement {
  constructor()
  connectedCallback()
  setupEventListeners()
  initSwiper()
  onVariantChange(e)
  onQuantitySelectorEvent(e)
  updateMedia(variantFeaturedMediaId)
  updateURL(variantId)
  updateVariantInputs(variantId)
  updateSourceFromDestination(html, id)
  renderSection(productUrlChanged, productUrl)
  // Getters
  variantSelector
  quantitySelector
  selectedOptionValues
  getSelectedVariant(html)
}
```

## API Reference

| Method / Property | Description |
|------------------|-------------|
| `constructor()` | Initializes the component and sets up abort controller and swiper references |
| `connectedCallback()` | Lifecycle hook that sets up event listeners and initializes Swiper if available |
| `setupEventListeners()` | Attaches event listeners for variant changes, quantity controls, and Swiper initialization |
| `initSwiper()` | Initializes Swiper.js galleries for thumbnail or carousel media views |
| `onVariantChange(e)` | Handles variant selector changes and triggers section re-render |
| `onQuantitySelectorEvent(e)` | Handles quantity input changes and button clicks with min/max validation |
| `updateMedia(variantFeaturedMediaId)` | Updates the media gallery to show the selected variant's featured image |
| `updateURL(variantId)` | Updates browser URL with variant parameter (skipped if `data-update-url="false"`) |
| `updateVariantInputs(variantId)` | Updates hidden variant ID inputs in product forms |
| `updateSourceFromDestination(html, id)` | Copies HTML content from fetched response to current DOM |
| `renderSection(productUrlChanged, productUrl)` | Fetches updated product section and applies changes to DOM |
| `variantSelector` | Getter for the variant selector element |
| `quantitySelector` | Getter for the quantity selector element |
| `selectedOptionValues` | Getter that returns array of selected option value IDs |

## Method Details

### constructor()

```javascript
export class ProductInfo extends HTMLElement {
  abortController = undefined;
  swiper = undefined;

  constructor() {
    super();
  }
}
```

Initializes the custom element and sets up instance properties:
- `abortController`: Used to cancel in-flight fetch requests
- `swiper`: Reference to the Swiper.js instance for media galleries

### connectedCallback()

```javascript
  connectedCallback() {
    this.setupEventListeners();
    if (typeof Swiper !== 'undefined') {
      this.initSwiper();
    }
  }
```

**Behavior:**
1. Sets up all event listeners for variant changes and quantity controls
2. Initializes Swiper galleries if Swiper.js is already loaded
3. Also listens for Swiper script load event to initialize when script loads asynchronously

### setupEventListeners()

```javascript
  setupEventListeners() {
    this.variantSelector?.addEventListener('change', this.onVariantChange.bind(this));
    this.quantitySelector.addEventListener('change', this.onQuantitySelectorEvent.bind(this));
    this.quantitySelector.querySelector('button[name="plus"]').addEventListener('click', this.onQuantitySelectorEvent.bind(this));
    this.quantitySelector.querySelector('button[name="minus"]').addEventListener('click', this.onQuantitySelectorEvent.bind(this));
    document.getElementById('swiper-script').addEventListener('load', this.initSwiper.bind(this));
  }
```

**Event Listeners:**
- Variant selector change events
- Quantity input change events
- Quantity increment/decrement button clicks
- Swiper script load event (for async script loading)

### initSwiper()

```javascript
  initSwiper() {
    const thumbnailGalleryEl = this.querySelector('.product-media-gallery__thumbnails');
    if (thumbnailGalleryEl) {

      const mainGalleryEl = this.querySelector('.product-media-gallery__main');
      if (mainGalleryEl) {
        this.swiper = new Swiper(mainGalleryEl, {
          spaceBetween: 10,
          thumbs: {
            swiper: new Swiper(thumbnailGalleryEl, {
              spaceBetween: 10,
              slidesPerView: 4,
              freeMode: true,
              watchSlidesProgress: true,
              navigation: {
                prevEl: thumbnailGalleryEl.querySelector('.swiper-button-prev'),
                nextEl: thumbnailGalleryEl.querySelector('.swiper-button-next'),
              },
              breakpoints: {
                768: {
                  slidesPerView: 5,
                  spaceBetween: 12,
                },
                1024: {
                  slidesPerView: 6,
                  spaceBetween: 15,
                }
              }
            }),
          },
        });
      }
    }

    const carouselGalleryEl = this.querySelector('.product-media-gallery__carousel');
    if (carouselGalleryEl) {
      this.swiper = new Swiper(carouselGalleryEl, {
        autoHeight: true,
        direction: 'horizontal',
        pagination: {
          el: carouselGalleryEl.querySelector('.swiper-pagination'),
        },
        navigation: {
          prevEl: carouselGalleryEl.querySelector('.swiper-button-prev'),
          nextEl: carouselGalleryEl.querySelector('.swiper-button-next'),
        },
      });
    }
  }
```

**Behavior:**
- Supports two gallery types:
  1. **Thumbnail Gallery**: Main gallery with thumbnail navigation (responsive breakpoints)
  2. **Carousel Gallery**: Simple horizontal carousel with pagination
- Initializes Swiper instances with appropriate configuration
- Only initializes if the corresponding DOM elements exist

### onVariantChange(e)

```javascript
  onVariantChange(e) {
    const productUrlChanged = e.target?.dataset?.productUrl ? (e.target?.dataset?.productUrl !== this.dataset.url) : false;
    const productUrl = e.target?.dataset?.productUrl || this.dataset.url;
    this.renderSection(productUrlChanged, productUrl);
  }
```

**Behavior:**
- Detects if the variant change also changes the product (via `data-product-url` attribute)
- Determines the product URL to fetch (from event target or component's data attribute)
- Triggers section re-render with the new variant/product information

### onQuantitySelectorEvent(e)

```javascript
  onQuantitySelectorEvent(e) {
    const quantityInput = this.quantitySelector.querySelector('input[type="number"]');
    let currentValue = parseInt(quantityInput.value);
    const minValue = parseInt(quantityInput.getAttribute('min')) || 0;
    const maxValue = parseInt(quantityInput.getAttribute('max')) || Infinity;

    if (e.target.name === 'minus' && currentValue > minValue) {
      quantityInput.value = currentValue - 1;
    } else if (e.target.name === 'plus' && currentValue < maxValue) {
      quantityInput.value = currentValue + 1;
    } else if (e.type === 'change') {
      if (currentValue < minValue) {
        quantityInput.value = minValue;
      } else if (currentValue > maxValue) {
        quantityInput.value = maxValue;
      }
    }
  }
```

**Behavior:**
- Handles quantity increment/decrement button clicks
- Validates input changes against min/max constraints
- Clamps values to valid range if user enters invalid values

### updateMedia(variantFeaturedMediaId)

```javascript
  updateMedia(variantFeaturedMediaId) {
    if (!variantFeaturedMediaId) return;
    const mediaSlide = this.querySelector(`.swiper-slide[data-media-id="${variantFeaturedMediaId}"]`);
    if (!mediaSlide) return;

    const slideIndex = parseInt(mediaSlide.dataset.mediaIndex);
    this.swiper?.slideTo(slideIndex);
  }
```

**Behavior:**
- Finds the media slide matching the variant's featured media ID
- Updates Swiper to show the corresponding slide
- Only updates if both the media ID and Swiper instance exist

### updateURL(variantId)

```javascript
  updateURL(variantId) {
    // this.querySelector('share-button')?.updateUrl(
    //   `${window.shopUrl}${url}${variantId ? `?variant=${variantId}` : ''}`
    // );

    // Don't update URL if this is in a modal/quick-add context
    if (this.dataset.updateUrl === 'false') return;

    if (!window.location.pathname.includes('/products/')) return;
    window.history.replaceState({}, '', `${this.dataset.url}${variantId ? `?variant=${variantId}` : ''}`);
  }
```

**Behavior:**
- Updates browser URL with variant parameter using `history.replaceState`
- Skips URL update if `data-update-url="false"` (for modal/quick-add contexts)
- Only updates on product pages (pathname includes `/products/`)

### renderSection(productUrlChanged, productUrl)

```javascript
  renderSection(productUrlChanged, productUrl) {
    this.abortController?.abort();
    this.abortController = new AbortController();

    // If the section is in a modal, use the original section id without the modal suffix
    const sectionId = this.dataset.updateUrl === 'false' ? this.dataset.section.split('-modal')[0] : this.dataset.section;
    fetch(`${productUrl}?option_values=${this.selectedOptionValues}&section_id=${sectionId}`, {
      signal: this.abortController.signal,
    })
      .then((response) => response.text())
      .then((responseText) => {
        // If the section is in a modal, replace the original section id with the modal section id
        if (this.dataset.updateUrl === 'false') {
          responseText = responseText.replaceAll(this.dataset.section.split('-modal')[0], this.dataset.section);
        }

        // Parse the response text into an HTML document
        const html = new DOMParser().parseFromString(responseText, 'text/html');
        const variant = this.getSelectedVariant(html);
        if (productUrlChanged) {
          // If the product url has changed, replace the current section with the new section
          const productInfo = html.querySelector('product-info');
          this.replaceWith(productInfo);
          productInfo.updateURL(variant?.id);
        } else {
          this.updateMedia(variant?.featured_media?.id);
          this.updateURL(variant?.id);
          this.updateVariantInputs(variant?.id);
          this.updateSourceFromDestination(html, `add-to-cart-container-${this.dataset.section}`);
          this.updateSourceFromDestination(html, `variant-selector-${this.dataset.section}`);
          this.updateSourceFromDestination(html, `price-${this.dataset.section}`);
          this.updateSourceFromDestination(html, `sku-${this.dataset.section}`);
          this.updateSourceFromDestination(html, `inventory-${this.dataset.section}`);
        }
      })
      .catch((error) => {
        if (error.name === 'AbortError') {
          console.log('Fetch aborted by user');
        } else {
          console.error(error);
        }
      });
  }
```

**Behavior:**
1. Aborts any previous in-flight requests
2. Constructs fetch URL with selected option values and section ID
3. Handles modal contexts by adjusting section IDs
4. Parses response and extracts variant information
5. If product changed: replaces entire component with new product info
6. If same product: updates media, URL, variant inputs, and specific DOM sections (price, SKU, inventory, add-to-cart, variant selector)
7. Handles errors gracefully (abort errors are expected, others are logged)

## Custom Element Definition

```javascript
if (!customElements.get('product-info')) {
  customElements.define('product-info', ProductInfo);
}
```

Ensures the element is registered only once across bundles or hot reload sessions.

## Integration with Shopify Liquid

```liquid
<product-info
  data-url="{{ product.url }}"
  data-section="{{ section.id }}"
  data-update-url="true"
  class="product__info"
>
  <!-- Variant selector -->
  <variant-selector data-picker-type="dropdown">
    <!-- Variant options -->
  </variant-selector>

  <!-- Quantity selector -->
  <quantity-selector>
    <button name="minus">-</button>
    <input type="number" min="1" max="10" value="1">
    <button name="plus">+</button>
  </quantity-selector>

  <!-- Product media gallery -->
  <div class="product-media-gallery__main">
    <!-- Swiper slides -->
  </div>

  <!-- Product details sections with IDs -->
  <div id="price-{{ section.id }}">...</div>
  <div id="sku-{{ section.id }}">...</div>
  <div id="inventory-{{ section.id }}">...</div>
  <div id="add-to-cart-container-{{ section.id }}">...</div>
</product-info>

<script src="{{ 'section-product.js' | asset_url }}" type="module"></script>
```

## Implementation Notes

- The component requires `data-url` and `data-section` attributes on the element
- Set `data-update-url="false"` to disable URL updates (useful for modals)
- Variant selector must be a `<variant-selector>` element with either dropdown or button picker type
- Quantity selector must contain an input with min/max attributes and buttons with `name="plus"` and `name="minus"`
- Media slides must have `data-media-id` and `data-media-index` attributes for gallery synchronization
- Sections to update must have IDs matching the pattern: `{section-name}-{section.id}`
- Swiper.js must be loaded before or the component will wait for the script load event
- The component uses AbortController to cancel previous requests when new variant changes occur
- For modal contexts, section IDs are modified to include `-modal` suffix to prevent conflicts

