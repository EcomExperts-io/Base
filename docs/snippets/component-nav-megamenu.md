# component-nav-megamenu Snippet

`snippets/component-nav-megamenu.liquid` renders a full-width megamenu navigation layout for desktop headers. When a menu item with children is clicked, it expands a wide dropdown panel below the header using a 6-column grid layout. The megamenu supports 3 levels of navigation (parent → child → grandchild) and uses Alpine.js for toggle behavior and smooth transitions.

---

## What It Does

- Renders a full-width megamenu that expands below the header.
- Uses a 6-column grid layout to display child links in organized columns.
- Supports 3 levels of navigation hierarchy (parent → child → grandchild).
- Provides toggleable megamenu panels using Alpine.js state management.
- Uses smooth transitions for megamenu show/hide animations.
- Marks current page links with `aria-current="page"`.
- Handles click-outside detection to close open megamenus.

---

## Parameters

| Parameter          | Type    | Default | Description                                                      |
|--------------------|---------|---------|------------------------------------------------------------------|
| `menu`             | linklist| **required** | Menu object (linklist) to render.                                |
| `menu_color_scheme`| string  | optional | Color scheme handle for megamenu background styling.            |

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | Inline `{% stylesheet %}` block with comprehensive megamenu styling |
| JavaScript | Alpine.js (required for megamenu state management) |
| Icons | `icon-caret.svg` (inline via `inline_asset_content`) |
| Data | Requires `menu` linklist object with `links` array |

- Alpine.js powers megamenu state (`x-data`, `x-show`, `@click.outside`).
- Inline styles provide all megamenu-specific CSS (no external CSS file required).
- Grid layout uses CSS Grid with 6 columns for organized child link display.

---

## Dynamic Styles

The snippet includes inline styles for megamenu positioning, grid layout, and typography:

```liquid
{% stylesheet %}
  #main-header .nav-megamenu {
    position: absolute;
    left: 0;
    top: 100%;
    width: 100%;
    margin-top: 1px;
  }
  #main-header .nav-megamenu .page-width {
    display: grid;
    grid-template-columns: repeat(6, minmax(0, 1fr));
    margin-inline: auto;
    align-items: flex-start;
    padding: 30px 20px;
  }
  /* ... additional styling ... */
{% endstylesheet %}
```

- **Full-width positioning**: Megamenu spans entire header width with `width: 100%` and `left: 0`.
- **Grid layout**: Uses 6-column grid (`grid-template-columns: repeat(6, minmax(0, 1fr))`) for organized child links.
- **Absolute positioning**: Positioned absolutely below header with `top: 100%`.
- **Page width container**: Inner content uses `.page-width` class for centered, constrained width.

---

## Markup Structure

```liquid
<ul>
  {% for link in menu.links %}
    <li x-data="{ menuOpen: false }" @click.outside="menuOpen = false">
      {% if link.links != blank %}
        <!-- Parent link with megamenu -->
      {% else %}
        <!-- Simple link without megamenu -->
      {% endif %}
    </li>
  {% endfor %}
</ul>
```

- **Alpine.js state**: Each top-level menu item has independent state for megamenu visibility.
- **Click outside**: Closes megamenu when clicking outside via `@click.outside`.

### Parent Link with Megamenu

```liquid
{% if link.links != blank %}
  <button
    @click="menuOpen = !menuOpen"
    :class="{ 'menu-open': menuOpen }"
    class="menu-toggle"
  >
    {{- link.title | escape -}}
    {{- 'icon-caret.svg' | inline_asset_content -}}
  </button>
  <div
    x-show="menuOpen"
    x-transition
    x-cloak
    class="nav-megamenu color-{{ menu_color_scheme }} gradient"
  >
    <!-- Grid layout with child links -->
  </div>
{% endif %}
```

- **Toggle behavior**: Clicking button toggles megamenu visibility.
- **Caret icon**: Shows caret icon to indicate expandable menu.
- **Alpine.js directives**:
  - `@click="menuOpen = !menuOpen"`: Toggles megamenu
  - `:class="{ 'menu-open': menuOpen }"`: Adds class when open
  - `x-show="menuOpen"`: Shows/hides megamenu
  - `x-transition`: Smooth show/hide animation
  - `x-cloak`: Prevents flash of unstyled content

