# Collections Grid Section (`sections/collections.liquid`)

`sections/collections.liquid` renders a simple grid of every collection accessible through the global `collections` object. Each card links to the collection page, shows the featured image, and includes a short description preview with an arrow icon.

---

## Dependencies & Assets

| Type | Files / Notes |
|------|---------------|
| Icons | `icon-arrow.svg` (inline via `inline_asset_content`) |
| Data  | Relies on the global `collections` object (shop-level collections) |

- No external CSS/JS assets are loaded; all styling lives inside the `{% stylesheet %}` block scoped to this section.

---

## Dynamic Styles

The section sets a CSS custom property for grid gap via the section setting:

```liquid
<div
  class="collections"
  style="--grid-gap: {{ section.settings.grid_gap }}px"
>
  …
</div>

{% stylesheet %}
.collections {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--grid-gap);
}
@media screen and (max-width: 768px) {
  .collections {
    grid-template-columns: repeat(2, 1fr);
    padding: 0 10px;
    gap: 4px;
  }
}
{% endstylesheet %}
```

- Desktop uses a 3-column grid with customizable gap.
- Mobile collapses to two columns with reduced spacing.

---

## Markup Structure

```liquid
<h1 class="collections__heading">{{ 'collections.title' | t }}</h1>

<div
  class="collections"
  style="--grid-gap: {{ section.settings.grid_gap }}px"
>
  {% for collection in collections %}
    <a class="collection-card" href="{{ collection.url }}">
      {% if collection.featured_image %}
        <div class="collection-card__image">
          {{ collection.featured_image
            | image_url: width: 600, height: 600, crop: 'center'
            | image_tag
          }}
        </div>
      {% endif %}

      <div class="collection-card__content">
        <span>{{ collection.title }}</span>
        <span class="collection-card__arrow">
          {{ 'icon-arrow.svg' | inline_asset_content }}
        </span>
        {% if collection.description %}
          <p>{{ collection.description | strip_html | truncatewords: 15 }}</p>
        {% endif %}
      </div>
    </a>
  {% endfor %}
</div>
```

- Heading is localized via `collections.title`.
- Each card:
  - Optional image wrapper maintains a square ratio via pseudo-element and absolutely positioned `<img>`.
  - Content row contains title + arrow icon; description is truncated to 15 words.
- Cards link directly to `collection.url`; there’s no pagination or filtering UI.

---

## Behavior

- Purely presentational; there’s no JavaScript.
- All text uses translation keys, so strings can be localized.
- Responsive behavior handled in CSS (`@media screen and (max-width: 768px)`).

---

## Settings Schema

```json
{
  "name": "t:general.collections_grid",
  "settings": [
    {
      "type": "range",
      "id": "grid_gap",
      "label": "t:labels.grid_gap",
      "min": 0,
      "max": 50,
      "step": 5,
      "unit": "px",
      "default": 10
    }
  ],
  "presets": [
    { "name": "t:general.collections_grid" }
  ]
}
```

- Single range setting controls spacing between cards (0–50px, default 10px).
- Preset name is localized via `t:general.collections_grid`.

---

## Implementation Notes

1. The section iterates over `collections`, which includes all collections; if you need a curated list, consider switching to a `collection_list` setting instead.
2. Image tags use fixed width/height (600px square) with `crop: 'center'` to maintain consistent card ratios.
3. The CSS uses BEM-style class names (`collection-card__image`, `collection-card__content`) scoped via the stylesheet block inside the section file.
4. Ensure `icon-arrow.svg` exists in `assets/`; missing icons will break the arrow display.

