# Product Highlights Section (`sections/product-highlights.liquid`)

`sections/product-highlights.liquid` renders a two-column highlights section: text content and a list of up to four feature items on the left, and a supporting image on the right. Each feature item can include an icon and short text. The section supports color schemes and responsive padding.

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | `section-product-highlights.css`, inline `{%- style -%}` block for responsive padding |
| JS   | None |
| Blocks | `feature` block type (limit: 4) |
| Data | Relies on `section.settings` and `section.blocks` |

- No JavaScript dependencies; the section is purely presentational.

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
<div class="color-{{ section.settings.color_scheme }} product-highlights section-{{ section.id }}-padding">
  <div class="page-width">
    <div class="product-highlights__container">
      <div class="product-highlights__content">
        <!-- Title, description, feature list -->
      </div>
      <div class="product-highlights__media">
        <!-- Image -->
      </div>
    </div>
  </div>
</div>
```

### Content area

```liquid
{%- if title != blank -%}
  <h2 class="product-highlights__title">{{ title | escape }}</h2>
{%- endif -%}

{%- if description != blank -%}
  <p class="product-highlights__description">{{ description | escape }}</p>
{%- endif -%}

{%- if blocks_to_show > 0 -%}
  <ul class="product-highlights__features">
    {%- for block in section.blocks -%}
      <!-- Feature item -->
    {%- endfor -%}
  </ul>
{%- endif -%}
```

### Feature item

```liquid
<li class="product-highlights__feature" {{ block.shopify_attributes }}>
  {%- if feature_icon != blank -%}
    <div class="product-highlights__feature-icon">
      <img
        srcset="
          {%- if feature_icon.width >= 50 -%}{{ feature_icon | image_url: width: 50 }} 50w,{%- endif -%}
          {%- if feature_icon.width >= 100 -%}{{ feature_icon | image_url: width: 100 }} 100w,{%- endif -%}
          {{ feature_icon | image_url }} {{ feature_icon.width }}w
        "
        src="{{ feature_icon | image_url: width: 50 }}"
        sizes="50px"
        alt="{{ feature_icon.alt | default: feature_text | escape }}"
        loading="lazy"
        width="{{ feature_icon.width }}"
        height="{{ feature_icon.height }}"
        class="product-highlights__icon"
      >
    </div>
  {%- else -%}
    <div class="product-highlights__feature-icon-placeholder">
      {{ 'image' | placeholder_svg_tag: 'placeholder-svg' }}
    </div>
  {%- endif -%}

  {%- if feature_text != blank -%}
    <span class="product-highlights__feature-text">{{ feature_text | escape }}</span>
  {%- endif -%}
</li>
```

- Icon alt text falls back to the feature text.
- Placeholder icon uses Shopify’s placeholder SVG.

### Media image

```liquid
{%- if image != blank -%}
  <img
    srcset="
      {%- if image.width >= 400 -%}{{ image | image_url: width: 400 }} 400w,{%- endif -%}
      {%- if image.width >= 600 -%}{{ image | image_url: width: 600 }} 600w,{%- endif -%}
      {%- if image.width >= 800 -%}{{ image | image_url: width: 800 }} 800w,{%- endif -%}
      {%- if image.width >= 1000 -%}{{ image | image_url: width: 1000 }} 1000w,{%- endif -%}
      {{ image | image_url }} {{ image.width }}w
    "
    src="{{ image | image_url: width: 800 }}"
    sizes="(min-width: 750px) 50vw, 100vw"
    alt="{{ image.alt | default: title | escape }}"
    loading="lazy"
    width="{{ image.width }}"
    height="{{ image.height }}"
    class="product-highlights__image"
  >
{%- else -%}
  <div class="product-highlights__image-placeholder">
    {{ 'image' | placeholder_svg_tag: 'placeholder-svg' }}
  </div>
{%- endif -%}
```

---

## Behavior

- **Purely presentational**: No JavaScript required.
- **Responsive layout**: Desktop shows two columns; mobile stacks with the image first.
- **Conditional rendering**: Title/description/features render only when values are provided.
- **Lazy loading**: Feature icons and the main image use `loading="lazy"`.

---

## Schema

```json
{
  "name": "Product Highlights",
  "tag": "section",
  "class": "product-highlights",
  "settings": [
    { "type": "color_scheme", "id": "color_scheme", "label": "t:sections.all.colors.label", "default": "scheme-1" },
    { "type": "range", "id": "padding_top", "label": "Padding Top", "min": 0, "max": 100, "step": 4, "unit": "px", "default": 40 },
    { "type": "range", "id": "padding_bottom", "label": "Padding Bottom", "min": 0, "max": 100, "step": 4, "unit": "px", "default": 40 },
    { "type": "image_picker", "id": "image", "label": "Image" },
    { "type": "text", "id": "title", "label": "Title", "default": "Product Highlights Title" },
    { "type": "textarea", "id": "description", "label": "Description", "default": "Product Highlights description will appear here." }
  ],
  "blocks": [
    {
      "type": "feature",
      "name": "Feature",
      "limit": 4,
      "settings": [
        { "type": "image_picker", "id": "icon", "label": "Icon" },
        { "type": "text", "id": "text", "label": "Text", "default": "Feature text" }
      ]
    }
  ],
  "presets": [{ "name": "Product Highlights" }]
}
```

---

## Implementation Notes

1. **Block limit**: Up to 4 feature blocks.
2. **Alt fallback**: Feature icon alt falls back to feature text; main image alt falls back to the title.
3. **Responsive images**: Feature icons use 50/100 widths; main image uses 400/600/800/1000 widths.
4. **Mobile order**: CSS displays the image first on mobile (media `order: 1`, content `order: 2`).
5. **VitePress mustache safety**: If referencing Liquid mustaches in prose/inline code, escape them like `\{\{ ... \}\}` to avoid blank pages. [[memory:13638067]]

