# css-variables Snippet

`snippets/css-variables.liquid` injects theme CSS custom properties (CSS variables) for typography and color schemes. It outputs `@font-face` rules for all font variations and generates per-scheme CSS variables used across the theme. The component also includes Alpine.js `x-cloak` styling to prevent flash of unstyled content.

---

## What It Does

- Generates `@font-face` rules for body and heading fonts with all variations.
- Creates CSS custom properties for each color scheme.
- Calculates background contrast colors dynamically.
- Sets typography CSS variables (font families, weights, styles).
- Sets layout CSS variables (page width, margins).
- Includes Alpine.js `x-cloak` styling.
- Outputs body color rules for all color schemes.

---

## Parameters

None. This snippet takes no parameters.

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | Inline `{% style %}` block with all CSS variables |
| JavaScript | None required (but Alpine.js `x-cloak` styling included) |
| Shopify Filters | `font_face`, `font_modify`, `color_brightness`, `color_lighten`, `color_darken` |
| Data | Requires theme settings: `type_body_font`, `type_heading_font`, `color_schemes`, `max_page_width`, `min_page_margin` |

- All CSS generated inline via `{% style %}` block.
- No external CSS files required.
- Shopify font and color filters handle font loading and color calculations.

---

## Dynamic Styles

The snippet generates comprehensive inline styles including:

### Alpine.js Cloak

```liquid
[x-cloak] {
  display: none !important;
}
```

- **Alpine.js support**: Hides elements with `x-cloak` attribute until Alpine.js loads.

### Font Face Rules

```liquid
{{ settings.type_body_font | font_face: font_display: 'swap' }}
{{ settings.type_body_font | font_modify: 'weight', 'bold' | font_face: font_display: 'swap' }}
{{ settings.type_body_font | font_modify: 'weight', 'bold' | font_modify: 'style', 'italic' | font_face: font_display: 'swap' }}
{{ settings.type_body_font | font_modify: 'style', 'italic' | font_face: font_display: 'swap' }}
```

- **Font variations**: Generates `@font-face` rules for:
    - Regular
    - Bold
    - Bold italic
    - Italic

### Color Scheme Variables

```liquid
.color-{{ scheme.id }} {
  --color-background: {{ scheme.settings.background.red }},{{ scheme.settings.background.green }},{{ scheme.settings.background.blue }};
  --color-foreground: {{ scheme.settings.text.red }},{{ scheme.settings.text.green }},{{ scheme.settings.text.blue }};
  /* ... additional color variables ... */
}
```

- **Per-scheme variables**: Each color scheme gets its own CSS variables.
- **RGB format**: Colors stored as RGB values (comma-separated) for use with `rgba()` and `rgb()`.

### Typography Variables

```liquid
:root {
  --font-body-family: {{ settings.type_body_font.family }}, {{ settings.type_body_font.fallback_families }};
  --font-body-weight: {{ settings.type_body_font.weight }};
  --font-heading-family: {{ settings.type_heading_font.family }}, {{ settings.type_heading_font.fallback_families }};
  /* ... additional typography variables ... */
}
```

- **Font families**: Includes font family and fallback families.
- **Font weights**: Includes regular and bold weights.
- **Font scales**: Includes scale variables (default: 1).

### Layout Variables

```liquid
:root {
  --page-width: {{ settings.max_page_width }}px;
  --page-margin: {{ settings.min_page_margin }}px;
}
```

- **Page width**: Maximum page width in pixels.
- **Page margin**: Minimum page margin in pixels.

---

## Markup Structure

The snippet outputs only CSS (no HTML markup). It uses a `{% style %}` block to generate inline styles.

---

## Behavior

- **Font loading**: Generates `@font-face` rules for all font variations with `font-display: swap`.
- **Color scheme generation**: Loops through all color schemes and generates CSS variables.
- **Contrast calculation**: Dynamically calculates background contrast color based on brightness.
- **Variable scope**: Variables scoped to `:root` and `.color-[scheme-id]` classes.
- **Body styling**: Applies color rules to body and all color scheme classes.

---

## Usage Example

```liquid
{% render 'css-variables' %}
```

Typically used in:
- Theme layout (`layout/theme.liquid`) in `<head>` section

---

## Implementation Notes

1. **No parameters**: Snippet takes no parameters - reads all data from theme settings.

2. **Font face generation**: Generates `@font-face` rules for:
    - Body font: regular, bold, bold italic, italic
    - Heading font: regular, bold, bold italic, italic

