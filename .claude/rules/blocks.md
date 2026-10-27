---
description: Development standards and best practices for creating/configuring/styling theme blocks, including static and nested blocks, schema configuration, CSS, and usage examples
paths:
  - "blocks/**/*.liquid"
---

# Theme Blocks Development Standards

Follow [Shopify's theme blocks documentation](https://shopify.dev/docs/storefronts/themes/architecture/blocks/theme-blocks/quick-start?framework=liquid.txt).
Theme blocks nest under sections and other blocks, carry their own settings
and presets, and may be placed statically by the developer. They render once
a [template](templates.md) references them.

## Block Structure

```liquid
{% doc %}
  Block description and usage examples

  @example
  {% content_for 'block', type: 'block-name', id: 'unique-id' %}
{% enddoc %}

<div {{ block.shopify_attributes }} class="block-name">
  {{ block.settings.heading | escape }}
</div>

{% stylesheet %}
  /* BEM, and only CSS exclusive to this block; shared CSS goes in assets/base.css */
{% endstylesheet %}

{% schema %}
{
  "name": "t:names.block_name",
  "settings": [],
  "presets": []
}
{% endschema %}
```

`{{ block.shopify_attributes }}` goes on the root element, and is required for
the theme editor whether or not `"tag": null` removes the wrapper.

## Static Blocks

A static block is placed by the developer with a fixed `id`; it appears in the
editor as a locked block whose settings the merchant may still override, and
can sit beside a dynamic area:

```liquid
{% content_for 'block', type: 'product-gallery', id: 'main-gallery', settings: {
  enable_zoom: true,
  thumbnails_position: "bottom"
} %}

<div class="product-extra-content">
  {% content_for 'blocks' %}
</div>
```

## Nested Blocks

A container block renders its children with `{% content_for 'blocks' %}` and
passes its own settings down as custom properties:

```liquid
<div
  class="group group--{{ block.settings.layout_direction }}"
  style="--gap: {{ block.settings.gap }}px;"
  {{ block.shopify_attributes }}
>
  {% content_for 'blocks' %}
</div>
```

A preset may seed children:

```json
{
  "presets": [
    {
      "name": "t:names.two_column_layout",
      "settings": { "layout_direction": "horizontal" },
      "blocks": [
        { "type": "text" },
        { "type": "text" }
      ]
    }
  ]
}
```

## Schema

Rules in [schemas.md](schemas.md). A section accepts theme blocks with
`{ "type": "@theme" }`, app blocks with `{ "type": "@app" }`, or names the
block types it allows:

```json
{
  "blocks": [
    { "type": "text", "name": "t:names.text" },
    { "type": "image", "name": "t:names.image" }
  ]
}
```

## CSS

Rules in [css-standards.md](css-standards.md) and [css-in-markup.md](css-in-markup.md).
Settings reach the stylesheet as custom properties on the root's `style` attribute:

```liquid
<div
  class="custom-block"
  style="
    --block-padding: {{ block.settings.padding }}px;
    --text-align: {{ block.settings.alignment }};
  "
  {{ block.shopify_attributes }}
>
```

## Content Guards

Test each content setting against `blank` and render nothing when there is
nothing to show:

```liquid
<div class="content-block" {{ block.shopify_attributes }}>
  {% if block.settings.heading != blank %}
    <h3 class="content-block__heading">{{ block.settings.heading | escape }}</h3>
  {% endif %}

  {% if block.settings.image %}
    {{ block.settings.image | image_url: width: 800 | image_tag: alt: block.settings.image.alt | escape }}
  {% endif %}

  {% if block.settings.button_text != blank %}
    <a href="{{ block.settings.button_url }}" class="content-block__button">
      {{ block.settings.button_text | escape }}
    </a>
  {% endif %}
</div>
```

## Examples Referenced

[text.liquid](examples/block-example-text.liquid) - Basic content block
[group.liquid](examples/block-example-group.liquid) - Container with nested blocks
