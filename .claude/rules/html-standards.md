---
description: Modern HTML standards for writing .liquid markup
paths:
  - "**/*.liquid"
---

# Modern HTML Standards

Everything a shopper needs to buy must be "Baseline widely available".
Progressive enhancement may use "Baseline 2024", for non-blocking UX only.

## Native Interactive Elements

**Expandable content:** `<details>` and `<summary>`, not a JavaScript toggle —
FAQs, product details, filters. For an animated accordion copy the `<details>`
in `snippets/component-filters-sidebar.liquid` and `sections/product.liquid`.
Chrome slots a `<details>` element's content under `::details-content`, which
the theme's `*` box-sizing reset cannot match, so a declared height on a row
inside `<details>` silently gains its padding: re-assert `box-sizing: border-box`
on the `<details>` root and on the `<summary>`.

**Modals:** `<dialog>`, not a custom overlay. `assets/component-product-media-modal.js`
is the only `showModal()` in the theme and the pattern to copy.

**Tooltips and menus:** the `popover` attribute.

**Forms:** `<search>` around a search form; `<output>` for a calculated result;
the specific input type (`email`, `tel`, `url`, `search`, `number`, `date`);
`<fieldset>`/`<legend>` for a group; native validation attributes (`required`,
`pattern`, `min`, `max`, `step`, `minlength`, `maxlength`) and `autocomplete`
on personal fields rather than JavaScript validation.

## Progressive Enhancement

1. Semantic HTML that works without JavaScript
2. CSS for visual enhancement
3. JavaScript for advanced interaction and accessibility
4. Never break core functionality for older browsers

## Accessibility

The standard is `accessibility.md`. In markup: `tabindex="0"` on a custom
interactive element and never a positive value; focus trapped inside a modal;
`aria-expanded` on collapsible content; `role` only where native semantics do
not already say it (the attribute is `role`; `aria-role` does not exist);
motion disabled under `@media (prefers-reduced-motion: reduce)`.

## Mark what comes from the store: `data-verify-mask`

Live values — product titles, prices, review counts, store images — never
match a design mock, so `verify-against-reference` masks them before it diffs.
It finds them by one attribute, placed on the element whose box should be
ignored, not on a wrapper:

```liquid
<span class="product-card__price" data-verify-mask>{{ card_product.price | money }}</span>
```

It has no runtime effect, and it documents that Figma is design-only.

## ID Naming Convention

`CamelCase`, suffixed with the section or block id — the only values
guaranteed unique on a page:

```html
<section id="FeaturedCollection-{{ section.id }}">
<div id="ProductCard-{{ block.id }}">
<dialog id="ProductModal-{{ product.id }}-{{ section.id }}">
```

## Examples

**Expandable FAQ:**
```html
<details class="faq">
  <summary class="faq__question">{{ 'faq.shipping_question' | t }}</summary>
  <div class="faq__answer">{{ 'faq.shipping_answer' | t }}</div>
</details>
```

**Modal dialog:**
```html
<button type="button" class="product__quick-view" data-dialog="ProductModal-{{ product.id }}-{{ section.id }}">
  {{ 'products.quick_view' | t }}
</button>

<dialog id="ProductModal-{{ product.id }}-{{ section.id }}" class="product-modal">
  <form method="dialog">
    <button type="submit" class="modal__close">{{ 'general.close' | t }}</button>
  </form>
  <div class="modal__content">
    {% render 'component-product-details', product: product %}
  </div>
</dialog>
```

**Popover menu:**
```html
<button type="button" popovertarget="CartMenu-{{ section.id }}" class="header__cart">
  {{ 'cart.title' | t }} ({{ cart.item_count }})
</button>

<div id="CartMenu-{{ section.id }}" popover class="cart-popover">
  {% render 'component-cart-drawer' %}
</div>
```

**Search form:**
```html
<search class="header__search">
  <form action="{{ routes.search_url }}" method="get">
    <input
      type="search"
      name="q"
      aria-label="{{ 'general.search' | t }}"
      placeholder="{{ 'general.search_placeholder' | t }}"
      value="{{ search.terms | escape }}"
    >
    <button type="submit">{{ 'general.search' | t }}</button>
  </form>
</search>
```

**Product card** — settings come in as custom properties; responsiveness is a
`min-width` media query in the stylesheet, never a container query:

```html
<div class="product-card" style="--product-card-gap: {{ settings.gap }}px;">
  <div class="product-card__media">
    {{ product.featured_image | image_url: width: 800 | image_tag }}
  </div>
  <div class="product-card__info">
    <h3>{{ product.title | escape }}</h3>
    <output class="product-card__price" data-verify-mask>{{ product.price | money }}</output>
  </div>
</div>
```

## Avoid These Patterns

Custom JavaScript for show/hide toggles, accordions (`<details>`), modals
(`<dialog>`), tooltips and dropdown menus (`popover`, `<select>`), or form
validation (native attributes).
