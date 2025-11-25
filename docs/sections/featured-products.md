# Featured Products Section (`sections/featured-products.liquid`)

`sections/featured-products.liquid` renders a carousel of curated product cards selected via blocks. It uses Swiper for carousel functionality and displays products with images, ratings, prices, and sale badges. The section supports customizable headings, alignment options, colors, and a "View All" link that can be displayed as a button or text link.

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | `swiper7.4.1.min.css`, `section-featured-products.css` |
| JS   | `swiper7.4.1.min.js` (deferred), `section-featured-products.js` (module) |
| Custom Element | `<featured-products>` defined in `section-featured-products.js` |
| Blocks | `product_card` block type (no limit) |
| Data | Relies on `section.blocks` for product selection and `section.settings` for display options |

- Swiper library handles carousel navigation with prev/next arrow buttons.
- Custom element manages carousel initialization and behavior.
- Products are selected individually via blocks, allowing merchants to curate which products appear.

---

## Dynamic Styles

The section uses CSS custom properties set via a `<style>` block and inline styles:

```liquid
<style>
  .featured-products-section {
    --button-bg-color: {{ button_background_color }};
    --button-text-color: {{ button_text_color }};
    --product-content-alignment: {{ product_content_alignment }};
    --review-content-alignment: {{ review_content_alignment }};
    --stars-color: {{ stars_color }};
  }
</style>

<span class="product-card__stars" style="color: {{ stars_color | default: '#FFD700' }}">

<h3 class="product-card__title" style="color: {{ product_info_text_color | default: '#111111' }}">

<div class="product-card__price" style="color: {{ product_info_text_color | default: '#111111' }}">
```

- CSS variables set for button colors, alignment options, and stars color.
- Inline styles applied to stars, product titles, and prices with fallback defaults.
- Alignment classes applied via CSS variable: `product-card__info--{{ product_content_alignment }}` and `product-card__reviews--{{ review_content_alignment }}`.

---

## Markup Structure

```liquid
{%- if products_to_show > 0 -%}
  <featured-products data-section-id="{{ section.id }}" class="featured-products-section" style="position: relative;">
    <div class="page-width featured-products-content">
      <div class="featured-products__header">
        <!-- Heading and subheading -->
        <!-- View All link (if not button) -->
      </div>

      <div id="featured-products-{{ section.id }}" class="featured-products__swiper swiper">
        <div class="featured-products__swiper-arrows">
          <!-- Prev/Next arrow buttons -->
        </div>
        <div class="swiper-wrapper">
          {%- for block in section.blocks -%}
            <!-- Product card slides -->
          {%- endfor -%}
        </div>
      </div>

      <!-- View All button (if enabled) -->
    </div>
  </featured-products>
{%- endif -%}
```

- Section only renders if at least one product block is added.
- Custom element `<featured-products>` wraps the entire section for JavaScript control.
- Swiper container uses unique ID based on section ID for multiple instances.

### Header

```liquid
<div class="featured-products__header">
  <div class="featured-products__titles featured-products__titles--{{ heading_alignment }}">
    {%- if heading != blank -%}
      <h2 class="featured-products__heading">{{ heading | escape }}</h2>
    {%- endif -%}
    {%- if subheading != blank -%}
      <p class="featured-products__subheading">{{ subheading | escape }}</p>
    {%- endif -%}
  </div>
  {%- if view_all_text != blank and view_all_url != blank and show_view_all_as_button != true -%}
    <a href="{{ view_all_url }}" class="featured-products__view-all link underlined-link">
      {{ view_all_text | escape }}
    </a>
  {%- endif -%}
</div>
```

- Heading alignment controlled via CSS class: `featured-products__titles--{{ heading_alignment }}`.
- "View All" link appears as text link when `show_view_all_as_button` is false.

### Swiper Carousel

```liquid
<div id="featured-products-{{ section.id }}" class="featured-products__swiper swiper">
  <div class="featured-products__swiper-arrows">
    <div class="swiper-button-prev featured-products__swiper-prev">
      <!-- SVG arrow icon -->
    </div>
    <div class="swiper-button-next featured-products__swiper-next">
      <!-- SVG arrow icon -->
    </div>
  </div>
  <div class="swiper-wrapper">
    <!-- Product slides -->
  </div>
</div>
```

- Swiper structure with prev/next navigation arrows (inline SVG icons).
- Unique section ID ensures multiple instances work independently.

### Product Card

