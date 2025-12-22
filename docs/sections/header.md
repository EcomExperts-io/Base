# Header Section (`sections/header.liquid`)

`sections/header.liquid` renders the site header with logo, navigation menu, search functionality, cart icon, and customer account access. It supports multiple layout configurations, sticky header behavior, and responsive design. The section uses Alpine.js for search interactions and includes JavaScript for scroll-based header behavior.

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | Inline `{% style %}` block |
| JS   | `component-localization-form.js` (module, conditional) |
| Snippets | `component-nav-drawer`, `component-nav-dropdown`, `component-nav-megamenu`, `component-localization-form`, `component-predictive-search`, `component-cart-notification`, `component-cart-drawer` |
| Icons | `icon-search.svg`, `icon-account.svg`, `icon-cart.svg`, `icon-close.svg` (inline via `inline_asset_content`) |
| Libraries | Alpine.js (for search state management) |
| Blocks | `@app` blocks (max 3) |
| Data | Relies on `section.settings`, global `settings` object, and `cart` object |

- Search functionality uses Alpine.js for state management (`x-data`, `x-show`, `x-model`).
- Sticky header behavior handled by inline JavaScript.
- Cart count updates via Liquid Ajax Cart (`data-ajax-cart-bind="item_count"`).

---

## Dynamic Styles

The section uses extensive inline styles with dynamic values. Key dynamic CSS includes:

```liquid
#shopify-section-{{ section.id }} {
  position: {% unless section.settings.sticky_header_type == 'none' %}sticky{% else %}relative{% endunless %};
  margin-bottom: {{ section.settings.margin_bottom }}px;
  {% if section.settings.show_line_separator %}
    border-bottom: 1px solid rgb(var(--color-foreground), 0.2);
  {% endif %}
}

#main-header {
  grid-template-columns: {% if section.settings.logo_position == 'middle-center' or section.settings.logo_position == 'top-center' %}
    1fr auto 1fr
  {% else %}
    auto 1fr auto
  {% endif %};
  padding-top: {{ section.settings.padding_top }}px;
  padding-bottom: {{ section.settings.padding_bottom }}px;
}

.header-logo {
  height: {{ settings.logo_height | append: 'px' }};
}
```

- **Position**: Sticky or relative based on `sticky_header_type` setting.
- **Grid layout**: Changes based on `logo_position` (middle-center/top-center vs others).
- **Padding**: Top and bottom padding from section settings (0–36px, default 20px).
- **Logo height**: Controlled by theme setting `settings.logo_height`.
- **Mobile padding**: Responsive padding calculated as `padding_top / 1.5` and `padding_bottom / 1.5`.

---

## Markup Structure

```liquid
<div class="color-{{ section.settings.color_scheme }}" x-data="{ cartOpen: false }" @cart-open.window="cartOpen = true">
  <header id="main-header" x-data="{ searchOpen: false, searchTerm: '{{ search.terms | escape }}' }">
    <!-- Navigation drawer -->
    <!-- Search icon (conditional) -->
    <!-- Logo -->
    <!-- Navigation menu -->
    <!-- Header actions (localization, search, account, cart) -->
    <!-- Search overlay -->
  </header>
  
  <!-- Cart notification/drawer (conditional) -->
</div>
```

- Header wrapped in color scheme container with Alpine.js cart state.
- Main header uses Alpine.js for search state management.
- Conditional rendering based on logo position and menu settings.

### Logo

```liquid
{% if request.page_type == 'index' %}<h1 class="header-logo-container" style="margin: 0">{% endif %}
<a href="{{ routes.root_url }}" class="header-shop_link">
  {% if settings.logo != blank %}
    {{ settings.logo | image_url: width: 900 | image_tag: class: 'header-logo' }}
  {% else %}
    <span class="header-shop_name">{{ shop.name }}</span>
  {% endif %}
</a>
{% if request.page_type == 'index' %}</h1>{% endif %}
```

