# Cart Section (`sections/cart.liquid`)

`sections/cart.liquid` powers the main cart page. It renders line items, notes, discounts, totals, and checkout controls, all kept in sync with Liquid Ajax Cart attributes.

---

## Dependencies & Assets

| Type | Files / Components |
|------|--------------------|
| CSS  | `cart.css`, inline `{% style %}` block for padding |
| JS   | `cart-discount.js` (module) |
| Snippets | `cart-discount` |
| Icons | `icon-minus.svg`, `icon-plus.svg`, `icon-close.svg`, `icon-discount.svg`, `icon-info.svg` |

- AJAX bindings rely on Liquid Ajax Cart (`data-ajax-cart-section`, `data-ajax-cart-quantity-*`, `data-ajax-cart-request-button`).
- Section color scheme uses `color-\{\{ section.settings.color_scheme \}\}` classes to stay on theme.

---

## Dynamic Styles

Inline styles map padding settings to CSS:

```liquid
{% style %}
  .cart__wrapper {
    padding-top: {{ section.settings.padding_top | append: 'px' }};
    padding-bottom: {{ section.settings.padding_bottom | append: 'px' }};
    padding-left: 1rem;
    padding-right: 1rem;
  }
{% endstyle %}
```

- `padding_top` / `padding_bottom` come from section settings (0–100px).
- Horizontal padding remains fixed at 1rem.

---

## Markup Structure

```liquid
{{ 'cart.css' | asset_url | stylesheet_tag }}

<div id="cart-main" class="color-{{ section.settings.color_scheme }}">
  {% if cart.item_count > 0 %}
    <div class="cart__wrapper">
      <!-- Header -->
      <!-- Items -->
      <!-- Footer -->
    </div>
  {% else %}
    <!-- Empty cart state -->
  {% endif %}
</div>

<script src="{{ 'cart-discount.js' | asset_url }}" type="module" fetchpriority="low"></script>
```

### Header

```liquid
<div class="cart-header">
  <h2>{{ 'cart.title' | t }} ({{ cart.item_count }})</h2>
  <a href="{{ routes.all_products_collection_url }}">
    {{ 'general.continue_shopping' | t }}
  </a>
</div>
```

### Line Items

```liquid
<div class="cart-items" data-ajax-cart-section data-ajax-cart-section-scroll>
  {% for line_item in cart.items %}
    {% assign line_item_index = forloop.index %}
    <div class="cart-item">
      <div class="cart-item__media">
        {% if line_item.image %}
          {{ line_item.image | image_url: width: 200 | image_tag: alt: line_item.title }}
        {% else %}
          {{ 'product-1' | placeholder_svg_tag }}
        {% endif %}
      </div>

      <div class="cart-item__details">
        <div class="cart-item__heading">
          <a href="{{ line_item.url }}">{{ line_item.title | escape }}</a>
          <small class="cart-item__price">
            {% if line_item.original_price > line_item.final_price %}
              <s>{{ line_item.original_price | money }}</s>
            {% endif %}
            <span>{{ line_item.final_price | money }}</span>
          </small>
        </div>

        <!-- Variant options, custom properties, selling plan, line-level discounts -->

        <div class="cart-item__action">
          <ajax-cart-quantity>
            <a
              data-ajax-cart-quantity-minus
              href="{{ routes.cart_change_url }}?line={{ line_item_index }}&quantity={{ line_item.quantity | minus: 1 }}"
            >
              {{ 'icon-minus.svg' | inline_asset_content }}
            </a>
            <input
              data-ajax-cart-quantity-input="{{ line_item_index }}"
              name="updates[]"
              value="{{ line_item.quantity }}"
              type="number"
              form="my-ajax-cart-form"
            >
            <a
              data-ajax-cart-quantity-plus
              href="{{ routes.cart_change_url }}?line={{ line_item_index }}&quantity={{ line_item.quantity | plus: 1 }}"
            >
              {{ 'icon-plus.svg' | inline_asset_content }}
            </a>
          </ajax-cart-quantity>

          <div class="cart-item__remove">
            {{ 'icon-close.svg' | inline_asset_content }}
            <a href="{{ line_item.url_to_remove }}" data-ajax-cart-request-button>
              {{ 'cart.remove' | t }}
            </a>
          </div>
        </div>

        <div class="cart-item__total">
          {% if line_item.original_line_price != line_item.final_line_price %}
            <s>{{ line_item.original_line_price | money }}</s>
            <span>{{ line_item.final_line_price | money }}</span>
          {% else %}
            <span>{{ line_item.original_line_price | money }}</span>
          {% endif %}
        </div>
      </div>

      <div class="cart-item__errors">
        <div data-ajax-cart-errors="{{ line_item.key }}"></div>
        {{ 'icon-info.svg' | inline_asset_content }}
      </div>
    </div>
  {% endfor %}
</div>
```

