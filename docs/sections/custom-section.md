# Custom Section (`sections/custom-section.liquid`)

`sections/custom-section.liquid` provides a flexible, full-width container section with optional background image support. It uses CSS Grid for content layout and accepts `@theme` blocks, making it a versatile foundation for custom content layouts. The section positions background images absolutely behind content and centers content using a CSS Grid variable.

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | Inline `{% stylesheet %}` block |
| Blocks | Supports `@theme` blocks via `{% content_for 'blocks' %}` |
| Data | Relies on `section.settings.background_image` and CSS variable `--content-grid` |

- No JavaScript dependencies; the section is purely presentational.
- No external CSS files; all styles are defined in the `{% stylesheet %}` block.
- Content layout depends on the `--content-grid` CSS variable being defined elsewhere in the theme.

---

## Markup Structure

```liquid
<div class="custom-section full-width">
  {% if section.settings.background_image %}
    <div class="custom-section__background">
      {{ section.settings.background_image | image_url: width: 2000 | image_tag }}
    </div>
  {% endif %}

  <div class="custom-section__content">
    {% content_for 'blocks' %}
  </div>
</div>
```

### Structure Breakdown

- **Container**: Full-width wrapper with `custom-section` and `full-width` classes.
- **Background image**: Conditionally rendered when `section.settings.background_image` is set. Image is rendered at 2000px width and positioned absolutely behind content.
- **Content area**: Uses `{% content_for 'blocks' %}` to render all blocks assigned to the section. Content is centered via CSS Grid column placement.

### Background Image

```liquid
{% if section.settings.background_image %}
  <div class="custom-section__background">
    {{ section.settings.background_image | image_url: width: 2000 | image_tag }}
  </div>
{% endif %}
```

- **Conditional rendering**: Only displays when a background image is selected in theme settings.
- **Image sizing**: Fixed width of 2000px; height scales automatically to maintain aspect ratio.
- **Positioning**: Image is centered both horizontally and vertically using CSS transforms.

### Content Blocks

```liquid
<div class="custom-section__content">
  {% content_for 'blocks' %}
</div>
```

- **Block rendering**: Uses `{% content_for 'blocks' %}` to render all `@theme` blocks assigned to the section.
- **Grid layout**: Content is placed in grid column 2, which centers it based on the `--content-grid` variable definition.
- **Flexibility**: Any `@theme` block can be added, making this section highly customizable.

---

## Behavior

- **Full-width layout**: Section spans 100% of viewport width.
- **Background image overlay**: Background images are positioned behind content and do not interfere with block rendering.
- **CSS Grid centering**: Content is centered using CSS Grid, requiring the `--content-grid` variable to be defined (typically in theme base CSS).
- **Block-based content**: All content is managed through blocks, allowing merchants to customize without editing code.
- **No JavaScript**: All rendering is server-side; no client-side interactions required.

---

## Schema

```json
{
  "name": "t:general.custom_section",
  "blocks": [{ "type": "@theme" }],
  "settings": [
    {
      "type": "image_picker",
      "id": "background_image",
      "label": "t:labels.background"
    }
  ],
  "presets": [
    {
      "name": "t:general.custom_section"
    }
  ]
}
```

### Section Settings

| Setting ID | Type | Purpose |
|------------|------|---------|
| `background_image` | image_picker | Optional background image displayed behind content |

### Blocks

- **`@theme` blocks**: Accepts any theme block type, allowing merchants to add any supported block to the section.
- **No block limit**: Merchants can add as many blocks as needed.

### Presets

- Includes a preset named `t:general.custom_section` for easy section addition.

---

## Implementation Notes

1. **Translation keys**: Section name, setting labels, and preset name use translation filters (`t:general.custom_section`, `t:labels.background`).

2. **CSS variable dependency**: The section relies on `--content-grid` being defined in the theme's CSS. This variable should define the grid columns (e.g., `1fr auto 1fr` for centered content). Ensure this variable exists in the theme's base stylesheet.

3. **Background image sizing**: Images are rendered at 2000px width. For better performance on high-DPI displays, consider:
   - Using responsive srcset
   - Adding `loading="lazy"` if the section is below the fold
   - Using `fetchpriority="low"` for below-fold images

4. **Full-width class**: The section uses a `full-width` class. Ensure this class is defined in the theme's CSS and handles full-width layout appropriately (may need to break out of page-width containers).

5. **Block flexibility**: Since the section accepts `@theme` blocks, merchants can add any block type. Consider documenting which blocks work well with this section's layout.

6. **Background image positioning**: The background image uses absolute positioning with transforms for centering. This ensures the image covers the full section area while maintaining aspect ratio. The image may be cropped if its aspect ratio doesn't match the section height.

7. **Content grid column**: All content is placed in grid column 2. If `--content-grid` is not properly defined, content may not center correctly. The typical pattern is:
   ```css
   --content-grid: 1fr minmax(0, var(--page-width)) 1fr;
   ```
   This creates equal side columns and a centered content column matching the page width.

8. **Z-index layering**: Background image uses `z-index: -1` to ensure it stays behind content. Ensure no child elements use negative z-index values that might conflict.

9. **Overflow handling**: Both the section and background container use `overflow: hidden` to prevent content from spilling outside the section bounds.

10. **Responsive considerations**: The section is full-width, but content centering depends on `--content-grid`. Ensure this variable is responsive or that the grid adapts to different screen sizes appropriately.

