---
description: Snippet development standards and best practices guide
paths:
  - "snippets/**/*.liquid"
---

# Snippet Development Standards

## Snippet Documentation

Every snippet has a `{% doc %}` block. **The type comes before the name, in
braces, and a dash separates the description:** `@param {type} name - description`,
with an optional param's name in square brackets. That is the form Shopify's
`ValidDocParamTypes` validates; the JSDoc order `@param name {Type}` is
silently skipped, so a snippet documented that way has no validated coverage.

```liquid
{% doc %}
  Product Card Component

  Renders a product card with customizable options.

  @param {product} product - Product object
  @param {boolean} [show_vendor] - Display vendor name (default: false)
  @param {string} [image_ratio] - Image aspect ratio (default: 'adapt')
  @param {string} [card_class] - Additional CSS classes

  @example
    {% render 'component-product-card',
       product: product,
       show_vendor: true,
       image_ratio: 'square'
    %}
{% enddoc %}
```

## Parameter Handling

Default every optional parameter and return early when a required one is missing:

```liquid
{% liquid
  assign product = product | default: empty
  assign show_vendor = show_vendor | default: false
  assign image_ratio = image_ratio | default: 'adapt'
  assign card_class = card_class | default: ''

  unless product != empty
    echo '<!-- Error: product parameter required for component-product-card -->'
    break
  endunless
%}
```

## Common Snippet Patterns

**Icon:**
```liquid
{% doc %}
  @param {string} icon - Icon name
  @param {string} [size] - Icon size class (default: 'icon--medium')
{% enddoc %}

{% liquid
  assign size = size | default: 'icon--medium'

  unless icon != blank
    break
  endunless
%}

<svg class="icon {{ size }}" aria-hidden="true" focusable="false">
  <use href="#icon-{{ icon }}"></use>
</svg>
```

**Price:**
```liquid
{% doc %}
  @param {product} product - Product object
  @param {boolean} [show_compare_at] - Show compare at price (default: true)
{% enddoc %}

{% liquid
  assign show_compare_at = show_compare_at | default: true
%}

<div class="price">
  <div class="price__regular">{{ product.price | money }}</div>

  {% if show_compare_at and product.compare_at_price > product.price %}
    <div class="price__compare-at"><s>{{ product.compare_at_price | money }}</s></div>
  {% endif %}
</div>
```

## Testing Patterns

List the cases the snippet must survive in a comment:

```liquid
{% comment %}
  Test cases: product without image, with compare_at_price, out of stock
{% endcomment %}
```

See [snippet-example.liquid](examples/snippet-example.liquid) for a full worked example.
