# component-nav-dropdown Snippet

`snippets/component-nav-dropdown.liquid` renders a nested navigation dropdown menu with support for up to 3 levels of menu hierarchy (parent, child, grandchild). It can render in drawer style for mobile navigation or inline style for desktop header dropdowns. The component uses Alpine.js for submenu state management and provides smooth transitions for menu expansion.

---

## What It Does

- Renders a nested navigation menu from a Shopify linklist.
- Supports 3 levels of menu nesting (parent → child → grandchild).
- Provides toggleable submenus with Alpine.js state management.
- Can render in drawer style (for mobile) or inline style (for desktop header).
- Uses smooth transitions for submenu show/hide animations.
- Marks current page links with `aria-current="page"`.
- Handles click-outside detection to close open submenus.

---

## Parameters

| Parameter          | Type    | Default | Description                                                      |
|--------------------|---------|---------|------------------------------------------------------------------|
| `nav_style`        | string  | optional | `'drawer'` to render with drawer-specific classes, otherwise inline header style. |
| `menu`             | linklist| **required** | Menu object (linklist) to render.                                |
| `menu_color_scheme`| string  | optional | Color scheme handle for dropdown background styling.             |

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | Inline `{% style %}` block (conditional - only for inline header style) |
| JavaScript | Alpine.js (required for submenu state management) |
| Icons | `icon-caret.svg` (inline via `inline_asset_content`) |
| Data | Requires `menu` linklist object with `links` array |

- Alpine.js powers submenu state (`x-data`, `x-show`, `@click.outside`).
- Inline styles only included when `nav_style != 'drawer'` (for desktop header styling).
- Drawer styling handled by `component-nav-drawer` snippet.

---

## Dynamic Styles

The snippet conditionally includes inline styles only for inline header style (not drawer):

```liquid
{% unless nav_style == 'drawer' %}
  {% style %}
    #main-header .nav-dropdown,
    #main-header .nav-dropdown_child {
      position: absolute;
      top: 100%;
      gap: 0;
      align-items: stretch;
      flex-direction: column;
      margin-top: 1px;
      overflow: hidden;
    }
    #main-header .nav-dropdown {
      box-shadow: rgba(0, 0, 0, 0.1) 0 1px 3px 0, rgba(0, 0, 0, 0.06) 0 1px 2px 0;
    }
    /* ... additional styling ... */
  {% endstyle %}
{% endunless %}
```

- **Conditional styles**: Styles only apply when `nav_style != 'drawer'`.
- **Absolute positioning**: Dropdowns positioned absolutely below parent link.
- **Box shadow**: Dropdown has shadow for depth and separation.
- **Min width**: Dropdown items have `min-width: 20ch` for readability.

---

## Markup Structure

```liquid
<ul {% if nav_style == 'drawer' %}class="menu-drawer_navigation"{% endif %}>
  {% for link in menu.links %}
    <li x-data="{ menuOpen: false, activeSubMenu: null }" @click.outside="menuOpen = false; activeSubMenu = null">
      {% if link.links != blank %}
        <!-- Parent link with children -->
      {% else %}
        <!-- Simple link without children -->
      {% endif %}
    </li>
  {% endfor %}
</ul>
```

- **Conditional class**: Adds `menu-drawer_navigation` class when `nav_style == 'drawer'`.
- **Alpine.js state**: Each top-level menu item has independent state for submenu and nested submenu.
- **Click outside**: Closes all submenus when clicking outside.

### Parent Link with Children

```liquid
{% if link.links != blank %}
  <div
    @click="menuOpen = !menuOpen"
    :class="{ 'menu-open': menuOpen }"
    class="menu-toggle"
  >
    {{- link.title | escape -}}
    {{- 'icon-caret.svg' | inline_asset_content -}}
  </div>
  <ul
    x-show="menuOpen"
    class="nav-{{ nav_style }} color-{{ menu_color_scheme }} gradient"
    x-transition
    role="list"
    x-cloak
  >
    <!-- Child links -->
  </ul>
{% endif %}
```

- **Toggle behavior**: Clicking parent link toggles child submenu.
- **Caret icon**: Shows caret icon to indicate expandable menu.
- **Alpine.js directives**:
  - `@click="menuOpen = !menuOpen"`: Toggles submenu
  - `:class="{ 'menu-open': menuOpen }"`: Adds class when open
  - `x-show="menuOpen"`: Shows/hides submenu
  - `x-transition`: Smooth show/hide animation
  - `x-cloak`: Prevents flash of unstyled content

### Child Links

```liquid
{%- for childlink in link.links -%}
  <li>
    {% if childlink.links == blank %}
      <!-- Simple child link -->
    {% else %}
      <!-- Child link with grandchildren -->
    {% endif %}
  </li>
{%- endfor -%}
```