```liquid
<div class="featured-products__card swiper-slide" {{ block.shopify_attributes }}>
  <div class="product-card">
    <a href="{{ product.url | default: '#' }}" class="product-card__link">
      <div class="product-card__image-wrapper">
        {%- if product.featured_media -%}
          {%- assign image = product.featured_media.preview_image -%}
          <img
            srcset="
              {%- if image.width >= 350 -%}{{ image | image_url: width: 350 }} 350w,{%- endif -%}
              {%- if image.width >= 550 -%}{{ image | image_url: width: 550 }} 550w,{%- endif -%}
              {%- if image.width >= 750 -%}{{ image | image_url: width: 750 }} 750w,{%- endif -%}
              {%- if image.width >= 1100 -%}{{ image | image_url: width: 1100 }} 1100w,{%- endif -%}
              {%- if image.width >= 1500 -%}{{ image | image_url: width: 1500 }} 1500w,{%- endif -%}
              {{ image | image_url }} {{ image.width }}w
            "
            src="{{ image | image_url: width: 750 }}"
            sizes="(min-width: 990px) calc(var(--page-width) / 4 - 2rem * 3 / 4), (min-width: 750px) calc(100vw / 2 - 2rem / 2 - 4rem), calc(100vw / 2 - 1rem / 2 - 2rem)"
            alt="{{ image.alt | escape }}"
            loading="lazy"
            width="264"
            height="317"
            class="product-card__image"
          >
        {%- else -%}
          {{ 'product-1' | placeholder_svg_tag: 'placeholder-svg product-card__image' }}
        {%- endif -%}

        {%- if product.compare_at_price > product.price -%}
          <span class="product-card__badge">Save {{ saved_amount }}</span>
        {%- endif -%}
      </div>

      <div class="product-card__info product-card__info--{{ product_content_alignment }}">
        <div class="product-card__reviews product-card__reviews--{{ review_content_alignment }}">
          <span class="visually-hidden">Rating:</span>
          <span class="product-card__stars" style="color: {{ stars_color | default: '#FFD700' }}">
            ★★★★☆
          </span>
          <a href="#reviews" class="product-card__review-link">
            <span class="product-card__review-count">10 Reviews</span>
          </a>
        </div>
        <h3 class="product-card__title" style="color: {{ product_info_text_color | default: '#111111' }}">
          {{ product.title | default: 'Product Title' }}
        </h3>
        <div class="product-card__price" style="color: {{ product_info_text_color | default: '#111111' }}">
          {%- if product.price -%}
            {%- if product.compare_at_price > product.price -%}
              <s class="price__compare-at">{{ product.compare_at_price | money }}</s>
            {%- endif -%}
            <span class="price__regular {% if product.compare_at_price > product.price %}price--on-sale{% endif %}">
              {{ product.price | money }}
            </span>
          {% else %}
            <span class="price__regular">{{ 20000 | money }}</span>
          {% endif %}
        </div>
      </div>
    </a>
  </div>
</div>
```

- **Responsive images**: Full srcset with breakpoints (350w, 550w, 750w, 1100w, 1500w) and responsive sizes attribute.
- **Sale badge**: Displays "Save [amount]" when `compare_at_price > price`.
- **Reviews**: Hardcoded rating display (★★★★☆) and review count (10 Reviews). Consider making this dynamic.
- **Price display**: Shows compare-at price (strikethrough) when on sale, regular price otherwise. Falls back to $200.00 if no price.
- **Alignment**: Product content and reviews use alignment classes from settings.

### View All Button

```liquid
{%- if show_view_all_as_button and view_all_text != blank and view_all_url != blank -%}
  <div class="featured-products__button-wrapper">
    <a href="{{ view_all_url }}" class="featured-products__view-all-button button">
      {{ view_all_text | escape }}
    </a>
  </div>
{%- endif -%}
```

- Conditionally renders as button when `show_view_all_as_button` is true.
- Uses CSS variables for button colors (`--button-bg-color`, `--button-text-color`).

---

## JavaScript Behavior

The section uses a custom element `<featured-products>` defined in `section-featured-products.js`:

- **Swiper initialization**: Sets up carousel with navigation arrows.
- **Section ID tracking**: Uses `data-section-id` attribute to support multiple instances.
- **Module loading**: JavaScript loads as ES module for modern browser support.

Swiper handles:
- Touch/swipe navigation
- Arrow button navigation
- Responsive breakpoints
- Slide transitions

---

## Schema

