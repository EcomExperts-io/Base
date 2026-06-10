# Cart Section (`sections/cart.liquid`)

`sections/cart.liquid` powers the main cart page. It renders line items, notes, discounts, totals, and checkout controls inside a `<cart-page>` custom element that re-renders itself from Section Rendering API HTML after every cart mutation.

---

## Dependencies & Assets

| Type | Files / Components |
|------|--------------------|
| CSS  | `cart.css`, inline `{% style %}` block for padding |
| JS   | `component-cart-page.js` (module), `component-cart-discount.js` (module) |
| Snippets | `component-cart-discount` |
| Icons | `icon-minus.svg`, `icon-plus.svg`, `icon-close.svg`, `icon-discount.svg`, `icon-info.svg` |

- Cart interactivity comes from the native cart engine (`assets/cart.js`, loaded globally from `layout/theme.liquid`): it intercepts quantity stepper/remove link clicks (`a[href*="/cart/change"]`), quantity input changes (`.cart-quantity input`), and cart note changes via event delegation — no data attributes needed.
- `<cart-page>` (defined in `component-cart-page.js`) listens for `cart:change` and swaps in the freshly rendered section HTML bundled with every cart request.
- Section color scheme uses `color-\{\{ section.settings.color_scheme \}\}` classes to stay on theme.

---

## Dynamic Styles

Inline styles map padding settings to CSS:

```liquid
{% style %}
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
{% endstyle %}
```

- `padding_top` / `padding_bottom` come from section settings (0–100px).
- Mobile padding is 75% of the desktop value.

---

## Markup Structure

```liquid
{{ 'cart.css' | asset_url | stylesheet_tag }}

<div class="color-{{ section.settings.color_scheme }} section-{{ section.id }}-padding">
  <div class="page-width">
    <cart-page>
      {% if cart.item_count > 0 %}
        <div id="cart-main">
          <!-- Header -->
          <!-- Items -->
          <!-- Footer -->
        </div>
      {% else %}
        <!-- Empty cart state -->
      {% endif %}
    </cart-page>
  </div>
</div>

<script src="{{ 'component-cart-page.js' | asset_url }}" type="module"></script>
<script src="{{ 'component-cart-discount.js' | asset_url }}" type="module" fetchpriority="low"></script>
```

- The whole section body is wrapped in `<cart-page>` so it can re-render itself from the `cart:change` event's bundled section HTML.

### Header

```liquid
<div class="cart-header">
  <h2>Your cart ({{ cart.item_count }})</h2>
  <a href="{{ routes.all_products_collection_url }}"> Continue shopping </a>
</div>
```

### Line Items

```liquid
<div class="cart-items">
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
          <div class="cart-quantity">
            <a href="{{ routes.cart_change_url }}?line={{ line_item_index }}&quantity={{ line_item.quantity | minus: 1 }}">
              {{ 'icon-minus.svg' | inline_asset_content }}
            </a>
            <input
              name="updates[]"
              value="{{ line_item.quantity }}"
              type="number"
              form="cart-checkout-form"
            >
            <a href="{{ routes.cart_change_url }}?line={{ line_item_index }}&quantity={{ line_item.quantity | plus: 1 }}">
              {{ 'icon-plus.svg' | inline_asset_content }}
            </a>
          </div>

          <div class="cart-item__remove">
            {{ 'icon-close.svg' | inline_asset_content }}
            <a href="{{ line_item.url_to_remove }}">Remove</a>
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
        <div class="cart-item__error"></div>
        {{ 'icon-info.svg' | inline_asset_content }}
      </div>
    </div>
  {% endfor %}
</div>
```

- Variant options, custom properties, and selling plans are rendered via `<dl class="cart-item__options">`.
- Line-level discounts show under each item with `cart-discounts` list.
- The quantity stepper is a plain `.cart-quantity` div: `cart.js` intercepts clicks on its `/cart/change` links (rapid +/- clicks are debounced for 250ms and collapsed into one request) and `change` events on the input.
- The remove link is a plain anchor to `line_item.url_to_remove` (`quantity=0`) — also intercepted by `cart.js`.
- Per-line errors render into the empty `.cart-item__error` div; the info icon next to it only shows when the div has content.

### Footer & Checkout

```liquid
<div class="cart-footer">
  {% if settings.show_cart_note %}
    <div class="cart-note">
      <label for="CartNote">Order special instructions</label>
      <textarea name="note" id="CartNote">{{ cart.note }}</textarea>
    </div>
  {% endif %}

  <div class="cart-actions">
    {% render 'component-cart-discount', section_id: section.id %}

    <div class="cart-charges">
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
        <span class="cart-total__label">Estimated total</span>
        <span>{{ cart.total_price | money }}</span>
      </div>
      <small class="cart-total__small">Taxes, discounts and shipping calculated at checkout.</small>
    </div>

    {% form 'cart', cart, id: 'cart-checkout-form' %}
      <button type="submit" name="checkout">Check out</button>
    {% endform %}
  </div>
</div>
```

- `component-cart-discount` snippet handles discount codes, and its JS module listens for apply/remove actions.
- The cart note textarea auto-saves: `cart.js` listens for `change` events on `cart-page textarea[name="note"]` and POSTs the note to `/cart/update.js`.
- The checkout form id is `cart-checkout-form`; the line item quantity inputs reference it via their `form` attribute so a no-JS submit posts `updates[]` to `/cart`.
- Totals re-render with the rest of the section when `<cart-page>` receives a `cart:change` event.

### Empty State

```liquid
{% else %}
  <div class="cart__warnings">
    <h1 class="cart__empty-text">Your cart is empty</h1>
    <a href="{{ routes.all_products_collection_url }}" class="button"> Continue shopping </a>
    <h2>Have an account?</h2>
    <p class="cart__login-paragraph"><a href="{{ routes.account_login_url }}">Log in</a> to check out faster.</p>
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

1. Keep the markup the cart engine relies on intact: `.cart-quantity` around the stepper links/input, `a[href*="/cart/change"]` hrefs, `.cart-item__error` divs, and `textarea[name="note"]` — `cart.js` finds them via event delegation, no data attributes required.
2. Keep the `<cart-page>` wrapper and `component-cart-page.js` include so the section re-renders after `cart:change`; while a request is in flight, `cart.js` sets `html.cart-busy` and `cart.css` dims `.cart-items`.
3. The checkout form id must stay `cart-checkout-form` (the quantity inputs' `form` attribute references it).
4. `component-cart-discount.js` should only load once per page—this section includes it with `fetchpriority="low"`.
5. All icons referenced via `inline_asset_content` must exist under `assets/`.

