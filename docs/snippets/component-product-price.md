# component-product-price Snippet

`snippets/component-product-price.liquid` renders a product's price block including regular price, sale price, compare-at price, unit price, and optional sale/sold-out badges. It supports volume pricing messaging, variant-based pricing, and currency code display. The component handles complex pricing scenarios including products with varying prices and quantity-based pricing breaks.

---

## What It Does

- Renders product or variant prices with proper formatting.
- Displays regular and sale prices with compare-at price strikethrough.
- Shows unit pricing (price per unit of measurement).
- Supports volume pricing with price range display.
- Displays optional "Sale" and "Sold Out" badges.
- Handles currency code display when enabled.
- Provides accessible price labels for screen readers.
- Applies dynamic CSS classes based on price state.

---

## Parameters

| Parameter            | Type    | Default | Description                                                      |
|----------------------|---------|---------|------------------------------------------------------------------|
| `product`            | object  | optional | Product object to render prices for.                             |
| `placeholder`        | boolean | optional | Render placeholder pricing when no product.                      |
| `use_variant`        | boolean | optional | Use selected/first variant instead of product-level pricing.    |
| `show_badges`        | boolean | optional | Show "Sale" and "Sold Out" badges.                              |
| `price_class`        | string  | optional | Extra CSS class to append to price wrapper.                      |
| `show_compare_at_price` | boolean | optional | Show compare-at price when applicable (for volume pricing).     |

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | External stylesheet (likely `component-product-price.css`) |
| JavaScript | None required |
| Shopify Filters | `money`, `money_with_currency`, `money_without_currency` |
| Data | Requires `product` object with pricing properties, `settings.currency_code_enabled` |

- No external JavaScript required - all functionality handled by Liquid.
- External CSS handles all price styling and badge display.
- Shopify money filters handle currency formatting.

---

## Dynamic Styles

The snippet does not include inline styles. All styling is handled by external CSS files. However, the component uses dynamic CSS classes based on price state:

```liquid
class="
  price
  {%- if price_class %} {{ price_class }}{% endif -%}
  {%- if available == false %} price--sold-out{% endif -%}
  {%- if compare_at_price > price and product.quantity_price_breaks_configured? != true %} price--on-sale{% endif -%}
  {%- if compare_at_price > price and product.quantity_price_breaks_configured? %} volume-pricing--sale-badge{% endif -%}
  {%- if product.price_varies == false and product.compare_at_price_varies %} price--no-compare{% endif -%}
  {%- if show_badges %} price--show-badge{% endif -%}
"
```

- **Dynamic classes**: Price wrapper classes change based on:
    - Custom class (`price_class` parameter)
    - Sold out state
    - Sale state
    - Volume pricing state
    - Price variation state
    - Badge display state

---

## Markup Structure

```liquid
<div class="price [dynamic classes]">
  <div class="price__container">
    <div class="price__regular">
      <!-- Regular price display -->
    </div>
    <div class="price__sale">
      <!-- Sale price display -->
    </div>
    <small class="unit-price">
      <!-- Unit price display -->
    </small>
  </div>
  {%- if show_badges -%}
    <!-- Sale and Sold Out badges -->
  {%- endif -%}
</div>
```

- **Two price displays**: `price__regular` and `price__sale` - CSS controls which is visible.
- **Unit price**: Displayed in `<small>` element when unit pricing available.
- **Badges**: Optional sale and sold-out badges.

### Regular Price Display

```liquid
<div class="price__regular">
  {%- if product.quantity_price_breaks_configured? -%}
    <!-- Volume pricing range -->
  {%- else -%}
    <!-- Standard price -->
  {%- endif -%}
</div>
```

- **Volume pricing**: Shows price range when quantity breaks configured.
- **Standard pricing**: Shows single price otherwise.

### Sale Price Display

```liquid
<div class="price__sale">
  {%- unless product.price_varies == false and product.compare_at_price_varies %}
    <span>
      <s class="price-item price-item--regular">
        {{ compare_at_price | money }}
      </s>
    </span>
  {%- endunless -%}
  <span class="price-item price-item--sale price-item--last">
    {{ money_price }}
  </span>
</div>
```

- **Compare-at price**: Strikethrough price shown when on sale.
- **Sale price**: Current sale price displayed.
- **Conditional compare-at**: Compare-at price hidden in certain variation scenarios.

### Unit Price Display

