---
description: Writing CSS in a .css file — specificity, variables, nesting, media queries, logical properties, layout, performance
paths:
  - "**/*.css"
---

# CSS Standards

Class naming, custom-property namespacing and settings passed through a `style`
attribute are in `css-in-markup.md`. New CSS goes in a `.css` file loaded with
`stylesheet_tag`, never in the Liquid.

## Specificity Rules

- **Never** use IDs as selectors; **avoid** elements as selectors.
- **Avoid** `!important`; if you must, comment why on the same or previous line.
- Aim for `0 1 0` — a single `.class`. Keep parent/child selectors to `0 4 0`
  at most (`.parent:hover .child` is sometimes the only way).
- A selector should be readable at a glance; go easy on `:has`, `:where`, `:nth-child`.

## CSS Variables

- A hardcoded value is set on a variable first, then used: `--touch-target-size: 44px;`.
- **Never** hardcode colours; use the colour-scheme variables.

Global variables live on `:root` in `snippets/css-variables.liquid`:

```css
:root {
  --page-width: 1400px;
  --font-body--family: {{ settings.type_body_font.family }}, {{ settings.type_body_font.fallback_families }};
}
```

Anything not global is scoped to its component, and may reference globals:

```css
.facets {
  --drawer-padding: var(--padding-md);
  --facets-open-z-index: 4;
  --facets-clear-shadow: 0px -4px 14px 0px rgb(var(--color-foreground-rgb) / var(--opacity-10));
}
```

`color-mix()` is unsupported on iOS below 16.2; use it only as progressive enhancement.

### Redundancy

Vary the variable, not the declaration:

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

## Container queries — do not use them

The theme has no `container-type` or `@container`; use the `min-width` media
queries everything else uses. A component that must reflow to a slot of
varying width is raised, not quietly built on a second responsive system.

## CSS Functions

```css
.component {
  padding: clamp(1rem, 4vw, 3rem);
  width: min(100%, 800px);
}
```

## Media Queries

- Mobile first: `min-width` queries only.
- Use `screen` on every media query.
- Breakpoint values: grep `assets/` and match what the theme settled on
  (`sections.md`); do not introduce a new scale.

## CSS Nesting Rules

- Never nest beyond the first level, except media queries and the modifier
  case below.
- `&` only for a direct relationship: states (`&:hover`, `&:focus-visible`)
  and modifiers that affect each other (`.button--integrated { &.button--text }`).

Nest media queries inside the rule, even when there is nothing to override yet:

```css
.header {
  width: 100%;

  @media screen and (min-width: 750px) {
    width: 100px;
  }
}
```

A parent modifier that changes several children may nest them, so the
if-like relationship reads in one place:

```css
.parent--full-screen {
  grid-columns: 1fr;

  .child {
    grid-column: 1;
  }
}
```

That is still one level of nesting.

## Logical Properties

Use logical properties for padding, margin, border, text-align and inset, so
RTL works by default.

✅ Do this:

```css
.element {
  padding-inline: 2rem;
  padding-block: 1rem;
  margin-inline: auto;
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
  border-right: 1rem solid var(--color-background);
  text-align: left;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
}
```

## Using `:is()`

Same styles on several selectors: a comma list, not `:is()`.

```css
/* Do this */
.facets__label,
.facets__clear-all,
.clear-filter {
  ...;
}

/* Not this */
:is(.facets__label, .facets__clear-all, .clear-filter) {
  ...;
}
```

`:is()` is for a shared parent or a shared child:

```css
/* Do this */
.parent:is(.child-1, .child-2) {
  ...;
}

:is(.parent, .parent-2) .child {
  ...;
}

/* Not this */
.parent .child-1,
.parent .child-2 {
  ...;
}
```

Keep every selector inside one `:is()` at the same specificity.

## Accessibility

Motion (position, size, rotation) is disabled under reduced motion; opacity
and colour transitions need no override (`accessibility.md`, section 9):

```css
@media (prefers-reduced-motion: reduce) {
  .product-card {
    transition: none;
  }
}
```

Every interactive element has a visible focus style, on `:focus-visible`:

```css
.button:focus-visible {
  outline: 2px solid rgb(var(--color-focus));
  outline-offset: 2px;
}
```

Contrast and colour-as-the-only-cue are in `accessibility.md`, section 7.

## Performance

- Animate `transform` and `opacity`, never layout properties
  (`width`, `height`, `margin`, `padding`).
- `will-change` only while the animation runs; reset it after.

```css
.product-card {
  transition: transform 0.2s ease;
}

.product-card:hover {
  transform: translateY(-2px);
  will-change: transform;
}

.product-card:not(:hover) {
  will-change: auto;
}
```

## CSS Property Order

```css
.component {
  /* 1. Layout & positioning */
  position: relative;
  display: flex;
  flex-direction: column;

  /* 2. Box model */
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

  /* 5. Animation & transforms */
  transition: transform 0.2s ease;
}
```

## Common Pitfalls

- `position: fixed` meets the mobile keyboard; test it there.
- Test at 200% zoom.
- No magic numbers: a variable or `calc()`.
- `vh` misbehaves on mobile; use `dvh`.

### Defensive CSS

```css
.product-card {
  overflow-wrap: break-word;
  min-width: 0; /* lets a flex item shrink below its content size */
  aspect-ratio: 1 / 1; /* no layout shift while the image loads */
  background: rgb(var(--color-surface-secondary)); /* visible when the image is missing */
}
```

Six more where every computed style reads correct and the page renders wrong
(symptom, cause and fix in `.claude/references/layout-pitfalls.md`):

- Inside a scrolling flex container every child that is not the scroll area
  needs `flex-shrink: 0` — an `aspect-ratio` box most of all.
- `aspect-ratio` on a flex item needs `min-block-size: 0` (`min-inline-size: 0`
  in a row), or the automatic minimum sizes it to the merchant's photo.
- A first or last child's block margin collapses out through a section wrapper
  whose padding setting can be 0. Space the child with padding, not margin.
- A component that sets its own `display` beats the UA's `[hidden]`; declare
  `.x[hidden] { display: none; }` beside it.
- A `font-weight` is only as real as the face `css-variables.liquid` loads;
  `font_modify` emits nothing for a weight the library lacks and the browser
  synthesises. Enumerate `[...document.fonts]` — `document.fonts.check()` lies.
- A span in a second font inside a fixed `line-height` grows the line; give it
  `line-height: 0` (`1` is not enough in desktop Chrome).

No duplicated rule blocks: an edit to the first copy is overridden by the
second. `check-conventions.py` warns on a run of 40+ lines that repeats.

## Commenting

```css
/* =============================================================================
   Component Name
   ============================================================================= */

/**
 * Brief component description
 */
.component {
}

/* Component modifiers
   ========================================================================== */
.component--modifier {
}
```

## Example Component Structure

The section loads its stylesheet with `stylesheet_tag` and passes merchant
settings in as custom properties on the wrapper (`css-in-markup.md`):

```liquid
{{ 'section-featured-collection.css' | asset_url | stylesheet_tag }}

<div
  class="featured-collection color-{{ section.settings.color_scheme }}"
  style="--featured-collection-columns: {{ section.settings.columns | default: 4 }};"
>
  <div class="featured-collection__grid">…</div>
</div>
```

```css
/* assets/section-featured-collection.css */
.featured-collection__grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--spacing-md);

  @media screen and (min-width: 750px) {
    grid-template-columns: repeat(var(--featured-collection-columns), 1fr);
  }
}
```
