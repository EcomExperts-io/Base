# Product Section (`sections/product.liquid`)

`sections/product.liquid` renders Shopify's main product detail page with a flexible block-based structure. It combines product media galleries, variant selection, pricing, purchasing options, and dynamic content blocks. The section uses a custom element (`<product-info>`) to manage variant state and coordinate updates via the Section Rendering API.

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | `swiper7.4.1.min.css`, `component-product-price.css`, `section-product.css`, `component-product-media-modal.css` (conditional), `component-product-card.css` (conditional), `component-complementary-products.css` (conditional), `component-quick-add.css` (conditional), `component-pickup-availability.css` (conditional), `component-product-share-button.css` (conditional) |
| JavaScript | `section-product.js`, `swiper7.4.1.min.js`, `component-product-card.js` (conditional), `product-recommendations.js` (conditional), `component-quick-add.js` (conditional), `component-modal-opener.js` (conditional), `component-pickup-availability.js` (conditional), `component-product-share-button.js` (conditional), `component-product-media-modal.js` (conditional), `component-product-media-magnify.js` (conditional), `component-selling-plans.js` (conditional) |
| Custom Elements | `<product-info>`, `<variant-selector>`, `<quantity-selector>`, `<ajax-cart-product-form>`, `<pickup-availability>`, `<product-recommendations>`, `<selling-plans-widget>` |
| Snippets | `component-product-media-gallery`, `component-product-price`, `component-product-share-button`, `component-product-card`, `component-pickup-availability`, `component-product-media-modal` |
| Icons | `icon-spinner.svg`, `icon-unavailable.svg`, `icon-caret.svg`, `icon-inventory-status.svg` (inline via `inline_asset_content`) |

- Many assets are conditionally loaded based on section settings and block types.
- Custom elements handle interactive behavior and state management.
- Section uses Swiper for media carousel functionality.

---

## Dynamic Styles

Dynamic styles are generated via an inline `{% style %}` block:

```liquid
{%- style -%}
  .section-{{ section.id }}-padding {
    padding-top: {{ section.settings.padding_top | times: 0.75 | round: 0 }}px;
    padding-bottom: {{ section.settings.padding_bottom | times: 0.75 | round: 0 }}px;
  }

  .option__label {
    font-size: {{ section.settings.variant_label_font_size }}px;
    font-weight: {{ section.settings.variant_label_font_weight }};
  }

  {% for block in section.blocks %}
    {% case block.type %}
      {% when 'title' %}
        .product__title h1 {
          font-size: {{ block.settings.title_font_size }}px;
          font-weight: {{ block.settings.title_font_weight }};
        }
      {% when 'description' %}
        .product__description {
          font-size: {{ block.settings.description_font_size }}px;
          font-weight: {{ block.settings.description_font_weight }};
        }
      {% when 'price' %}
        .price-item {
          font-size: {{ block.settings.price_font_size }}px;
          font-weight: {{ block.settings.price_font_weight }};
        }
    {% endcase %}
  {% endfor %}

  @media screen and (min-width: 769px) {
    .section-{{ section.id }}-padding {
      padding-top: {{ section.settings.padding_top }}px;
      padding-bottom: {{ section.settings.padding_bottom }}px;
    }
  }
{%- endstyle -%}
```

- **Responsive padding**: Mobile padding is 75% of desktop padding for better mobile spacing.
- **Block-specific styles**: Title, description, and price blocks have customizable colors, font sizes, and font weights.
- **Variant label styling**: Global variant label styling applies to all variant pickers.

---

## Markup Structure

```liquid
<product-info
  data-url="{{ product.url}}"
  data-section="{{ section.id }}"
  class="color-{{ section.settings.color_scheme }} section-{{ section.id }}-padding"
>
  <!-- CSS and JavaScript assets -->
  <!-- Dynamic styles -->
  
  <div class="page-width">
    <div class="product flex product--{{ section.settings.media_size }} product--{{ section.settings.media_position }} {% if section.settings.constrain_to_viewport %}constrain-height{% endif %}">
      <div class="product__media-wrapper flex__item media-{{ section.settings.media_fit }}">
        {% render 'component-product-media-gallery', ... %}
      </div>
      <div class="product__info-wrapper flex__item {% if section.settings.enable_sticky_info %}product__info-sticky {% endif %}">
        {%- for block in section.blocks -%}
          {%- case block.type -%}
            <!-- Block rendering -->
          {%- endcase -%}
        {%- endfor -%}
      </div>
    </div>
  </div>
  
  <!-- Media modal (conditional) -->
  <!-- JavaScript assets -->
</product-info>
```

- **Custom element wrapper**: `<product-info>` manages variant state and coordinates updates.
- **Two-column layout**: Media gallery on one side, product info on the other.
- **Flexible media positioning**: Media can be positioned left or right via `media_position` setting.
- **Sticky info**: Product info can stick to viewport on scroll when enabled.

### Block Types

