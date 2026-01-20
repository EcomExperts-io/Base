# Related Products Section (`sections/related-products.liquid`)

`sections/related-products.liquid` renders Shopify product recommendations (“You may also like”) on product pages. Recommendations are fetched asynchronously using the `product-recommendations` custom element. The section supports two layouts: **grid** and **carousel** (Swiper). When carousel is enabled, the `related-products-carousel` custom element initializes Swiper after recommendations load.

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | Inline `{% style %}` block inside the section |
| CSS  | `component-product-card.css`, `component-product-price.css` |
| JS   | `product-recommendations.js` (module), `component-product-card.js` (module) |
| JS (conditional) | `section-related-products.js` (module, only when layout is `carousel`) |
| Custom Elements | `<product-recommendations>`, `<related-products-carousel>` (carousel layout) |
| Snippets | `component-product-card` |
| Data | Uses Shopify recommendations object (`recommendations`) + `product` context |

Notes:

- `product-recommendations.js` lazy-loads section markup from Shopify’s Product Recommendations endpoint (`routes.product_recommendations_url`).
- Carousel mode requires Swiper to be available globally (`window.Swiper`).

---

## Dynamic Styles

The section defines a large inline `{% style %}` block that includes:

- Responsive padding via `.section-\{\{ section.id \}\}-padding`
- Heading sizing via `heading_size` (`h0`, `h1`, `h2`)
- Grid layout columns using `columns_desktop` and `columns_mobile`
- Carousel styles including navigation button styles and responsive behavior

Example (responsive padding):

```liquid
{% style %}
  .section-{{ section.id }}-padding {
    padding-top: {{ section.settings.padding_top | times: 0.75 | round: 0 }}px;
    padding-bottom: {{ section.settings.padding_bottom | times: 0.75 | round: 0 }}px;
  }

  @media screen and (min-width: 750px) {
    .section-{{ section.id }}-padding {
      padding-top: {{ section.settings.padding_top }}px;
      padding-bottom: {{ section.settings.padding_bottom }}px;
    }
  }
{% endstyle %}
```

---

## Markup Structure

The outer wrapper uses section color scheme and padding:

```liquid
<div class="color-{{ section.settings.color_scheme }} gradient section-{{ section.id }}-padding">
  <!-- grid or carousel -->
</div>
```

Both layouts render the same recommendation content when available:

```liquid
{% if recommendations.performed and recommendations.products_count > 0 %}
  <h2 class="related-products__heading {{ section.settings.heading_size }}">
    {{ section.settings.heading }}
  </h2>
  <!-- product cards -->
{% endif %}
```

### Data source (AJAX recommendations)

Both layouts use a `<product-recommendations>` element with `data-url` pointing to Shopify’s recommendations endpoint.

Example `data-url` format (kept inside a code block to avoid VitePress mustache parsing issues [[memory:13638067]]):

```liquid
data-url="{{ routes.product_recommendations_url }}?section_id={{ section.id }}&product_id={{ product.id }}&limit={{ products_to_show }}&intent=related"
```

### Grid layout

```liquid
<product-recommendations
  class="related-products page-width isolate"
  data-url="..."
  data-layout="grid"
>
  {% if recommendations.performed and recommendations.products_count > 0 %}
    <ul class="related-products__grid" role="list">
      {% for recommendation in recommendations.products %}
        <li class="related-products__grid-item">
          {% render 'component-product-card',
            card_product: recommendation,
            show_vendor: section.settings.show_vendor,
            enable_swatches: section.settings.enable_swatches,
            swatch_trigger: section.settings.swatch_trigger,
            swatch_type: section.settings.swatch_type,
            media_aspect_ratio: section.settings.image_ratio,
            quick_add: section.settings.enable_quick_add,
            section_id: section.id
          %}
        </li>
      {% endfor %}
    </ul>
  {% endif %}
</product-recommendations>
```

### Carousel layout

Carousel wraps the recommendations element in `<related-products-carousel>` and uses Swiper markup:

```liquid
<related-products-carousel data-section-id="{{ section.id }}">
  <product-recommendations class="related-products page-width isolate" data-url="..." data-layout="carousel">
    {% if recommendations.performed and recommendations.products_count > 0 %}
      <div class="related-products__carousel-wrapper">
        <button class="swiper-button-prev related-products__nav" type="button" aria-label="Previous">
          <!-- inline SVG -->
        </button>

        <div id="related-products-{{ section.id }}" class="related-products__carousel swiper">
          <ul class="swiper-wrapper" role="list">
            {% for recommendation in recommendations.products %}
              <li class="swiper-slide">
                {% render 'component-product-card', card_product: recommendation %}
              </li>
            {% endfor %}
          </ul>
        </div>

        <button class="swiper-button-next related-products__nav" type="button" aria-label="Next">
          <!-- inline SVG -->
        </button>
      </div>
    {% endif %}
  </product-recommendations>
</related-products-carousel>
```

---

## JavaScript Behavior

### `product-recommendations` (lazy fetch)

`assets/product-recommendations.js` defines a `product-recommendations` custom element that:

- Observes itself with `IntersectionObserver` (rootMargin `0px 0px 200px 0px`)
- When intersecting, fetches `this.dataset.url`
- Parses returned HTML and extracts `<product-recommendations>` content
- Replaces its own innerHTML with the fetched recommendations content

### `related-products-carousel` (carousel init)

`assets/section-related-products.js` defines `related-products-carousel`:

- If slides already exist, initializes Swiper immediately.
- Otherwise uses `MutationObserver` to wait until `.swiper-slide` elements appear (after AJAX load), then initializes Swiper.
- Destroys Swiper and disconnects observers on `disconnectedCallback`.

Swiper configuration highlights:
- `slidesPerView`: 1.2 → 2 → 3 → 4 at breakpoints (480 / 750 / 990)
- Navigation buttons wired via `.swiper-button-prev` and `.swiper-button-next`

---

## Behavior

- **Product-page only**: `enabled_on.templates` is set to `["product"]`.
- **Async loading**: Recommendations are loaded lazily when the element approaches the viewport.
- **Grid or carousel**: Controlled by `layout_style` setting.
- **Conditional carousel JS**: `section-related-products.js` only loads when `layout_style == 'carousel'`.

---

## Schema

```json
{
  "name": "Related products",
  "enabled_on": { "templates": ["product"] },
  "settings": [
    { "type": "inline_richtext", "id": "heading", "default": "You may also like" },
    { "type": "select", "id": "heading_size", "default": "h1" },
    { "type": "select", "id": "layout_style", "default": "grid" },
    { "type": "range", "id": "products_to_show", "default": 4 },
    { "type": "range", "id": "columns_desktop", "default": 4 },
    { "type": "select", "id": "columns_mobile", "default": "2" },
    { "type": "select", "id": "image_ratio", "default": "adapt" },
    { "type": "checkbox", "id": "show_vendor", "default": false },
    { "type": "select", "id": "enable_quick_add", "default": "standard" },
    { "type": "checkbox", "id": "enable_swatches", "default": true },
    { "type": "text", "id": "swatch_trigger", "default": "Color" },
    { "type": "select", "id": "swatch_type" },
    { "type": "color_scheme", "id": "color_scheme", "default": "scheme-1" },
    { "type": "range", "id": "padding_top", "default": 36 },
    { "type": "range", "id": "padding_bottom", "default": 36 }
  ]
}
```

---

## Implementation Notes

1. **Liquid + VitePress**: Keep Liquid mustaches inside fenced code blocks, or escape them in prose, to avoid blank docs pages [[memory:13638067]].
2. **Fetch endpoint**: `data-url` hits `routes.product_recommendations_url` with `section_id`, `product_id`, `limit`, and `intent=related`.
3. **Recommendations object**: The section only renders cards when `recommendations.performed` and `recommendations.products_count > 0`.
4. **Swiper requirement**: Carousel mode requires `window.Swiper` to be present; otherwise JS logs an error.
5. **Deferred init**: Carousel uses a `MutationObserver` because the slides are injected after AJAX load.
6. **Assets loaded by section**: `product-recommendations.js` and `component-product-card.js` are always loaded; `section-related-products.js` loads only for carousel.
