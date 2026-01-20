# Logos Section (`sections/logos.liquid`)

`sections/logos.liquid` renders an infinitely scrolling horizontal strip of logos. Logos are configured via blocks, duplicated in markup for a seamless looping animation. The section supports color schemes, responsive padding, configurable logo height, and configurable animation duration.

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | `section-logos.css`, inline `{%- style -%}` block for responsive padding and CSS variables |
| JS   | None |
| Blocks | `logo` block type |
| Data | Relies on `section.blocks` and `section.settings` |

- No JavaScript dependencies; the section is purely presentational.
- Animation is handled entirely by CSS (`@keyframes logos-scroll`).

---

## Dynamic Styles

### Responsive padding

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
{%- endstyle -%}
```

- **Responsive padding**: Mobile padding is 75% of desktop value; full padding applies at 750px+.

### CSS variables (logo size + animation speed)

The section sets CSS variables inline on the wrapper:

```liquid
<div
  class="color-{{ section.settings.color_scheme }} section-{{ section.id }}-padding"
  style="
    --logo-height: {{ logo_height }}px;
    --animation-duration: {{ animation_duration }}s;
  "
>
```

- `--logo-height` controls `.logos__item` height in CSS.
- `--animation-duration` controls the marquee animation speed.

---

## Markup Structure

```liquid
{%- if blocks_to_show > 0 -%}
  <div
    class="color-{{ section.settings.color_scheme }} section-{{ section.id }}-padding"
    style="
      --logo-height: {{ logo_height }}px;
      --animation-duration: {{ animation_duration }}s;
    "
  >
    <div class="page-width">
      <div class="logos__container">
        <div class="logos__track">
          <!-- Logos (first pass) -->
          <!-- Logos (duplicated pass for seamless loop) -->
        </div>
      </div>
    </div>
  </div>
{%- endif -%}
```

- The section renders only if at least one logo block exists.
- The `.logos__track` contains **two loops** over the same blocks to create a continuous marquee.

### Logo item (first pass)

```liquid
{%- for block in section.blocks -%}
  {%- assign logo = block.settings.logo -%}
  <div class="logos__item {% if logo == blank %}blank{% endif %}" {{ block.shopify_attributes }}>
    {%- if logo != blank -%}
      <img
        srcset="
          {%- if logo.width >= 50 -%}{{ logo | image_url: width: 50 }} 50w,{%- endif -%}
          {%- if logo.width >= 100 -%}{{ logo | image_url: width: 100 }} 100w,{%- endif -%}
          {%- if logo.width >= 150 -%}{{ logo | image_url: width: 150 }} 150w,{%- endif -%}
          {{ logo | image_url }} {{ logo.width }}w
        "
        src="{{ logo | image_url: width: 100 }}"
        sizes="{{ logo_height }}px"
        alt="{{ logo.alt | escape }}"
        loading="lazy"
        width="{{ logo.width }}"
        height="{{ logo.height }}"
        class="logos__image"
      >
    {%- else -%}
      {{ 'image' | placeholder_svg_tag: 'placeholder-svg' }}
    {%- endif -%}
  </div>
{%- endfor -%}
```

- **Responsive logo images**: Uses 50w/100w/150w breakpoints plus original.
- **Placeholder**: When no logo is set, uses Shopify’s placeholder SVG.
- **Alt text**: Uses the image alt text (escaped).

### Duplicated logos (for seamless loop)

The same blocks are rendered again, marked as decorative:

```liquid
{%- for block in section.blocks -%}
  {%- assign logo = block.settings.logo -%}
  <div class="logos__item {% if logo == blank %}blank{% endif %}" aria-hidden="true">
    {%- if logo != blank -%}
      <img
        src="{{ logo | image_url: width: 100 }}"
        alt=""
        loading="lazy"
        width="{{ logo.width }}"
        height="{{ logo.height }}"
        class="logos__image"
      >
    {%- else -%}
      {{ 'image' | placeholder_svg_tag: 'placeholder-svg' }}
    {%- endif -%}
  </div>
{%- endfor -%}
```

- `aria-hidden="true"` and `alt=""` prevent duplicate content for screen readers.

---

## Behavior

- **Purely presentational**: No JavaScript required.
- **Continuous marquee**: CSS animates `.logos__track` using `@keyframes logos-scroll`.
- **Hover pause**: `.logos__track:hover` pauses animation for better UX.
- **Mobile speed tweak**: On mobile, CSS reduces duration (`* 0.83`) to keep animation feeling consistent.

---

## Schema

```json
{
  "name": "Logos",
  "tag": "section",
  "class": "logos",
  "settings": [
    { "type": "color_scheme", "id": "color_scheme", "label": "t:sections.all.colors.label", "default": "scheme-1" },
    { "type": "range", "id": "animation_duration", "label": "Animation Duration", "min": 10, "max": 60, "step": 5, "unit": "s", "default": 30 },
    { "type": "range", "id": "padding_top", "label": "Padding Top", "min": 0, "max": 100, "step": 4, "unit": "px", "default": 40 },
    { "type": "range", "id": "padding_bottom", "label": "Padding Bottom", "min": 0, "max": 100, "step": 4, "unit": "px", "default": 40 },
    { "type": "range", "id": "logo_height", "label": "Logo Height", "min": 40, "max": 120, "step": 10, "unit": "px", "default": 60 }
  ],
  "blocks": [
    {
      "type": "logo",
      "name": "Logo",
      "settings": [{ "type": "image_picker", "id": "logo", "label": "Logo" }]
    }
  ],
  "presets": [{ "name": "Logos" }]
}
```

---

## Implementation Notes

1. **Duplicate rendering**: The second logo loop is required so the animation can scroll continuously without an obvious “jump”.
2. **Animation distance**: `section-logos.css` animates the track from `translateX(0)` to `translateX(-50%)`, which assumes the duplicated content spans exactly twice the width.
3. **Accessibility**: The duplicated logo set uses `aria-hidden="true"` and empty `alt` to avoid duplicate announcements.
4. **Sizing**: `--logo-height` controls the visible height; images use `height: 100%` and `width: auto` to preserve aspect ratio.
5. **Blank logos**: If a block has no image, `.blank` class applies a placeholder background color.
6. **VitePress mustache safety**: If referencing Liquid mustaches in prose/inline code, escape them like `\{\{ section.id \}\}` to avoid blank pages. [[memory:13638067]]

