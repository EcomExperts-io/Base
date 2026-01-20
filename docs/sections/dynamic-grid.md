# Dynamic Grid Section (`sections/dynamic-grid.liquid`)

`sections/dynamic-grid.liquid` renders a highly configurable grid of blocks with optional section heading/description and an optional section-level button. The grid supports different layouts (“text on image” vs “text below image”), configurable column counts per breakpoint, and per-block custom styling and custom column widths via CSS variables.

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | Inline `<style>` (in the section file itself) |
| JS   | None |
| Blocks | `block` block type (max 20) |
| Data | Relies on `section.settings` and `block.settings` |

- No external CSS/JS assets are loaded via `asset_url` in this section; styling is defined inline in the section file.

---

## Dynamic Styles

This section relies heavily on CSS custom properties set inline on the root element and on each block.

### Section-level CSS variables

```liquid
<div
  id="{{ section.id }}"
  class="dynamic-grid-section"
  style="
    --background-color: {{ section.settings.background_color }};
    --spacing-top-desktop: {{ section.settings.spacing_top_desktop }}px;
    --spacing-top-mobile: {{ section.settings.spacing_top_mobile }}px;
    --spacing-bottom-desktop: {{ section.settings.spacing_bottom_desktop }}px;
    --spacing-bottom-mobile: {{ section.settings.spacing_bottom_mobile }}px;
    --section-title-font-weight: {% if section.settings.section_title_font_weight == 'bold' %}bold{% else %}normal{% endif %};
    --section-title-color: {{ section.settings.section_title_color }};
    --section-description-color: {{ section.settings.section_description_color }};
    --section-title-font-size-desktop: {{ section.settings.section_title_font_size_desktop }}px;
    --section-title-font-size-mobile: {{ section.settings.section_title_font_size_mobile }}px;
    --section-description-font-size-desktop: {{ section.settings.section_description_font_size_desktop }}px;
    --section-description-font-size-mobile: {{ section.settings.section_description_font_size_mobile }}px;
    --section-title-transform: {% if section.settings.section_uppercase_title %}uppercase{% else %}initial{% endif %};
    --section-description-transform: {% if section.settings.section_uppercase_description %}uppercase{% else %}initial{% endif %};
    --section-content-alignment: {% if section.settings.section_content_alignment == 'left' %}left{% elsif section.settings.section_content_alignment == 'right' %}right{% else %}center{% endif %};
    --section-content-alignment-mobile: {% if section.settings.section_content_alignment_mobile == 'left' %}left{% elsif section.settings.section_content_alignment_mobile == 'right' %}right{% else %}center{% endif %};
    --section-button-background: {{ section.settings.button_background_color }};
    --section-button-color: {{ section.settings.section_button_text_color }};
    --section-border-color: {{ section.settings.button_border_color }};
    --section-button-font-size-desktop: {{ section.settings.section_button_font_size_desktop }};
    --section-button-font-size-mobile: {{ section.settings.section_button_font_size_mobile }};
  "
>
```

- The inline `style` attribute is used as the “configuration layer” for the `<style>` rules at the bottom of the file.
- Note: in prose/inline code, escape Liquid mustaches like `\{\{ section.id \}\}` to avoid VitePress blank pages. [[memory:13638067]]

### Grid column variables

```liquid
<div
  class="dynamic-grid-wrapper {% if section.settings.style == 'text-on-image' %}text-on-image{% endif %}"
  style="
    --cols-desktop: {{ section.settings.rows_desktop }};
    --cols-tablet: {{ section.settings.rows_tablet }};
    --cols-mobile: {{ section.settings.rows_mobile }};
  "
>
```

---

## Markup Structure

### Section header + description

```liquid
{% if section.settings.title != blank %}
  <h2 class="dynamic-grid-section-title">
    {{ section.settings.title }}
  </h2>
{% endif %}

{% if section.settings.section_description != blank %}
  <div class="dynamic-grid-section-description">
    {{ section.settings.section_description }}
  </div>
{% endif %}
```

### Grid block wrapper (`<a>` vs `<div>`)

Each block renders as a link when `block.settings.button_link` is present; otherwise it renders as a `<div>`.

```liquid
{% if b.button_link != blank %}
  <a
    href="{{ b.button_link }}"
    {{ block.shopify_attributes }}
    class="grid-block {% if b.custom_column_width %}custom-column-width{% endif %}"
    style="{{ block_styles | strip }}"
  >
{% else %}
  <div
    {{ block.shopify_attributes }}
    class="grid-block {% if b.custom_column_width %}custom-column-width{% endif %}"
    style="{{ block_styles | strip }}"
  >
{% endif %}
```

