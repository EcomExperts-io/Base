# Design System

The catalogue of CSS custom properties (design tokens) the theme exposes, where they come from, and
how to use them.

**Source of truth:** `snippets/css-variables.liquid`. Every token below is read directly from that
file — none are invented. (Some rule files call this file `theme-styles-variables.liquid`; that name
does **not** exist in the repo — the real file is `snippets/css-variables.liquid`.) A line-by-line
walkthrough also lives at [`snippets/css-variables`](/snippets/css-variables).

---

## How tokens are generated

`snippets/css-variables.liquid` is rendered once in `<head>` (`{% render 'css-variables' %}` in
`layout/theme.liquid`) and emits an inline `{% style %}` block that:

1. Loads `@font-face` rules for the body and heading fonts (regular, bold, bold-italic, italic) with
   `font-display: swap`.
2. Loops `settings.color_schemes` and emits one rule per scheme:
   `:root, .color-<scheme.id> { … }` (the first scheme also targets `:root`).
3. Emits typography and layout tokens on `:root`.
4. Adds the Alpine.js `[x-cloak] { display: none !important; }` rule to prevent a flash of unstyled
   content before Alpine initializes.

> **Colors are stored as RGB triplets, not hex.** Each color token is a comma-separated
> `r,g,b` value (e.g. `--color-background: 255,255,255`). Consume it through `rgb()`/`rgba()` so you
> can control opacity:
>
> ```css
> color: rgb(var(--color-foreground));
> background: rgba(var(--color-foreground), 0.75);
> ```

---

## Color tokens (per color scheme)

These are emitted for `:root` and every `.color-<scheme.id>` class. Values come from each color
scheme's settings.

| Token | Source setting | Meaning |
|-------|----------------|---------|
| `--color-background` | `scheme.settings.background` (RGB) | Scheme background |
| `--gradient-background` | `scheme.settings.background_gradient` or `background` | Background gradient (falls back to solid) |
| `--color-foreground` | `scheme.settings.text` (RGB) | Primary text/foreground |
| `--color-background-contrast` | computed from background brightness | Contrast color derived from the background |
| `--color-shadow` | `scheme.settings.shadow` (RGB) | Shadow color |
| `--color-button` | `scheme.settings.button` (RGB) | Primary button background |
| `--color-button-text` | `scheme.settings.button_label` (RGB) | Primary button label |
| `--color-secondary-button` | `scheme.settings.secondary_button` (RGB) | Secondary button background |
| `--color-secondary-button-text` | `scheme.settings.secondary_button_label` (RGB) | Secondary button label |
| `--color-link` | `scheme.settings.secondary_button_label` (RGB) | Link color (shares the secondary button label color) |
| `--color-badge-foreground` | `scheme.settings.text` (RGB) | Badge text |
| `--color-badge-background` | `scheme.settings.background` (RGB) | Badge background |
| `--color-badge-border` | `scheme.settings.text` (RGB) | Badge border |
| `--payment-terms-background-color` | `rgb(scheme.settings.background.rgb)` | Background for the payment-terms component |

### Background contrast logic

`--color-background-contrast` is computed in Liquid from the background's brightness:

- brightness ≤ 26 → background lightened by 50%
- brightness ≤ 65 → background lightened by 5%
- brightness > 65 → background darkened by 25%

This keeps a usable contrast color regardless of how light/dark the scheme background is.

### Body defaults

After the scheme loop, the snippet applies base body styling to `body` plus every `.color-*` class:

```css
color: rgba(var(--color-foreground), 0.75);
background-color: rgb(var(--color-background));
```

---

## Typography tokens (`:root`)

| Token | Source | Notes |
|-------|--------|-------|
| `--font-body-family` | `settings.type_body_font.family` + fallback families | |
| `--font-body-style` | `settings.type_body_font.style` | |
| `--font-body-weight` | `settings.type_body_font.weight` | |
| `--font-body-weight-bold` | `weight + 300`, capped at 900 | Derived bold weight |
| `--font-body-scale` | `1` | Default scale (overridable) |
| `--font-heading-family` | `settings.type_heading_font.family` + fallback families | |
| `--font-heading-style` | `settings.type_heading_font.style` | |
| `--font-heading-weight` | `settings.type_heading_font.weight` | |
| `--font-heading-scale` | `1` | Default scale (overridable) |

---

## Layout tokens (`:root`)

| Token | Source | Notes |
|-------|--------|-------|
| `--page-width` | `settings.max_page_width` | In `px` |
| `--page-margin` | `settings.min_page_margin` | In `px` |

> These are the only global layout/spacing tokens emitted by `css-variables.liquid` today. The
> spacing/typography "scale" examples in `.cursor/references/css-reference.md` (e.g. `--space-*`,
> `--font-size-*`, `--breakpoint-*`) are **illustrative conventions**, not tokens currently emitted
> by this theme. If you need a spacing scale, **confirm with the team** before introducing one.

---

## Color schemes in practice

Color schemes are defined in the theme settings (`config/settings_schema.json` /
`config/settings_data.json`) and surface in the theme editor. To make a section/block honor the
merchant's chosen scheme, add the scheme class to the wrapper:

```liquid
<section class="color-{{ section.settings.color_scheme }}">
  …
</section>
```

Everything inside then resolves `--color-*` against that scheme. This is why components should use
`var(--color-*)` tokens and **never hardcode hex values** (see `css-standards.mdc`): a hardcoded
color won't respond to the active scheme.

---

## BEM naming (quick reference)

Class names follow BEM (full guide in `.cursor/references/css-reference.md`):

- **Block:** `.product-card`
- **Element:** `.product-card__title`
- **Modifier:** `.product-card--featured`
- Words within a name are separated with single dashes; elements use `__`; modifiers use `--`.

---

## Related

- `snippets/css-variables` — line-by-line breakdown of the source snippet
- `.cursor/references/css-reference.md` — full CSS guide (modern features, performance, etc.)
- `css-standards.mdc` — the non-negotiable CSS rules
