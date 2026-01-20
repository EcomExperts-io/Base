# Animated Features V2 Section (`sections/animated-features-v2.liquid`)

`sections/animated-features-v2.liquid` renders a two-column features showcase with an animated scrolling digit counter effect. The section displays an image with label on the left and animated content on the right, including a percentage heading with digit-rolling animation, subheading, up to 4 checkmark features, and a disclaimer.

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | `section-animated-features-v2.css`, inline `{%- style -%}` block for CSS custom properties |
| JS   | `section-animated-features-v2.js` (module) |
| Custom Element | `<animated-features-v2>` defined in `section-animated-features-v2.js` |
| Data | Relies on `section.settings` for all configuration (image, 4 features) |

- Custom element manages scroll animations via IntersectionObserver and digit-rolling animation.
- Digit animation creates a slot machine-style counting effect for percentage values.
- All styling controlled via CSS custom properties set dynamically from section settings.

---

## Dynamic Styles

The section uses CSS custom properties set via a `{%- style -%}` block:

```liquid
{%- style -%}
  .section-{{ section.id }}-padding {
    padding-top: {{ section.settings.padding_top | times: 0.75 | round: 0 }}px;
    padding-bottom: {{ section.settings.padding_bottom | times: 0.75 | round: 0 }}px;
  }

  @media screen and (min-width: 750px) {
    .section-{{ section.id }}-padding {
      padding-top: {{ section.settings.padding_top }}px;
      padding-bottom: {{ section.settings.padding_bottom }}px;
    }
  }

  .animated-features-v2[data-section-id="{{ section.id }}"] {
    --animation-speed: {{ section.settings.animation_speed | default: 1.2 }}s;
    --digit-animation-speed: {{ section.settings.animation_speed | default: 1.2 | times: 1.5 }}s;
  }
{%- endstyle -%}
```

- **Responsive padding**: Mobile padding is 75% of desktop value, full padding applied at 750px+ breakpoint.
- **Animation speed**: Base animation speed (default 1.2s, range 0.5–3s) controls entrance animations.
- **Digit animation speed**: Calculated as 150% of base speed for digit-rolling effect (slower for visual impact).

---

## Markup Structure

```liquid
<animated-features-v2
  class="color-{{ section.settings.color_scheme }} animated-features-v2 section-{{ section.id }}-padding"
  data-section-id="{{ section.id }}"
  data-animation-speed="{{ section.settings.animation_speed | default: 1.2 }}"
>
  <div class="page-width">
    <div class="animated-features-v2__container">
      <div class="animated-features-v2__left">
        <!-- Left: image and label -->
      </div>
      <div class="animated-features-v2__right">
        <!-- Right: heading, subheading, features, disclaimer -->
      </div>
    </div>
  </div>
</animated-features-v2>
```

- Custom element `<animated-features-v2>` wraps entire section for JavaScript control.
- Section ID used for unique styling and animation targeting.
- Two-column layout: left side for image, right side for content.

### Left Side - Image

```liquid
<div class="animated-features-v2__left">
  {%- if section.settings.image != blank -%}
    <div class="animated-features-v2__image-wrapper">
      <img
        src="{{ section.settings.image | image_url: width: 600 }}"
        srcset="{{ section.settings.image | image_url: width: 600 }} 1x, {{ section.settings.image | image_url: width: 1200 }} 2x"
        alt="{{ section.settings.image.alt | default: section.settings.image_label | escape }}"
        loading="lazy"
        width="{{ section.settings.image.width }}"
        height="{{ section.settings.image.height }}"
        class="animated-features-v2__image"
      >
    </div>
  {%- else -%}
    <div class="animated-features-v2__image-placeholder">
      {{ 'image' | placeholder_svg_tag: 'placeholder-svg' }}
    </div>
  {%- endif -%}

  {%- if section.settings.image_label != blank -%}
    <div class="animated-features-v2__image-label">{{ section.settings.image_label | escape }}</div>
  {%- endif -%}
</div>
```

- **Responsive image**: 1x and 2x srcset for retina displays (600w and 1200w).
- **Alt text fallback**: Uses image alt text, falls back to `image_label` if alt is empty.
- **Placeholder**: Shows placeholder SVG when no image is selected.
- **Image label**: Optional text label displayed below image (escaped for security).
- **Aspect ratio**: Image maintains 1:1 aspect ratio via CSS.

### Right Side - Content

