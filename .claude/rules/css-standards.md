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

Global variables are defined in `snippets/css-variables.liquid`. This is the
complete list; no other global token exists:

| Where | Variables |
|---|---|
| `:root` | `--page-width`, `--page-margin`, `--font-body-family`, `--font-body-style`, `--font-body-weight`, `--font-body-weight-bold`, `--font-body-scale`, `--font-heading-family`, `--font-heading-style`, `--font-heading-weight`, `--font-heading-scale` |
| each `.color-<scheme>` class; the first scheme also on `:root` | `--color-background`, `--color-background-contrast`, `--color-foreground`, `--color-shadow`, `--color-button`, `--color-button-text`, `--color-secondary-button`, `--color-secondary-button-text`, `--color-link`, `--color-badge-foreground`, `--color-badge-background`, `--color-badge-border`, `--gradient-background` |

There is no global spacing, font-size, border, focus or opacity token. A
`var(--name)` that is not in the table must be declared in the same component.

### Colour tokens are comma-separated triplets

Every `--color-*` token holds three comma-separated numbers, for example
`--color-foreground: 18,18,18`. Use exactly these two forms:

```css
.card {
  color: rgb(var(--color-foreground)); /* solid */
  border: 1px solid rgba(var(--color-foreground), 0.2); /* with alpha */
}
```

Never write `rgb(var(--color-foreground) / 0.2)`. The slash form needs
space-separated channels, so with a comma triplet the declaration is invalid
and nothing paints. Never use a `--color-*` token bare
(`color: var(--color-foreground)`); it is not a colour on its own.

### Component variables

Anything not global is declared on its component, prefixed with the component
name, and may reference globals:

```css
.facets {
  --facets-padding: 2rem;
  --facets-open-z-index: 4;
  --facets-clear-shadow: 0 -4px 14px 0 rgba(var(--color-foreground), 0.1);

  padding: var(--facets-padding);
}
```

`color-mix()` is unsupported on iOS below 16.2; use it only as progressive enhancement.

### Redundancy

Vary the variable, not the declaration:

```css
/* Do this */
.button {
  --button-color: var(--color-button);

  background: rgba(var(--button-color), 0.75);
}

.button--secondary {
  --button-color: var(--color-secondary-button);
}

/* Not this */
.button {
  background: rgba(var(--color-button), 0.75);
}

.button--secondary {
  background: rgba(var(--color-secondary-button), 0.75);
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
- Use `screen` on every width query (`min-width`, `max-width`). Feature queries —
  `prefers-reduced-motion`, `hover`, `pointer` — need none.
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
  border-inline-end: 1rem solid rgb(var(--color-background));
  text-align: start;
  inset: 0;
}
```

❌ Not this:

```css
.element {
  padding: 1rem 2rem;
  margin: 0 auto;
  border-right: 1rem solid rgb(var(--color-background));
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
  outline: 2px solid rgb(var(--color-foreground));
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
  /* 0. Component variables */
  --component-padding: 2rem;

  /* 1. Layout & positioning */
  position: relative;
  display: flex;
  flex-direction: column;

  /* 2. Box model */
  width: 100%;
  margin: 0;
  padding: var(--component-padding);
  border: 1px solid rgba(var(--color-foreground), 0.2);

  /* 3. Typography */
  font-family: var(--font-body-family);
  font-weight: var(--font-body-weight);

  /* 4. Visual */
  background: rgb(var(--color-background));
  color: rgb(var(--color-foreground));

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
  background: rgba(var(--color-foreground), 0.04); /* visible when the image is missing */
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
settings in as custom properties on the wrapper (`css-in-markup.md`).
`--featured-collection-columns` is set by the `style` attribute below;
`--featured-collection-gap` is declared in the stylesheet:

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
  --featured-collection-gap: 2.4rem;

  display: grid;
  grid-template-columns: 1fr;
  gap: var(--featured-collection-gap);

  @media screen and (min-width: 750px) {
    grid-template-columns: repeat(var(--featured-collection-columns), 1fr);
  }
}
```
