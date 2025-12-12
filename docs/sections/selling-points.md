# Selling Points Section (`sections/selling-points.liquid`)

`sections/selling-points.liquid` renders a grid of selling point cards with icons, titles, and descriptions. The section supports customizable spacing, colors, and icon sizes, making it ideal for displaying key features, benefits, or USPs. Each selling point is defined via blocks with optional custom icons.

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | `section-selling-points.css` |
| Blocks | `selling_point` block type (no limit) |
| Data | Relies on `section.blocks` for selling points and `section.settings` for styling options |

- No JavaScript dependencies; the section is purely presentational.
- Selling points are added individually via blocks, allowing merchants to add as many as needed.

---

## Dynamic Styles

The section uses CSS custom properties set via inline styles:

```liquid
<div
  class="selling-points-section"
  style="
    --selling-points-padding-top: {{ padding_top }}px;
    --selling-points-padding-bottom: {{ padding_bottom }}px;
    --selling-points-background-color: {{ background_color }};
    --selling-points-text-color: {{ text_color }};
    --selling-points-title-color: {{ title_color }};
    --selling-points-icon-size: {{ icon_size }}px;
  "
>
```

- `--selling-points-padding-top`: Top padding (0–100px, default 40px).
- `--selling-points-padding-bottom`: Bottom padding (0–100px, default 40px).
- `--selling-points-background-color`: Section background color (default: #FFFFFF).
- `--selling-points-text-color`: Description text color (default: #000000).
- `--selling-points-title-color`: Title color (default: #000000).
- `--selling-points-icon-size`: Icon size (40–120px, default 60px).

---

## Markup Structure

```liquid
{%- if blocks_to_show > 0 -%}
  <div class="selling-points-section" style="...">
    <div class="page-width">
      <div class="selling-points__grid">
        {%- for block in section.blocks -%}
          <!-- Selling point item -->
        {%- endfor -%}
      </div>
    </div>
  </div>
{%- endif -%}
```

- Section only renders if at least one selling point block is added.
- Grid layout adapts responsively based on CSS.

### Selling Point Item

```liquid
<div class="selling-points__item" {{ block.shopify_attributes }}>
  <div class="selling-points__icon-wrapper">
    {%- if icon != blank -%}
      <img
        srcset="
          {%- if icon.width >= 50 -%}{{ icon | image_url: width: 50 }} 50w,{%- endif -%}
          {%- if icon.width >= 100 -%}{{ icon | image_url: width: 100 }} 100w,{%- endif -%}
          {%- if icon.width >= 150 -%}{{ icon | image_url: width: 150 }} 150w,{%- endif -%}
          {{ icon | image_url }} {{ icon.width }}w
        "
        src="{{ icon | image_url: width: 100 }}"
        sizes="{{ icon_size }}px"
        alt="{{ icon.alt | escape }}"
        loading="lazy"
        width="{{ icon.width }}"
        height="{{ icon.height }}"
        class="selling-points__icon"
      >
    {%- else -%}
      <div class="selling-points__icon-placeholder">
        {{ 'image' | placeholder_svg_tag: 'placeholder-svg' }}
      </div>
    {%- endif -%}
  </div>

  <div class="selling-points__content">
    {%- if title != blank -%}
      <h3 class="selling-points__title">{{ title | escape | default: 'Selling Point Title' }}</h3>
    {%- endif -%}

    {%- if description != blank -%}
      <p class="selling-points__description">
        {{ description | escape | default: 'Selling point description text' }}
      </p>
    {%- endif -%}
  </div>
</div>
```

- **Icon handling**: Uses custom uploaded icon when provided, otherwise shows placeholder SVG.
- **Responsive images**: Srcset with breakpoints (50w, 100w, 150w) sized based on `icon_size` setting.
- **Conditional rendering**: Title and description only render when content is provided.
- **Text escaping**: All user input is escaped for security.
- **Defaults**: Falls back to placeholder text ("Selling Point Title" / "Selling point description text") when content is empty.

---

## Behavior

- Purely presentational; there's no JavaScript.
- Section only renders when at least one selling point block is added.
- Grid layout is responsive and adapts to different screen sizes via CSS.
- All colors, spacing, and icon sizes are customizable via settings.

---

## Schema

```json
{
  "name": "Selling Points",
  "tag": "section",
  "class": "selling-points",
  "settings": [
    {
      "type": "header",
      "content": "Spacing Settings"
    },
    {
      "type": "range",
      "id": "padding_top",
      "label": "Padding Top",
      "min": 0,
      "max": 100,
      "step": 4,
      "unit": "px",
      "default": 40
    },
    {
      "type": "range",
      "id": "padding_bottom",
      "label": "Padding Bottom",
      "min": 0,
      "max": 100,
      "step": 4,
      "unit": "px",
      "default": 40
    },
    {
      "type": "header",
      "content": "Color Settings"
    },
    {
      "type": "color",
      "id": "background_color",
      "label": "Background Color",
      "default": "#FFFFFF"
    },
    {
      "type": "color",
      "id": "text_color",
      "label": "Text Color",
      "default": "#000000"
    },
    {
      "type": "color",
      "id": "title_color",
      "label": "Title Color",
      "default": "#000000"
    },
    {
      "type": "header",
      "content": "Icon Settings"
    },
    {
      "type": "range",
      "id": "icon_size",
      "label": "Icon Size",
      "min": 40,
      "max": 120,
      "step": 10,
      "unit": "px",
      "default": 60
    }
  ],
  "blocks": [
    {
      "type": "selling_point",
      "name": "Selling Point",
      "settings": [
        {
          "type": "image_picker",
          "id": "icon",
          "label": "Icon"
        },
        {
          "type": "text",
          "id": "title",
          "label": "Title",
          "default": "Selling Point Title"
        },
        {
          "type": "textarea",
          "id": "description",
          "label": "Description",
          "default": "Selling point description text"
        }
      ]
    }
  ],
  "presets": [
    {
      "name": "Selling Points",
      "blocks": [
        { "type": "selling_point" },
        { "type": "selling_point" },
        { "type": "selling_point" },
        { "type": "selling_point" }
      ]
    }
  ]
}
```

### Section Settings

| Setting ID | Type | Default | Purpose |
|------------|------|---------|---------|
| `padding_top` | range (px) | 40 | Top section padding (0–100px, step 4) |
| `padding_bottom` | range (px) | 40 | Bottom section padding (0–100px, step 4) |
| `background_color` | color | #FFFFFF | Section background color |
| `text_color` | color | #000000 | Description text color |
| `title_color` | color | #000000 | Title color |
| `icon_size` | range (px) | 60 | Icon size (40–120px, step 10) |

### Blocks

- **`selling_point`**: Individual selling point block (no limit)
  - `icon`: Image picker for custom icon
  - `title`: Text field for selling point title
  - `description`: Textarea for selling point description

### Presets

- Includes a preset with 4 empty selling point blocks for quick setup.

---

## Implementation Notes

1. **Icon optimization**: Icons should be uploaded at appropriate sizes (ideally 100–150px square) for best quality. Larger images will be resized automatically.

2. **Responsive grid**: Grid layout is controlled via `section-selling-points.css`. Ensure the CSS handles responsive breakpoints appropriately.

3. **Placeholder handling**: When no icon is uploaded, a placeholder SVG is shown. The placeholder uses Shopify's `image` placeholder.

4. **Text defaults**: The `default` filter is applied after `escape`, which may cause default text to appear even when fields have content. Consider removing the `| default: '...'` filters if not needed.

5. **Icon srcset**: Icon images generate srcset breakpoints at 50w, 100w, and 150w, with the `sizes` attribute matching the `icon_size` setting for optimal image delivery.

6. **Unlimited blocks**: Unlike some sections, this one has no block limit. Merchants can add as many selling points as needed.

7. **CSS custom properties**: All dynamic styling is controlled via CSS custom properties, making it easy to theme and customize.

8. **Conditional rendering**: Section only renders when `blocks_to_show > 0`. Empty sections won't display.

9. **Translation keys**: Section name and labels are hardcoded in English. Consider using translation filters (`t:`) for localization.

10. **Shopify attributes**: Block elements include `block.shopify_attributes` for proper block management in the theme editor.

11. **Color customization**: Background, title, and description colors can all be customized independently for maximum flexibility.

12. **Spacing control**: Padding can be adjusted in 4px increments from 0 to 100px for both top and bottom.

