# Announcement Bar Section (`sections/announcement-bar.liquid`)

`sections/announcement-bar.liquid` renders an optional announcement bar (header group) that can cycle through multiple announcements. It supports background/text colors, an optional link, and an optional emoji per announcement. Rotation is handled with Alpine.js state (`x-data`) and interval timers, with previous/next arrow controls when multiple announcements exist.

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | Inline `{% style %}` block inside the section |
| JS   | Alpine.js directives in markup (`x-data`, `x-init`, `x-show`, `x-transition`) |
| Blocks | `announcement` block type |
| Data | Relies on `section.settings` and `section.blocks` |

Notes:

- This section assumes Alpine.js is available globally in the theme (since it uses Alpine directives).

---

## Dynamic Styles

The section scopes colors to the section wrapper using the section’s Shopify wrapper ID:

```liquid
{% style %}
  #shopify-section-{{ section.id }} {
    background-color: {{ section.settings.background_color }};
    color: {{ section.settings.text_color }};
  }
{% endstyle %}
```

- The rest of the CSS for layout, arrows, and animations is defined in the same `{% style %}` block.

---

## Markup Structure

The section only renders when enabled and there is at least one announcement block:

```liquid
{% if section.settings.show_announcement and section.blocks.size > 0 %}
  <section class="announcement-bar-section">
    <div class="announcement-bar" x-data="...">
      <div class="page-width announcement-bar__content">
        <!-- Prev arrow (conditional) -->
        <!-- Messages -->
        <!-- Next arrow (conditional) -->
      </div>
    </div>
  </section>
{% endif %}
```

### Prev/next controls (only when multiple blocks)

```liquid
{% if section.blocks.size > 1 %}
  <button
    @click="idx = idx === 0 ? total - 1 : idx - 1"
    aria-label="Previous announcement"
    class="announcement-bar__arrow announcement-bar__arrow--prev"
    x-show="total > 1"
    type="button"
  >
    <!-- inline SVG -->
  </button>
{% endif %}
```

Next is symmetrical (`idx = idx === total - 1 ? 0 : idx + 1`).

### Announcement items

Each block renders one “message” container, and Alpine toggles visibility by index:

```liquid
{% for block in section.blocks %}
  <div
    {{ block.shopify_attributes }}
    x-show="idx === {{ forloop.index0 }}"
    x-transition:fade.300ms
    :class="idx === {{ forloop.index0 }} ? 'fade-in' : ''"
  >
    {{ block.settings.text }}

    {% if block.settings.link_text and block.settings.link_url %}
      <a href="{{ block.settings.link_url }}" class="announcement-bar__link" style="color: {{ text_color }};">
        {{ block.settings.link_text }}
      </a>
    {% endif %}

    {% if block.settings.emoji != blank %}
      <span class="announcement-bar__emoji">{{ block.settings.emoji }}</span>
    {% endif %}
  </div>
{% endfor %}
```

Notes:

- `block.settings.text` is a plain text setting and is output directly.
- Link color is set inline to match `section.settings.text_color`.

---

## Behavior

### Rotation logic (Alpine)

The announcement bar uses an Alpine state object with:
- `idx`: current announcement index
- `total`: number of announcements
- `interval`: timer handle
- `startAutoScroll()` / `stopAutoScroll()`

Auto-rotate is started via `x-init="startAutoScroll()"` and pauses on:
- mouse enter / leave
- focus in / out

Interval is based on `auto_rotate_interval` seconds.

### Height CSS variable

The section sets a CSS variable `--announcement-bar-height` to the height of `.announcement-bar__content`. This can be used elsewhere in the theme (e.g., to offset sticky header spacing).

---

## Schema

```json
{
  "name": "Announcement Bar",
  "enabled_on": { "groups": ["header"] },
  "settings": [
    { "type": "checkbox", "id": "show_announcement", "label": "Show announcement", "default": true },
    { "type": "color", "id": "background_color", "label": "Background color", "default": "#000000" },
    { "type": "color", "id": "text_color", "label": "Text color", "default": "#FFFFFF" },
    { "type": "range", "id": "auto_rotate_interval", "label": "Auto-rotate interval (seconds)", "min": 2, "max": 15, "step": 1, "default": 4 }
  ],
  "blocks": [
    {
      "type": "announcement",
      "name": "Announcement",
      "settings": [
        { "type": "text", "id": "text", "label": "Text", "default": "Welcome to our store" },
        { "type": "text", "id": "link_text", "label": "Link text" },
        { "type": "url", "id": "link_url", "label": "Link URL" },
        { "type": "text", "id": "emoji", "label": "Emoji", "default": "🎉" }
      ]
    }
  ],
  "presets": [{ "name": "Announcement Bar" }]
}
```

---

## Implementation Notes

1. **Alpine dependency**: Without Alpine.js, the rotation logic and show/hide behavior won’t work.
2. **Controls**: Prev/next arrows only render when there are multiple blocks.
3. **Animation**: Uses CSS animation `fadeInAnim` and Alpine transition `x-transition:fade.300ms`.
4. **VitePress mustache safety**: If referencing Liquid mustaches in prose/inline code, escape them like `\{\{ ... \}\}` to avoid blank pages. [[memory:13638067]]

