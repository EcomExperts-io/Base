# Hero Section (`sections/hero.liquid`)

`sections/hero.liquid` renders a hero banner section with customizable background (image or video), text content, call-to-action button, and optional endorsement block. The section supports flexible content alignment, overlay controls, and responsive image handling. Background videos can be hosted or embedded from YouTube/Vimeo.

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | `section-hero.css`, inline `<style>` block for CSS custom properties |
| Data | Relies on `section.settings` for all configuration |

- No JavaScript dependencies; the section is purely presentational.
- Video backgrounds (YouTube/Vimeo) may require custom JavaScript for optimal background video behavior.
- All styling controlled via CSS custom properties set dynamically from section settings.

---

## Dynamic Styles

The section uses CSS custom properties set via a `<style>` block:

```liquid
<style>
  #{{ section_id }} {
    --hero-text-color: {{ section.settings.text_color }};
    --hero-overlay-color: {{ section.settings.overlay_color }};
    --hero-overlay-opacity: {{ section.settings.overlay_opacity | divided_by: 100.0 }};
    --hero-content-alignment: {{ content_alignment }};
    --hero-vertical-alignment: {{ vertical_alignment }};
    --hero-button-color: {{ button_color }};
    --hero-button-text-color: {{ button_text_color }};
  }
</style>
```

- **Text color**: Applied to all text content via `--hero-text-color`.
- **Overlay color**: Background overlay color via `--hero-overlay-color`.
- **Overlay opacity**: Converted from percentage (0–90%) to decimal (0.0–0.9) via `divided_by: 100.0`.
- **Content alignment**: Horizontal alignment (left, center, right) via `--hero-content-alignment`.
- **Vertical alignment**: Vertical positioning (top, center, bottom) via `--hero-vertical-alignment`.
- **Button colors**: Background and text colors for CTA button.

---

## Markup Structure

```liquid
<div id="{{ section_id }}" class="hero-banner hero-banner-section">
  <div class="hero-banner__background">
    <!-- Background image or video -->
    <div class="hero-banner__background-overlay"></div>
  </div>

  <div class="hero-banner__content hero-banner__content--h-{{ content_alignment }} hero-banner__content--v-{{ vertical_alignment }}">
    <!-- Stars/rating text -->
    <!-- Heading -->
    <!-- Subheading -->
    <!-- Button -->
  </div>

  <!-- Endorsement block (conditional) -->
</div>
```

- Section ID generated as `hero-banner-\{\{ section.id \}\}` for unique targeting.
- Content alignment classes applied: `hero-banner__content--h-{alignment}` and `hero-banner__content--v-{alignment}`.

### Background

```liquid
<div class="hero-banner__background">
  {% if background_type == 'video' %}
    {% if video_background_hosted != blank %}
      {{ video_background_hosted | video_tag: autoplay: true, loop: true, muted: true, playsinline: true }}
    {% elsif video_background_url != blank %}
      <!-- YouTube/Vimeo iframe embedding -->
    {% endif %}
  {% else %}
    {% if image_background != blank %}
      {{ image_background | image_url: width: 2000 | image_tag: loading: 'lazy', widths: '400, 600, 800, 1000, 1200, 1400, 1600, 1800, 2000' }}
    {% else %}
      {{ 'lifestyle-1' | placeholder_svg_tag: 'placeholder-svg' }}
    {% endif %}
  {% endif %}
  <div class="hero-banner__background-overlay"></div>
</div>
```

- **Video priority**: Hosted video preferred, falls back to external URL (YouTube/Vimeo).
- **Hosted video**: Uses Shopify's `video_tag` filter with autoplay, loop, muted, and playsinline attributes.
- **YouTube embedding**: Extracts video ID and creates iframe with autoplay, loop, and background mode parameters.
- **Vimeo embedding**: Extracts video ID and creates iframe with background mode enabled.
- **Image fallback**: Shows placeholder SVG when no image is selected.
- **Responsive images**: Full srcset with breakpoints from 400w to 2000w.
- **Overlay**: Separate div for CSS-controlled overlay styling.

### Content

