# Shop Categories Section (`sections/shop-categories.liquid`)

`sections/shop-categories.liquid` renders a Swiper slider of collection “category” cards. Each slide links to a collection and shows an image with a title overlay. The section includes optional navigation controls (prev/next + progress bar) that appear when there is more than one block.

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | `section-shop-categories.css`, inline `{%- style -%}` block for responsive padding |
| JS   | `section-shop-categories.js` (module) |
| Custom Element | `<shop-categories>` defined in `section-shop-categories.js` |
| Blocks | `category` block type |
| Icons | `icon-arrow-prev.svg`, `icon-arrow-next.svg` (inline via `inline_asset_content`) |
| Data | Relies on `section.blocks` and `section.settings` |

Notes:

- This section requires Swiper to be available globally (`window.Swiper`).

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

---

## Markup Structure

```liquid
<div class="shop-categories color-{{ section.settings.color_scheme }} section-{{ section.id }}-padding">
  <shop-categories data-section-id="{{ section.id }}">
    <div class="page-width">
      <div id="shop-categories-{{ section.id }}" class="shop-categories__slider swiper">
        <div class="swiper-wrapper">
          <!-- Slides -->
        </div>

        <!-- Controls (only if more than 1 block) -->
      </div>
    </div>
  </shop-categories>
</div>
```

### Slides

Each block produces one Swiper slide linking to a collection:

```liquid
<div class="swiper-slide" {{ block.shopify_attributes }}>
  <a href="{{ collection_url }}" class="shop-categories__card">
    <div class="shop-categories__image-wrapper">
      <!-- image or placeholder -->
      <div class="shop-categories__overlay">
        <h3 class="shop-categories__title">
          {{ collection_title | escape }}
        </h3>
      </div>
    </div>
  </a>
</div>
```

Image priority:
- `custom_image`
- `collection.featured_image`
- Placeholder (`collection-1`)

---

## JavaScript Behavior

`assets/section-shop-categories.js` defines a `<shop-categories>` custom element that:

- Initializes Swiper using the slider element ID `#shop-categories-${sectionId}`.
- Uses breakpoints:
  - Mobile: `slidesPerView: 1.5`
  - Desktop: `slidesPerView: 4`
- Updates navigation button disabled state and the progress bar on init and slide change.
- Destroys Swiper in `disconnectedCallback`.

Progress bar logic:
- Fills to 100% when the last visible slide reaches the final slide.
- Otherwise sets width based on `(lastVisibleIndex + 1) / totalSlides`.

---

## Behavior

- **Carousel UI**: Uses Swiper for horizontal scrolling.
- **Controls**: Only shown when there is more than one block.
- **Preview fallback**: CSS displays a grid before Swiper initializes (`.shop-categories__slider:not(.swiper-initialized) .swiper-wrapper`).

---

## Schema

```json
{
  "name": "Shop Categories",
  "tag": "section",
  "class": "section-shop-categories",
  "settings": [
    { "type": "color_scheme", "id": "color_scheme", "label": "t:sections.all.colors.label", "default": "scheme-1" },
    { "type": "range", "id": "padding_top", "default": 36 },
    { "type": "range", "id": "padding_bottom", "default": 36 }
  ],
  "blocks": [
    {
      "type": "category",
      "name": "Category",
      "settings": [
        { "type": "collection", "id": "collection", "label": "Collection" },
        { "type": "text", "id": "custom_title", "label": "Custom Title" },
        { "type": "image_picker", "id": "custom_image", "label": "Custom Image" }
      ]
    }
  ],
  "presets": [{ "name": "Shop Categories" }]
}
```

---

## Implementation Notes

1. **Swiper dependency**: Requires `window.Swiper` to be present; otherwise JS logs an error.
2. **Preview grid**: Before Swiper initializes, CSS shows a 4-column grid for better theme editor preview.
3. **Progress bar**: The JS computes progress based on the “last visible” slide index.
4. **VitePress mustache safety**: If referencing Liquid mustaches in prose/inline code, escape them like `\{\{ ... \}\}` to avoid blank pages. [[memory:13638067]]