- **Two types**: Child links can be simple links or have their own children (grandchildren).

### Simple Child Link

```liquid
{% if childlink.links == blank %}
  <a
    href="{{ childlink.url }}"
    class="header__menu-item"
    {% if childlink.current %}
      aria-current="page"
    {% endif %}
  >
    {{ childlink.title | escape }}
  </a>
{% endif %}
```

- **Current page indicator**: Uses `aria-current="page"` for accessibility.
- **Title escaping**: Link titles are escaped for security.

### Child Link with Grandchildren

```liquid
{% else %}
  <div
    @click="activeSubMenu = (activeSubMenu === '{{ childlink.title | escape }}' ? null : '{{ childlink.title | escape }}')"
    :class="{ 'menu-open': activeSubMenu === '{{ childlink.title | escape }}' }"
    class="menu-toggle"
  >
    {{- childlink.title | escape -}}
    {{- 'icon-caret.svg' | inline_asset_content -}}
  </div>
  <ul
    x-show="activeSubMenu === '{{ childlink.title | escape }}'"
    class="nav-dropdown_child"
    x-transition
    role="list"
    x-cloak
  >
    {%- for grandchildlink in childlink.links -%}
      <li>
        <a
          href="{{ grandchildlink.url }}"
          class="header__menu-item"
          {% if grandchildlink.current %}
            aria-current="page"
          {% endif %}
        >
          {{ grandchildlink.title | escape }}
        </a>
      </li>
    {%- endfor -%}
  </ul>
{% endif %}
```

- **Nested submenu**: Supports third level of navigation (grandchildren).
- **Active submenu tracking**: Uses `activeSubMenu` variable to track which child's submenu is open.
- **Title-based identification**: Uses child link title to identify which submenu is active.
- **Toggle behavior**: Clicking child link toggles its grandchild submenu.

### Simple Link (No Children)

```liquid
{% else %}
  <a
    href="{{ link.url }}"
    {% if link.current %}
      aria-current="page"
    {% endif %}
  >
    {{- link.title | escape -}}
  </a>
{% endif %}
```

- **Direct link**: Simple link without submenu when parent has no children.

---

## Behavior

- **Submenu toggle**: Clicking parent link with children opens/closes its submenu.
- **Nested submenu toggle**: Clicking child link with grandchildren opens/closes its nested submenu.
- **Click outside**: Clicking outside closes all open submenus.
- **Smooth transitions**: Alpine.js `x-transition` provides smooth show/hide animations.
- **Current page indication**: Links to current page marked with `aria-current="page"`.
- **Multiple submenus**: Only one submenu per level can be open at a time (controlled by state variables).

---

## Usage Example

For drawer navigation:

```liquid
{% render 'component-nav-dropdown',
  nav_style: 'drawer',
  menu: section.settings.menu,
  menu_color_scheme: section.settings.menu_color_scheme
%}
```

For inline header navigation:

```liquid
{% render 'component-nav-dropdown',
  menu: section.settings.menu,
  menu_color_scheme: section.settings.menu_color_scheme
%}
```

Typically used in:
- `component-nav-drawer` (with `nav_style: 'drawer'`)
- Header sections (without `nav_style` parameter for inline style)

---

## Implementation Notes

1. **Alpine.js requirement**: Snippet requires Alpine.js to be loaded in the theme for submenu state management.

2. **Conditional styling**: Inline styles only included when `nav_style != 'drawer'` to avoid conflicts with drawer styling.

3. **Menu structure**: Supports Shopify's standard 3-level menu structure:
    - Level 1: Top-level menu items
    - Level 2: Child links (first submenu)
    - Level 3: Grandchild links (nested submenu)

4. **State management**: Each top-level menu item has independent Alpine.js state:
    - `menuOpen`: Controls first-level submenu visibility
    - `activeSubMenu`: Tracks which child's submenu is open (stores child link title)

5. **Submenu identification**: Nested submenus are identified by child link title, allowing multiple children with submenus.

6. **Click outside handling**: Uses `@click.outside` directive to close all submenus when clicking outside the menu structure.

7. **Icon dependency**: Requires `icon-caret.svg` in the `assets/` folder for expandable menu indicators.

8. **CSS class dependencies**: Snippet relies on CSS classes:
    - `.menu-drawer_navigation` (when `nav_style == 'drawer'`)
    - `.menu-toggle`
    - `.menu-open`
    - `.nav-\{\{ nav_style \}\}` (e.g., `.nav-drawer` or `.nav-dropdown`)
    - `.nav-dropdown_child`
    - `.header__menu-item`
    - `.color-\{\{ menu_color_scheme \}\}`
    - `.gradient`