```liquid
<div class="hero-banner__content hero-banner__content--h-{{ content_alignment }} hero-banner__content--v-{{ vertical_alignment }}">
  {% if stars_text != blank %}
    <div class="hero-banner__stars"><span class="stars">★★★★★</span> {{ stars_text }}</div>
  {% endif %}

  {% if heading != blank %}
    <h2 class="hero-banner__heading">{{ heading | escape }}</h2>
  {% endif %}

  {% if subheading != blank %}
    <p class="hero-banner__subheading">{{ subheading | escape }}</p>
  {% endif %}

  {% if button_text != blank and button_link != blank %}
    <a href="{{ button_link }}" class="hero-banner__button">
      {{ button_text | escape }}
    </a>
  {% endif %}
</div>
```

- **Stars/rating**: Hardcoded 5-star display (★★★★★) with optional text.
- **Conditional rendering**: Each element only displays when content is provided.
- **Button**: Only renders when both text and link are provided.
- **Text escaping**: All user input is escaped for security.

### Endorsement Block

```liquid
{% if show_endorsement %}
  <div class="hero-banner__endorsement">
    {% if endorsement_name != blank %}
      <div class="hero-banner__endorsement-name">{{ endorsement_name | escape }}</div>
    {% endif %}
    {% if endorsement_signature_image != blank %}
      <div class="hero-banner__endorsement-signature">
        {{ endorsement_signature_image | image_url: width: 200 | image_tag: loading: 'lazy', widths: '50, 100, 150, 200' }}
      </div>
    {% endif %}
  </div>
{% endif %}
```

- Conditionally renders when `show_endorsement` is enabled.
- Displays endorser name and optional signature image.
- Signature image uses responsive srcset (50w to 200w).

---

## Behavior

- **Purely presentational**: No JavaScript required for basic functionality.
- **Video backgrounds**: External video URLs (YouTube/Vimeo) use iframe embedding; may require custom JavaScript for true background video behavior.
- **Responsive images**: Full srcset implementation for optimal image delivery.
- **CSS custom properties**: All styling controlled via CSS variables for easy theming.
- **Conditional rendering**: Content elements only render when data is provided.

---

## Schema

```json
{
  "name": "Hero",
  "tag": "section",
  "class": "section-hero-banner",
  "settings": [
    {
      "type": "radio",
      "id": "background_type",
      "label": "Background Type",
      "options": [
        { "value": "image", "label": "Image" },
        { "value": "video", "label": "Video" }
      ],
      "default": "image"
    },
    {
      "type": "image_picker",
      "id": "image_background",
      "label": "Image Background"
    },
    {
      "type": "video",
      "id": "video_background_hosted",
      "label": "Hosted Video Background"
    },
    {
      "type": "url",
      "id": "video_background_url",
      "label": "Video URL (YouTube/Vimeo)"
    },
    {
      "type": "color",
      "id": "overlay_color",
      "label": "Background Overlay Color",
      "default": "#000000"
    },
    {
      "type": "range",
      "id": "overlay_opacity",
      "min": 0,
      "max": 90,
      "step": 5,
      "unit": "%",
      "label": "Background Overlay Opacity",
      "default": 30
    },
    {
      "type": "select",
      "id": "content_alignment",
      "label": "Horizontal Alignment",
      "options": [
        { "value": "left", "label": "Left" },
        { "value": "center", "label": "Center" },
        { "value": "right", "label": "Right" }
      ],
      "default": "center"
    },
    {
      "type": "select",
      "id": "vertical_alignment",
      "label": "Vertical Alignment",
      "options": [
        { "value": "top", "label": "Top" },
        { "value": "center", "label": "Center" },
        { "value": "bottom", "label": "Bottom" }
      ],
      "default": "bottom"
    },
    {
      "type": "color",
      "id": "text_color",
      "label": "Text Color",
      "default": "#FFFFFF"
    },
    {
      "type": "text",
      "id": "stars_text",
      "label": "Rating Text",
      "default": "Trusted By 30,539+ Players"
    },
    {
      "type": "text",
      "id": "heading",
      "label": "Heading",
      "default": "END OF SEASON SALE"
    },
    {
      "type": "text",
      "id": "subheading",
      "label": "Subheading",
      "default": "Pro level protection for every level"
    },
    {
      "type": "text",
      "id": "button_text",
      "label": "Button Text",
      "default": "SAVE OVER 30%"
    },
    {
      "type": "url",
      "id": "button_link",
      "label": "Button Link"
    },
    {
      "type": "color",
      "id": "button_color",
      "label": "Button Background Color",
      "default": "#FFFFFF"
    },
    {
      "type": "color",
      "id": "button_text_color",
      "label": "Button Text Color",
      "default": "#000000"
    },
    {
      "type": "checkbox",
      "id": "show_endorsement",
      "label": "Show Endorsement Block",
      "default": true
    },
    {
      "type": "text",
      "id": "endorsement_name",
      "label": "Endorser Name",
      "default": "TJ Oshie"
    },
    {
      "type": "image_picker",
      "id": "endorsement_signature_image",
      "label": "Endorser Signature Image"
    }
  ],
  "presets": [
    {
      "name": "Hero Banner"
    }
  ]
}
```

