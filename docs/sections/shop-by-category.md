# Shop By Category Section (`sections/shop-by-category.liquid`)

`sections/shop-by-category.liquid` renders a “Shop by category” layout with a featured collection image and a list of collection links. Each collection is configured via blocks and can provide a custom title and a custom image. On desktop, hovering/focusing a collection link swaps the featured image via a custom element.

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | `section-shop-by-category.css`, inline `{%- style -%}` block for responsive padding |
| JS   | `section-shop-by-category.js` (deferred) |
| Custom Element | `<shop-by-category>` defined in `section-shop-by-category.js` |
| Blocks | `collection` block type |
| Data | Relies on `section.blocks` and `section.settings` |

---

## Dynamic Styles

### Responsive padding

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

### Button color variables

The section sets button colors via CSS variables on the `<shop-by-category>` wrapper:

```liquid
<shop-by-category
  class="color-{{ section.settings.color_scheme }} section-{{ section.id }}-padding"
  style="
    --button: var(--color-{{ button_type }});
    --button-text: var(--color-{{ button_type }}-text);
  "
>
```

`section-shop-by-category.css` uses these variables for the collection link “pill” styling.

---

## Markup Structure

```liquid
{%- if blocks_to_show > 0 -%}
  <shop-by-category class="color-{{ section.settings.color_scheme }} section-{{ section.id }}-padding">
    <div class="page-width">
      <div class="shop-by-category__container">
        <div class="shop-by-category__image-wrapper">
          <!-- Featured image -->
        </div>
        <div class="shop-by-category__content">
          <!-- Heading + collection links -->
        </div>
      </div>
    </div>
  </shop-by-category>
{%- endif -%}
```

- The section only renders if at least one block exists.
- The featured image is derived from the **first block** (custom image → collection featured image).

### Featured image (left)

```liquid
<div class="shop-by-category__image-wrapper {% if collection_image == blank %}blank{% endif %}">
  {%- if collection_image != blank -%}
    <img
      srcset="
        {%- if collection_image.width >= 300 -%}{{ collection_image | image_url: width: 300 }} 300w,{%- endif -%}
        {%- if collection_image.width >= 600 -%}{{ collection_image | image_url: width: 600 }} 600w,{%- endif -%}
        {%- if collection_image.width >= 900 -%}{{ collection_image | image_url: width: 900 }} 900w,{%- endif -%}
        {{ collection_image | image_url }} {{ collection_image.width }}w
      "
      src="{{ collection_image | image_url: width: 600 }}"
      sizes="(min-width: 750px) 50vw, 100vw"
      alt="{{ collection_image.alt | default: first_collection.title | escape }}"
      loading="lazy"
      width="{{ collection_image.width }}"
      height="{{ collection_image.height }}"
      class="shop-by-category__featured-image"
    >
  {%- else -%}
    {{ 'image' | placeholder_svg_tag: 'placeholder-svg' }}
  {%- endif -%}
</div>
```

### Collection links (right)

Each block renders as an `<a>` with a `data-featured-image` URL used by JS:

```liquid
{% assign collection_title = block.settings.custom_title | default: block.settings.collection.title %}
{% assign collection_url = block.settings.collection.url %}
{% assign collection_featured_image = block.settings.custom_image | default: block.settings.collection.featured_image %}

<a
  href="{{ collection_url }}"
  {{ block.shopify_attributes }}
  data-featured-image="{{ collection_featured_image | image_url: width: 800 }}"
  class="shop-by-category__collection-item"
>
  {{ collection_title }}
  <div class="shop-by-category__collection-item-icon">
    <span aria-hidden="true">{{ 'icon-arrow-next.svg' | inline_asset_content }}</span>
  </div>
</a>
```

Fallback (when title/url are missing) uses a `<li>` placeholder.

---

## JavaScript Behavior

`assets/section-shop-by-category.js` defines a `<shop-by-category>` custom element that:

- Collects all `.shop-by-category__collection-item` links.
- On `mouseover` and `focus`, reads `data-featured-image` and swaps the `.shop-by-category__featured-image` `src`.
- Does nothing when `window.innerWidth <= 1080` (the featured image is hidden on smaller viewports via CSS).

---

## Behavior

- **Purely presentational layout + small enhancement**: The section works without JS (links still function); JS only improves the desktop experience by swapping the featured image.
- **Responsive behavior**: The featured image column is hidden at ≤1080px (CSS), and the JS image-swap is disabled in that range.

---

## Schema

```json
{
  "name": "Shop By Category",
  "tag": "section",
  "settings": [
    { "type": "color_scheme", "id": "color_scheme", "label": "t:sections.all.colors.label", "default": "scheme-1" },
    { "type": "text", "id": "heading", "label": "Heading" },
    {
      "type": "select",
      "id": "button_type",
      "label": "Button Style",
      "options": [
        { "value": "button", "label": "Primary" },
        { "value": "secondary-button", "label": "Secondary" }
      ],
      "default": "button"
    },
    { "type": "range", "id": "padding_top", "label": "Padding Top", "min": 0, "max": 100, "step": 4, "unit": "px", "default": 40 },
    { "type": "range", "id": "padding_bottom", "label": "Padding Bottom", "min": 0, "max": 100, "step": 4, "unit": "px", "default": 40 }
  ],
  "blocks": [
    {
      "type": "collection",
      "name": "Collection",
      "settings": [
        { "type": "collection", "id": "collection", "label": "Collection" },
        { "type": "text", "id": "custom_title", "label": "Custom Title" },
        { "type": "image_picker", "id": "custom_image", "label": "Custom Image" }
      ]
    }
  ],
  "presets": [{ "name": "Shop By Category" }]
}
```

---

## Implementation Notes

1. **Featured image source**: The large featured image uses the first block’s custom image or the first block’s collection featured image.
2. **Image swap trigger**: Each link carries `data-featured-image` (800w) for swapping on hover/focus.
3. **Responsive breakpoint mismatch**: JS disables swapping at `<=1080`, and CSS hides the image at `<=1080`. Keep these in sync if you adjust layout.
4. **VitePress mustache safety**: If referencing Liquid mustaches in prose/inline code, escape them like `\{\{ ... \}\}` to avoid blank pages. [[memory:13638067]]

