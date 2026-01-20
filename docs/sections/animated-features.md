# Animated Features Section (`sections/animated-features.liquid`)

`sections/animated-features.liquid` renders an interactive features showcase with animated cards that flip on click to reveal additional content. The section displays a two-column layout with text content on the left (heading, subheading, button, and notes) and a 2x2 grid of animated feature cards on the right. Cards support images, labels, and flippable back content with scroll-triggered animations and customizable animation speeds.

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | `section-animated-features.css`, inline `{%- style -%}` block for CSS custom properties |
| JS   | `section-animated-features.js` (module) |
| Custom Element | `<animated-features>` defined in `section-animated-features.js` |
| Data | Relies on `section.settings` for all configuration (4 feature cards) |

- Custom element manages scroll animations via IntersectionObserver and card flip interactions.
- All styling controlled via CSS custom properties set dynamically from section settings.
- Animation speeds are configurable and cascade to child elements.

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

  .animated-features[data-section-id="{{ section.id }}"] {
    --animation-speed: {{ section.settings.animation_speed | default: 1.2 }}s;
    --card-animation-speed: {{ section.settings.animation_speed | default: 1.2 | times: 0.83 | round: 2 }}s;
    --card-flip-speed: {{ section.settings.animation_speed | default: 1.2 | times: 0.5 | round: 2 }}s;
  }
{%- endstyle -%}
```

- **Responsive padding**: Mobile padding is 75% of desktop value, full padding applied at 750px+ breakpoint.
- **Animation speed**: Base animation speed (default 1.2s, range 0.5–3s) controls all animations.
- **Card animation speed**: Calculated as 83% of base speed for card entrance animations.
- **Card flip speed**: Calculated as 50% of base speed for card flip transitions.

---

## Markup Structure

```liquid
<animated-features
  class="color-{{ section.settings.color_scheme }} animated-features section-{{ section.id }}-padding"
  data-section-id="{{ section.id }}"
  data-animation-speed="{{ section.settings.animation_speed | default: 1.2 }}"
>
  <div class="page-width">
    <div class="animated-features__container">
      <div class="animated-features__left">
        <!-- Left content: heading, subheading, button, notes -->
      </div>
      <div class="animated-features__right">
        <div class="animated-features__grid">
          <!-- 4 feature cards -->
        </div>
      </div>
    </div>
  </div>
</animated-features>
```

- Custom element `<animated-features>` wraps entire section for JavaScript control.
- Section ID used for unique styling and animation targeting.
- Two-column layout: left side for text content, right side for card grid.

### Left Content

```liquid
<div class="animated-features__left">
  <div class="animated-features__left-content">
    {%- if section.settings.heading != blank -%}
      <h2 class="animated-features__heading">{{ section.settings.heading | escape }}</h2>
    {%- endif -%}

    {%- if section.settings.subheading != blank -%}
      <div class="animated-features__subheading">{{ section.settings.subheading }}</div>
    {%- endif -%}

    {%- if section.settings.button_text != blank -%}
      <a
        href="{{ section.settings.button_link }}"
        class="animated-features__button {{ section.settings.button_type }}"
      >
        {{ section.settings.button_text | escape }}
      </a>
    {%- endif -%}
  </div>

  {%- if section.settings.notes != blank -%}
    <div class="animated-features__notes">{{ section.settings.notes }}</div>
  {%- endif -%}
</div>
```

- **Heading**: Main section title (text input, escaped).
- **Subheading**: Supporting text (textarea, raw HTML allowed).
- **Button**: CTA with configurable style (Primary or Secondary) and link.
- **Notes**: Additional richtext content displayed below main content.

### Feature Cards Grid

```liquid
<div class="animated-features__right">
  <div class="animated-features__grid">
    {%- for i in (1..4) -%}
      {%- assign image_key = 'image_' | append: i -%}
      {%- assign label_key = 'label_' | append: i -%}
      {%- assign flipped_text_key = 'flipped_text_' | append: i -%}
      {%- assign current_image = section.settings[image_key] -%}
      {%- assign current_label = section.settings[label_key] -%}
      {%- assign current_flipped_text = section.settings[flipped_text_key] -%}

      <div class="animated-features__card" id="animated-features-card-{{ i }}">
        <div class="animated-features__card-inner">
          <div class="animated-features__card-front">
            <!-- Front: icon, image, label -->
          </div>
          <div class="animated-features__card-back">
            <!-- Back: icon, flipped text -->
          </div>
        </div>
      </div>
    {%- endfor -%}
  </div>