```liquid
<small class="unit-price caption{% if product.selected_or_first_available_variant.unit_price_measurement == nil %} hidden{% endif %}">
  <span class="visually-hidden">{{ 'products.product.price.unit_price' | t }}</span>
  <span class="price-item price-item--last">
    <span>{{- product.selected_or_first_available_variant.unit_price | money -}}</span>
    <span aria-hidden="true">/</span>
    <span class="visually-hidden">&nbsp;{{ 'accessibility.unit_price_separator' | t }}&nbsp;</span>
    <span>
      {%- if product.selected_or_first_available_variant.unit_price_measurement.reference_value != 1 -%}
        {{- product.selected_or_first_available_variant.unit_price_measurement.reference_value -}}
      {%- endif -%}
      {{ product.selected_or_first_available_variant.unit_price_measurement.reference_unit }}
    </span>
  </span>
</small>
```

- **Conditional display**: Hidden when unit pricing not available.
- **Accessible format**: Includes visually hidden labels and separator.
- **Reference value**: Shows measurement value if not 1 (e.g., "100" in "100ml").

### Badges

```liquid
{%- if show_badges -%}
  <span class="badge price__badge-sale">
    {{ 'products.product.on_sale' | t }}
  </span>
  <span class="badge price__badge-sold-out">
    {{ 'products.product.sold_out' | t }}
  </span>
{%- endif -%}
```

- **Sale badge**: Shows "On Sale" text.
- **Sold out badge**: Shows "Sold Out" text.
- **CSS control**: CSS controls which badge is visible based on state.

---

## Behavior

- **Price calculation**: Calculates prices based on product or variant (controlled by `use_variant`).
- **Currency formatting**: Formats prices using Shopify money filters.
- **Currency code**: Includes currency code when `settings.currency_code_enabled` is true.
- **Price variation**: Handles products with varying prices across variants.
- **Volume pricing**: Displays price range for quantity-based pricing.
- **Sale detection**: Detects sale state by comparing price to compare-at price.
- **Badge visibility**: CSS controls badge visibility based on sale/sold-out state.
- **Accessibility**: Includes visually hidden labels for screen readers.

---

## Usage Example

Basic usage:

```liquid
{% render 'component-product-price', product: product %}
```

With variant pricing:

```liquid
{% render 'component-product-price',
  product: product,
  use_variant: true
%}
```

With badges:

```liquid
{% render 'component-product-price',
  product: product,
  show_badges: true
%}
```

With custom class:

```liquid
{% render 'component-product-price',
  product: product,
  price_class: 'product-card__price'
%}
```

Typically used in:
- Product pages (`sections/product.liquid`)
- Product cards (`snippets/component-product-card.liquid`)
- Collection pages
- Search results
- Any component displaying product pricing

---

## Implementation Notes

1. **Target selection**: Component selects pricing target based on parameters:
    - `use_variant`: Uses `product.selected_or_first_available_variant`
    - `placeholder`: Uses `null` (renders placeholder)
    - Otherwise: Uses `product` object

2. **Price calculation**: Prices calculated from target object:
    - `compare_at_price`: From target's compare-at price
    - `price`: From target's price (defaults to 1999 if null)
    - `price_min`/`price_max`: From product's price range
    - `available`: From target's availability (defaults to false)

3. **Currency formatting**: Prices formatted using:
    - `money`: Standard money format
    - `money_with_currency`: Includes currency code (when enabled)
    - `money_without_currency`: Currency code only (for structured data)

4. **Currency code setting**: Checks `settings.currency_code_enabled` to determine format.

5. **Price variation handling**: When `target == product` and `product.price_varies`, uses translation with "from" prefix.

6. **Volume pricing**: Detects `product.quantity_price_breaks_configured?` to show price range instead of single price.

7. **Compare-at price display**: Compare-at price shown when:
    - `show_compare_at_price` is true
    - `compare_at_price` exists
    - Not in certain variation scenarios

8. **Price display logic**: Two price divs (`price__regular` and `price__sale`) - CSS controls visibility based on sale state.

9. **Sale detection**: Sale detected when `compare_at_price > price`.

10. **CSS class system**: Dynamic classes applied based on:
    - `price--sold-out`: When product unavailable
    - `price--on-sale`: When on sale (non-volume pricing)
    - `volume-pricing--sale-badge`: When on sale with volume pricing
    - `price--no-compare`: When price doesn't vary but compare-at does
    - `price--show-badge`: When badges enabled

