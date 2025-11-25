# component-product-card Snippet

`snippets/component-product-card.liquid` renders a reusable product card wrapper around the `<product-card>` custom element. It outputs the media, pricing, vendor, optional swatches, and quick add controls inside a consistent markup structure so grids and carousels can reuse the same UI.


---

## What It Does

- Wraps card markup in `<product-card>` so `component-product-card.js` can handle swatch interactions.
- Renders media (image or placeholder) with badge overlays for sold-out/on-sale states.
- Outputs product title, vendor text, and price via `component-product-price`.
- Optionally renders variant swatches based on a trigger option (e.g., Color) and swatch type (color chip vs image).
- Includes quick add logic: either opens a modal to choose options or submits the first available variant.

---

## Parameters

| Parameter             | Type     | Default        | Description                                                                        |
|-----------------------|----------|----------------|------------------------------------------------------------------------------------|
| `card_product`        | product  | **required**   | Product object to render (must be passed).                                         |
| `show_vendor`         | boolean  | `false`        | Displays the vendor text below the title.                                          |
| `enable_swatches`     | boolean  | `false`        | Toggles variant swatches UI.                                                       |
| `swatch_trigger`      | string   | `blank`        | Product option name to match when rendering swatches (e.g., `Color`).              |
| `swatch_type`         | string   | `color`/`image`| Determines whether swatches show color chips or variant images.                    |
| `media_aspect_ratio`  | string   | `adapt`        | Controls image aspect ratio (square/adapt/portrait).                               |
| `button_text_color`   | string   | `blank`        | Optional inline style for quick-add button text.                                   |
| `button_border_color` | string   | `blank`        | Optional inline style for quick-add button border (passed through to button).      |
| `section_id`          | string   | context        | Section identifier used to namespace quick-add modal IDs (implicitly provided).    |
| `quick_add`           | string   | `nil`          | Determines quick add behavior (`standard` enables modal/quick form).               |

---

## Markup Structure

```liquid
<product-card class="product-card" data-product-id="{{ card_product.id }}">
  <div class="product-card-child">
    <a href="{{ card_product.url }}" class="card-media">
      <!-- Media (image or placeholder) + badge wrapper -->
    </a>
    <div class="card-information">
      <!-- Title, vendor, price, swatches, quick add -->
    </div>
  </div>
</product-card>
```

### Media Section
- Uses `card_product.featured_image` when available; falls back to the `'product-1'` placeholder.
- Adds `card-media-no-image` class if no image exists.
- Includes badge markup:
  - Sold out: `products.product.sold_out`
  - On sale: `products.product.on_sale`

### Info Section
- Heading links to the product URL.
- Optional vendor span.
- Price block renders `component-product-price` with `show_compare_at_price: true`.
- Swatches render when `enable_swatches` is true:
  - Iterates options to match `swatch_trigger`.
  - Outputs `.color-swatch` spans with `data-variant-id`, `data-swatch-color`, optional `src/srcset`, and image markup when `swatch_type == 'image'`.
  - Fallback color swatches use inline `background-color` derived from the option value handle.

### Quick Add
- `product_form_id` combines `quick-add-`, `section_id`, and the product ID for unique IDs.
- When `quick_add == 'standard'`:
  - If multiple variants or quantity rules exist, renders a modal opener button and `<quick-add-modal>` container that loads variant content asynchronously.
  - Otherwise, renders an `<ajax-cart-product-form>` with hidden variant ID and quick-add submit button.
- Buttons include loading spinners and localized labels (`products.product.add_to_cart`, `products.product.choose_options`, etc.).

---

## JavaScript & Components

- Requires `component-product-card.js` (already included via section assets) to enable swatch-driven image swapping.
- Uses platform custom elements:
  - `<product-card>` for the interactive card wrapper.
  - `<modal-opener>` and `<quick-add-modal>` for the Quick Add experience.
  - `<ajax-cart-product-form>` for direct submissions.
- Icons loaded via `inline_asset_content` (`icon-close.svg`, `icon-spinner.svg`).

---

## Usage Example

```liquid
{% render 'component-product-card',
  card_product: product,
  show_vendor: section.settings.show_vendor,
  enable_swatches: section.settings.enable_swatches,
  swatch_trigger: section.settings.swatch_trigger,
  swatch_type: section.settings.swatch_type,
  quick_add: section.settings.quick_add,
  section_id: section.id,
  button_text_color: section.settings.button_text_color,
  button_border_color: section.settings.button_border_color
%}
```

Place this snippet inside product grids (collections, featured sections, recommendations). The section should ensure it loads the CSS/JS assets listed in each section’s documentation so the markup styles and behaviors activate correctly.

---

## Implementation Notes

1. Always pass `card_product`; the snippet assumes it’s present and will fail silently without it.
2. Ensure swatch data aligns with actual variants; mismatched `swatch_trigger` values produce empty swatch lists.
3. When customizing button styles, keep `button_text_color` and `button_border_color` sanitized or map them through theme settings (the snippet directly outputs them).
4. Quick add modal IDs use `section_id`; when embedding this snippet in different sections, pass unique section IDs to prevent ID collisions.

