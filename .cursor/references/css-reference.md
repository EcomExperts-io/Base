# CSS Reference

Long-form CSS guidance extracted from `.cursor/rules/css-standards.mdc`. The slim rule keeps
the non-negotiable constraints; this file holds the full guides, worked examples, and
reference material. Load it with the Read tool when you need depth beyond the rule.

---

## CSS Variables — Detailed Examples

### Global Variables

Global variables should be scoped to the `:root` selector in `snippets/theme-styles-variables.liquid`.

**Example of global variables**

```css
/* in snippets/theme-styles-variables.liquid */
:root {
    --page-width: 1400px;
     --font-body--family: {{ settings.type_body_font.family }}, {{ settings.type_body_font.fallback_families }}; /* Referencing a theme setting */
     --font-{{ preset_name_dash }}--family: {{ settings[preset_font] | prepend: 'var(--font-' | append: '--family)' }}; /* Using Liquid to set a variable */
}
```

### Scoped Variables

Be sure to scope your CSS variables to the component they are being used in, if they are not meant to be global. Scoped variables can reference global variables.

**Example of scoped variables**

```css
/* in assets/facets.css */
.facets {
  --drawer-padding: var(--padding-md); /* Referencing a global variable */
  --facets-upper-z-index: 3;
  --facets-open-z-index: 4;

  --facets-clear-shadow: 0px -4px 14px 0px rgb(var(--color-foreground-rgb) / var(--opacity-10)); /* Referencing a Color Scheme variable */
}
```

### Semantic Color Variables

Use semantic naming for better maintainability:

```css
:root {
  /* Base colors */
  --color-primary: {{ settings.colors_accent_1 }};
  --color-secondary: {{ settings.colors_accent_2 }};

  /* Semantic colors */
  --color-text-primary: rgb(var(--color-foreground));
  --color-text-secondary: rgb(var(--color-foreground) / 0.75);
  --color-text-disabled: rgb(var(--color-foreground) / 0.38);

  /* Interactive states */
  --color-interactive-default: rgb(var(--color-accent));
  /* color-mix isn't supported in earlier version of iOS <16.2 so limit its usage to progressive enhancement */
  --color-interactive-hover: color-mix(in srgb, rgb(var(--color-accent)) 90%, black);
  --color-interactive-pressed: color-mix(in srgb, rgb(var(--color-accent)) 80%, black);
  --color-interactive-disabled: rgb(var(--color-accent) / 0.38);
}
```

### Design Token System

Establish consistent spacing and typography scales:

```css
:root {
  /* Spacing scale */
  --space-3xs: 0.25rem; /* 4px */
  --space-2xs: 0.5rem; /* 8px */
  --space-xs: 0.75rem; /* 12px */
  --space-sm: 1rem; /* 16px */
  --space-md: 1.5rem; /* 24px */
  --space-lg: 2rem; /* 32px */
  --space-xl: 3rem; /* 48px */
  --space-2xl: 4rem; /* 64px */
  --space-3xl: 6rem; /* 96px */

  /* Typography scale */
  --font-size-xs: 0.75rem; /* 12px */
  --font-size-sm: 0.875rem; /* 14px */
  --font-size-base: 1rem; /* 16px */
  --font-size-lg: 1.125rem; /* 18px */
  --font-size-xl: 1.25rem; /* 20px */
  --font-size-2xl: 1.5rem; /* 24px */
  --font-size-3xl: 1.875rem; /* 30px */
}
```

### Redundancy

Use variables to reduce property assignment redundancy.

```css
/* Do this */
.button {
  background: rgb(var(--button-color) / 0.75);
}

.button--secondary {
  --button-color: var(--secondary-color);
}

/* Not this */
.button {
  background: rgb(var(--primary-color) / 0.75);
}

.button--secondary {
  background: rgb(var(--secondary-color) / 0.75);
}
```

---

## BEM Naming Convention — Full Guide

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