### Block media (desktop + mobile)

```liquid
{% if b.image %}
  <div class="block-image block-image-desktop">
    <img
      src="{{ b.image | image_url }}"
      alt="{{ b.title | escape }}"
      width="{{ b.image.width }}"
      height="{{ b.image.height }}"
      loading="lazy"
    >
  </div>
{% else %}
  <div class="block-image-placeholder block-image-desktop">
    {{ 'image' | placeholder_svg_tag: 'placeholder-svg' }}
  </div>
{% endif %}

{% if b.image_mobile %}
  {% assign image_mobile = b.image_mobile %}
{% else %}
  {% assign image_mobile = b.image %}
{% endif %}

<div class="block-image block-image-mobile">
  {% if image_mobile %}
    <img
      src="{{ image_mobile | image_url }}"
      alt="{{ b.title | escape }}"
      width="{{ image_mobile.width }}"
      height="{{ image_mobile.height }}"
      loading="lazy"
    >
  {% else %}
    <div class="block-image-placeholder block-image-mobile">
      {{ 'image' | placeholder_svg_tag: 'placeholder-svg' }}
    </div>
  {% endif %}
</div>
```

### Block content

```liquid
<div class="block-content">
  {% if b.title != blank %}
    <h3 class="block-title">{{ b.title }}</h3>
  {% endif %}

  {% if b.description != blank %}
    <div class="block-description">{{ b.description }}</div>
  {% endif %}

  {% if b.button_text != blank %}
    <div class="block-button">{{ b.button_text }}</div>
  {% endif %}
</div>
```

### Section-level button

```liquid
{% if section.settings.button_text != blank and section.settings.button_url != blank %}
  <a href="{{ section.settings.button_url }}" class="dynamic-grid-section-button">
    {{ section.settings.button_text }}
  </a>
{% endif %}
```

---

## Behavior

- **Purely presentational**: No JavaScript is used.
- **Responsive layout**: Uses CSS variables (`--cols-desktop`, `--cols-tablet`, `--cols-mobile`) to control column counts at breakpoints.
- **Two layout styles**:
  - `text-below-image`: Regular card layout.
  - `text-on-image`: Adds `.text-on-image` and positions `.block-content` absolutely over the image.
- **Per-block customization**: When `custom_styling_enabled` is true, block-level CSS variables override global section variables.
- **Optional linking**: A block becomes clickable when `button_link` is set.

---

## Schema

This section has a large schema (many layout + typography controls, plus per-block overrides). Below is an excerpt of the main structure (see the full schema inside `sections/dynamic-grid.liquid`).

```json
{
  "name": "Dynamic Grid",
  "settings": [
    { "type": "select", "id": "style", "default": "text-below-image" },
    { "type": "select", "id": "rows_desktop", "default": "3" },
    { "type": "select", "id": "rows_tablet", "default": "2" },
    { "type": "select", "id": "rows_mobile", "default": "1" }
  ],
  "blocks": [
    {
      "type": "block",
      "name": "Grid Block",
      "settings": [
        { "type": "image_picker", "id": "image" },
        { "type": "image_picker", "id": "image_mobile" },
        { "type": "text", "id": "title" },
        { "type": "text", "id": "description" },
        { "type": "text", "id": "button_text" },
        { "type": "url", "id": "button_link" }
      ]
    }
  ],
  "max_blocks": 20
}
```

---

## Implementation Notes

1. **Schema placement**: The `{% schema %}` block appears at the top of the file (before markup), which is unusual but still valid in practice.
2. **CSS is inline**: All styling is embedded in the section file via `<style>...</style>` rather than a theme asset.
3. **CSS-variable driven**: Most visual settings are applied by setting CSS variables on the root element and blocks, then consuming them in the inline `<style>`.
4. **Block-level overrides**: Block styles are built via `{% capture block_styles %}` and conditionally use either block values or global values depending on `custom_styling_enabled`.
5. **Clickable cards**: When a block has `button_link`, the whole block becomes an `<a>` element (important for semantics and click area).
6. **Image URLs**: Images use `image_url` without explicit width, which can lead to larger downloads depending on the theme’s defaults.
7. **Font-size `px` handling**: The section sets some variables without `px` (e.g. `--section-button-font-size-desktop`), and later appends `px` in CSS using `var(...)px`. Ensure the variable values are numeric.
8. **Text-on-image positioning**: When `style` is `text-on-image`, the content is absolutely positioned using `--text-on-image-top-position` and its negative counterpart.
9. **Mustache safety in docs**: If you reference Liquid mustaches in prose/inline code, escape them like `\{\{ section.id \}\}` to avoid VitePress pages rendering blank. [[memory:13638067]]