- Logo wrapped in `<h1>` on homepage for SEO, otherwise plain link.
- Falls back to shop name text if no logo image is set.
- Logo height controlled by `settings.logo_height` theme setting.

### Navigation Menu

```liquid
{% if section.settings.menu != blank and section.settings.menu_type_desktop != 'drawer' %}
  <nav class="header-menu-position-{{ section.settings.menu_position }}">
    {% if section.settings.menu_type_desktop == 'dropdown' %}
      {% render 'component-nav-dropdown', ... %}
    {% elsif section.settings.menu_type_desktop != 'drawer' %}
      {% render 'component-nav-megamenu', ... %}
    {% endif %}
  </nav>
{% endif %}
```

- Menu renders only when menu is selected and desktop type is not "drawer".
- Supports dropdown and megamenu navigation styles.
- Menu position class applied: `header-menu-position-\{\{ section.settings.menu_position \}\}`.

### Search Functionality

```liquid
<div id="header-actions_search" @click="searchOpen = !searchOpen; $nextTick(() => { if (searchOpen) $refs.searchInput.focus() })">
  {{ 'icon-search.svg' | inline_asset_content }}
</div>

<div id="header-search" :class="{ 'active': searchOpen }">
  {%- if settings.predictive_search_enabled -%}
    {%- render 'component-predictive-search', context: 'header' -%}
  {%- else -%}
    <form action="{{ routes.search_url }}" method="get" role="search">
      <input type="search" name="q" x-model="searchTerm" x-ref="searchInput" ...>
      <!-- Reset and submit buttons -->
    </form>
  {%- endif -%}
</div>
```

- Search toggle uses Alpine.js to show/hide search overlay.
- Supports predictive search (when enabled) or standard search form.
- Search input uses `x-model` for two-way binding and `x-ref` for focus management.

### Header Actions

```liquid
<div class="header-actions">
  <!-- Localization selectors (conditional) -->
  <!-- Search icon (conditional based on logo position) -->
  <!-- Customer account icon (conditional) -->
  <!-- App blocks -->
  <!-- Cart icon -->
</div>
```

- Localization selectors render when country/language selectors are enabled.
- Search icon position varies based on logo position setting.
- Customer account icon shows when accounts are enabled and `enable_customer_avatar` is true.
- Cart icon includes item count badge with Liquid Ajax Cart binding.

---

## JavaScript Behavior

### Sticky Header

```javascript
window.addEventListener('scroll', () => {
  const currentScroll = window.pageYOffset || document.documentElement.scrollTop;
  
  if (currentScroll > 0) {
    header.classList.add('scrolled-header');
  } else {
    header.classList.remove('scrolled-header');
  }
  
  if (section.settings.sticky_header_type == 'on-scroll-up') {
    // Hide on scroll down, show on scroll up
  }
});
```

- **Scroll detection**: Adds `scrolled-header` class when page is scrolled.
- **On-scroll-up mode**: Hides header on scroll down, shows on scroll up.
- **Logo size reduction**: When `sticky_header_type == 'reduce-logo-size'`, logo height reduces by 10px on scroll.

### Header Height Tracking

```javascript
function updateHeaderHeight() {
  const headerHeight = header.offsetHeight;
  document.documentElement.style.setProperty('--header-height', `${headerHeight}px`);
}
```

- Calculates header height and sets CSS variable `--header-height`.
- Updates on window resize and load events.
- Used for scroll-based positioning calculations.

### Alpine.js Integration

- **Search state**: `x-data="{ searchOpen: false, searchTerm: '...' }"` manages search visibility and input value.
- **Cart drawer**: `x-data="{ cartOpen: false }"` manages cart drawer state when `cart_type == 'drawer'`.
- **Click outside**: `@click.outside="searchOpen = false"` closes search when clicking outside.

---

## Schema