---

## Modern CSS Features

### Container Queries

Use container queries for truly responsive components:

```css
.product-grid {
  container-type: inline-size;
}

@container (min-width: 400px) {
  .product-card {
    display: grid;
    grid-template-columns: 1fr 1fr;
  }
}
```

### CSS Functions

Leverage modern CSS functions for better responsiveness:

```css
.component {
  /* Fluid spacing */
  padding: clamp(1rem, 4vw, 3rem);

  /* Intrinsic sizing */
  width: min(100%, 800px);

  /* Dynamic colors */
  /* color-mix isn't supported in earlier version of iOS <16.2 so limit its usage */
  background: color-mix(in srgb, rgb(var(--color-primary)) 90%, white);
}
```

### Cascade Layers

For better CSS organization in complex themes:

```css
@layer reset, base, components, utilities, overrides;

@layer components {
  .button {
    /* Component styles here won't conflict with utilities */
  }
}
```

### View Transitions

```css
@view-transition {
  navigation: auto;
}

.page-content {
  view-transition-name: main-content;
}
```

---

## Media Queries — Advanced

### Context-Aware Queries

Use feature queries alongside media queries:

```css
@supports (display: grid) {
  .product-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  }
}

@supports not (display: grid) {
  .product-grid {
    display: flex;
    flex-wrap: wrap;
  }
}
```

### Print Styles

Always consider print stylesheets:

```css
@media print {
  .no-print {
    display: none !important;
  }

  a[href^='http']:after {
    content: ' (' attr(href) ')';
  }
}
```

---

## Logical Properties

Where appropriate, use logical properties to have baseline support for Right-to-Left (RTL) languages.
Focusing on these properties:

- padding
- margin
- border
- text-align
- top, bottom, left, right

✅ Do this:

```css
.element {
  padding-inline: 2rem;
  padding-block: 1rem;
  margin-inline: auto;
  margin-block: 0;
  border-inline-end: 1rem solid var(--color-background);
  text-align: start;
  inset: 0;
}
```

❌ Not this:

```css
.element {
  padding: 1rem 2rem;
  margin: 0 auto;
  border-bottom: 1rem solid var(--color-background);
  text-align: left;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
}
```

---

## Layout Patterns

### CSS Grid for Layouts

```css
.section-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--spacing-lg);
}
```

### Flexbox for Components

```css
.product-card {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}
```

### Aspect Ratio for Media

```css
.product-card__image {
  aspect-ratio: 4 / 3;
  object-fit: cover;
}
```

---

## Fancy Selectors

### Using `:is()`

When giving the same styles to multiple selectors, use a comma separated list.

✅ Do this:

```css
.facets__label,
.facets__clear-all,
.clear-filter {
  ...;
}
```

❌ Not this:

```css
:is(.facets__label, .facets__clear-all, .clear-filter) {
  ...;
}
```

However, if you are giving the same styles to a parent-child relationship with different selectors, you may use `:is()`.

✅ Do this:

```css
.parent:is(.child-1, .child-2) {
  ...;
}
```

❌ Not this:

```css
.parent .child-1,
.parent .child-2 {
  ...;
}
```

✅ Do this:

```css
:is(.parent, .parent-2) .child {
  ...;
}
```

❌ Not this:

```css
.parent .child,
.parent-2 .child {
  ...;
}
```

Try to keep the same specificity for all selectors within a single `:is()` to avoid increasing the overall specificity of the selector unintentionally.

---

## Accessibility

### Motion and Animation

- Always respect user motion preferences
- Provide fallbacks for users who prefer reduced motion

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

### Focus Management

- Ensure all interactive elements have visible focus indicators
- Use `:focus-visible` for better UX

```css
.button:focus-visible {
  outline: 2px solid rgb(var(--color-focus));
  outline-offset: 2px;
}
```

### Color and Contrast