3. **Font display swap**: All fonts use `font-display: swap` for better performance.

4. **Color scheme loop**: Loops through `settings.color_schemes` to generate variables for each scheme.

5. **Scheme class generation**: Builds selector list for body color rules: `body, .color-scheme1, .color-scheme2, ...`

6. **RGB color format**: Colors stored as RGB values (comma-separated) for use with:
    - `rgb(var(--color-background))`
    - `rgba(var(--color-foreground), 0.75)`

7. **Background contrast calculation**: Dynamically calculates contrast color based on background brightness:
    - Brightness ≤ 26: Lighten by 50%
    - Brightness ≤ 65: Lighten by 5%
    - Brightness > 65: Darken by 25%

8. **Gradient background**: Uses `background_gradient` if set, otherwise falls back to `background`.

9. **Color variables generated**:
    - `--color-background`
    - `--gradient-background`
    - `--color-foreground`
    - `--color-background-contrast`
    - `--color-shadow`
    - `--color-button`
    - `--color-button-text`
    - `--color-secondary-button`
    - `--color-secondary-button-text`
    - `--color-link`
    - `--color-badge-foreground`
    - `--color-badge-background`
    - `--color-badge-border`
    - `--payment-terms-background-color`

10. **Typography variables generated**:
    - `--font-body-family`
    - `--font-body-style`
    - `--font-body-weight`
    - `--font-body-weight-bold`
    - `--font-body-scale`
    - `--font-heading-family`
    - `--font-heading-style`
    - `--font-heading-weight`
    - `--font-heading-scale`

11. **Layout variables generated**:
    - `--page-width`
    - `--page-margin`

12. **Alpine.js cloak**: Includes `[x-cloak]` styling to prevent flash of unstyled content.

13. **Root variables**: Typography and layout variables set on `:root` for global access.

14. **Scheme-specific variables**: Color variables set on `.color-[scheme-id]` classes.

15. **Body color rules**: Applies color rules to `body` and all color scheme classes.

16. **Font modification**: Uses `font_modify` filter to create font variations (bold, italic).

17. **Color brightness**: Uses `color_brightness` filter to calculate background brightness.

18. **Color manipulation**: Uses `color_lighten` and `color_darken` filters for contrast calculation.

19. **Scheme class building**: Builds comma-separated list of scheme classes for body selector.

20. **First scheme handling**: First scheme uses `:root,` prefix in selector.

21. **RGB extraction**: Extracts RGB values from color objects for CSS variable format.

22. **Gradient fallback**: Falls back to solid background if gradient not set.

23. **Payment terms color**: Includes special variable for payment terms background.

24. **Font fallback families**: Includes fallback font families for better compatibility.

25. **Bold weight calculation**: Calculates bold weight as `weight + 300` capped at 900.

26. **Font scale defaults**: Font scales default to 1 (can be overridden).

27. **Page width format**: Page width includes `px` unit.

28. **Page margin format**: Page margin includes `px` unit.

29. **Body color opacity**: Body foreground color uses `rgba()` with 0.75 opacity.

30. **Body background**: Body background uses `rgb()` for solid color.

31. **No HTML output**: Snippet outputs only CSS, no HTML markup.

32. **Inline styles**: All CSS generated inline in `<style>` tag.

33. **Performance**: Inline styles prevent additional HTTP request but increase HTML size.

34. **Font loading strategy**: `font-display: swap` ensures text remains visible during font load.

35. **Color scheme flexibility**: Each color scheme can have different color values.

36. **Variable naming**: Variables use kebab-case naming convention.

37. **RGB format advantage**: RGB format allows opacity control via `rgba()`.

38. **Contrast calculation logic**: Contrast calculation ensures readable text on any background.

39. **Gradient support**: Supports both gradient and solid backgrounds.

40. **Scheme class prefix**: All scheme classes use `.color-` prefix.

41. **Body selector**: Body and scheme classes share same color rules.

42. **Font weight limits**: Bold weight calculation ensures it doesn't exceed 900.

43. **Font style support**: Supports both regular and italic font styles.

44. **Font weight support**: Supports regular and bold font weights.

45. **Fallback families**: Includes fallback font families for better compatibility.

46. **Payment terms integration**: Includes special variable for payment terms component.

47. **Badge colors**: Includes separate variables for badge foreground, background, and border.

48. **Button colors**: Includes separate variables for primary and secondary buttons.

49. **Link color**: Link color uses secondary button label color.

50. **Shadow color**: Includes shadow color variable for depth effects.