```json
{
  "name": "t:sections.header.name",
  "class": "section-header",
  "max_blocks": 3,
  "settings": [
    {
      "type": "select",
      "id": "logo_position",
      "options": [
        { "value": "top-left", "label": "..." },
        { "value": "top-center", "label": "..." },
        { "value": "middle-left", "label": "..." },
        { "value": "middle-center", "label": "..." }
      ],
      "default": "middle-left",
      "label": "t:sections.header.settings.logo_position.label"
    },
    {
      "type": "select",
      "id": "menu_position",
      "options": [
        { "value": "left", "label": "Left" },
        { "value": "center", "label": "Center" },
        { "value": "right", "label": "Right" }
      ],
      "default": "center",
      "label": "Menu position"
    },
    {
      "type": "link_list",
      "id": "menu",
      "default": "main-menu",
      "label": "t:sections.header.settings.menu.label"
    },
    {
      "type": "select",
      "id": "menu_type_desktop",
      "options": [
        { "value": "dropdown", "label": "..." },
        { "value": "mega", "label": "..." },
        { "value": "drawer", "label": "..." }
      ],
      "default": "dropdown",
      "label": "t:sections.header.settings.menu_type_desktop.label"
    },
    {
      "type": "select",
      "id": "sticky_header_type",
      "options": [
        { "value": "none", "label": "..." },
        { "value": "on-scroll-up", "label": "..." },
        { "value": "always", "label": "..." },
        { "value": "reduce-logo-size", "label": "..." }
      ],
      "default": "on-scroll-up",
      "label": "t:sections.header.settings.sticky_header_type.label"
    },
    {
      "type": "checkbox",
      "id": "show_line_separator",
      "default": true,
      "label": "t:sections.header.settings.show_line_separator.label"
    },
    {
      "type": "color_scheme",
      "id": "color_scheme",
      "label": "t:sections.all.colors.label",
      "default": "scheme-1"
    },
    {
      "type": "color_scheme",
      "id": "menu_color_scheme",
      "label": "t:sections.header.settings.menu_color_scheme.label",
      "default": "scheme-1"
    },
    {
      "type": "checkbox",
      "id": "enable_country_selector",
      "default": false,
      "label": "t:sections.header.settings.enable_country_selector.label"
    },
    {
      "type": "checkbox",
      "id": "enable_language_selector",
      "default": false,
      "label": "t:sections.header.settings.enable_language_selector.label"
    },
    {
      "type": "checkbox",
      "id": "enable_customer_avatar",
      "default": true,
      "label": "t:sections.header.settings.enable_customer_avatar.label"
    },
    {
      "type": "select",
      "id": "mobile_logo_position",
      "options": [
        { "value": "center", "label": "..." },
        { "value": "left", "label": "..." }
      ],
      "default": "center",
      "label": "t:sections.header.settings.mobile_logo_position.label"
    },
    {
      "type": "range",
      "id": "margin_bottom",
      "min": 0,
      "max": 100,
      "step": 4,
      "unit": "px",
      "label": "t:sections.header.settings.margin_bottom.label",
      "default": 0
    },
    {
      "type": "range",
      "id": "padding_top",
      "min": 0,
      "max": 36,
      "step": 4,
      "unit": "px",
      "label": "t:sections.all.padding.padding_top",
      "default": 20
    },
    {
      "type": "range",
      "id": "padding_bottom",
      "min": 0,
      "max": 36,
      "step": 4,
      "unit": "px",
      "label": "t:sections.all.padding.padding_bottom",
      "default": 20
    }
  ],
  "blocks": [
    {
      "type": "@app"
    }
  ]
}
```

### Section Settings

