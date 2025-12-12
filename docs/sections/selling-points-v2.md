# Selling Points V2 Section (`sections/selling-points-v2.liquid`)

`sections/selling-points-v2.liquid` renders a modern grid of selling point cards with optional mobile slider functionality. Each card features a title, description, decorative icon, and optional link. The section uses Swiper for mobile carousel behavior and supports customizable spacing and colors. This version offers a more streamlined design without custom icons, focusing on text content with optional interactivity.

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | `swiper7.4.1.min.css`, `section-selling-points-v2.css` |
| JS   | `swiper7.4.1.min.js` (deferred), `section-selling-points-v2.js` (module) |
| Custom Element | `<selling-points-v2>` defined in `section-selling-points-v2.js` |
| Blocks | `selling_point` block type (no limit) |
| Data | Relies on `section.blocks` for selling points and `section.settings` for display options |

- Swiper library handles mobile slider functionality when enabled.
- Custom element manages slider initialization based on viewport size.
- Desktop view shows grid; mobile can switch between grid and slider modes.

---

## Dynamic Styles

The section uses inline styles for dynamic values:

```liquid
<selling-points-v2
  data-section-id="{{ section.id }}"
  data-enable-mobile-slider="{{ enable_mobile_slider }}"
  class="selling-points-v2-section"
  style="
    padding-top: {{ padding_top }}px;
    padding-bottom: {{ padding_bottom }}px;
    background-color: {{ background_color }};
    color: {{ text_color }};
  "
>

<h3 class="selling-points-v2__title" style="color: {{ title_color }};">

<p class="selling-points-v2__description" style="color: {{ text_color }};">

<span class="selling-points-v2__icon" style="color: {{ text_color }};">
```