### Megamenu Grid Layout

```liquid
<div class="nav-megamenu color-{{ menu_color_scheme }} gradient">
  <ul class="page-width" role="list">
    {%- for childlink in link.links -%}
      <li>
        <a href="{{ childlink.url }}" class="nav-megamenu_heading" {% if childlink.current %}aria-current="page"{% endif %}>
          {{ childlink.title | escape }}
        </a>
        {%- if childlink.links != blank -%}
          <ul class="nav-megamenu_child" role="list">
            {%- for grandchildlink in childlink.links -%}
              <li>
                <a href="{{ grandchildlink.url }}" {% if grandchildlink.current %}aria-current="page"{% endif %}>
                  {{ grandchildlink.title | escape }}
                </a>
              </li>
            {%- endfor -%}
          </ul>
        {%- endif -%}
      </li>
    {%- endfor -%}
  </ul>
</div>
```

- **6-column grid**: Child links displayed in 6-column grid layout.
- **Child headings**: Child links styled as headings (`nav-megamenu_heading`) with bold font weight.
- **Grandchild links**: Nested grandchild links displayed below child headings.
- **Current page indication**: Links to current page marked with `aria-current="page"`.

### Simple Link (No Megamenu)

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

- **Direct link**: Simple link without megamenu when parent has no children.

---

## Behavior

- **Megamenu toggle**: Clicking parent link with children opens/closes its megamenu.
- **Click outside**: Clicking outside closes open megamenu.
- **Smooth transitions**: Alpine.js `x-transition` provides smooth show/hide animations.
- **Current page indication**: Links to current page marked with `aria-current="page"`.
- **Full-width display**: Megamenu spans entire header width for maximum content space.
- **Grid organization**: Child links organized in 6-column grid for easy scanning.

---

## Usage Example

```liquid
{% render 'component-nav-megamenu',
  menu: section.settings.menu,
  menu_color_scheme: section.settings.menu_color_scheme
%}
```

Typically used in:
- Header (`sections/header.liquid`) when `menu_type_desktop == 'mega'` or not 'dropdown'/'drawer'
- Desktop navigation (not used on mobile - mobile uses drawer)

---

## Implementation Notes

1. **Alpine.js requirement**: Snippet requires Alpine.js to be loaded in the theme for megamenu state management.

2. **Full-width layout**: Megamenu spans entire header width (`width: 100%`, `left: 0`) for maximum content space.

3. **Grid layout**: Uses CSS Grid with 6 columns (`grid-template-columns: repeat(6, minmax(0, 1fr))`) to organize child links.

4. **State management**: Each top-level menu item has independent Alpine.js state:
    - `menuOpen`: Controls megamenu visibility

5. **Click outside handling**: Uses `@click.outside` directive to close megamenu when clicking outside.

6. **Icon dependency**: Requires `icon-caret.svg` in the `assets/` folder for expandable menu indicators.

7. **CSS class dependencies**: Snippet relies on CSS classes:
    - `.nav-megamenu`
    - `.menu-toggle`
    - `.menu-open`
    - `.nav-megamenu_heading`
    - `.nav-megamenu_child`
    - `.page-width`
    - `.color-\{\{ menu_color_scheme \}\}`
    - `.gradient`

8. **Alpine.js directives**:
    - `x-data="{ menuOpen: false }"`: Initializes state per menu item
    - `@click="menuOpen = !menuOpen"`: Toggles megamenu
    - `:class="{ 'menu-open': menuOpen }"`: Adds class when megamenu open
    - `x-show="menuOpen"`: Shows/hides megamenu
    - `x-transition`: Provides smooth show/hide animations
    - `x-cloak`: Prevents flash of unstyled content
    - `@click.outside="menuOpen = false"`: Closes megamenu on outside click

9. **Title escaping**: All link titles are escaped using `escape` filter for security.

10. **Current page detection**: Uses `link.current`, `childlink.current`, and `grandchildlink.current` to detect current page.

11. **Accessibility features**:
    - `aria-current="page"` for current page links
    - `role="list"` for semantic structure
    - Proper link semantics
    - Keyboard navigation support via Alpine.js

