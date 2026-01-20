# Brand Story V2 Section (`sections/brand-story-v2.liquid`)

`sections/brand-story-v2.liquid` renders an interactive “story list + image” section. The left side shows a list of story items (heading + richtext description) and the right side shows the corresponding image. On desktop, hovering/focusing list items updates the image; on smaller screens, items expand/collapse on click. The section uses a custom element and CSS transitions for a smooth experience.

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | `section-brand-story-v2.css`, inline `{%- style -%}` block for responsive padding |
| JS   | `section-brand-story-v2.js` (module) |
| Custom Element | `<brand-story-v2>` defined in `section-brand-story-v2.js` |
| Blocks | `story_item` block type |
| Data | Relies on `section.blocks` (content) and `section.settings` (layout + color) |

---

## Dynamic Styles

The section uses responsive padding set via a `{%- style -%}` block:

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

---

## Markup Structure

```liquid
<brand-story-v2
  class="color-{{ section.settings.color_scheme }} brand-story-v2 section-{{ section.id }}-padding"
  data-section-id="{{ section.id }}"
>
  <div class="page-width">
    <div class="brand-story-v2__container">
      <div class="brand-story-v2__left">
        <!-- List of story items -->
      </div>
      <div class="brand-story-v2__right">
        <!-- Image panel -->
      </div>
    </div>
  </div>
</brand-story-v2>
```

- **Custom element wrapper**: `<brand-story-v2>` is required for the JS behavior.
- **Section scoping**: Uses `data-section-id="\{\{ section.id \}\}"` for per-instance uniqueness.

### Left Side — Story List

```liquid
<ul class="brand-story-v2__list">
  {%- for block in section.blocks -%}
    <li
      class="brand-story-v2__item{% if forloop.first %} is-active{% endif %}"
      data-block-index="{{ forloop.index0 }}"
      {%- if block.settings.image != blank -%}
        data-image-url="{{ block.settings.image | image_url: width: 800 }}"
      {%- endif -%}
      {{ block.shopify_attributes }}
    >
      <button
        type="button"
        class="brand-story-v2__heading-button"
        aria-expanded="{% if forloop.first %}true{% else %}false{% endif %}"
      >
        <h3 class="brand-story-v2__heading">{{ block.settings.heading | default: 'Heading' }}</h3>
      </button>

      <div class="brand-story-v2__description">
        {%- if block.settings.description != blank -%}
          <div class="brand-story-v2__description-content">
            {{ block.settings.description }}
          </div>
        {%- else -%}
          <div class="brand-story-v2__description-content">
            <p>Add your description here.</p>
          </div>
        {%- endif -%}
      </div>
    </li>
  {%- endfor -%}
</ul>
```

- The first item is active by default (`is-active`) and has `aria-expanded="true"`.
- `block.settings.description` is richtext and is output unescaped (expected to contain HTML).

### Right Side — Image Panel

```liquid
<div class="brand-story-v2__image-wrapper">
  {%- for block in section.blocks -%}
    {%- if block.settings.image != blank -%}
      <img
        src="{{ block.settings.image | image_url: width: 800 }}"
        alt="{{ block.settings.image.alt | default: block.settings.heading | escape }}"
        loading="lazy"
        width="{{ block.settings.image.width }}"
        height="{{ block.settings.image.height }}"
        class="brand-story-v2__media{% unless forloop.first %} is-hidden{% endunless %}"
        data-block-index="{{ forloop.index0 }}"
      >
    {%- else -%}
      <div
        class="brand-story-v2__image-placeholder brand-story-v2__media{% unless forloop.first %} is-hidden{% endunless %}"
        data-block-index="{{ forloop.index0 }}"
      >
        {{ 'image' | placeholder_svg_tag: 'placeholder-svg' }}
      </div>
    {%- endif -%}
  {%- endfor -%}
</div>
```

- Images/placeholders are rendered for each block; only the first is visible initially (others have `is-hidden`).
- Alt text falls back to the block heading.

---

## JavaScript Behavior

The section uses a custom element `<brand-story-v2>` defined in `section-brand-story-v2.js`:

- **Desktop (window width > 900px)**:
  - `mouseenter` and `focus` on an item updates the image panel.
  - Clicking the button also updates the image.
- **Mobile (window width <= 900px)**:
  - Clicking toggles the active accordion item (`is-active`) and `aria-expanded`.

Image swapping:
- Finds the visible `.brand-story-v2__media` (not `is-hidden`) and swaps to the target `data-block-index`.
- Adds/removes animation classes (`slide-up`, `slide-up-out`) to animate transitions.

---

## Behavior

- **Interactive list**: Desktop hover/focus changes the image; mobile click expands/collapses items.
- **Accordion animation**: CSS transitions use `max-height` + `opacity`.
- **Image animation**: Uses `slide-up` / `slide-up-out` classes for swapping images.
- **Sticky left column**: CSS sets `.brand-story-v2__left` to `position: sticky`.

---

## Schema

```json
{
  "name": "Brand Story V2",
  "tag": "section",
  "class": "brand-story-v2",
  "settings": [
    { "type": "color_scheme", "id": "color_scheme", "label": "t:sections.all.colors.label", "default": "scheme-1" },
    { "type": "header", "content": "Spacing Settings" },
    { "type": "range", "id": "padding_top", "label": "Padding Top", "min": 0, "max": 100, "step": 4, "unit": "px", "default": 40 },
    { "type": "range", "id": "padding_bottom", "label": "Padding Bottom", "min": 0, "max": 100, "step": 4, "unit": "px", "default": 40 }
  ],
  "blocks": [
    {
      "type": "story_item",
      "name": "Story Item",
      "settings": [
        { "type": "text", "id": "heading", "label": "Heading", "default": "Add heading here" },
        { "type": "richtext", "id": "description", "label": "Description", "default": "<p>Add your description here.</p>" },
        { "type": "image_picker", "id": "image", "label": "Image" }
      ]
    }
  ],
  "presets": [
    {
      "name": "Brand Story V2",
      "blocks": [{ "type": "story_item" }, { "type": "story_item" }, { "type": "story_item" }, { "type": "story_item" }]
    }
  ]
}
```

### Section Settings

| Setting ID | Type | Default | Purpose |
|------------|------|---------|---------|
| `color_scheme` | color_scheme | `scheme-1` | Section color scheme |
| `padding_top` | range (px) | 40 | Top padding |
| `padding_bottom` | range (px) | 40 | Bottom padding |

### Blocks

- **`story_item`**
  - `heading`: Text heading (shown in list)
  - `description`: Richtext (accordion content)
  - `image`: Image shown in the right panel

### Presets

- Includes a preset with 4 story items.

---

## Implementation Notes

1. **Breakpoint logic**: JS uses `window.innerWidth <= 900` to switch between accordion vs hover behavior.
2. **ARIA state**: JS updates `aria-expanded` based on the active item for accessibility.
3. **Richtext output**: `block.settings.description` is output unescaped (expected HTML from the richtext editor).
4. **Media mapping**: Images are matched to list items via `data-block-index`.

