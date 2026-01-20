# Product Details Section (`sections/product-details.liquid`)

`sections/product-details.liquid` renders an accordion-style set of “detail” blocks. Each block contains a title, rich text content, and up to two images. The accordion open/close behavior is handled with Alpine.js directives (`x-data`, `x-show`, `x-transition`).

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | `section-product-details.css`, inline `{%- style -%}` block for responsive padding |
| JS   | Uses Alpine.js directives in markup (no section-specific JS file) |
| Blocks | `detail` block type |
| Icons | `icon-plus.svg`, `icon-minus.svg` (inline via `inline_asset_content`) |
| Data | Relies on `section.blocks` and block settings |

Notes:

- This section assumes Alpine.js is available globally in the theme (since it uses `x-data`, `x-show`, `x-transition`, `x-cloak`).

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
<div class="color-{{ section.settings.color_scheme }} product-details section-{{ section.id }}-padding">
  <div class="page-width">
    <div class="product-details__container" x-data="{ openBlock: 0 }">
      {%- for block in section.blocks -%}
        <!-- Accordion block -->
      {%- endfor -%}
    </div>
  </div>
</div>
```

### Accordion header (toggle)

```liquid
<button
  @click="openBlock = openBlock === {{ forloop.index0 }} ? null : {{ forloop.index0 }}"
  class="product-details__header"
  :aria-expanded="openBlock === {{ forloop.index0 }}"
  type="button"
>
  <h3 class="product-details__title">{{ block.settings.title | default: 'Product Details' }}</h3>

  <span class="product-details__icon" x-show="openBlock !== {{ forloop.index0 }}">
    {{ 'icon-plus.svg' | inline_asset_content }}
  </span>
  <span class="product-details__icon" x-show="openBlock === {{ forloop.index0 }}" x-cloak>
    {{ 'icon-minus.svg' | inline_asset_content }}
  </span>
</button>
```

- Default open block is index 0 (`x-data="{ openBlock: 0 }"`).
- Icons switch based on open state.

### Accordion content

```liquid
<div
  x-show="openBlock === {{ forloop.index0 }}"
  x-transition
  class="product-details__content"
  x-cloak
>
  <div class="product-details__content-wrapper">
    <div class="product-details__text-column">
      <!-- Richtext content -->
    </div>
    <div class="product-details__images-column">
      <!-- Up to 2 images -->
    </div>
  </div>
</div>
```

Content is richtext and is output unescaped:

```liquid
{%- if block.settings.content != blank -%}
  <div class="product-details__content-text">
    {{ block.settings.content }}
  </div>
{%- else -%}
  <div class="product-details__content-text">
    <p>Add key product information here, such as fit, materials, or care instructions.</p>
  </div>
{%- endif -%}
```

### Images (two slots)

Each block can render `image_1` and `image_2`. Each image uses a responsive srcset (200/400/600 widths) and falls back to a placeholder when missing.

---

## Behavior

- **Accordion UI**: Implemented with Alpine.js state (`openBlock`) and transitions.
- **Initial state**: First block is open by default.
- **Responsive layout**: Desktop uses a two-column content layout (text 40% / images 60%); mobile stacks.
- **Lazy loading**: Images use `loading="lazy"`.

---

## Schema

```json
{
  "name": "Product Details",
  "tag": "section",
  "class": "product-details",
  "settings": [
    { "type": "color_scheme", "id": "color_scheme", "label": "t:sections.all.colors.label", "default": "scheme-1" },
    { "type": "range", "id": "padding_top", "label": "Padding Top", "min": 0, "max": 100, "step": 4, "unit": "px", "default": 40 },
    { "type": "range", "id": "padding_bottom", "label": "Padding Bottom", "min": 0, "max": 100, "step": 4, "unit": "px", "default": 40 }
  ],
  "blocks": [
    {
      "type": "detail",
      "name": "Detail Block",
      "settings": [
        { "type": "text", "id": "title", "label": "Title", "default": "Product Details" },
        { "type": "richtext", "id": "content", "label": "Content", "default": "<p>Add key product information here, such as fit, materials, or care instructions.</p>" },
        { "type": "image_picker", "id": "image_1", "label": "Image 1" },
        { "type": "image_picker", "id": "image_2", "label": "Image 2" }
      ]
    }
  ],
  "presets": [{ "name": "Product Details" }]
}
```

---

## Implementation Notes

1. **Alpine dependency**: Without Alpine.js, the accordion won’t open/close (content may remain hidden due to `x-cloak`).
2. **Initial open block**: `openBlock` defaults to `0`, so the first block starts expanded.
3. **ARIA state**: `:aria-expanded` is bound to the open state; icons also swap based on state.
4. **Richtext output**: `block.settings.content` is output unescaped (expected HTML from richtext editor).
5. **Images**: Each block supports up to 2 images with srcset (200/400/600) and placeholders.
6. **VitePress mustache safety**: If referencing Liquid mustaches in prose/inline code, escape them like `\{\{ ... \}\}` to avoid blank pages. [[memory:13638067]]

