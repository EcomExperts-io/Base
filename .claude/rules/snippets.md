---
description: Snippet development standards and best practices guide
paths:
  - "snippets/**/*.liquid"
---

# Snippet Development Standards

## Snippet Documentation

Every snippet must include a `{% doc %}` block using LiquidDoc.

**The type comes before the name, in braces, and a dash separates the
description:** `@param {type} name - description`. Optional params wrap the name
in square brackets. Every one of this theme's 45 declarations uses this form, and it is
what Shopify's `ValidDocParamTypes` check validates — the JSDoc-style
`@param name {Type} description` reads fine to a human and is silently skipped by
the checker, so a snippet documented that way has no validated parameter coverage
at all.

```liquid
{% doc %}
  Product Card Component

  Renders a product card with customizable options.

  @param {product} product - Product object
  @param {boolean} [show_vendor] - Display vendor name (default: false)
  @param {boolean} [show_quick_add] - Show quick add button (default: false)
  @param {string} [image_ratio] - Image aspect ratio (default: 'adapt')
  @param {boolean} [lazy_load] - Enable lazy loading (default: true)
  @param {string} [card_class] - Additional CSS classes

  @example
    {% render 'product-card',
       product: product,
       show_vendor: true,
       image_ratio: 'square'
    %}
{% enddoc %}
```

## Parameter Handling

Always provide defaults and validate parameters:

```liquid
{% liquid
  # Parameter validation and defaults
  assign product = product | default: empty
  assign show_vendor = show_vendor | default: false
  assign show_quick_add = show_quick_add | default: false
  assign image_ratio = image_ratio | default: 'adapt'
  assign lazy_load = lazy_load | default: true
  assign card_class = card_class | default: ''

  # Early return if required parameters missing
  unless product != empty
    echo '<!-- Error: product parameter required for product-card snippet -->'
    break
  endunless
%}
```

## Common Snippet Patterns

**Icon Snippet:**
```liquid
{% doc %}
  @param {string} icon - Icon name
  @param {string} [size] - Icon size class (default: 'icon--medium')
  @param {string} [class] - Additional classes
{% enddoc %}

{% liquid
  assign icon = icon | default: ''
  assign size = size | default: 'icon--medium'
  assign class = class | default: ''

  unless icon != blank
    break
  endunless
%}

<svg class="icon {{ size }} {{ class }}" aria-hidden="true" focusable="false">
  <use href="#icon-{{ icon }}"></use>
</svg>
```

**Price Snippet:**
```liquid
{% doc %}
  @param {product} product - Product object
  @param {boolean} [show_compare_at] - Show compare at price (default: true)
  @param {boolean} [show_unit_price] - Show unit price (default: false)
{% enddoc %}

{% liquid
  assign show_compare_at = show_compare_at | default: true
  assign show_unit_price = show_unit_price | default: false
%}

<div class="price">
  <div class="price__regular">
    {{ product.price | money }}
  </div>

  {% if show_compare_at and product.compare_at_price > product.price %}
    <div class="price__compare-at">
      <s>{{ product.compare_at_price | money }}</s>
    </div>
  {% endif %}

  {% if show_unit_price and product.selected_or_first_available_variant.unit_price_measurement %}
    <div class="price__unit">
      {{ product.selected_or_first_available_variant.unit_price | money }}/
      {%- if product.selected_or_first_available_variant.unit_price_measurement.reference_value != 1 -%}
        {{ product.selected_or_first_available_variant.unit_price_measurement.reference_value }}
      {%- endif -%}
      {{ product.selected_or_first_available_variant.unit_price_measurement.reference_unit }}
    </div>
  {% endif %}
</div>
```

## Testing Patterns

Include testing scenarios in comments:

```liquid
{% comment %}
  Test cases:
  - Product with variants
  - Product without image
  - Product with compare_at_price
  - Product with unit pricing
  - Out of stock product
{% endcomment %}
```

See [snippet-example.liquid](examples/snippet-example.liquid) for a full worked example.
