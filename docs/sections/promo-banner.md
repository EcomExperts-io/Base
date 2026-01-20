# Promo Banner Section (`sections/promo-banner.liquid`)

`sections/promo-banner.liquid` renders a product-focused promo banner with product title, short description, price, and a “SHOP NOW” CTA, alongside an image. The product is selected via a product picker setting, and a custom image can optionally override the product’s featured image. Layout and image behavior are controlled via CSS variables.

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | `section-promo-banner.css`, inline `{%- style -%}` block for responsive padding |
| JS   | None |
| Data | Relies on `section.settings` and the selected `product` |

- No JavaScript dependencies; the section is purely presentational.

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

  .section-{{ section.id }}-icon-size {
    --selling-points-icon-size: {{ section.settings.icon_size }}px;
  }
{%- endstyle -%}
```

- **Responsive padding**: Mobile padding is 75% of desktop value; full padding applies at 750px+.
- The `--selling-points-icon-size` variable is defined, but this section’s markup doesn’t reference it.

### Promo banner CSS variables

The section sets layout + image variables inline:

```liquid
<div
  class="color-{{ section.settings.color_scheme }} section-{{ section.id }}-padding"
  style="
    --promo-banner-image-placement: {{ image_placement }};
    --promo-banner-image-height: {{ image_height }}px;
    --promo-banner-image-fit: {{ image_fit }};
    --promo-banner-image-position: {{ image_position }};
    --promo-banner-button-color: {{ button_background_color }};
    --promo-banner-button-text-color: {{ button_text_color }};
  "
>
```

`section-promo-banner.css` consumes these variables for:
- Desktop flex direction (`--promo-banner-image-placement`)
- Image max-height, object-fit, object-position

---

## Markup Structure

```liquid
<div class="promo-banner__container">
  <div class="promo-banner__content">
    <!-- Title, description, price, CTA -->
  </div>

  <div class="promo-banner__image-wrapper">
    <!-- Image -->
  </div>
</div>
```

### Content (title, description, price, CTA)

The section derives product values from the selected product:
- `product_title` from `product.title`
- `product_description` from `product.description | strip_html | truncatewords: 20`
- `product_price` from `product.price_min | money`
- `product_url` from `product.url`

```liquid
{%- if product_title != blank -%}
  <h3 class="promo-banner__title">{{ product_title | escape }}</h3>
{% else %}
  <h3 class="promo-banner__title">Promo Product's Title</h3>
{%- endif -%}

{%- if product_description != blank -%}
  <p class="promo-banner__description">{{ product_description }}</p>
{% else %}
  <p class="promo-banner__description">Promo Product's Description</p>
{%- endif -%}

{%- if product_price != blank -%}
  <div class="promo-banner__price">{{ product_price }}</div>
{% else %}
  <div class="promo-banner__price">$69.00</div>
{%- endif -%}

<a href="{{ product_url }}" class="promo-banner__button-link">
  <span class="promo-banner__button">SHOP NOW</span>
</a>
```

Notes:
- Description is output without escaping (it is already stripped/truncated earlier).
- The CTA text is hardcoded as “SHOP NOW”.

### Image

The image uses the custom image if provided; otherwise it falls back to the product’s featured image:

```liquid
{%- liquid
  assign product_image = custom_image | default: product.featured_image
-%}
```

Rendering:

```liquid
<div class="promo-banner__image-wrapper {% if product_image == blank %}blank{% endif %}">
  {%- if product_image != blank -%}
    <img
      srcset="
        {%- if product_image.width >= 300 -%}{{ product_image | image_url: width: 300 }} 300w,{%- endif -%}
        {%- if product_image.width >= 600 -%}{{ product_image | image_url: width: 600 }} 600w,{%- endif -%}
        {%- if product_image.width >= 900 -%}{{ product_image | image_url: width: 900 }} 900w,{%- endif -%}
        {{ product_image | image_url }} {{ product_image.width }}w
      "
      src="{{ product_image | image_url: width: 600 }}"
      sizes="(min-width: 750px) 50vw, 100vw"
      alt="{{ product_image.alt | default: product_title | escape }}"
      loading="lazy"
      width="{{ product_image.width }}"
      height="{{ product_image.height }}"
      class="promo-banner__image"
    >
  {%- else -%}
    {{ 'image' | placeholder_svg_tag: 'placeholder-svg' }}
  {%- endif -%}
</div>
```

- Adds `.blank` class when there’s no image (CSS applies placeholder background color).
- Responsive srcset uses 300w / 600w / 900w.

---

## Behavior

- **Purely presentational**: No JS.
- **Responsive layout**:
  - Desktop (≥750px): uses `flex-direction: var(--promo-banner-image-placement)` (row or row-reverse)
  - Mobile: stacks content then image
- **Fallback content**: If no product is selected, the section displays placeholder text and a placeholder image.

---

## Schema

```json
{
  "name": "Promo Banner",
  "tag": "section",
  "class": "promo-banner",
  "settings": [
    { "type": "color_scheme", "id": "color_scheme", "label": "t:sections.all.colors.label", "default": "scheme-1" },
    { "type": "product", "id": "product", "label": "Product" },
    { "type": "image_picker", "id": "custom_image", "label": "Custom Image" },
    { "type": "select", "id": "image_placement", "default": "row" },
    { "type": "range", "id": "image_height", "min": 400, "max": 800, "step": 50, "default": 500 },
    { "type": "select", "id": "image_fit", "default": "cover" },
    { "type": "select", "id": "image_position", "default": "center" },
    { "type": "range", "id": "padding_top", "default": 40 },
    { "type": "range", "id": "padding_bottom", "default": 40 }
  ],
  "presets": [{ "name": "Promo Banner" }]
}
```

---

## Implementation Notes

1. **Product required for real data**: Without selecting a product, the section falls back to placeholder text/price/image, and the link may be empty.
2. **Description is derived**: Uses `product.description | strip_html | truncatewords: 20` for a short excerpt.
3. **Image override**: `custom_image` overrides `product.featured_image`.
4. **Layout switching**: Desktop image placement is controlled by `image_placement` (`row` = image right, `row-reverse` = image left).
5. **Button styling variables**: The section sets `--promo-banner-button-color` and `--promo-banner-button-text-color`, but `section-promo-banner.css` currently styles the button using theme color variables (`--color-button` / `--color-button-text`). If you expect the banner button colors to change, ensure CSS consumes the promo variables.
6. **VitePress mustache safety**: If referencing Liquid mustaches in prose/inline code, escape them like `\{\{ ... \}\}` to avoid blank pages. [[memory:13638067]]

