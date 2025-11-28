# ProductRecommendations Web Component

`assets/product-recommendations.js` exports the `ProductRecommendations` class, which extends `HTMLElement` and is registered as the custom element `<product-recommendations>`. This component lazily loads product recommendations when the element enters the viewport, improving initial page load performance.

**Source:** [`assets/product-recommendations.js`](../../assets/product-recommendations.js)

## Overview

The `ProductRecommendations` component:
- Uses Intersection Observer API to detect when the element enters the viewport
- Fetches product recommendations from Shopify's recommendation API
- Loads recommendations only when needed (lazy loading)
- Uses a 200px bottom margin to start loading before the element is fully visible
- Replaces the element's content with fetched recommendations

## Class Structure

```javascript
export class ProductRecommendations extends HTMLElement {
  constructor()
  connectedCallback()
  handleIntersection(entries, observer)
}
```

## API Reference

| Method | Description |
|--------|-------------|
| `constructor()` | Initializes the component and binds the intersection handler |
| `connectedCallback()` | Lifecycle hook that creates IntersectionObserver and begins observing |
| `handleIntersection(entries, observer)` | Handles intersection events, fetches recommendations, and updates DOM |

## Method Details

### constructor()

```javascript
export class ProductRecommendations extends HTMLElement {
  constructor() {
    super();
    this.handleIntersection = this.handleIntersection.bind(this);
    this.observer = null;
  }
}
```

**Initialization:**
- Binds the intersection handler method for proper context
- Initializes observer reference as null

### connectedCallback()

```javascript
  connectedCallback() {
    this.observer = new IntersectionObserver(this.handleIntersection, {
      rootMargin: '0px 0px 200px 0px'
    });

    this.observer.observe(this);
  }
```

**Behavior:**
- Creates IntersectionObserver with 200px bottom margin (starts loading 200px before element is visible)
- Begins observing the element itself

### handleIntersection(entries, observer)

```javascript
  handleIntersection(entries, observer) {
    if (!entries[0].isIntersecting) return;

    observer.unobserve(this);

    const url = this.dataset.url;

    fetch(url)
      .then(response => response.text())
      .then(text => {
        const html = document.createElement('div');
        html.innerHTML = text;
        const recommendations = html.querySelector('product-recommendations');

        if (recommendations && recommendations.innerHTML.trim().length) {
          this.innerHTML = recommendations.innerHTML;
        }
      })
      .catch(e => {
        console.error(e);
      });
  }
```

**Behavior:**
1. Checks if element is intersecting (visible)
2. Stops observing after first intersection (loads only once)
3. Fetches recommendations from URL in `data-url` attribute
4. Parses response HTML and extracts the recommendations content
5. Replaces element's innerHTML with fetched recommendations (only if content exists)
6. Handles errors by logging to console

**Note:** The component only updates if the fetched content has non-empty innerHTML, preventing empty states from being displayed.

## Custom Element Definition

```javascript
if (!customElements.get('product-recommendations')) {
  customElements.define('product-recommendations', ProductRecommendations);
}
```

Ensures the element is registered only once across bundles or hot reload sessions.

## Integration with Shopify Liquid

```liquid
<product-recommendations
  data-url="{{ routes.product_recommendations_url }}?product_id={{ product.id }}&limit=4"
>
  <!-- Placeholder content or loading state -->
  <div class="product-recommendations__loading">
    Loading recommendations...
  </div>
</product-recommendations>

<script src="{{ 'product-recommendations.js' | asset_url }}" type="module"></script>
```

## Implementation Notes

- The component requires a `data-url` attribute with the recommendations API endpoint
- Recommendations are loaded lazily when the element approaches the viewport (200px margin)
- The component only loads once per page load (stops observing after first intersection)
- If the fetched content is empty, the element's content remains unchanged
- The component gracefully handles fetch errors without breaking the page
- Use Shopify's `routes.product_recommendations_url` helper to generate the correct URL
- The component works with Shopify's built-in product recommendations feature

