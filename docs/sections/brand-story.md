# Brand Story Section (`sections/brand-story.liquid`)

`sections/brand-story.liquid` renders a two-column “comparison” layout: the left side shows two images with optional labels (for comparing “Other Brands” vs “Demo”), and the right side shows a heading and description. The section supports a color scheme and responsive padding.

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | `section-brand-story.css`, inline `{%- style -%}` block for responsive padding |
| Data | Relies on `section.settings` for all configuration |

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
<section
  id="BrandStory-{{ section.id }}"
  class="brand-story section-{{ section.id }}-padding color-{{ section.settings.color_scheme }}"
>
  <div class="page-width">
    <div class="brand-story__container">
      <div class="brand-story__left">
        <!-- Comparison images -->
      </div>
      <div class="brand-story__right">
        <!-- Heading + description -->
      </div>
    </div>
  </div>
</section>
```

- **Unique ID**: `BrandStory-\{\{ section.id \}\}` ensures uniqueness per section instance.
- **Color scheme**: Applied via `color-\{\{ section.settings.color_scheme \}\}`.

### Left Side — Comparison Images

The left column renders two “image items” (`image_1` / `image_2`). Each item shows:
- An image (responsive srcset) **or** a placeholder SVG if missing
- An optional label (`label_1` / `label_2`)

#### Image 1

```liquid
{%- if section.settings.image_1 != blank -%}
  <img
    srcset="
      {%- if section.settings.image_1.width >= 300 -%}{{ section.settings.image_1 | image_url: width: 300 }} 300w,{%- endif -%}
      {%- if section.settings.image_1.width >= 400 -%}{{ section.settings.image_1 | image_url: width: 400 }} 400w,{%- endif -%}
      {%- if section.settings.image_1.width >= 500 -%}{{ section.settings.image_1 | image_url: width: 500 }} 500w,{%- endif -%}
      {{ section.settings.image_1 | image_url }} {{ section.settings.image_1.width }}w
    "
    src="{{ section.settings.image_1 | image_url: width: 500 }}"
    sizes="(min-width: 750px) 50vw, 100vw"
    alt="{{ section.settings.image_1.alt | default: section.settings.label_1 | escape }}"
    loading="lazy"
    width="{{ section.settings.image_1.width }}"
    height="{{ section.settings.image_1.height }}"
  >
{%- else -%}
  {{ 'image' | placeholder_svg_tag: 'placeholder-svg' }}
{%- endif -%}
```

- **Alt fallback**: Uses image alt text; falls back to `label_1`.
- **Responsive images**: 300w / 400w / 500w + original.

#### Image 2

```liquid
{%- if section.settings.image_2 != blank -%}
  <img
    srcset="
      {%- if section.settings.image_2.width >= 300 -%}{{ section.settings.image_2 | image_url: width: 300 }} 300w,{%- endif -%}
      {%- if section.settings.image_2.width >= 400 -%}{{ section.settings.image_2 | image_url: width: 400 }} 400w,{%- endif -%}
      {%- if section.settings.image_2.width >= 500 -%}{{ section.settings.image_2 | image_url: width: 500 }} 500w,{%- endif -%}
      {{ section.settings.image_2 | image_url }} {{ section.settings.image_2.width }}w
    "
    src="{{ section.settings.image_2 | image_url: width: 500 }}"
    sizes="(min-width: 750px) 50vw, 100vw"
    alt="{{ section.settings.image_2.alt | default: section.settings.label_2 | escape }}"
    loading="lazy"
    width="{{ section.settings.image_2.width }}"
    height="{{ section.settings.image_2.height }}"
  >
{%- else -%}
  {{ 'image' | placeholder_svg_tag: 'placeholder-svg' }}
{%- endif -%}
```

- **Alt fallback**: Uses image alt text; falls back to `label_2`.

### Right Side — Content

```liquid
{%- if section.settings.heading != blank -%}
  <h2 class="brand-story__heading">{{ section.settings.heading | escape }}</h2>
{%- endif -%}

{%- if section.settings.description != blank -%}
  <div class="brand-story__description">
    {{ section.settings.description | escape }}
  </div>
{%- endif -%}
```

- **Heading**: Escaped text.
- **Description**: Escaped textarea output (renders as plain text, not rich text).

---

## Behavior

- **Purely presentational**: No JavaScript required.
- **Image fallbacks**: Uses placeholder SVG when an image isn’t set.
- **Conditional rendering**: Heading/description/labels only render when values are provided.
- **Performance**: Images use `loading="lazy"` and include `width`/`height` to reduce layout shift.

---

## Schema

```json
{
  "name": "Brand Story",
  "tag": "section",
  "class": "section-brand-story",
  "settings": [
    { "type": "header", "content": "Color Settings" },
    { "type": "color_scheme", "id": "color_scheme", "label": "t:sections.all.colors.label", "default": "scheme-1" },

    { "type": "header", "content": "Spacing Settings" },
    { "type": "range", "id": "padding_top", "label": "t:sections.all.padding.padding_top", "min": 0, "max": 100, "step": 4, "unit": "px", "default": 40 },
    { "type": "range", "id": "padding_bottom", "label": "t:sections.all.padding.padding_bottom", "min": 0, "max": 100, "step": 4, "unit": "px", "default": 40 },

    { "type": "header", "content": "Left Side - Comparison Images" },
    { "type": "image_picker", "id": "image_1", "label": "Image 1" },
    { "type": "text", "id": "label_1", "label": "Label 1", "default": "OTHER BRANDS" },
    { "type": "image_picker", "id": "image_2", "label": "Image 2" },
    { "type": "text", "id": "label_2", "label": "Label 2", "default": "DEMO" },

    { "type": "header", "content": "Right Side - Content" },
    { "type": "text", "id": "heading", "label": "Heading", "default": "Heading" },
    { "type": "textarea", "id": "description", "label": "Description", "default": "Description content will appear here." }
  ],
  "presets": [{ "name": "Brand Story" }]
}
```

### Section Settings

| Setting ID | Type | Default | Purpose |
|------------|------|---------|---------|
| `color_scheme` | color_scheme | `scheme-1` | Section color scheme |
| `padding_top` | range (px) | 40 | Top padding |
| `padding_bottom` | range (px) | 40 | Bottom padding |
| `image_1` | image_picker | — | Comparison image #1 |
| `label_1` | text | `OTHER BRANDS` | Label for image #1 |
| `image_2` | image_picker | — | Comparison image #2 |
| `label_2` | text | `DEMO` | Label for image #2 |
| `heading` | text | `Heading` | Right-side heading |
| `description` | textarea | `Description content will appear here.` | Right-side description |

### Presets

- Includes a preset named “Brand Story”.

---

## Implementation Notes

1. **Escaped description**: `description` is output with `| escape`, so it will render as plain text (not rich text).
2. **Alt fallback**: Image alt falls back to the corresponding label (`label_1` / `label_2`).
3. **Responsive images**: Uses srcset at 300/400/500 widths plus original, with `sizes="(min-width: 750px) 50vw, 100vw"`.
4. **Placeholders**: Uses Shopify’s `image` placeholder SVG when an image isn’t set.
5. **Section ID**: Uses `BrandStory-\{\{ section.id \}\}` to ensure uniqueness.