### Section Settings

| Setting ID | Type | Default | Purpose |
|------------|------|---------|---------|
| `background_type` | radio | `image` | Background media type (image or video) |
| `image_background` | image_picker | — | Background image |
| `video_background_hosted` | video | — | Hosted video file |
| `video_background_url` | url | — | External video URL (YouTube/Vimeo) |
| `overlay_color` | color | #000000 | Background overlay color |
| `overlay_opacity` | range (%) | 30 | Overlay opacity (0–90%, step 5) |
| `content_alignment` | select | `center` | Horizontal content alignment (left, center, right) |
| `vertical_alignment` | select | `bottom` | Vertical content alignment (top, center, bottom) |
| `text_color` | color | #FFFFFF | Text color for all content |
| `stars_text` | text | "Trusted By 30,539+ Players" | Rating/trust text |
| `heading` | text | "END OF SEASON SALE" | Main heading |
| `subheading` | text | "Pro level protection for every level" | Subheading text |
| `button_text` | text | "SAVE OVER 30%" | CTA button text |
| `button_link` | url | — | CTA button destination |
| `button_color` | color | #FFFFFF | Button background color |
| `button_text_color` | color | #000000 | Button text color |
| `show_endorsement` | checkbox | `true` | Toggle endorsement block |
| `endorsement_name` | text | "TJ Oshie" | Endorser name |
| `endorsement_signature_image` | image_picker | — | Signature image |

### Presets

- Includes a preset named "Hero Banner" for quick section addition.

---

## Implementation Notes

1. **Section ID generation**: Section ID is constructed as `hero-banner-\{\{ section.id \}\}` to ensure uniqueness and avoid conflicts.

2. **Video background limitations**: External video URLs (YouTube/Vimeo) use iframe embedding, which may not provide true background video behavior. The code includes comments noting that custom JavaScript may be required. Hosted videos are recommended for better performance and reliability.

3. **YouTube video ID extraction**: The code extracts video ID from various YouTube URL formats:
   - `youtube.com/watch?v=VIDEO_ID`
   - `youtu.be/VIDEO_ID`
   - Handles query parameters and URL variations

4. **Vimeo video ID extraction**: Extracts video ID from Vimeo URLs by taking the last segment after splitting by `/`.

5. **Overlay opacity calculation**: Overlay opacity is converted from percentage (0–90%) to decimal (0.0–0.9) using `divided_by: 100.0` for CSS usage.

6. **Hardcoded stars**: The rating display uses hardcoded 5 stars (★★★★★). Consider making this configurable if different ratings are needed.

7. **Placeholder image**: Falls back to `lifestyle-1` placeholder SVG when no background image is selected. Ensure this placeholder exists in Shopify's placeholder library.

8. **Responsive images**: Background images use full srcset with breakpoints (400w to 2000w) for optimal performance across devices.

9. **Content alignment classes**: Alignment is applied via CSS classes (`hero-banner__content--h-{alignment}` and `hero-banner__content--v-{alignment}`) in addition to CSS custom properties.

10. **Button conditional**: Button only renders when both `button_text` and `button_link` are provided. Ensure both are set for button to display.

11. **Text escaping**: All user-provided text (heading, subheading, button_text, etc.) is escaped using the `escape` filter for security.

12. **Endorsement block**: Endorsement section is completely optional and only renders when `show_endorsement` is enabled. Both name and signature image are optional within the endorsement block.

13. **CSS custom properties**: All dynamic styling is controlled via CSS custom properties, making it easy to theme and customize via CSS without modifying Liquid code.

14. **Video autoplay**: Hosted videos use `autoplay: true` in the `video_tag` filter. Ensure videos are optimized for autoplay (muted, appropriate format).

15. **Translation keys**: Section name and labels are hardcoded in English. Consider using translation filters (`t:`) for localization if needed.

16. **Video iframe parameters**: YouTube and Vimeo iframes include parameters for autoplay, looping, and background mode. Note that some browsers may restrict autoplay behavior.