12. **Color scheme integration**: Megamenu uses theme color scheme via `color-\{\{ menu_color_scheme \}\}` class.

13. **Gradient class**: Megamenu includes `gradient` class for additional styling options.

14. **Page width container**: Inner content uses `.page-width` class for centered, constrained width matching theme page width.

15. **Grid column distribution**: Child links distributed evenly across 6 columns using `minmax(0, 1fr)` for flexible sizing.

16. **Child link styling**: Child links styled as headings with `font-weight: 600` for visual hierarchy.

17. **Grandchild link styling**: Grandchild links have reduced padding (`padding: 6px 0`) and standard font size.

18. **Megamenu padding**: Grid container has `padding: 30px 20px` for comfortable spacing.

19. **Grid alignment**: Grid items aligned to top with `align-items: flex-start` for consistent layout.

20. **Nested submenu positioning**: Grandchild links use `position: static` to appear inline below child headings.

21. **Transition animations**: Megamenu show/hide uses Alpine.js `x-transition` for smooth animations.

22. **Multiple megamenus**: Only one megamenu can be open at a time (controlled by independent `menuOpen` state per menu item).

23. **No translation keys**: Menu labels come directly from Shopify menu object, not translation files.

24. **Menu link structure**: Relies on Shopify's menu structure:
    - `menu.links`: Top-level links
    - `link.links`: Child links
    - `childlink.links`: Grandchild links

25. **Empty link check**: Uses `link.links != blank` to determine if link has children.

26. **Caret icon display**: Caret icon shown for all links with children to indicate expandable menu.

27. **Link URL handling**: All links use `link.url`, `childlink.url`, `grandchildlink.url` from Shopify menu object.

28. **Security**: All user-generated content (link titles) is escaped using `escape` filter.

29. **Responsive behavior**: Megamenu designed for desktop - mobile typically uses drawer navigation instead.

30. **Z-index management**: Megamenu should have appropriate z-index to appear above other content (handled by CSS).

31. **Header context**: Megamenu styles scoped to `#main-header` to avoid conflicts with other navigation.

32. **Grid responsiveness**: 6-column grid may need media query adjustments for smaller screens (handled by theme CSS).

33. **Button semantics**: Uses `<button>` element for toggle, which is semantically correct for interactive elements.

34. **No JavaScript file**: Snippet doesn't require a separate JavaScript file - all behavior handled by Alpine.js.

35. **Performance**: Inline styles prevent additional HTTP request but increase HTML size.

36. **Accessibility improvements needed**: Consider adding:
    - `aria-expanded` attributes for megamenu toggles
    - `aria-haspopup` attributes
    - Keyboard navigation enhancements
    - Focus management when megamenu opens/closes

37. **Grid column count**: Fixed 6-column grid may not be optimal for all menu structures. Consider making it configurable or responsive.

38. **Child link distribution**: Child links distributed evenly across columns - if there are fewer than 6 child links, some columns will be empty.

39. **Grandchild link display**: Grandchild links displayed as simple vertical list below child headings.

40. **Margin and spacing**: Megamenu has `margin-top: 1px` to create slight gap from header, and grid container has internal padding.

41. **Centered content**: Grid container uses `margin-inline: auto` for horizontal centering within full-width megamenu.

42. **Heading font weight**: Child links use `font-weight: 600` to distinguish them from grandchild links.

43. **Link hierarchy**: Visual hierarchy created through:
    - Child links: Bold headings
    - Grandchild links: Regular text with reduced padding

44. **Menu depth limit**: Supports exactly 3 levels of nesting (parent, child, grandchild). Deeper nesting not supported.

45. **Desktop-only**: Megamenu designed for desktop navigation - mobile navigation typically uses drawer component.

46. **Full-width advantage**: Full-width layout allows for rich content display, ideal for large navigation structures.

47. **Grid flexibility**: Grid uses `minmax(0, 1fr)` to allow columns to shrink below content size if needed.

48. **Page width constraint**: Inner content constrained by `.page-width` class to match theme's page width setting.

49. **Color scheme scoping**: All styles scoped to `#main-header` to ensure they only apply in header context.

50. **Transition timing**: Alpine.js `x-transition` provides default transition timing - can be customized via CSS.

