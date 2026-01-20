# Featured Collections V2 Section (`sections/featured-collections-v2.liquid`)

`sections/featured-collections-v2.liquid` renders a tabbed, Swiper-powered carousel of products for multiple collections. Each block represents a collection tab; switching tabs shows the corresponding product carousel. Products render using the `component-product-card` snippet, with optional swatches and optional quick add.

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | `section-featured-collections-v2.css`, `component-product-card.css`, `component-product-price.css` |
| JS   | `section-featured-collections-v2.js` (module), `component-product-card.js` (module) |
| Custom Element | `<featured-collections-v2>` defined in `section-featured-collections-v2.js` |
| Blocks | `collection_card` block type (limit: 5) |
| Data | Relies on `section.blocks` (collections) and `section.settings` (layout + product card options) |

Optional (only when `quick_add` is set to `standard`):

- CSS: `component-quick-add.css`
- JS: `component-quick-add.js`, `component-modal-opener.js`

Notes:

- The carousel uses **Swiper** (`new Swiper(...)`) in `section-featured-collections-v2.js`. This section assumes Swiper is available globally.

---

## Dynamic Styles

The section uses responsive padding set via a `{%- style -%}` block:

```liquid
{%- style -%}
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
{%- endstyle -%}
```

- **Responsive padding**: Mobile padding is 75% of desktop value; full padding applies at 750px+.

---

## Markup Structure

```liquid
{%- if collections_to_show > 0 -%}
  <featured-collections-v2
    data-section-id="{{ section.id }}"
    class="color-{{ section.settings.color_scheme }} section-{{ section.id }}-padding"
  >
    <div class="page-width featured-collections-v2__content">
      <div class="featured-collections-v2__header" style="text-align: {{ heading_alignment }};">
        <!-- Heading + tabs -->
      </div>

      <div class="featured-collections-v2__swipers-container">
        <!-- One Swiper container per collection block -->
      </div>
    </div>
  </featured-collections-v2>
{%- endif -%}
```

- Section renders only when at least one collection block exists.
- `<featured-collections-v2>` custom element manages tab switching and Swiper initialization.

### Header + Tabs

Tabs are implemented with hidden radio inputs and labels. Each input points to a Swiper container via `data-target-swiper`.

```liquid
<div class="featured-collections-v2__tabs">
  {% for block in section.blocks %}
    <input
      hidden
      type="radio"
      name="collection-title-{{ section.id }}"
      id="tab-{{ block.id }}"
      data-target-swiper="swiper-{{ block.id }}"
      {% if forloop.first %}checked{% endif %}
    >

    <label class="featured-collections-v2__tab-label" for="tab-{{ block.id }}">
      {{- block.settings.custom_title -}}
    </label>
  {% endfor %}
</div>
```

- The first tab is selected by default.
- Avoid using unescaped Liquid mustaches in inline/prose; if you reference IDs, escape them like `tab-\{\{ block.id \}\}`. [[memory:13638067]]

### Swiper Containers (one per block)

```liquid
{% for block in section.blocks %}
  {% assign current_collection = block.settings.collection %}

  <div
    {{ block.shopify_attributes }}
    id="swiper-{{ block.id }}"
    data-product-grid-gap="{{ product_grid_gap }}"
    data-products-on-desktop="{{ products_on_desktop }}"
    data-products-on-mobile="{{ products_on_mobile }}"
    class="featured-collections-v2__swiper swiper {% unless forloop.first %}hidden{% endunless %}"
  >
    <div class="featured-collections-v2__swiper-arrows">
      <div class="swiper-button-prev featured-collections-v2__swiper-prev">
        {{ 'icon-arrow-prev.svg' | inline_asset_content }}
      </div>
      <div class="swiper-button-next featured-collections-v2__swiper-next">
        {{ 'icon-arrow-next.svg' | inline_asset_content }}
      </div>
    </div>

    <div data-product-grid class="swiper-wrapper">
      <!-- Slides -->
    </div>
  </div>
{% endfor %}
```

- Only the first swiper is visible initially; others use `.hidden` (`display: none` in CSS).
- Each swiper carries configuration via `data-` attributes (gap and slides per breakpoint).

### Slides: Products vs Placeholders

If the selected collection has products, real products are rendered using `component-product-card`:

```liquid
{% for product in current_collection.products limit: total_products_limit %}
  <div class="swiper-slide">
    {% render 'component-product-card',
      card_product: product,
      show_vendor: section.settings.show_vendor,
      enable_swatches: section.settings.enable_swatches,
      swatch_trigger: section.settings.swatch_trigger,
      swatch_type: section.settings.swatch_type,
      quick_add: section.settings.quick_add,
      section_id: section.id,
      button_text_color: section.settings.button_text_color,
      button_border_color: section.settings.button_border_color
    %}
  </div>
{% endfor %}
```

If the collection is blank or has no products, placeholder slides render:

```liquid
{%- for i in (1..6) -%}
  <div class="swiper-slide">
    <div class="featured-collections-v2__placeholder-card">
      <div class="featured-collections-v2__placeholder-card-inner">
        <div class="featured-collections-v2__placeholder-card-media">
          {%- capture current -%}{% cycle 1, 2, 3, 4, 5, 6 %}{%- endcapture -%}
          {{ 'product-' | append: current | placeholder_svg_tag: 'placeholder-svg' }}
        </div>
      </div>
      <div class="featured-collections-v2__placeholder-card-content">
        <h3 class="placeholder-card__heading">
          <a role="link" aria-disabled="true" class="full-unstyled-link">
            {{ block.settings.custom_title }} Product {{ i }}
          </a>
        </h3>
        <div class="placeholder-card__price">
          <span class="price-item price-item--regular"> $19.99 </span>
        </div>
      </div>
    </div>
  </div>
{%- endfor -%}
```