```json
{
  "name": "Featured Products",
  "tag": "section",
  "class": "featured-products",
  "settings": [
    {
      "type": "text",
      "id": "heading",
      "label": "Heading",
      "default": "Shop the Pro Selection"
    },
    {
      "type": "text",
      "id": "subheading",
      "label": "Subheading",
      "default": "Skate like the pros"
    },
    {
      "type": "text",
      "id": "view_all_text",
      "label": "'View All' Link Text",
      "default": "View All"
    },
    {
      "type": "url",
      "id": "view_all_url",
      "label": "'View All' Link URL"
    },
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
    {
      "type": "checkbox",
      "id": "show_view_all_as_button",
      "label": "Show 'View All' as Button",
      "default": true
    },
    {
      "type": "color",
      "id": "button_background_color",
      "label": "Button Background Color",
      "default": "#2E2E2E"
    },
    {
      "type": "color",
      "id": "button_text_color",
      "label": "Button Text Color",
      "default": "#ffffff"
    },
    {
      "type": "select",
      "id": "product_content_alignment",
      "label": "Product Content Alignment",
      "options": [
        { "value": "left", "label": "Left" },
        { "value": "center", "label": "Center" },
        { "value": "right", "label": "Right" }
      ],
      "default": "left"
    },
    {
      "type": "select",
      "id": "review_content_alignment",
      "label": "Review Content Alignment",
      "options": [
        { "value": "left", "label": "Left" },
        { "value": "center", "label": "Center" },
        { "value": "right", "label": "Right" }
      ],
      "default": "left"
    },
    {
      "type": "color",
      "id": "product_info_text_color",
      "label": "Product Info Text Color",
      "default": "#111111"
    },
    {
      "type": "color",
      "id": "stars_color",
      "label": "Stars Color",
      "default": "#FFD700"
    }
  ],
  "blocks": [
    {
      "type": "product_card",
      "name": "Product Card",
      "settings": [
        {
          "type": "product",
          "id": "product",
          "label": "Product"
        }
      ]
    }
  ],
  "presets": [
    {
      "name": "Featured Products",
      "blocks": [
        { "type": "product_card" },
        { "type": "product_card" },
        { "type": "product_card" },
        { "type": "product_card" },
        { "type": "product_card" }
      ]
    }
  ]
}
```

### Section Settings

| Setting ID | Type | Default | Purpose |
|------------|------|---------|---------|
| `heading` | text | "Shop the Pro Selection" | Main section heading |
| `subheading` | text | "Skate like the pros" | Section subheading |
| `view_all_text` | text | "View All" | Text for View All link/button |
| `view_all_url` | url | — | URL for View All link/button |
| `heading_alignment` | select | `center` | Header text alignment (left, center, right) |
| `show_view_all_as_button` | checkbox | `true` | Display View All as button vs. text link |
| `button_background_color` | color | #2E2E2E | Button background color |
| `button_text_color` | color | #ffffff | Button text color |
| `product_content_alignment` | select | `left` | Product info alignment (left, center, right) |
| `review_content_alignment` | select | `left` | Review section alignment (left, center, right) |
| `product_info_text_color` | color | #111111 | Color for product title and price |
| `stars_color` | color | #FFD700 | Color for rating stars |

### Blocks

- **`product_card`**: Individual product card block (no limit)
  - `product`: Product picker (required for product data)

### Presets

- Includes a preset with 5 empty product card blocks for quick setup.

---

## Implementation Notes

1. **Swiper dependency**: Requires Swiper 7.4.1 library. Ensure both CSS and JS files are loaded before the custom element initializes.

2. **Custom element**: The `<featured-products>` element must be defined in `section-featured-products.js`. Ensure the module loads correctly and handles Swiper initialization.

3. **Multiple instances**: Section ID is used to create unique Swiper instances. Multiple sections on the same page will work independently.

4. **Hardcoded reviews**: Rating display (★★★★☆) and review count (10 Reviews) are hardcoded. Consider:
   - Integrating with a review app
   - Making ratings dynamic based on product data
   - Adding settings to toggle review display

5. **Price fallback**: Falls back to $200.00 (20000 cents) when product has no price. Consider hiding price or showing "Price unavailable" instead.

6. **Sale badge calculation**: `saved_amount` is calculated as `compare_at_price - price`. Ensure this calculation handles edge cases correctly.

7. **Image dimensions**: Product images use fixed width/height attributes (264x317). Ensure images maintain aspect ratio or adjust dimensions accordingly.

8. **Responsive images**: Srcset includes multiple breakpoints; sizes attribute adapts to viewport:
   - Desktop (≥990px): `calc(var(--page-width) / 4 - 2rem * 3 / 4)`
   - Tablet (≥750px): `calc(100vw / 2 - 2rem / 2 - 4rem)`
   - Mobile: `calc(100vw / 2 - 1rem / 2 - 2rem)`

9. **Translation keys**: Section name and labels are hardcoded in English. Consider using translation filters (`t:`) for localization.

10. **Arrow icons**: Navigation arrows use inline SVG. Icons are hardcoded with stroke color #9D9D9D. Consider making arrow color configurable or using CSS to style them.

11. **Conditional rendering**: Section only renders when `products_to_show > 0` (i.e., at least one block exists). Empty sections won't display.

12. **Link fallback**: Product links default to `#` if no product is selected, which creates a non-functional link. Consider hiding cards without valid products.