- Variant options, custom properties, and selling plans are rendered via `<dl class="cart-item__options">`.
- Line-level discounts show under each item with `cart-discounts` list.

### Footer & Checkout

```liquid
<div class="cart-footer">
  {% if settings.show_cart_note %}
    <div class="cart-note">
      <label for="CartNote">{{ 'cart.seller_note' | t }}</label>
      <textarea name="note" form="cart" id="CartNote">{{ cart.note }}</textarea>
    </div>
  {% endif %}

  <div class="cart-actions">
    {% render 'cart-discount', section_id: section.id %}

    <div class="cart-charges" data-ajax-cart-section>
      {% if cart.cart_level_discount_applications.size > 0 %}
        <ul class="cart-discounts">
          {% for discount_application in cart.cart_level_discount_applications %}
            <li>
              {{ 'icon-discount.svg' | inline_asset_content }}
              {{ discount_application.title }} (-{{ discount_application.total_allocated_amount | money }})
            </li>
          {% endfor %}
        </ul>
      {% endif %}

      <div class="cart-total">
        <span class="cart-total__label">{{ 'cart.estimated_total' | t }}</span>
        <span>{{ cart.total_price | money }}</span>
      </div>
      <small class="cart-total__small">
        {{ 'cart.taxes_and_shipping_policy' | t }}
      </small>
    </div>

    {% form 'cart', cart, id: 'my-ajax-cart-form' %}
      <button type="submit" name="checkout">
        {{ 'cart.checkout' | t }}
      </button>
    {% endform %}
  </div>
</div>
```

- `cart-discount` snippet handles discount codes, and JS module listens for apply/remove actions.
- Totals block updates automatically thanks to `data-ajax-cart-section`.

### Empty State

```liquid
{% else %}
  <div class="cart__warnings">
    <h1 class="cart__empty-text">{{ 'sections.cart.empty' | t }}</h1>
    <a href="{{ routes.all_products_collection_url }}" class="button">
      {{ 'general.continue_shopping' | t }}
    </a>
    <h2>{{ 'sections.cart.login.title' | t }}</h2>
    <p class="cart__login-paragraph">
      {{ 'sections.cart.login.paragraph_html' | t: link: routes.account_login_url }}
    </p>
  </div>
{% endif %}
```

- Encourages shoppers to continue browsing and log in for faster checkout.

---

## Schema

```json
{
  "name": "t:sections.main-cart-items.name",
  "settings": [
    {
      "type": "color_scheme",
      "id": "color_scheme",
      "label": "t:sections.all.colors.label",
      "default": "scheme-1"
    },
    {
      "type": "header",
      "content": "t:sections.all.padding.section_padding_heading"
    },
    {
      "type": "range",
      "id": "padding_top",
      "min": 0,
      "max": 100,
      "step": 4,
      "unit": "px",
      "label": "t:sections.all.padding.padding_top",
      "default": 36
    },
    {
      "type": "range",
      "id": "padding_bottom",
      "min": 0,
      "max": 100,
      "step": 4,
      "unit": "px",
      "label": "t:sections.all.padding.padding_bottom",
      "default": 36
    }
  ]
}
```

- Merchants control palette + vertical spacing.
- No blocks defined; entire cart layout lives in this section.

---

## Implementation Notes

1. Translation keys must stay localized (`cart.title`, `cart.checkout`, `sections.cart.empty`, etc.).
2. Keep `data-ajax-cart-*` attributes intact so Liquid Ajax Cart can intercept quantity/remove actions.
3. `cart-discount.js` should only load once per page—this section includes it with `fetchpriority="low"`.
4. All icons referenced via `inline_asset_content` must exist under `assets/`.