The section supports the following block types (rendered in order):

#### Text Block
```liquid
{%- when 'text' -%}
  <p class="product__text {% if block.settings.text_style == 'uppercase' %} caption-with-letter-spacing{% elsif block.settings.text_style == 'subtitle' %} subtitle{% endif %}" {{ block.shopify_attributes }}>
    {{- block.settings.text -}}
  </p>
```

#### Title Block
```liquid
{%- when 'title' -%}
  <div class="product__title" {{ block.shopify_attributes }}>
    <h1>{{ product.title }}</h1>
  </div>
```

#### Price Block
```liquid
{%- when 'price' -%}
  <div id="price-{{ section.id }}" class="product__price" role="status" {{ block.shopify_attributes }}>
    {%- render 'component-product-price', product: product, use_variant: true, show_badges: true, price_class: 'price--large' -%}
  </div>
  <!-- Volume pricing note, tax info, installment form -->
```

- **Dynamic updates**: Price updates via Section Rendering API when variants change.
- **Volume pricing**: Shows note when quantity price breaks are configured.
- **Tax/duty info**: Displays tax and duty information when applicable.
- **Installment form**: Hidden form for payment terms display.

#### SKU Block
```liquid
{%- when 'sku' -%}
  <p class="product__sku{% if selected_variant.sku.size == 0 %} visibility-hidden{% endif %}" id="sku-{{ section.id }}" {{ block.shopify_attributes }}>
    {{- selected_variant.sku -}}
  </p>
```

- **Conditional visibility**: Hidden when variant has no SKU.

#### Variant Picker Block
```liquid
{%- when 'variant_picker' -%}
  <div class="product__variants" {{ block.shopify_attributes }}>
    {% unless product.has_only_default_variant %}
      <variant-selector id="variant-selector-{{ section.id }}" data-picker-type="{{ block.settings.picker_type }}">
        <!-- Dropdown or button picker -->
      </variant-selector>
    {% endunless %}
  </div>
```

- **Two picker types**: Dropdown (`picker_type == 'dropdown'`) or button swatches (`picker_type == 'button'`).
- **Variant selector**: Custom element manages variant selection and triggers updates.

#### Quantity Selector Block
```liquid
{%- when 'quantity_selector' -%}
  <div class="product__quantity" {{ block.shopify_attributes }}>
    <label class="option__label" for="Quantity-{{ section.id }}">Quantity</label>
    <quantity-selector>
      <!-- Minus button, input, plus button -->
    </quantity-selector>
  </div>
```

- **Quantity rules**: Input respects variant quantity rules (min, max, increment).
- **Cart quantity**: Shows current cart quantity for selected variant.

#### Description Block
```liquid
{%- when 'description' -%}
  {%- if product.description != blank -%}
    <div class="product__description" {{ block.shopify_attributes }}>
      <p>{{ product.description }}</p>
    </div>
  {%- endif -%}
```

#### Buy Buttons Block
```liquid
{%- when 'buy_buttons' -%}
  <div class="product-form__buttons" {{ block.shopify_attributes }}>
    <ajax-cart-product-form>
      {% form 'product', product, id: product_form_id, novalidate: 'novalidate' %}
        <!-- Add to cart button, dynamic checkout -->
      {% endform %}
    </ajax-cart-product-form>
    
    <!-- Pickup availability (conditional) -->
  </div>
```

- **AJAX cart integration**: Uses `ajax-cart-product-form` custom element for cart updates.
- **Dynamic checkout**: Optional Shop Pay, Apple Pay buttons.
- **Pickup availability**: Optional local pickup information.

#### Custom Liquid Block
```liquid
{%- when 'custom_liquid' -%}
  {{ block.settings.custom_liquid }}
```

#### Collapsible Tab Block
```liquid
{%- when 'collapsible_tab' -%}
  <div class="product__accordion accordion" {{ block.shopify_attributes }}>
    <details>
      <summary>
        <!-- Icon, heading -->
      </summary>
      <div class="accordion__content">
        <!-- Content or page content -->
      </div>
    </details>
  </div>
```

- **Native details element**: Uses semantic HTML5 `<details>` for accordion behavior.
- **Icon support**: Optional icon display in accordion header.

#### Inventory Block
```liquid
{%- when 'inventory' -%}
  <p class="product__inventory{% if selected_variant.inventory_management != 'shopify' %} visibility-hidden{% endif %}" id="inventory-{{ section.id }}" {{ block.shopify_attributes }}>
    <!-- Inventory status with icons and thresholds -->
  </p>
```

- **Inventory thresholds**: Shows low stock warning when quantity is below threshold.
- **Color-coded icons**: Different colors for in-stock, low-stock, out-of-stock states.

#### Share Block
```liquid
{%- when 'share' -%}
  {% assign share_url = product.selected_variant.url | default: product.url | prepend: request.origin %}
  {% render 'component-product-share-button', block: block, share_link: share_url, section_id: section.id %}
```

