---
description: The CSS decisions you make while writing markup — BEM class names, custom-property namespacing, and passing section/block settings through inline custom properties
paths:
  - "**/*.liquid"
  - "**/*.css"
---

# CSS in Markup

Split out of `css-standards.md`. This file holds the CSS decisions you make
**while writing markup** — the class names you type into HTML and the custom
properties you set on a `style` attribute. `css-standards.md` holds the rest
(specificity, nesting, media queries, logical properties, layout, performance)
and is scoped to `**/*.css`, because in this theme new CSS goes in a `.css`
file loaded with `stylesheet_tag`, not in the Liquid.

> **Writing CSS inside a `.liquid` file?** Then `css-standards.md` applies too
> and will not have been injected — open it. Note first that `sections.md`
> tells you not to: `{% stylesheet %}` is banned in new sections, and Base is
> 38 `stylesheet_tag` to 4 `{% stylesheet %}`.

## Namespace Your CSS Variables

Namespace your variables to avoid collisions unless you explicitly want them to bleed through to other components.

✅ Do this:

```css
.component {
  --component-padding: ...;
  --component-aspect-ratio: ...;
}
```

❌ Don't do this:

```css
.component {
  --padding: ...;
  --aspect-ratio: ...;
}
```

## Scoping CSS to Instances of Sections and Blocks

Reset CSS variable values inline on a `style` attribute with a section/block settings. This has a couple benefits:

- Less CSS in Liquid which allows us to use the `{% stylesheet %}` tag for all CSS.
- Reduces redundancy in CSS selectors and number of selectors in the HTML, i.e. `.selector--{{ block.id }}` pattern.

✅ Do this:

```html
<section
  style="
    --background-color: {{ settings.background_color }};
    --padding: {{ settings.padding }}px;
  "
>
  ...
</section>

<button style="--button-color: {{ settings.button_color }};">...</button>
```

❌ Don't do this:

```html
{% style %} .selector--{{ block.id }} { --button-color: {{ settings.button_color }}; } {% endstyle %}

<button class="selector--{{ block.id }}">...</button>
```

## BEM Naming Convention

Use the @BEM CSS convention for class names.

BEM TL;DR:

- **Block**: Component name (`.product-card`)
- **Element**: Block + element (`.product-card__title`)
- **Modifier**: Block/element + modifier (`.product-card--featured`)
- **Use dashes** to separate words in names

```css
/* Good BEM structure */
.product-card {
}
.product-card__image {
}
.product-card__title {
}
.product-card__price {
}
.product-card--featured {
}
.product-card__title--large {
}
```

```css
.block {
  ...;
}
.block--modifier {
  ...;
}
.block__element {
  ...;
}
.block__multi-word-element {
  ...;
}
.block__element--modifier {
  ...;
}
.block__element--multi-word-modifier {
  ...;
}
```

Dashes are used to separate words in blocks, elements, and modifiers.

Exception: We also use global @utility classes that can be applied to block and and elements without following BEM naming convention.

### Naming a "Block" (component)

The root "block" namespace must wrap any elements derived from it.

✅ Do this:

```html
<div class="my-component">
  <div class="my-component__wrapper"></div>
</div>
```

❌ Not this:

`.my-component__wrapper` is used as a parent to `.my-component`.

```html
<div class="my-component__wrapper my-component--page-width">
  <div class="my-component"></div>
</div>
```

### Naming an "Element" (child)

There should only be a _single_ "element" in a classname. Only the root "block" name needs to be included in child classnames. If additional naming specificity is necessary, use a "-" to seperate words or consider starting a new BEM scope altogether when an element could make sense as a standalone entity.

✅ Do this:

```html
<div class="my-component my-component--full-width">
  <div class="my-component__wrapper">
    <button class="my-component__button">
      <span class="my-component__button-label">My button</span>
    </button>
  </div>
</div>
```

✅ Or this:

Started new scope with `.button-component`.

```html
<div class="my-component my-component--full-width">
  <div class="my-component__wrapper">
    <button class="button-component">
      <span class="button-component__label">My button</span>
    </button>
  </div>
</div>
```

❌ Not this:

Multiple element names are used (`__wrapper__button__label`).

```html
<div class="my-component my-component--full-width">
  <div class="my-component__wrapper">
    <button class="my-component__wrapper__button">
      <span class="my-component__wrapper__button__label">My button</span>
    </button>
  </div>
</div>
```

### Naming a "Modifier" (variant)

Any "modifier" classname should always use a "--" and should always correspond to an existing block and element namespace. Never use a modifier class on an element that doesn't also have a base classname.

✅ Do this:

The `.button` class is the base classname and modified by `--secondary`.

```html
<button class="button button--secondary"></button>
```

❌ Not this:

The `.button` and `.button-secondary` classes are both named as _exclusive_ components and should not used together.

```html
<button class="button button-secondary"></button>
```

❌ Or this:

Modifer class is used without corresponding base classname.

```html
<button class="button--secondary"></button>
```

Also consider keeping modifiers at the highest element that makes sense. This makes the component more extensible and resilient as styling needs are changed or added in the future.

✅ Do this:

```html
<div class="my-component my-component--size-large my-component--page-width">
  <div class="my-component__wrapper"></div>
</div>
```

### Utility Classes

Utility classes are intended to act as global overrides for a single styling decision, e.g. alignment, show/hide, etc. BEM conventions are not followed, there is no hierarchy in utility classes and utility classes do not assume they are used with any particular block or element.

Name multi-word utility classes with hyphens `-`. Append any viewport specifications at the **end**, e.g. `hidden-mobile`.

✅ This is fine:

```css
.align-left {
  text-align: left;
}
```

```html
<div class="my-component align-left">
  <p class="my-component__text"></p>
</div>
```