11. **Accessibility features**:
    - `visually-hidden` labels for price types
    - `visually-hidden` separator for unit price
    - `aria-hidden="true"` on decorative separator
    - Semantic HTML structure

12. **Translation keys**: Uses translation keys from `locales/en.default.json`:
    - `products.product.price.regular_price`
    - `products.product.price.sale_price`
    - `products.product.price.unit_price`
    - `products.product.price.from_price_html`
    - `products.product.volume_pricing.price_range`
    - `products.product.on_sale`
    - `products.product.sold_out`
    - `accessibility.unit_price_separator`

13. **Unit price calculation**: Unit price calculated from variant's `unit_price` and `unit_price_measurement`.

14. **Unit price display**: Unit price hidden when `unit_price_measurement == nil`.

15. **Reference value**: Unit price reference value only shown if not 1 (e.g., "100" in "$1.00 / 100ml").

16. **Badge display**: Badges only render when `show_badges` is true, but CSS controls which is visible.

17. **Placeholder support**: Component can render placeholder pricing when `placeholder` is true and `target` is null.

18. **Price item classes**: Price elements use classes:
    - `price-item`: Base price item class
    - `price-item--regular`: Regular/compare-at price
    - `price-item--sale`: Sale price
    - `price-item--last`: Last price item in group

19. **Strikethrough price**: Compare-at price uses `<s>` tag for strikethrough styling.

20. **Conditional rendering**: Component only renders when `target != null` or `placeholder != null`.

21. **Price range translation**: Volume pricing uses translation with `minimum` and `maximum` variables.

22. **From price translation**: Varying prices use translation with `price` variable for "from" prefix.

23. **Currency code conditional**: Currency code included when `settings.currency_code_enabled` is true.

24. **Price variation scenarios**: Component handles complex scenarios:
    - Price varies, compare-at varies
    - Price doesn't vary, compare-at varies
    - Price varies, compare-at doesn't vary
    - Neither varies

25. **Volume pricing compare-at**: Compare-at price shown in volume pricing when `show_compare_at_price` is true.

26. **No compare-at in variations**: Compare-at price hidden when `product.price_varies == false and product.compare_at_price_varies`.

27. **Unit price measurement**: Unit price uses variant's `unit_price_measurement` for reference value and unit.

28. **Badge CSS control**: Badges always rendered but CSS controls visibility based on sale/sold-out state.

29. **Sold out class**: `price--sold-out` class applied when `available == false`.

30. **Sale class logic**: Sale class depends on volume pricing configuration:
    - `price--on-sale`: When not volume pricing
    - `volume-pricing--sale-badge`: When volume pricing

31. **Price container**: All price displays wrapped in `price__container` div.

32. **Regular price display**: Regular price shown when not on sale or in volume pricing mode.

33. **Sale price display**: Sale price shown when on sale (compare-at > price).

34. **Unit price positioning**: Unit price displayed after regular/sale prices in `<small>` element.

35. **Badge positioning**: Badges displayed after price container.

36. **Price formatting**: All prices formatted using Shopify money filters for proper currency display.

37. **Default price**: Price defaults to 1999 (in cents) if target price is null.

38. **Default availability**: Availability defaults to false if target availability is null.

39. **Money variable assignment**: Prices converted to money format early for reuse.

40. **Price min/max**: Product price min/max used for volume pricing range.

41. **Target comparison**: Component compares `target == product` to determine if using product-level pricing.

42. **Price varies check**: Checks `product.price_varies` to determine if prices differ across variants.

43. **Compare-at varies check**: Checks `product.compare_at_price_varies` for compare-at price variation.

44. **Quantity breaks check**: Checks `product.quantity_price_breaks_configured?` for volume pricing.

45. **Unit price measurement check**: Checks `unit_price_measurement == nil` to hide unit price.

46. **Reference value check**: Only shows reference value if not 1.

47. **Currency code setting**: Checks `settings.currency_code_enabled` for currency display.

48. **Translation interpolation**: Uses translation variables for dynamic content:
    - `from_price_html`: `price` variable
    - `volume_pricing.price_range`: `minimum`, `maximum` variables

49. **Accessibility labels**: All price types have visually hidden labels for screen readers.

50. **Semantic HTML**: Uses semantic elements (`<s>` for strikethrough, `<small>` for unit price).

