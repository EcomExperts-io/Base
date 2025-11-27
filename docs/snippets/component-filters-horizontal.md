# component-filters-horizontal Snippet

`snippets/component-filters-horizontal.liquid` renders a horizontal filter bar for collection and search pages. It displays filter buttons that open dropdown panels with filter values, supporting both standard checkbox filters and price range filters. The component uses Alpine.js for dropdown state management and integrates with the Section Rendering API for AJAX filter updates.

---

## What It Does

- Renders a horizontal row of filter buttons above the product grid.
- Each filter opens a dropdown panel with filter values (checkboxes or price range).
- Supports price range filters via `component-filters-price-range` snippet.
- Shows active filter count and reset link for each filter group.
- Uses Alpine.js for dropdown open/close state and click-outside detection.
- Integrates with Section Rendering API for seamless filter updates.
- Desktop-only display (hidden on mobile via `small-hide` class).

---

## Parameters

| Parameter          | Type    | Default | Description                                                      |
|--------------------|---------|---------|------------------------------------------------------------------|
| `results`          | object  | **required** | Collection or search object providing filters.                   |
| `show_filter_count`| boolean | optional | Show product count next to each filter value.                    |
| `filter_type`      | string  | optional | Filter type identifier (passed to price range component).        |
| `section`          | object  | **required** | Section object containing `id` for unique DOM targeting.         |

**Note**: The `section` object is accessed via `section.id` in the snippet, so it must be available in the Liquid context.

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | Inline `{% style %}` block with comprehensive filter styling |
| JavaScript | Alpine.js (required for dropdown state), Section Rendering API integration |
| Snippets | `component-filters-price-range` (for price range filters) |
| Icons | `icon-caret.svg`, `icon-square.svg`, `icon-checkmark.svg` (inline via `inline_asset_content`) |
| Data | Requires `results` object with `filters` array containing filter objects |

- Alpine.js powers dropdown state (`x-data`, `x-show`, `@click.away`).
- Inline styles provide all filter-specific CSS (no external CSS file required).
- Section Rendering API handles filter updates via `data-render-section` attributes.

---

## Dynamic Styles

The snippet includes inline styles for filter button, dropdown, and layout styling:

```liquid
{%- style -%}
  .filters-horizontal {
    display: flex;
    flex-wrap: wrap;
    align-items: flex-start;
    row-gap: 1.5rem;
    max-width: 700px;
  }

  .filter-content {
    border-width: 0.1rem;
    border-style: solid;
    border-color: rgba(var(--color-foreground), 0.1);
    border-radius: 0.4rem;
    box-shadow: 0 1.2rem 2.4rem rgba(var(--color-shadow), 0.15);
    background-color: rgb(var(--color-background));
    position: absolute;
    top: calc(100% + 10px);
    left: -12px;
    width: 350px;
    max-height: 550px;
    overflow-y: auto;
    z-index: 5;
  }

  /* ... additional styling ... */
{%- endstyle -%}
```

- **Flex layout**: Filters wrap to multiple rows if needed.
- **Dropdown positioning**: Absolute positioning below button with offset.
- **Dropdown styling**: Border, shadow, and rounded corners for card-like appearance.
- **Scrollable content**: Max height with overflow for long filter lists.

---

## Markup Structure

```liquid
<form id="filters-form" class="filters-horizontal small-hide">
  <h2 class="facets__heading">Filter:</h2>
  {%- for f in results.filters -%}
    <div class="facets__wrapper" x-data="{ open: false }">
      <!-- Filter button -->
      <!-- Dropdown content -->
    </div>
  {% endfor %}
</form>
```

- **Form wrapper**: All filters within single form with `id="filters-form"`.
- **Desktop-only**: Hidden on mobile via `small-hide` class.
- **Alpine.js state**: Each filter wrapper has independent `open` state.

### Filter Button

```liquid
<button type="button" x-on:click="open = !open" class="filter-button">
  {{ f.label | escape }}
  {{ 'icon-caret.svg' | inline_asset_content }}
</button>
```

- **Toggle behavior**: Clicking button toggles dropdown open/closed.
- **Icon indicator**: Caret icon indicates dropdown functionality.
- **Label escaping**: Filter label is escaped for security.