- `padding-top` / `padding-bottom`: Section spacing (0–100px, default 40px).
- `background-color`: Section background (default: #FEFEFE).
- `text_color`: Description and icon color (default: #000000).
- `title_color`: Title color (default: #000000).

---

## Markup Structure

```liquid
{%- if blocks_to_show > 0 -%}
  <selling-points-v2
    data-section-id="{{ section.id }}"
    data-enable-mobile-slider="{{ enable_mobile_slider }}"
    class="selling-points-v2-section"
    style="..."
  >
    <div class="page-width">
      <div
        id="selling-points-v2-{{ section.id }}"
        class="selling-points-v2__container {% if enable_mobile_slider %}selling-points-v2__container--slider{% endif %}"
      >
        <div class="selling-points-v2__grid swiper-wrapper">
          {%- for block in section.blocks -%}
            <!-- Selling point card -->
          {%- endfor -%}
        </div>

        {%- if enable_mobile_slider -%}
          <div class="selling-points-v2__pagination swiper-pagination"></div>
        {%- endif -%}
      </div>
    </div>
  </selling-points-v2>
{%- endif -%}
```

- Section uses custom element `<selling-points-v2>` for JavaScript control.
- Container uses unique ID based on section ID for multiple instances.
- Swiper classes (`swiper-wrapper`, `swiper-slide`) applied for slider functionality.
- Pagination dots only render when mobile slider is enabled.

### Selling Point Card

```liquid
<div class="selling-points-v2__item swiper-slide" {{ block.shopify_attributes }}>
  {%- if link_url != blank -%}
    <a href="{{ link_url }}" class="selling-points-v2__content selling-points-v2__content--link">
  {%- else -%}
    <div class="selling-points-v2__content">
  {%- endif -%}
    {%- if title != blank -%}
      <h3 class="selling-points-v2__title" style="color: {{ title_color }};">{{ title | escape }}</h3>
    {%- endif -%}

    {%- if description != blank -%}
      <p class="selling-points-v2__description" style="color: {{ text_color }};">{{ description | escape }}</p>
    {%- endif -%}

    <div class="selling-points-v2__icon-wrapper">
      <span class="selling-points-v2__icon" style="color: {{ text_color }};">
        {{ 'icon-details.svg' | inline_asset_content }}
      </span>
    </div>
  {%- if link_url != blank -%}
    </a>
  {%- else -%}
    </div>
  {%- endif -%}
</div>
```

- **Conditional linking**: Card becomes clickable when `link_url` is provided; wraps content in `<a>` tag.
- **Link styling**: Adds `selling-points-v2__content--link` class when card is clickable.
- **Decorative icon**: Uses `icon-details.svg` inline SVG asset (not customizable per block).
- **Conditional rendering**: Title and description only render when content is provided.
- **Text escaping**: All user input is escaped for security.

---

## JavaScript Behavior

The section uses a custom element `<selling-points-v2>` defined in `section-selling-points-v2.js`:

- **Mobile slider**: Initializes Swiper carousel on mobile devices when `enable_mobile_slider` is true.
- **Responsive behavior**: Detects viewport size and enables/disables slider accordingly.
- **Section ID tracking**: Uses `data-section-id` attribute to support multiple instances.
- **Module loading**: JavaScript loads as ES module for modern browser support.

Swiper handles:
- Touch/swipe navigation on mobile
- Pagination dots
- Responsive breakpoints
- Slide transitions

---

## Schema

```json
{
  "name": "Selling Points V2",
  "tag": "section",
  "class": "selling-points-v2",
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
      "default": "#FEFEFE"
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
      "content": "Mobile Settings"
    },
    {
      "type": "checkbox",
      "id": "enable_mobile_slider",
      "label": "Enable Mobile Slider",
      "default": true,
      "info": "When enabled, cards will display as a slider on mobile devices. When disabled, cards will stack vertically."
    }
  ],
  "blocks": [
    {
      "type": "selling_point",
      "name": "Selling Point",
      "settings": [
        {
          "type": "text",
          "id": "title",
          "label": "Title",
          "default": "15% OFF FIRST ORDER"
        },
        {
          "type": "textarea",
          "id": "description",
          "label": "Description",
          "default": "Subscribe to our mailing list for 15% off your first order"
        },
        {
          "type": "url",
          "id": "link_url",
          "label": "Link URL",
          "info": "Optional: Add a link to make the entire card clickable"
        }
      ]
    }
  ],
  "presets": [
    {
      "name": "Selling Points V2",
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
| `background_color` | color | #FEFEFE | Section background color |
| `text_color` | color | #000000 | Description and icon color |
| `title_color` | color | #000000 | Title color |
| `enable_mobile_slider` | checkbox | `true` | Toggle mobile slider/carousel mode |

### Blocks

- **`selling_point`**: Individual selling point block (no limit)
  - `title`: Text field for selling point title (default: "15% OFF FIRST ORDER")
  - `description`: Textarea for selling point description
  - `link_url`: Optional URL to make entire card clickable

### Presets

- Includes a preset with 4 empty selling point blocks for quick setup.

---

## Implementation Notes

1. **Swiper dependency**: Requires Swiper 7.4.1 library. Ensure both CSS and JS files are loaded before the custom element initializes.

2. **Custom element**: The `<selling-points-v2>` element must be defined in `section-selling-points-v2.js`. Ensure the module loads correctly and handles Swiper initialization.

3. **Multiple instances**: Section ID is used to create unique Swiper instances. Multiple sections on the same page will work independently.

4. **Mobile slider behavior**: When enabled, cards display as a carousel on mobile devices. When disabled, cards stack vertically. Desktop always shows grid layout.

5. **Fixed icon**: All cards use the same decorative icon (`icon-details.svg`). Unlike the original selling-points section, icons are not customizable per block.

6. **Interactive cards**: Cards can be made clickable by adding a `link_url`. The entire card becomes a link when URL is provided.

7. **Link styling**: Cards with links receive the `selling-points-v2__content--link` class for hover/active states. Ensure CSS provides appropriate visual feedback.

8. **Responsive layout**: Grid layout is controlled via `section-selling-points-v2.css`. Ensure the CSS handles responsive breakpoints and slider/grid modes.

9. **Pagination dots**: Swiper pagination dots only appear when mobile slider is enabled. Position and style controlled via CSS.

10. **Translation keys**: Section name and labels are hardcoded in English. Consider using translation filters (`t:`) for localization.

11. **Shopify attributes**: Block elements include `block.shopify_attributes` for proper block management in the theme editor.

12. **Unlimited blocks**: No block limit; merchants can add as many selling points as needed.

13. **Script loading**: Swiper script loads with `defer` attribute, while custom element loads as ES module. Ensure proper load order to avoid initialization issues.

14. **Swiper initialization**: JavaScript should check if Swiper library is loaded before initializing. Handle mobile viewport detection to enable/disable slider dynamically.

15. **Conditional rendering**: Section only renders when `blocks_to_show > 0`. Empty sections won't display.

16. **Color customization**: Background, title, and description colors can all be customized independently for maximum flexibility.

17. **Accessibility**: Ensure clickable cards have proper focus states and keyboard navigation. Consider adding `aria-label` attributes to cards with links for better screen reader support.

---

## Comparison with Original Selling Points Section

| Feature | Selling Points | Selling Points V2 |
|---------|----------------|-------------------|
| Custom icons per block | ✅ Yes | ❌ No (fixed icon) |
| Mobile slider | ❌ No | ✅ Yes (optional) |
| Clickable cards | ❌ No | ✅ Yes (optional) |
| Icon size control | ✅ Yes | ❌ No |
| JavaScript required | ❌ No | ✅ Yes (for slider) |
| Use case | Feature lists, USPs | Promotions, CTAs |

**Use Selling Points when:**
- You need custom icons for each point
- You want a simple, JavaScript-free section
- You need to control icon sizes

**Use Selling Points V2 when:**
- You want mobile slider functionality
- You need clickable cards linking to pages
- You prefer a more modern, streamlined design
- Content is promotional in nature