---

## JavaScript Behavior

The section uses a custom element `<featured-collections-v2>` defined in `section-featured-collections-v2.js`:

- **Tab switching**: listens to `change` on the radio inputs and toggles `.hidden` on swiper containers.
- **Swiper initialization**: initializes Swiper on each `.swiper` element and stores instances for cleanup.
- **Hidden swipers support**: Swiper is initialized with `observer: true` and `observeParents: true` to support showing/hiding containers.
- **Cleanup**: `disconnectedCallback` destroys swiper instances.

Key configuration pulled from each swiper container:
- `data-product-grid-gap`
- `data-products-on-desktop`
- `data-products-on-mobile`

Breakpoints used:
- `750`: slides per view = `products_on_mobile`
- `990`: slides per view = `products_on_desktop`

---

## Behavior

- **Tabbed collections**: Each block creates a tab and a matching carousel.
- **Responsive carousels**: Slides-per-view changes at `750px` and `990px` breakpoints.
- **Placeholders**: If a collection has no products, placeholder cards render (6 slides).
- **Optional quick add**: When enabled, loads additional assets and product cards can provide quick add UI.

---

## Schema

```json
{
  "name": "Featured Collections V2",
  "tag": "section",
  "class": "featured-collections-v2",
  "settings": [
    { "type": "color_scheme", "id": "color_scheme", "label": "t:sections.all.colors.label", "default": "scheme-1" },
    { "type": "text", "id": "heading", "label": "Heading", "default": "Find the perfect fit for your game" },
    {
      "type": "select",
      "id": "heading_alignment",
      "label": "Heading Alignment",
      "options": [
        { "value": "left", "label": "Left" },
        { "value": "center", "label": "Center" },
        { "value": "right", "label": "Right" }
      ],
      "default": "center"
    },
    { "type": "range", "id": "total_products_limit", "label": "Total Products Limit", "min": 2, "max": 15, "step": 1, "default": 6 },
    { "type": "checkbox", "id": "show_vendor", "default": false, "label": "t:sections.main-collection-product-grid.settings.show_vendor.label" },
    { "type": "select", "id": "quick_add", "default": "none", "label": "t:sections.main-collection-product-grid.settings.quick_add.label" },
    { "type": "checkbox", "id": "enable_swatches", "default": true, "label": "t:sections.main-collection-product-grid.settings.enable_swatches.label" },
    { "type": "select", "id": "swatch_type", "default": "color", "label": "t:sections.main-collection-product-grid.settings.swatch_type.label" },
    { "type": "text", "id": "swatch_trigger", "default": "Color", "label": "Swatch trigger" },
    { "type": "header", "content": "Layout Settings" },
    { "type": "range", "id": "product_grid_gap", "label": "Product Grid Gap", "min": 10, "max": 30, "step": 2, "default": 16 },
    { "type": "range", "id": "products_on_desktop", "label": "Products on Desktop", "min": 2, "max": 6, "step": 1, "default": 4 },
    { "type": "range", "id": "products_on_mobile", "label": "Products on Mobile", "min": 2, "max": 6, "step": 2, "default": 2 },
    { "type": "range", "id": "padding_top", "label": "Padding Top", "min": 0, "max": 100, "step": 4, "unit": "px", "default": 80 },
    { "type": "range", "id": "padding_bottom", "label": "Padding Bottom", "min": 0, "max": 100, "step": 4, "unit": "px", "default": 60 }
  ],
  "blocks": [
    {
      "type": "collection_card",
      "name": "Collection Card",
      "limit": 5,
      "settings": [
        { "type": "collection", "id": "collection", "label": "Collection" },
        { "type": "image_picker", "id": "custom_image", "label": "Custom Image (optional)" },
        { "type": "text", "id": "custom_title", "label": "Custom Title (optional)" }
      ]
    }
  ],
  "presets": [{ "name": "Featured Collections V2" }]
}
```

---

## Implementation Notes

1. **Swiper dependency**: `section-featured-collections-v2.js` calls `new Swiper(...)` and assumes Swiper is available globally.
2. **Hidden swiper containers**: Swipers for non-active tabs start hidden (`display: none`). Swiper uses `observer`/`observeParents` to work when a container is shown.
3. **Tabs use radio inputs**: Tabs are accessible labels tied to hidden radios; switching triggers `change`.
4. **Per-tab configuration**: Gap and slides-per-view counts are passed through `data-` attributes on each swiper container.
5. **Placeholders**: When a collection is missing or empty, 6 placeholder slides render with placeholder SVGs and a hardcoded `$19.99` price.
6. **Product card rendering**: Real products render via `{% render 'component-product-card' %}` and inherit many behaviors (swatches, quick add).
7. **Quick add assets are conditional**: Extra quick-add assets are loaded only when `quick_add` is `standard`.
8. **Inline mustaches in docs**: If referencing Liquid mustaches in prose/inline code, escape them like `\{\{ ... \}\}` to avoid VitePress blank pages. [[memory:13638067]]