### Dropdown Content

```liquid
<div
  x-cloak
  x-show="open"
  @click.away="open = false"
  x-transition
  class="filter-content js-filter"
  id="Details-{{ f.param_name | escape }}-{{ section.id }}"
>
  <div class="facets__head-wrapper">
    <span class="facet-name">
      {{ f.label }}
      {% if f.active_values.size > 0 %}
        ({{ f.active_values.size }})
      {% endif %}
    </span>
    {% if f.active_values.size > 0 %}
      <a class="facet-reset" data-render-section-url="{{ f.url_to_remove }}" href="{{ f.url_to_remove }}">
        reset
      </a>
    {% endif %}
  </div>
  <ul class="facets__list">
    <!-- Filter values or price range -->
  </ul>
</div>
```

- **Alpine.js directives**:
  - `x-cloak`: Hides content until Alpine.js initializes.
  - `x-show="open"`: Shows/hides based on state.
  - `@click.away`: Closes dropdown when clicking outside.
  - `x-transition`: Smooth show/hide animation.
- **Active count**: Shows number of active filters in header.
- **Reset link**: Allows clearing all active filters for this group.
- **Unique ID**: Uses filter param name and section ID for uniqueness.

### Filter Values

```liquid
{%- for v in f.values -%}
  {% assign input_id = 'Filter-' | append: f.param_name | escape | append: '-' | append: forloop.index %}
  <li class="facets__item">
    <label class="facet-checkbox">
      <input
        type="checkbox"
        id="{{ input_id }}"
        name="{{ v.param_name }}"
        value="{{ v.value }}"
        data-render-section="filters-form"
        {% if v.active %}checked{% endif %}
        {% if v.count == 0 and v.active == false %}disabled{% endif %}
      >
      {{- 'icon-square.svg' | inline_asset_content -}}
      <div class="svg-wrapper">
        {{- 'icon-checkmark.svg' | inline_asset_content -}}
      </div>
      {{- v.label }} {% if show_filter_count %} ({{ v.count }}){% endif %}
    </label>
  </li>
{%- endfor -%}
```

- **Custom checkboxes**: Uses icon-based checkboxes for styling.
- **Active state**: Pre-checks active filters.
- **Disabled state**: Disables filters with 0 results (unless already active).
- **Section Rendering API**: `data-render-section="filters-form"` triggers AJAX updates.
- **Filter count**: Optionally shows product count next to each value.

### Price Range Filter

```liquid
{% if f.type == 'price_range' %}
  {% render 'component-filters-price-range', filter: f, id_prefix: 'Filter-', filter_type: filter_type %}
{% endif %}
```

- **Conditional rendering**: Renders price range component for price filters.
- **Parameter passing**: Passes filter object, ID prefix, and filter type.

---

## Behavior

- **Dropdown toggle**: Clicking filter button opens/closes its dropdown.
- **Click outside**: Clicking outside dropdown closes it automatically.
- **Filter updates**: Checkbox changes trigger Section Rendering API requests.
- **Reset functionality**: Reset link clears all active filters for that group.
- **Multiple dropdowns**: Multiple filter dropdowns can be open simultaneously.
- **Smooth transitions**: Alpine.js `x-transition` provides smooth animations.
- **Active filter count**: Header shows count of active filters in parentheses.
- **Disabled filters**: Filters with 0 results are disabled to prevent invalid selections.

---

## Usage Example

```liquid
{% render 'component-filters-horizontal',
  results: collection,
  show_filter_count: section.settings.show_filter_count,
  filter_type: section.settings.filter_type,
  section: section
%}
```

Or for search pages:

```liquid
{% render 'component-filters-horizontal',
  results: search,
  show_filter_count: section.settings.show_filter_count,
  section: section
%}
```

Typically used in:
- Collection pages (`sections/collection.liquid`)
- Search pages (`sections/search.liquid`)
- As desktop filter option (mobile uses drawer)

---

## Implementation Notes

1. **Alpine.js requirement**: Snippet requires Alpine.js to be loaded in the theme for dropdown state management.