9. **Alpine.js directives**:
    - `x-data="{ menuOpen: false, activeSubMenu: null }"`: Initializes state per menu item
    - `@click="menuOpen = !menuOpen"`: Toggles first-level submenu
    - `:class="{ 'menu-open': menuOpen }"`: Adds class when submenu open
    - `x-show="menuOpen"`: Shows/hides first-level submenu
    - `@click="activeSubMenu = (activeSubMenu === '\{\{ childlink.title | escape \}\}' ? null : '\{\{ childlink.title | escape \}\}')"`: Toggles nested submenu
    - `:class="{ 'menu-open': activeSubMenu === '\{\{ childlink.title | escape \}\}' }"`: Adds class when nested submenu open
    - `x-show="activeSubMenu === '\{\{ childlink.title | escape \}\}'"`: Shows/hides nested submenu
    - `x-transition`: Provides smooth show/hide animations
    - `x-cloak`: Prevents flash of unstyled content
    - `@click.outside="menuOpen = false; activeSubMenu = null"`: Closes all submenus on outside click

10. **Title escaping**: All link titles are escaped using `escape` filter for security.

11. **Current page detection**: Uses `link.current`, `childlink.current`, and `grandchildlink.current` to detect current page.

12. **Accessibility features**:
    - `aria-current="page"` for current page links
    - `role="list"` for semantic structure
    - Proper link semantics
    - Keyboard navigation support via Alpine.js

13. **Nested submenu logic**: Nested submenu toggles by comparing `activeSubMenu` with child link title:
    - If already open for this child: closes it (sets to `null`)
    - If closed or open for different child: opens it (sets to child title)

14. **Color scheme integration**: Dropdowns use theme color scheme via `color-\{\{ menu_color_scheme \}\}` class.

15. **Gradient class**: Dropdowns include `gradient` class for additional styling options.

16. **Drawer vs inline styles**: 
    - Drawer style: No additional inline styles, relies on drawer container styling
    - Inline style: Includes inline styles for absolute positioning and dropdown appearance

17. **Box shadow**: Inline style dropdowns have box shadow for depth (only when `nav_style != 'drawer'`).

18. **Min width**: Inline style dropdown items have `min-width: 20ch` for better readability.

19. **Submenu positioning**: 
    - Inline style: Absolute positioning below parent link
    - Drawer style: Static positioning within drawer flow

20. **Nested submenu positioning**: Nested submenus (grandchildren) use `position: static` in inline style to appear inline rather than absolutely positioned.

21. **Transition animations**: All submenu show/hide uses Alpine.js `x-transition` for smooth animations.

22. **Multiple open submenus**: Only one submenu per level can be open at a time:
    - Only one first-level submenu open (controlled by `menuOpen`)
    - Only one nested submenu open (controlled by `activeSubMenu`)

23. **Title-based submenu tracking**: Uses child link title as identifier for nested submenu state, which works but may have issues if multiple children have the same title.

24. **No translation keys**: Menu labels come directly from Shopify menu object, not translation files.

25. **Menu link structure**: Relies on Shopify's menu structure:
    - `menu.links`: Top-level links
    - `link.links`: Child links
    - `childlink.links`: Grandchild links

26. **Empty link check**: Uses `link.links != blank` to determine if link has children.

27. **Caret icon display**: Caret icon shown for all links with children to indicate expandable menu.

28. **Link URL handling**: All links use `link.url`, `childlink.url`, `grandchildlink.url` from Shopify menu object.

29. **Security**: All user-generated content (link titles) is escaped using `escape` filter.

30. **Responsive behavior**: Drawer style adapts to mobile, inline style adapts to desktop header positioning.

31. **Flexbox layout**: Menu items use flexbox for proper alignment and spacing.

32. **Border styling**: Menu items have bottom borders for visual separation (handled by drawer or inline styles).

33. **Hover effects**: Link hover effects handled by CSS (not shown in snippet but likely in theme CSS).

34. **Z-index management**: Inline style dropdowns should have appropriate z-index to appear above other content (handled by CSS).

35. **Menu depth limit**: Supports exactly 3 levels of nesting (parent, child, grandchild). Deeper nesting not supported.

36. **Active submenu state**: The `activeSubMenu` variable stores the title of the currently open nested submenu, allowing only one nested submenu to be open at a time.

37. **Title comparison**: Nested submenu toggle uses string comparison with escaped titles, which should work but may have edge cases with special characters.

38. **No JavaScript file**: Snippet doesn't require a separate JavaScript file - all behavior handled by Alpine.js.

39. **Performance**: Inline styles only included when needed (not for drawer style), reducing HTML size.

40. **Accessibility improvements needed**: Consider adding:
    - `aria-expanded` attributes for submenu toggles
    - `aria-haspopup` attributes
    - Keyboard navigation enhancements
    - Focus management when submenus open/close