```liquid
<div class="animated-features-v2__right">
  {%- if section.settings.heading_percentage != blank -%}
    <h2 class="animated-features-v2__heading" data-percentage="{{ section.settings.heading_percentage | escape }}">
      {{ section.settings.heading_percentage | escape }}
    </h2>
  {%- endif -%}

  {%- if section.settings.subheading != blank -%}
    <div class="animated-features-v2__subheading">{{ section.settings.subheading }}</div>
  {%- endif -%}

  <div class="animated-features-v2__features">
    {%- for i in (1..4) -%}
      {%- assign feature_key = 'feature_' | append: i -%}
      {%- assign current_feature = section.settings[feature_key] -%}

      {%- if current_feature != blank -%}
        <div class="animated-features-v2__feature" id="animated-features-v2-feature-{{ i }}">
          <div class="animated-features-v2__checkmark">
            {{ 'icon-checkmark.svg' | inline_asset_content }}
          </div>
          <span class="animated-features-v2__feature-text">{{ current_feature | escape }}</span>
        </div>
      {%- endif -%}
    {%- endfor -%}
  </div>

  {%- if section.settings.disclaimer != blank -%}
    <div class="animated-features-v2__disclaimer">{{ section.settings.disclaimer }}</div>
  {%- endif -%}
</div>
```

- **Heading**: Percentage value (e.g., "70%") that animates with digit-rolling effect.
- **Data attribute**: `data-percentage` stores original value for JavaScript animation.
- **Subheading**: Supporting text (textarea, allows line breaks but not HTML).
- **Features**: Up to 4 checkmark features, only renders if feature text is not blank.
- **Checkmark icon**: Inline SVG icon displayed before each feature text.
- **Disclaimer**: Optional richtext content displayed below features (supports HTML).

---

## JavaScript Behavior

The section uses a custom element `<animated-features-v2>` defined in `section-animated-features-v2.js`:

- **Scroll animations**: IntersectionObserver triggers animations when elements enter viewport (20% threshold).
- **Digit-rolling animation**: Creates slot machine-style counting effect for percentage heading.
- **Animation details**: Parses percentage value, creates vertical scrollers, animates each digit with staggered delay.
- **Lifecycle management**: Proper cleanup in `disconnectedCallback`.

---

## Behavior

- **Scroll-triggered animations**: All content elements fade in and slide up when entering viewport.
- **Digit-rolling effect**: Percentage heading animates from 0 to target value with slot machine effect.
- **Staggered digit animation**: Each digit in the percentage animates with slight delay for visual appeal.
- **Configurable speed**: All animations respect the `animation_speed` setting.
- **Responsive layout**: Two-column layout on desktop, stacks on mobile.
- **Color scheme support**: Integrates with Shopify color scheme system.
- **Conditional rendering**: Features only display if text is provided (1-4 features).

---

## Schema

### Section Settings

| Setting ID | Type | Default | Purpose |
|---------|------|---------|---------|
| `color_scheme` | color_scheme | `scheme-1` | Shopify color scheme for section |
| `animation_speed` | range (s) | 1.2 | Base animation speed (0.5–3s, step 0.1) |
| `padding_top` | range (px) | 40 | Top padding (0–100px, step 4) |
| `padding_bottom` | range (px) | 40 | Bottom padding (0–100px, step 4) |
| `image` | image_picker | — | Left side image |
| `image_label` | text | "Image Label" | Text label below image |
| `heading_percentage` | text | "70%" | Percentage heading with digit animation |
| `subheading` | textarea | "Write subheading here" | Supporting text (allows line breaks) |
| `feature_1` to `feature_4` | text | "Feature 1-4" | Checkmark feature items |
| `disclaimer` | richtext | — | Disclaimer richtext content |

### Presets

- Includes a preset named "Animated Features V2" for quick section addition.

---

## Implementation Notes

1. **Digit animation mechanism**: Creates vertical scrollers with digits 0-9, translates to show target digit.

2. **Percentage format**: Should contain numeric value followed by optional suffix (e.g., "70%", "99.9%").

3. **Minimum 2 digits**: Values padded to 2 digits minimum for consistent animation.

4. **Animation speed**: Digit animation is 150% of base speed (slower for dramatic effect).

5. **Staggered delay**: Each digit animates with 0.1s delay creating left-to-right cascade.

6. **Zero handling**: Special case for digit "0" scrolls to position 10 for visual continuity.

7. **Animation cleanup**: After animation, heading innerHTML replaced with plain text for accessibility.

8. **Non-numeric fallback**: If heading doesn't match percentage pattern, displays as plain text.

9. **Icon dependency**: Requires `icon-checkmark.svg` in assets folder.

10. **Image sizing**: Uses 1x (600w) and 2x (1200w) srcset, 1:1 aspect ratio via CSS.

11. **Conditional features**: Features only render if text is not blank (allows 1-4 features).

12. **Responsive padding**: Mobile padding automatically 75% of desktop value.

13. **Multiple instances**: Section ID ensures multiple instances work independently.

14. **Progressive enhancement**: Content remains accessible without JavaScript.

15. **Memory management**: IntersectionObserver properly disconnected on cleanup.
