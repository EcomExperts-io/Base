# Hero V2 Section (`sections/hero-v2.liquid`)

`sections/hero-v2.liquid` renders a two-column hero layout: the left side contains main hero content (heading, description, CTA button) overlaid on a main media area (image or video), and the right side renders up to two promotional blocks (collection tiles) that link to collections.

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | `section-hero-v2.css`, inline `{%- style -%}` block for responsive padding |
| JS   | None |
| Data | Relies on `section.settings` and `section.blocks` |

- No JavaScript dependencies; the section is purely presentational.
- Background video embeds (YouTube/Vimeo) are implemented via iframes.

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

### Button colors (CSS variables)

The section sets button colors via CSS custom properties:

```liquid
<div
  class="hero-v2 section-{{ section.id }}-padding color-{{ section.settings.color_scheme }}"
  style="
    --button: var(--color-{{ button_type }});
    --button-text: var(--color-{{ button_type }}-text);
  "
>
```

- Button colors map to the active color scheme’s `--color-button` / `--color-button-text` (or secondary variants).

---

## Markup Structure

```liquid
<div class="hero-v2 section-{{ section.id }}-padding color-{{ section.settings.color_scheme }}">
  <div class="page-width">
    <div class="hero-v2__container">
      <div class="hero-v2__left">
        <!-- Overlaid content + main media -->
      </div>
      <div class="hero-v2__right">
        <!-- Up to 2 promo blocks -->
      </div>
    </div>
  </div>
</div>
```

### Left side: overlaid content

```liquid
<div
  class="
    hero-v2__content hero-v2__content--h-{{ content_alignment }}
    hero-v2__content--v-{{ vertical_alignment }}
  "
>
  {% if heading != blank %}
    <h1 class="hero-v2__heading">{{ heading | escape }}</h1>
  {% endif %}

  {% if description != blank %}
    <p class="hero-v2__description">{{ description | escape }}</p>
  {% endif %}

  {% if button_text != blank and button_link != blank %}
    <a href="{{ button_link }}" class="hero-v2__button">
      {{ button_text | escape }}
    </a>
  {% endif %}
</div>
```

- Content alignment is controlled via BEM modifier classes.

### Left side: main media (image or video)

```liquid
<div class="hero-v2__main-image">
  {% if background_type == 'video' %}
    {% if video_background_hosted != blank %}
      {{ video_background_hosted | video_tag: autoplay: true, loop: true, muted: true, playsinline: true, class: 'hero-v2__image' }}
    {% elsif video_background_url != blank %}
      <!-- YouTube/Vimeo iframe embedding -->
    {% else %}
      {{ 'image' | placeholder_svg_tag: 'placeholder-svg' }}
    {% endif %}
  {% else %}
    {% if main_image != blank %}
      <img
        srcset="
          {%- if main_image.width >= 400 -%}{{ main_image | image_url: width: 400 }} 400w,{%- endif -%}
          {%- if main_image.width >= 600 -%}{{ main_image | image_url: width: 600 }} 600w,{%- endif -%}
          {%- if main_image.width >= 800 -%}{{ main_image | image_url: width: 800 }} 800w,{%- endif -%}
          {%- if main_image.width >= 1000 -%}{{ main_image | image_url: width: 1000 }} 1000w,{%- endif -%}
          {{ main_image | image_url }} {{ main_image.width }}w
        "
        src="{{ main_image | image_url: width: 1000 }}"
        sizes="(min-width: 990px) 50vw, 100vw"
        alt="{{ main_image.alt | default: heading | escape }}"
        loading="eager"
        width="{{ main_image.width }}"
        height="{{ main_image.height }}"
        class="hero-v2__image"
      >
    {% else %}
      {{ 'image' | placeholder_svg_tag: 'placeholder-svg' }}
    {% endif %}
  {% endif %}
</div>
```

- **Hosted video** uses `video_tag` and is preferred for performance.
- **External video URLs** embed YouTube/Vimeo iframes.
- **Main image** uses responsive srcset up to 1000w and loads eagerly.

### Right side: promo blocks (up to 2)

```liquid
{%- for block in section.blocks limit: 2 -%}
  <!-- collection + custom title/image computed -->
  <div class="hero-v2__promo-block" {{ block.shopify_attributes }}>
    <!-- promo image -->
    <!-- promo link with title + arrow -->
  </div>
{%- endfor -%}
```

Promo link uses a position modifier class:

```liquid
<a
  href="{{ collection_url | default: '#' }}"
  class="hero-v2__promo-link hero-v2__promo-link--{{ content_position }}"
>
  <div class="hero-v2__promo-content">
    <span class="hero-v2__promo-title">{{ collection_title | escape }}</span>
    <span class="hero-v2__promo-arrow">{{ 'icon-arrow.svg' | inline_asset_content }}</span>
  </div>
</a>
```

---

## Behavior

- **Purely presentational**: No JavaScript required.
- **Conditional rendering**: Elements only render when content is provided (heading/description/button).
- **Media fallbacks**: Placeholder SVG used when no media is available.
- **Promo blocks**: Up to 2 blocks render; each can be configured with a collection, custom title, and custom image.

---

## Schema

```json
{
  "name": "Hero V2",
  "tag": "section",
  "class": "section-hero-v2",
  "settings": [
    { "type": "color_scheme", "id": "color_scheme", "default": "scheme-1" },
    { "type": "radio", "id": "background_type", "default": "image" },
    { "type": "image_picker", "id": "main_image" },
    { "type": "video", "id": "video_background_hosted" },
    { "type": "url", "id": "video_background_url" },
    { "type": "text", "id": "heading" },
    { "type": "textarea", "id": "description" },
    { "type": "text", "id": "button_text" },
    { "type": "url", "id": "button_link" },
    { "type": "select", "id": "button_type", "default": "button" },
    { "type": "select", "id": "content_alignment", "default": "left" },
    { "type": "select", "id": "vertical_alignment", "default": "top" },
    { "type": "range", "id": "padding_top", "default": 36 },
    { "type": "range", "id": "padding_bottom", "default": 36 }
  ],
  "blocks": [
    {
      "type": "collection",
      "name": "Collection",
      "limit": 2,
      "settings": [
        { "type": "collection", "id": "collection" },
        { "type": "text", "id": "custom_title" },
        { "type": "image_picker", "id": "custom_image" },
        { "type": "select", "id": "content_position", "default": "top" }
      ]
    }
  ],
  "presets": [{ "name": "Hero V2" }]
}
```

---

## Implementation Notes

1. **Hosted vs external video**: Hosted video uses `video_tag` and is generally more reliable than YouTube/Vimeo iframes.
2. **YouTube ID parsing**: Extracts video ID via splitting on `v=` and `/`, and strips query params.
3. **Vimeo ID parsing**: Uses the last URL segment as the video ID.
4. **Eager loading**: Main image uses `loading="eager"` (good for above-the-fold hero).
5. **Promo block count**: Renders up to 2 promo blocks (`limit: 2`).
6. **Promo image fallback**: If no image is available, a placeholder SVG is shown.
7. **Title fallback chain**: `custom_title` → `collection.title` → `Collection title`.
8. **CSS variable mapping**: Button colors are set via `--button`/`--button-text` to match the selected `button_type`.
9. **VitePress mustache safety**: If referencing Liquid mustaches in prose/inline code, escape them like `\{\{ section.id \}\}` to avoid blank pages. [[memory:13638067]]