</div>
```

- **4 cards**: Fixed loop from 1 to 4, each card has front and back faces.
- **Dynamic settings**: Settings accessed via constructed keys.
- **Card structure**: Inner wrapper enables 3D flip animation via CSS transforms.

### Card Front

```liquid
<div class="animated-features__card-front">
  <div class="animated-features__icon">
    {{ 'icon-sync.svg' | inline_asset_content }}
  </div>
  {%- if current_image != blank -%}
    <img
      src="{{ current_image | image_url: width: 400 }}"
      srcset="{{ current_image | image_url: width: 400 }} 1x, {{ current_image | image_url: width: 800 }} 2x"
      alt="{{ current_image.alt | default: current_label | escape }}"
      loading="lazy"
      width="{{ current_image.width }}"
      height="{{ current_image.height }}"
      class="animated-features__image"
    >
  {%- else -%}
    <div class="animated-features__image-placeholder">
      {{ 'image' | placeholder_svg_tag: 'placeholder-svg' }}
    </div>
  {%- endif -%}
  {%- if current_label != blank -%}
    <div class="animated-features__label">{{ current_label | escape }}</div>
  {%- endif -%}
</div>
```

- **Sync icon**: Inline SVG icon displayed at top of card.
- **Responsive image**: 1x and 2x srcset for retina displays (400w and 800w).
- **Placeholder**: Shows placeholder SVG when no image is selected.
- **Label**: Optional text label displayed below image.

### Card Back

```liquid
<div class="animated-features__card-back">
  <div class="animated-features__icon">
    {{ 'icon-sync.svg' | inline_asset_content }}
  </div>
  <div class="animated-features__flipped-text">
    {{ current_flipped_text | default: 'Add the flipped text here' }}
  </div>
</div>
```

- **Sync icon**: Same icon as front for visual consistency.
- **Flipped text**: Richtext content (supports HTML formatting).

---

## JavaScript Behavior

The section uses a custom element `<animated-features>` defined in `section-animated-features.js`:

- **Scroll animations**: IntersectionObserver triggers animations when elements enter viewport (20% threshold).
- **Card flip**: Click handler toggles `is-flipped` class for 3D flip effect.
- **Lifecycle management**: Proper cleanup in `disconnectedCallback`.

---

## Behavior

- **Scroll-triggered animations**: All content elements fade in and slide up when entering viewport.
- **Card entrance animations**: Cards scale up from 0.8 to 1.0 when visible.
- **Interactive flip**: Cards flip on click to reveal back content (3D transform effect).
- **Configurable speed**: All animations respect the `animation_speed` setting.
- **Responsive layout**: Two-column layout on desktop, stacks on mobile.
- **Color scheme support**: Integrates with Shopify color scheme system.

---

## Schema

### Section Settings

| Setting ID | Type | Default | Purpose |
|------------|------|---------|---------|
| `color_scheme` | color_scheme | `scheme-1` | Shopify color scheme for section |
| `animation_speed` | range (s) | 1.2 | Base animation speed (0.5–3s, step 0.1) |
| `padding_top` | range (px) | 40 | Top padding (0–100px, step 4) |
| `padding_bottom` | range (px) | 40 | Bottom padding (0–100px, step 4) |
| `heading` | text | "Add Heading here" | Main section heading |
| `subheading` | textarea | "Add Subheading here" | Supporting text (allows line breaks) |
| `button_text` | text | "Read more" | CTA button text |
| `button_link` | url | — | CTA button destination |
| `button_type` | select | `button` | Button style (Primary or Secondary) |
| `notes` | richtext | — | Additional richtext content |
| `image_1` to `image_4` | image_picker | — | Feature card images |
| `label_1` to `label_4` | text | "Label 1-4" | Card front labels |
| `flipped_text_1` to `flipped_text_4` | richtext | — | Card back content |

### Presets

- Includes a preset named "Animated Features" for quick section addition.

---

## Implementation Notes

1. **Fixed card count**: Section always renders exactly 4 cards (hardcoded loop from 1 to 4).

2. **Animation speed cascade**: Base `animation_speed` setting controls three derived speeds.

3. **Responsive padding calculation**: Mobile padding is automatically 75% of desktop value.

4. **IntersectionObserver threshold**: Set to 0.2 (20%), animations trigger when 20% visible.

5. **Icon dependency**: Requires `icon-sync.svg` in assets folder.

6. **Image sizing**: Uses 1x (400w) and 2x (800w) srcset for retina displays.

7. **Alt text fallback**: Image alt text defaults to card label if not provided.

8. **Placeholder fallback**: Uses Shopify's `image` placeholder SVG when no image selected.

9. **Button conditional**: Button only renders when `button_text` is not blank.

10. **Richtext fields**: `subheading`, `notes`, and `flipped_text` support HTML.

11. **Text escaping**: `heading`, `button_text`, and `label` fields are escaped for security.

12. **Card flip mechanism**: Flip triggered by click event, controlled via `is-flipped` CSS class.

13. **Animation persistence**: Once elements animate in, they remain visible.

14. **Multiple instances**: Section ID ensures multiple instances work independently.

15. **Color scheme integration**: Uses Shopify's color scheme system.

16. **Button color mapping**: Button colors use CSS custom properties mapping to color scheme variables.

17. **Grid layout**: Card grid uses CSS Grid (2x2 layout).

18. **Translation keys**: Section name uses translation filter.

19. **Memory management**: IntersectionObserver properly disconnected on cleanup.

20. **Progressive enhancement**: Content remains accessible without JavaScript.
