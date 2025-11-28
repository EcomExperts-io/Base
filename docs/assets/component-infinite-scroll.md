# InfiniteScroll Web Component

`assets/component-infinite-scroll.js` exports the `InfiniteScroll` class, which extends `HTMLElement` and is registered as the custom element `<infinite-scroll>`. This component automatically loads the next page of products when the element enters the viewport, providing seamless infinite scrolling for collection pages.

**Source:** [`assets/component-infinite-scroll.js`](../../assets/component-infinite-scroll.js)

## Overview

The `InfiniteScroll` component:
- Uses the Intersection Observer API to detect when the element enters the viewport
- Automatically fetches the next page of products from the pagination link
- Appends new products to the existing product grid without page reload
- Replaces itself with the next page's infinite scroll element or removes itself when no more pages exist
- Shows a loading state during the fetch operation

## Class Structure

```javascript
export class InfiniteScroll extends HTMLElement {
  constructor()
  async loadNextPage()
}
```

## API Reference

| Method | Description |
|--------|-------------|
| `constructor()` | Initializes the component, sets up IntersectionObserver, and begins observing the element |
| `loadNextPage()` | Disconnects the observer, fetches the next page, appends products to the grid, and handles element replacement/removal |

## Method Details

### constructor()

```javascript
export class InfiniteScroll extends HTMLElement {
  constructor() {
    super();
    this.anchor = this.querySelector("a");
    if (!this.anchor) return;

    this.observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          this.loadNextPage();
        }
      });
    });

    this.observer.observe(this);
  }
}
```

**DOM References:**
- `this.anchor`: The anchor element (`<a>`) containing the pagination link (must be a direct child)

**Behavior:**
1. Calls `super()` to initialize the HTMLElement base class
2. Queries for an anchor element (`<a>`) as a direct child
3. Returns early if no anchor is found (component won't function without it)
4. Creates an `IntersectionObserver` that triggers `loadNextPage()` when the element enters the viewport
5. Begins observing the element itself (not the anchor)

**Note:** The component requires an anchor element with an `href` attribute pointing to the next page. If no anchor is found, the component silently fails.

### loadNextPage()

```javascript
  async loadNextPage() {
    this.observer.disconnect();

    this.anchor.style.display = "flex";
    this.anchor.innerText = "Loading...";

    const url = this.anchor.getAttribute("href");
    if (!url) return;

    try {
      const response = await fetch(url);
      const text = await response.text();
      const html = new DOMParser().parseFromString(text, "text/html");

      // Grab the product grid from the next page
      const newGrid = html.querySelector("[data-product-grid]");
      const grid = document.querySelector("[data-product-grid]");

      if (newGrid && grid) {
        Array.from(newGrid.children).forEach((child) => {
          grid.appendChild(child);
        });
      }

      // Handle next infinite scroll
      const newInfinite = html.querySelector("infinite-scroll");
      if (newInfinite) {
        this.replaceWith(newInfinite);
      } else {
        this.remove();
      }
    } catch (err) {
      console.error("InfiniteScroll error:", err);
    }

    this.anchor.style.display = "none";
    this.anchor.innerText = "";
  }
```

**Behavior:**
1. **Disconnects observer**: Prevents multiple simultaneous loads
2. **Shows loading state**: Sets anchor display to `flex` and text to "Loading..."
3. **Fetches next page**: Uses the anchor's `href` attribute to fetch the next page HTML
4. **Parses response**: Uses `DOMParser` to parse the fetched HTML
5. **Appends products**: Finds `[data-product-grid]` in both the new page and current page, then appends all children from the new grid to the current grid
6. **Handles pagination**: 
   - If the new page contains another `<infinite-scroll>` element, replaces the current element with it
   - If no more pages exist, removes the current element
7. **Error handling**: Logs errors to console if fetch fails
8. **Hides loading state**: Resets anchor display and text after completion

**Requirements:**
- The anchor element must have an `href` attribute with a valid URL
- The current page must contain an element with `[data-product-grid]` attribute
- The fetched page must also contain an element with `[data-product-grid]` attribute
- The anchor element should be styled to display as `flex` when visible

## Custom Element Definition

```javascript
if (!customElements.get("infinite-scroll")) {
  customElements.define("infinite-scroll", InfiniteScroll);
}
```

Ensures the element is registered only once across bundles or hot reload sessions.

## Integration with Shopify Liquid

```liquid
<div data-product-grid>
  {% for product in collection.products %}
    {% render 'component-product-card', product: product %}
  {% endfor %}
</div>

{% if paginate.next %}
  <infinite-scroll>
    <a href="{{ paginate.next.url }}" style="display: none;">
      {{ 'products.product.load_more' | t }}
    </a>
  </infinite-scroll>
{% endif %}

<script src="{{ 'component-infinite-scroll.js' | asset_url }}" type="module"></script>
```

## Implementation Notes

- The component must contain an anchor element (`<a>`) as a direct child with an `href` attribute pointing to the next page
- The product grid container must have the `[data-product-grid]` attribute
- The anchor element should be hidden by default (e.g., `display: none`) and will be shown during loading
- The component automatically handles pagination by replacing itself with the next page's infinite scroll element
- If there are no more pages, the component removes itself from the DOM
- The IntersectionObserver triggers when the element enters the viewport, so position it appropriately (typically at the bottom of the product grid)
- Error handling is minimal—failed fetches are logged to the console but don't show user-facing errors