- Maintain WCAG AA contrast ratios (4.5:1 for normal text, 3:1 for large text)
- Test with high contrast mode
- Never rely solely on color to convey information

```css
@media (prefers-color-scheme: dark) {
  :root {
    /* Dark theme variables */
  }
}
```

---

## Performance Considerations

### Animation Performance

- Use `transform` and `opacity` for animations
- Avoid animating layout properties (`width`, `height`, `margin`, `padding`)
- Use `will-change` sparingly and remove after animation

```css
.product-card {
  transition: transform 0.2s ease;
}

.product-card:hover {
  transform: translateY(-2px); /* Better than animating top/margin */
}

/* Only use will-change during animation */
.product-card:hover {
  will-change: transform;
}

.product-card:not(:hover) {
  will-change: auto;
}
```

### Layout Performance

- Use `contain` property for better rendering performance
- Prefer CSS Grid and Flexbox over complex positioning

```css
.product-grid {
  contain: layout style paint;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
}
```

---

## CSS Organization

### CSS Property Order

Maintain consistent property order within declarations:

```css
.component {
  /* 1. Layout & Positioning */
  position: relative;
  display: flex;
  flex-direction: column;

  /* 2. Box Model */
  width: 100%;
  margin: 0;
  padding: var(--space-md);
  border: 1px solid rgb(var(--color-border));

  /* 3. Typography */
  font-family: var(--font-body-family);
  font-size: var(--font-size-base);

  /* 4. Visual */
  background: rgb(var(--color-surface));
  color: rgb(var(--color-text));

  /* 5. Animation & Transforms */
  transition: transform 0.2s ease;
}
```

---

## Error Prevention

### Common Pitfalls

- **Never** use `position: fixed` without considering mobile keyboards
- **Always** test with zoom up to 200%
- **Avoid** magic numbers - use variables or calc() instead
- **Remember** that `vh` units can be problematic on mobile, use `dvh` to mitage this

### Defensive CSS

Write CSS that gracefully handles edge cases:

```css
.product-card {
  /* Prevent content overflow */
  word-wrap: break-word;
  overflow-wrap: break-word;

  /* Handle long content */
  min-width: 0; /* Allows flex items to shrink below content size */

  /* Prevent layout shift */
  aspect-ratio: 1 / 1;

  /* Fallback for missing images */
  background: rgb(var(--color-surface-secondary));
}
```

### Browser Support

- Test in browsers used by your audience
- Provide fallbacks for newer CSS features
- Use progressive enhancement approach

---

## CSS Documentation

### Commenting Standards

Use consistent commenting for better maintainability:

```css
/* =============================================================================
   Component Name
   ============================================================================= */

/**
 * Brief component description
 *
 * @example
 * <div class="component component--modifier">
 *   <div class="component__element">Content</div>
 * </div>
 */
.component {
  /* Implementation */
}

/* Component modifiers
   ========================================================================== */

/**
 * Modifier description
 */
.component--modifier {
  /* Modifier styles */
}

/* Component elements
   ========================================================================== */

/**
 * Element description
 */
.component__element {
  /* Element styles */
}
```

---

## Example Component Structure

```liquid
{% stylesheet %}
  .featured-collection {
    --section-padding: {{ section.settings.padding | default: 60 }}px;
    --bg-color: {{ section.settings.background_color | default: '#ffffff' }};
    --text-color: {{ section.settings.text_color | default: '#000000' }};

    padding: var(--section-padding) 0;
    background-color: var(--bg-color);
    color: var(--text-color);
    container-type: inline-size;
  }

  .featured-collection__grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: var(--spacing-md);
  }

  @container (min-width: 768px) {
    .featured-collection__grid {
      grid-template-columns: repeat({{ section.settings.columns | default: 4 }}, 1fr);
    }
  }

  @media (prefers-reduced-motion: reduce) {
    .featured-collection * {
      transition: none !important;
    }
  }
{% endstylesheet %}
```