#### Subscription Block
```liquid
{%- when 'subscription' -%}
  <div class="product__subscription">
    <selling-plans-widget data-section-id="{{ section.id }}" {{ block.shopify_attributes }}>
      <!-- One-time purchase option, selling plan groups -->
    </selling-plans-widget>
  </div>
```

- **Selling plans**: Displays subscription options with pricing adjustments.
- **Variant-specific plans**: Shows plans for each variant with proper pricing.

#### Complementary Products Block
```liquid
{%- when 'complementary' -%}
  <product-recommendations
    class="product-recommendations"
    data-url="{{ routes.product_recommendations_url }}?section_id={{ section.id }}&product_id={{ product.id }}&limit={{ block.settings.products_to_show }}&intent=complementary"
  >
    <!-- Product recommendations -->
  </product-recommendations>
```

- **AJAX loading**: Recommendations loaded via AJAX by custom element.
- **Product cards**: Uses `component-product-card` for consistent display.

---

## Behavior

- **Variant selection**: When variants are selected, the `<product-info>` custom element fetches updated HTML via the Section Rendering API and updates:
  - Product media gallery
  - Price, SKU, inventory
  - Add to cart button state
  - URL query parameters

- **Quantity rules**: Quantity selector respects variant quantity rules (min, max, increment).

- **Sticky info**: When enabled, product info column sticks to viewport on scroll.

- **Media gallery**: Uses Swiper for carousel functionality with multiple layout options (carousel, 2 columns, thumbnail).

- **Image zoom**: Supports lightbox, hover zoom, or no zoom based on settings.

- **AJAX cart**: Add to cart uses AJAX via `ajax-cart-product-form` custom element.

- **Pickup availability**: Fetches and displays local pickup information when enabled.

---

## Schema

The section includes an extensive schema with multiple block types and settings. Key settings include:

### Section Settings

- **Layout**: `media_size`, `media_position`, `media_fit`, `media_layout`, `mobile_media_layout`
- **Image zoom**: `image_zoom` (lightbox, hover, none)
- **Sticky info**: `enable_sticky_info`
- **Color scheme**: `color_scheme`
- **Padding**: `padding_top`, `padding_bottom`
- **Variant labels**: `variant_label_color`, `variant_label_font_size`, `variant_label_font_weight`

### Block Settings

Each block type has its own settings for customization (colors, font sizes, text styles, etc.). See the schema section in the Liquid file for complete details.

---

## Implementation Notes

1. **Custom element**: The `<product-info>` custom element (defined in `section-product.js`) manages all variant state and coordinates updates via the Section Rendering API.

2. **Section Rendering API**: When variants change, the section fetches updated HTML and selectively updates DOM elements (price, SKU, inventory, media, etc.) without full page reload.

3. **Media gallery**: Uses `component-product-media-gallery` snippet which handles images, videos, and 3D models with Swiper carousel.

4. **Variant selector**: The `<variant-selector>` custom element handles both dropdown and button-style pickers, triggering updates to the parent `<product-info>` element.

5. **Quantity selector**: The `<quantity-selector>` custom element handles increment/decrement buttons and validates against variant quantity rules.

6. **AJAX cart**: Uses `ajax-cart-product-form` custom element (likely from Liquid Ajax Cart library) for seamless cart updates.

7. **Pickup availability**: Uses `<pickup-availability>` custom element which fetches store availability data and displays it in a drawer.

8. **Complementary products**: Uses `<product-recommendations>` custom element which fetches recommendations via AJAX from Shopify's recommendation API.

9. **Selling plans**: Complex subscription logic handled by `<selling-plans-widget>` custom element with variant-specific pricing.

10. **Translation keys**: All user-facing text uses translation filters (e.g., `t:sections.main-product.blocks.*`).

11. **Conditional asset loading**: Many CSS and JavaScript files are only loaded when specific blocks or settings are enabled to optimize page load.

12. **Responsive design**: Mobile padding is 75% of desktop padding. Media layout can differ between desktop and mobile.

13. **Accessibility**: Proper ARIA roles, labels, and semantic HTML throughout. Form inputs have proper labels and error handling.

14. **Icon dependencies**: Multiple icons required: `icon-spinner.svg`, `icon-unavailable.svg`, `icon-caret.svg`, `icon-inventory-status.svg`.

15. **Product form ID**: Generated as `product-form-\{\{ section.id \}\}` to ensure uniqueness when multiple product sections exist.

16. **Selected variant**: Uses `product.selected_or_first_available_variant` as the default variant for initial display.

17. **Media modal**: Optional lightbox modal for product images when `image_zoom == 'lightbox'`.

18. **Video looping**: Optional video looping when `enable_video_looping` is enabled.

19. **Image magnify**: Optional hover zoom functionality when `image_zoom == 'hover'`.

20. **Block limits**: Some blocks have `"limit": 1` in schema to prevent duplicates (title, price, variant_picker, etc.).