| Setting ID | Type | Default | Purpose |
|------------|------|---------|---------|
| `logo_position` | select | `middle-left` | Logo placement (top-left, top-center, middle-left, middle-center) |
| `menu_position` | select | `center` | Menu alignment (left, center, right) |
| `menu` | link_list | `main-menu` | Navigation menu selection |
| `menu_type_desktop` | select | `dropdown` | Desktop menu style (dropdown, mega, drawer) |
| `sticky_header_type` | select | `on-scroll-up` | Sticky behavior (none, on-scroll-up, always, reduce-logo-size) |
| `show_line_separator` | checkbox | `true` | Display border below header |
| `color_scheme` | color_scheme | `scheme-1` | Header color palette |
| `menu_color_scheme` | color_scheme | `scheme-1` | Menu/drawer color palette |
| `enable_country_selector` | checkbox | `false` | Show country/region selector |
| `enable_language_selector` | checkbox | `false` | Show language selector |
| `enable_customer_avatar` | checkbox | `true` | Show customer account icon |
| `mobile_logo_position` | select | `center` | Mobile logo position (center, left) |
| `margin_bottom` | range (px) | 0 | Bottom margin (0–100px, step 4) |
| `padding_top` | range (px) | 20 | Top padding (0–36px, step 4) |
| `padding_bottom` | range (px) | 20 | Bottom padding (0–36px, step 4) |

### Blocks

- **`@app`**: App blocks (max 3 blocks)

---

## Implementation Notes

1. **Translation keys**: Most section names and labels use translation filters (`t:sections.header.*`), but some settings like `menu_position` and color labels are hardcoded in English.

2. **Alpine.js dependency**: Search functionality requires Alpine.js to be loaded in the theme. Ensure Alpine.js is included in `layout/theme.liquid`.

3. **Liquid Ajax Cart**: Cart count badge uses `data-ajax-cart-bind="item_count"` to automatically update. Ensure Liquid Ajax Cart is initialized.

4. **Logo height**: Logo height comes from theme settings (`settings.logo_height`), not section settings. Ensure this is configured in theme settings.

5. **Sticky header logic**: Complex JavaScript handles different sticky header types:
   - `none`: Header is relative, not sticky
   - `on-scroll-up`: Hides on scroll down, shows on scroll up
   - `always`: Always sticky at top
   - `reduce-logo-size`: Sticky with logo size reduction on scroll

6. **Grid layout**: Header uses CSS Grid with dynamic column configuration based on logo position. Middle-center and top-center positions use `1fr auto 1fr`, others use `auto 1fr auto`.

7. **Mobile responsive**: On mobile (≤1024px), desktop navigation and some actions are hidden. Mobile layout uses different grid configuration based on `mobile_logo_position`.

8. **Search positioning**: Search icon position varies:
   - Shows before logo when `logo_position == 'top-center'` or menu is blank
   - Shows in header actions otherwise

9. **Cart type integration**: Header conditionally renders cart notification or drawer based on `settings.cart_type`:
   - `drawer`: Renders `component-cart-drawer` snippet
   - `notification`: Renders `component-cart-notification` snippet
   - Otherwise: Cart icon links to cart page

10. **Predictive search**: When `settings.predictive_search_enabled` is true, uses `component-predictive-search` snippet instead of standard search form.

11. **Navigation snippets**: Different navigation components render based on `menu_type_desktop`:
   - `dropdown`: Uses `component-nav-dropdown`
   - `mega`: Uses `component-nav-megamenu`
   - `drawer`: Uses `component-nav-drawer` (always visible on mobile, conditional on desktop)

12. **Localization script**: `component-localization-form.js` only loads when country or language selectors are enabled.

13. **Header height variable**: JavaScript sets `--header-height` CSS variable for use in other parts of the theme (e.g., offset calculations).

14. **Homepage SEO**: Logo wrapped in `<h1>` tag only on homepage (`request.page_type == 'index'`) for better SEO.

15. **Menu drawer**: When `menu_type_desktop == 'drawer'`, navigation drawer is always visible on mobile and can be toggled on desktop.

16. **Responsive padding**: Mobile padding is calculated as `padding_top / 1.5` and `padding_bottom / 1.5` for tighter spacing on small screens.

