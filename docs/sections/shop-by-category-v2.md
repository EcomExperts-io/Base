# Shop By Category V2 Section (`sections/shop-by-category-v2.liquid`)

`sections/shop-by-category-v2.liquid` renders a responsive grid of “category cards”. Each card includes an image, title, and optional link. On desktop, the layout uses a flex “expand on hover” interaction (the hovered card grows wider). On mobile, it switches to a 2-column grid without the hover expansion behavior.

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | `section-shop-by-category-v2.css`, inline `{%- style -%}` block for responsive padding |
| JS   | None |
| Blocks | `category_card` block type |
| Icons | `icon-arrow-next.svg` (inline via `inline_asset_content`) |
| Data | Relies on `section.blocks` and `section.settings` |

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
<shop-by-category-v2 class="color-{{ section.settings.color_scheme }} section-{{ section.id }}-padding">
  <div class="page-width">
    <!-- Optional header -->
    <div class="shop-by-category-v2__grid">
      {%- for block in section.blocks -%}
        <!-- Category card -->
      {%- endfor -%}
    </div>
  </div>
</shop-by-category-v2>
```

### Optional heading

```liquid
{%- if heading != blank -%}
  <div class="shop-by-category-v2__header">
    <h2 class="shop-by-category-v2__heading">{{ heading | escape }}</h2>
  </div>
{%- endif -%}
```

### Category card

Each block renders a card that optionally becomes a link if `link` is provided.

```liquid
<div class="shop-by-category-v2__card" {{ block.shopify_attributes }}>
  {%- if block_link != blank -%}
    <a href="{{ block_link }}" class="shop-by-category-v2__card-link">
  {%- endif -%}

  <div class="shop-by-category-v2__card-image-wrapper">
    {%- if block_image != blank -%}
      <img
        srcset="
          {%- if block_image.width >= 300 -%}{{ block_image | image_url: width: 300 }} 300w,{%- endif -%}
          {%- if block_image.width >= 600 -%}{{ block_image | image_url: width: 600 }} 600w,{%- endif -%}
          {%- if block_image.width >= 900 -%}{{ block_image | image_url: width: 900 }} 900w,{%- endif -%}
          {{ block_image | image_url }} {{ block_image.width }}w
        "
        src="{{ block_image | image_url: width: 600 }}"
        sizes="(min-width: 750px) 50vw, 100vw"
        alt="{{ block_image.alt | default: block_title | escape }}"
        loading="lazy"
        width="{{ block_image.width }}"
        height="{{ block_image.height }}"
        class="shop-by-category-v2__card-image"
      >
    {%- else -%}
      <div class="shop-by-category-v2__card-image-placeholder">
        {{ 'image' | placeholder_svg_tag: 'placeholder-svg' }}
      </div>
    {%- endif -%}
  </div>

  {%- if block_title != blank -%}
    <div class="shop-by-category-v2__card-content">
      <h3 class="shop-by-category-v2__card-title">{{ block_title | escape }}</h3>
      <div class="shop-by-category-v2__card-arrow">
        {{ 'icon-arrow-next.svg' | inline_asset_content }}
      </div>
    </div>
  {%- endif -%}

  {%- if block_link != blank -%}
    </a>
  {%- endif -%}
</div>
```

---

## Behavior

- **Purely presentational**: No JS required.
- **Desktop interaction**: The grid is a flex row and uses hover to expand the hovered card:
  - Non-hovered cards shrink (`flex: 0.7`)
  - Hovered card expands (`flex: 1.5`)
- **Mobile layout**: Below 749px, the grid switches to a 2-column CSS grid and hover expansion is disabled.
- **Image hover zoom**: On desktop, the card image scales slightly on hover (`transform: scale(1.05)`).

---

## Schema

```json
{
  "name": "Shop By Category V2",
  "tag": "section",
  "class": "shop-by-category-v2",
  "settings": [
    { "type": "color_scheme", "id": "color_scheme", "label": "t:sections.all.colors.label", "default": "scheme-1" },
    { "type": "text", "id": "heading", "label": "Heading", "default": "Shop By Category V2" },
    { "type": "range", "id": "padding_top", "label": "Padding Top", "min": 0, "max": 100, "step": 4, "unit": "px", "default": 40 },
    { "type": "range", "id": "padding_bottom", "label": "Padding Bottom", "min": 0, "max": 100, "step": 4, "unit": "px", "default": 40 }
  ],
  "blocks": [
    {
      "type": "category_card",
      "name": "Category Card",
      "settings": [
        { "type": "image_picker", "id": "image_desktop", "label": "Image" },
        { "type": "text", "id": "title", "label": "Title", "default": "Title" },
        { "type": "url", "id": "link", "label": "Link" }
      ]
    }
  ],
  "presets": [{ "name": "Shop By Category V2" }]
}
```

---

## Implementation Notes

1. **Hover expansion is CSS-only**: The “expanding card” behavior is implemented entirely via CSS on desktop.
2. **Link wrapping**: Cards only become clickable when `link` is provided (wraps content in an `<a>`).
3. **Placeholder behavior**: Missing images render a placeholder SVG.
4. **Mobile behavior**: Mobile disables hover transitions and uses a 2-column grid.
5. **VitePress mustache safety**: If referencing Liquid mustaches in prose/inline code, escape them like `\{\{ ... \}\}` to avoid blank pages. [[memory:13638067]]

