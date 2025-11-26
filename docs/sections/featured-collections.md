# Featured Collections Section (`sections/featured-collections.liquid`)

`sections/featured-collections.liquid` renders a curated grid of collection cards selected via blocks. Each card displays a collection image (with optional custom image override), title (with optional custom title), and a "Shop Now" button. The section supports two card styles and customizable heading, spacing, and text colors.

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | `section-featured-collections.css` |
| Blocks | `collection_card` block type (limit: 5) |
| Data | Relies on `section.blocks` for collection selection and `section.settings` for display options |

- No JavaScript dependencies; the section is purely presentational.
- Collections are selected individually via blocks, allowing merchants to curate which collections appear.

---

## Dynamic Styles

The section uses inline styles for dynamic values:

```liquid
<div
  class="featured-collections__header"
  style="text-align: {{ heading_alignment }};"
>

<div class="featured-collections__grid" style="gap: {{ grid_gap }}px;">

<h3 class="collection-card__title" style="color: {{ text_color }}">

<span class="collection-card__shop-now" style="color: {{ text_color }}"
```

- `heading_alignment`: Controls header text alignment (left, center, right).
- `grid_gap`: Spacing between collection cards (0–40px, default 25px).
- `text_color`: Applied to collection titles and "Shop Now" buttons (default: #000000).

---

## Markup Structure

```liquid
{%- if collections_to_show > 0 -%}
  <div class="featured-collections-section">
    <div class="featured-collections__header" style="text-align: {{ heading_alignment }};">
      {%- if heading != blank -%}
        <h2 class="featured-collections__heading">{{ heading | escape }}</h2>
      {%- endif -%}
      {%- if subheading != blank -%}
        <p class="featured-collections__subheading">{{ subheading | escape }}</p>
      {%- endif -%}
    </div>

    <div class="featured-collections__grid" style="gap: {{ grid_gap }}px;">
      {%- for block in section.blocks -%}
        <!-- Collection card rendering -->
      {%- endfor -%}
    </div>
  </div>
{%- endif -%}
```

- Section only renders if at least one block (collection) is added.
- Header displays heading and subheading when provided.
- Grid iterates through blocks to render collection cards.

### Collection Card

```liquid
<div class="featured-collections__card grid__item" {{ block.shopify_attributes }}>
  <a href="{{ collection.url | default: '#' }}" class="collection-card__link {% if style == 'style2' %} collection-card__link--below{% endif %}">
    <div class="collection-card__image-wrapper media--portrait {% if collection_image == blank %} placeholder {% endif %}">
      {%- if collection_image != blank -%}
        <img
          srcset="
            {%- if collection_image.width >= 165 -%}{{ collection_image | image_url: width: 165 }} 165w,{%- endif -%}
            {%- if collection_image.width >= 360 -%}{{ collection_image | image_url: width: 360 }} 360w,{%- endif -%}
            {%- if collection_image.width >= 533 -%}{{ collection_image | image_url: width: 533 }} 533w,{%- endif -%}
            {%- if collection_image.width >= 720 -%}{{ collection_image | image_url: width: 720 }} 720w,{%- endif -%}
            {{ collection_image | image_url }} {{ collection_image.width }}w
          "
          src="{{ collection_image | image_url: width: 533 }}"
          sizes="(min-width: 990px) calc(var(--page-width) / 5 - 20px), (min-width: 769px) calc(100vw / 2 - 2rem), calc(100vw - 2rem)"
          alt="{{ collection_image.alt | escape }}"
          loading="lazy"
          width="{{ collection_image.width }}"
          height="{{ collection_image.height }}"
          class="collection-card__image"
        >
      {%- else -%}
        {{ 'collection-1' | placeholder_svg_tag: 'placeholder-svg collection-card__image' }}
      {%- endif -%}
    </div>
    <!-- Card info (title + Shop Now button) -->
  </a>
</div>
```

- **Image priority**: Uses `custom_image` if set, otherwise falls back to `collection.featured_image`, then `collection.image`.
- **Responsive images**: Full srcset with breakpoints (165w, 360w, 533w, 720w) and responsive sizes attribute.
- **Placeholder**: Shows SVG placeholder when no image is available.
- **Lazy loading**: Images use `loading="lazy"` for performance.

### Card Info (Style 1 vs Style 2)

```liquid
{%- if style == 'style2' -%}
  <div class="collection-card__info collection-card__info--below">
    <h3 class="collection-card__title" style="color: {{ text_color }}">
      {{ display_title | default: 'Collection Title' }}
    </h3>
    {%- unless hide_shop_now -%}
      <span class="collection-card__shop-now" style="color: {{ text_color }}">Shop Now</span>
    {%- endunless -%}
  </div>
{%- else -%}
  <div class="collection-card__info">
    <!-- Same structure, different CSS class -->
  </div>
{%- endif -%}
```

- **Style 1**: Text/button appears above or overlays the image.
- **Style 2**: Text/button appears below the image (adds `collection-card__link--below` and `collection-card__info--below` classes).
- **Title priority**: Uses `custom_title` if set, otherwise `collection.title`, with fallback to "Collection Title".
- **Shop Now button**: Conditionally hidden when `hide_shop_now` is true.

---

## Behavior

- Purely presentational; there's no JavaScript.
- Section only renders when at least one collection block is added.
- Responsive images adapt to viewport size via srcset and sizes attributes.
- Card style switching changes CSS classes but maintains the same HTML structure.
- All text is escaped for security.

---

## Schema

```json
{
  "name": "Featured Collections",
  "tag": "section",
  "class": "featured-collections",
  "settings": [
    {
      "type": "text",
      "id": "heading",
      "label": "Heading",
      "default": "Find the perfect fit for your game"
    },
    {
      "type": "text",
      "id": "subheading",
      "label": "Subheading",
      "default": "Browse through our collections"
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
      "type": "select",
      "id": "style",
      "label": "Card Style",
      "options": [
        { "value": "style1", "label": "Style 1 (Text/Button above or overlay)" },
        { "value": "style2", "label": "Style 2 (Text/Button below image)" }
      ],
      "default": "style2"
    },
    {
      "type": "range",
      "id": "grid_gap",
      "label": "Grid Gap",
      "default": 25,
      "unit": "px",
      "min": 0,
      "max": 40,
      "step": 1
    },
    {
      "type": "color",
      "id": "text_color",
      "label": "Text Color",
      "default": "#000000"
    },
    {
      "type": "checkbox",
      "id": "hide_shop_now",
      "label": "Hide 'Shop Now' Button",
      "default": true
    }
  ],
  "blocks": [
    {
      "type": "collection_card",
      "name": "Collection Card",
      "limit": 5,
      "settings": [
        {
          "type": "collection",
          "id": "collection",
          "label": "Collection"
        },
        {
          "type": "image_picker",
          "id": "custom_image",
          "label": "Custom Image (optional)",
          "info": "Overrides the collection image if set."
        },
        {
          "type": "text",
          "id": "custom_title",
          "label": "Custom Title (optional)",
          "info": "Overrides the collection title if set."
        }
      ]
    }
  ],
  "presets": [
    {
      "name": "Featured Collections",
      "blocks": [
        { "type": "collection_card" },
        { "type": "collection_card" },
        { "type": "collection_card" },
        { "type": "collection_card" },
        { "type": "collection_card" }
      ]
    }
  ]
}
```

### Section Settings

| Setting ID | Type | Default | Purpose |
|------------|------|---------|---------|
| `heading` | text | "Find the perfect fit for your game" | Main section heading |
| `subheading` | text | "Browse through our collections" | Section subheading |
| `heading_alignment` | select | `center` | Header text alignment (left, center, right) |
| `style` | select | `style2` | Card layout style (style1 or style2) |
| `grid_gap` | range (px) | 25 | Spacing between cards (0–40px) |
| `text_color` | color | #000000 | Color for titles and "Shop Now" buttons |
| `hide_shop_now` | checkbox | `true` | Toggle "Shop Now" button visibility |

### Blocks

- **`collection_card`**: Individual collection card block (limit: 5 per section)
  - `collection`: Collection picker (required for link functionality)
  - `custom_image`: Optional image override
  - `custom_title`: Optional title override

### Presets

- Includes a preset with 5 empty collection card blocks for quick setup.

---

## Implementation Notes

1. **Block limit**: Maximum of 5 collection cards per section; merchants must choose which collections to feature.

2. **Image fallback chain**: `custom_image` → `collection.featured_image` → `collection.image` → placeholder SVG. Ensure placeholder SVG exists if no images are available.

3. **Title fallback chain**: `custom_title` → `collection.title` → "Collection Title" (hardcoded fallback).

4. **Translation keys**: Section name and labels are hardcoded in English. Consider using translation filters (`t:`) for localization.

5. **Responsive images**: Srcset includes multiple breakpoints; sizes attribute adapts to viewport:
   - Desktop (≥990px): `calc(var(--page-width) / 5 - 20px)`
   - Tablet (≥769px): `calc(100vw / 2 - 2rem)`
   - Mobile: `calc(100vw - 2rem)`

6. **Style switching**: CSS classes change based on `style` setting, but HTML structure remains the same. Ensure both styles are defined in `section-featured-collections.css`.

7. **Conditional rendering**: Section only renders when `collections_to_show > 0` (i.e., at least one block exists). Empty sections won't display.

8. **Shop Now text**: "Shop Now" text is hardcoded in English. Consider making it translatable or configurable.

9. **Link fallback**: Collection links default to `#` if no collection is selected, which creates a non-functional link. Consider hiding cards without valid collections.

10. **Grid layout**: Grid structure is defined in CSS file; ensure `section-featured-collections.css` handles responsive grid behavior appropriately.