2. **Section Rendering API**: Filter changes use `data-render-section="filters-form"` to trigger AJAX updates. The form ID is `filters-form`.

3. **Desktop-only display**: Uses `small-hide` class to hide on mobile devices. Mobile typically uses `component-filters-drawer` instead.

4. **Filter group IDs**: Each filter dropdown uses unique ID: `Details-\{\{ f.param_name | escape \}\}-\{\{ section.id \}\}`

5. **Dropdown positioning**: Dropdowns are absolutely positioned below buttons with `top: calc(100% + 10px)` and `left: -12px` offset.

6. **Price range filters**: Price range filters are handled by `component-filters-price-range` snippet, not standard checkboxes.

7. **Disabled filters**: Filters with 0 results are disabled unless already active (to allow removing active filters with 0 results).

8. **Active filter count**: Shows count of active filters in dropdown header: `(\{\{ f.active_values.size \}\})`

9. **Reset link**: Reset link uses `data-render-section-url` and `href` attributes for Section Rendering API integration.

10. **Icon dependencies**: Requires the following icons in `assets/`:
    - `icon-caret.svg` (dropdown indicator)
    - `icon-square.svg` (checkbox unchecked state)
    - `icon-checkmark.svg` (checkbox checked state)

11. **Form structure**: All filters are within `<form id="filters-form">` for proper form submission handling.

12. **Checkbox styling**: Uses custom icon-based checkboxes (`icon-square.svg` and `icon-checkmark.svg`) instead of native checkboxes for consistent styling.

13. **Filter value IDs**: Each checkbox uses unique ID: `Filter-\{\{ f.param_name | escape \}\}-\{\{ forloop.index \}\}`

14. **Alpine.js directives**:
    - `x-data="{ open: false }"`: Initializes dropdown state
    - `x-on:click="open = !open"`: Toggles dropdown on button click
    - `x-show="open"`: Shows/hides dropdown
    - `@click.away="open = false"`: Closes on outside click
    - `x-transition`: Provides smooth animations
    - `x-cloak`: Prevents flash of unstyled content

15. **CSS class dependencies**: Snippet relies on CSS classes:
    - `.filters-horizontal`
    - `.facets__heading`
    - `.facets__wrapper`
    - `.filter-button`
    - `.filter-content`
    - `.facets__head-wrapper`
    - `.facet-name`
    - `.facet-reset`
    - `.facets__list`
    - `.facets__item`
    - `.facet-checkbox`
    - `.svg-wrapper`
    - `.js-filter`

16. **Max width constraint**: Filter container has `max-width: 700px` to prevent excessive width on large screens.

17. **Dropdown z-index**: Dropdown uses `z-index: 5` to appear above other content.

18. **Sticky header**: Dropdown header uses `position: sticky` to stay visible when scrolling filter values.

19. **Filter count display**: Filter counts are shown in parentheses next to filter value labels when `show_filter_count` is truthy.

20. **Section ID usage**: Section ID is used for unique DOM targeting in filter dropdown IDs.

21. **Price conversion**: Price range filters convert from cents to dollars by dividing by 100 (handled in `component-filters-price-range`).

22. **Accessibility considerations**:
    - Proper button labels
    - Form structure with labels
    - Semantic HTML (lists, labels)
    - Keyboard navigation support via Alpine.js

23. **Performance**: Inline styles prevent additional HTTP request but increase HTML size. Consider extracting to CSS file if used multiple times.

24. **Filter type parameter**: The `filter_type` parameter is passed to `component-filters-price-range` but may not be used in current implementation.

25. **Reset link styling**: Reset link uses `text-transform: capitalize` and underline styling for visibility.

26. **Dropdown width**: Fixed width of 350px for consistent dropdown sizing.

27. **Max height**: Dropdown has `max-height: 550px` with `overflow-y: auto` for scrollable long lists.

28. **Row gap**: Filters wrap with `row-gap: 1.5rem` for spacing when wrapping to multiple rows.

29. **Hover effects**: Filter buttons have underline hover effect for better UX.

30. **No translation keys**: Filter labels come directly from Shopify filter objects, not translation files.

