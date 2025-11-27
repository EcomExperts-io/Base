# component-filters-sidebar Snippet

`snippets/component-filters-sidebar.liquid` renders a vertical sidebar filter panel for collection and search pages. It displays filter groups as collapsible accordions using native `<details>` elements enhanced with Alpine.js, supports "show more" functionality for long filter lists, and integrates with the Section Rendering API for AJAX filter updates. The sidebar is sticky-positioned and scrollable for long filter lists.

---

## What It Does

- Renders a vertical sidebar with collapsible filter groups.
- Uses native `<details>` elements for accessibility with Alpine.js enhancement.
- Supports price range filters via `component-filters-price-range` snippet.
- Implements "show more/less" functionality for filters with many values (shows first 10 by default).
- Displays active filter count and reset links for each filter group.
- Sticky positioning keeps sidebar visible while scrolling.
- Desktop-only display (hidden on mobile via `small-hide` class).

---

## Parameters

| Parameter          | Type    | Default | Description                                                      |
|--------------------|---------|---------|------------------------------------------------------------------|
| `results`          | object  | **required** | Collection or search object providing filters.                   |
| `collapse_filters` | boolean | `false` | If true, all filter groups start collapsed.                      |
| `show_filter_count`| boolean | optional | Show product count next to each filter value.                    |
| `filter_type`      | string  | optional | Filter type identifier (passed to price range component).        |
| `section`          | object  | **required** | Section object containing `id` for unique DOM targeting.         |

**Note**: The `section` object is accessed via `section.id` in the snippet, so it must be available in the Liquid context.

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | Inline `{% style %}` block with comprehensive sidebar styling |
| JavaScript | Alpine.js (required for state management), Section Rendering API integration |
| Snippets | `component-filters-price-range` (for price range filters) |
| Icons | `icon-caret.svg`, `icon-square.svg`, `icon-checkmark.svg` (inline via `inline_asset_content`) |
| Data | Requires `results` object with `filters` array containing filter objects |

- Alpine.js powers accordion state and "show more" functionality.
- Inline styles provide all sidebar-specific CSS (no external CSS file required).
- Section Rendering API handles filter updates via `data-render-section` attributes.

---

## Dynamic Styles

The snippet includes inline styles for sidebar positioning, filter sections, and layout:

```liquid
{%- style -%}
  .filters-sidebar {
    margin-bottom: 20px;
    width: 260px;
    margin-right: 30px;
    flex-shrink: 0;
    position: sticky;
    top: calc(var(--header-height, 80px) + 20px);
    align-self: flex-start;
    max-height: calc(100vh - var(--header-height, 80px) - 40px);
    overflow-y: auto;
  }

  .facets__disclosure-vertical details[open] summary .icon-caret {
    transform: rotate(180deg);
  }

  /* ... additional styling ... */
{%- endstyle -%}
```

- **Sticky positioning**: Sidebar sticks to viewport with offset from header.
- **Fixed width**: 260px width with right margin for spacing.
- **Scrollable**: Max height with overflow for long filter lists.
- **Caret rotation**: Caret icon rotates 180° when filter group is open.

---

## Markup Structure

```liquid
<aside class="filters-sidebar small-hide">
  <div class="facets__main-head-wrapper">
    <h2 class="facets__heading">Filter:</h2>
  </div>
  <form id="filters-form">
    {% for f in results.filters %}
      <div class="filter-section facets__disclosure-vertical js-filter" x-data="{ open: {{ open }} }">
        <details x-bind:open="open" @toggle="open = $event.target.open">
          <!-- Summary and filter values -->
        </details>
      </div>
    {% endfor %}
  </form>
</aside>
```

- **Semantic HTML**: Uses `<aside>` for sidebar content.
- **Desktop-only**: Hidden on mobile via `small-hide` class.
- **Form wrapper**: All filters within single form with `id="filters-form"`.
- **Alpine.js integration**: Each filter group has independent `open` state.

### Filter Group Structure

```liquid
<div
  class="filter-section facets__disclosure-vertical js-filter"
  id="Details-{{ f.param_name | escape }}-{{ section.id }}"
  x-data="{ open: {{ open }} }"
>
  <details x-bind:open="open" @toggle="open = $event.target.open">
    <summary>
      <span>
        {{ f.label }}
        {% if f.active_values.size > 0 %}
          ({{ f.active_values.size }})
          <a class="reset-button" data-render-section-url="{{ f.url_to_remove }}" href="{{ f.url_to_remove }}">
            reset
          </a>
        {% endif %}
      </span>
      {{ 'icon-caret.svg' | inline_asset_content }}
    </summary>
    <div class="facets__display-vertical" x-data="{ showMore : $persist(false).as('sm-{{ f.param_name }}') }">
      <!-- Filter values -->
    </div>
  </details>
</div>
```

- **Native details element**: Uses semantic HTML5 `<details>` for accordion behavior.
- **Alpine.js binding**: `x-bind:open` syncs Alpine state with details open attribute.
- **Toggle handler**: `@toggle` updates Alpine state when details is toggled.
- **Active count**: Shows number of active filters in summary.
- **Reset link**: Allows clearing all active filters for that group.
- **Persistent show more**: Uses `$persist()` to remember "show more" state per filter.

### Filter Values with Show More

```liquid
{% for v in f.values %}
  {% assign input_id = 'Filter-' | append: f.param_name | escape | append: '-' | append: forloop.index %}
  <label
    class="facet-checkbox"
    {% if forloop.index > show_more_number %}
      x-show="showMore"
      x-transition
    {% endif %}
  >
    <input
      id="{{ input_id }}"
      type="checkbox"
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
{% endfor %}
{%- if f.type != 'price_range' and f.values.size > show_more_number -%}
  <button
    type="button"
    class="filters__show-more"
    x-on:click="showMore = !showMore"
    x-text="showMore ? 'Show less' : 'Show more'"
  >
    Show more
  </button>
{%- endif %}
```

- **Show more threshold**: First 10 filter values shown by default (`show_more_number = 10`).
- **Conditional display**: Values beyond threshold hidden with `x-show="showMore"`.
- **Smooth transitions**: `x-transition` provides smooth show/hide animation.
- **Dynamic button text**: Button text changes between "Show more" and "Show less".
- **Persistent state**: "Show more" state persists per filter using `$persist()`.

---

## Behavior

- **Accordion toggle**: Clicking summary opens/closes filter group.
- **Show more/less**: Button toggles visibility of additional filter values.
- **Filter updates**: Checkbox changes trigger Section Rendering API requests.
- **Reset functionality**: Reset link clears all active filters for that group.
- **Sticky positioning**: Sidebar stays visible while scrolling product grid.
- **Scrollable content**: Sidebar scrolls independently when content exceeds max height.
- **Persistent states**: Both accordion open state and "show more" state can persist (via `collapse_filters` and `$persist()`).

---

## Usage Example

```liquid
{% render 'component-filters-sidebar',
  results: collection,
  collapse_filters: section.settings.collapse_filters,
  show_filter_count: section.settings.show_filter_count,
  filter_type: section.settings.filter_type,
  section: section
%}
```

Or for search pages:

```liquid
{% render 'component-filters-sidebar',
  results: search,
  collapse_filters: section.settings.collapse_filters,
  show_filter_count: section.settings.show_filter_count,
  section: section
%}
```

Typically used in:
- Collection pages (`sections/collection.liquid`) with vertical filter layout
- Search pages (`sections/search.liquid`) with vertical filter layout
- As desktop filter option (mobile uses drawer)

---

## Implementation Notes

1. **Alpine.js requirement**: Snippet requires Alpine.js to be loaded in the theme for accordion and "show more" state management.

2. **Section Rendering API**: Filter changes use `data-render-section="filters-form"` to trigger AJAX updates. The form ID is `filters-form`.

3. **Desktop-only display**: Uses `small-hide` class to hide on mobile devices. Mobile typically uses `component-filters-drawer` instead.

4. **Filter group IDs**: Each filter group uses unique ID: `Details-\{\{ f.param_name | escape \}\}-\{\{ section.id \}\}`

5. **Sticky positioning**: Sidebar uses `position: sticky` with `top: calc(var(--header-height, 80px) + 20px)` to account for header height.

6. **Price range filters**: Price range filters are handled by `component-filters-price-range` snippet, not standard checkboxes.

7. **Disabled filters**: Filters with 0 results are disabled unless already active (to allow removing active filters with 0 results).

8. **Active filter count**: Shows count of active filters in summary: `(\{\{ f.active_values.size \}\})`

9. **Reset link**: Reset link uses `data-render-section-url` and `href` attributes for Section Rendering API integration.

10. **Show more threshold**: Default threshold is 10 filter values (`show_more_number = 10`). Values beyond this are hidden until "Show more" is clicked.

11. **Persistent show more state**: Uses Alpine.js `$persist()` plugin to remember "show more" state per filter:
    ```liquid
    x-data="{ showMore : $persist(false).as('sm-{{ f.param_name }}') }"
    ```
    Each filter gets its own persisted state key based on param name.

12. **Icon dependencies**: Requires the following icons in `assets/`:
    - `icon-caret.svg` (accordion indicator)
    - `icon-square.svg` (checkbox unchecked state)
    - `icon-checkmark.svg` (checkbox checked state)

13. **Form structure**: All filters are within `<form id="filters-form">` for proper form submission handling.

14. **Checkbox styling**: Uses custom icon-based checkboxes (`icon-square.svg` and `icon-checkmark.svg`) instead of native checkboxes for consistent styling.

15. **Filter value IDs**: Each checkbox uses unique ID: `Filter-\{\{ f.param_name | escape \}\}-\{\{ forloop.index \}\}`

16. **Alpine.js directives**:
    - `x-data="{ open: \{\{ open \}\} }"`: Initializes accordion state (true/false based on `collapse_filters`)
    - `x-bind:open="open"`: Syncs Alpine state with details open attribute
    - `@toggle="open = $event.target.open"`: Updates Alpine state when details toggles
    - `x-data="{ showMore : $persist(false).as('sm-\{\{ f.param_name \}\}') }"`: Persistent "show more" state
    - `x-show="showMore"`: Shows/hides additional filter values
    - `x-transition`: Provides smooth show/hide animation
    - `x-on:click="showMore = !showMore"`: Toggles "show more" state
    - `x-text="showMore ? 'Show less' : 'Show more'"`: Dynamic button text

17. **CSS class dependencies**: Snippet relies on CSS classes:
    - `.filters-sidebar`
    - `.facets__main-head-wrapper`
    - `.facets__heading`
    - `.filter-section`
    - `.facets__disclosure-vertical`
    - `.facets__display-vertical`
    - `.facet-checkbox`
    - `.filters__show-more`
    - `.reset-button`
    - `.svg-wrapper`
    - `.js-filter`

18. **Collapse filters option**: When `collapse_filters` is true, all filter groups start collapsed (`open = false`). Otherwise, they start expanded (`open = true`).

19. **Max height calculation**: Sidebar max height accounts for header: `calc(100vh - var(--header-height, 80px) - 40px)`

20. **Header height variable**: Uses CSS custom property `--header-height` with fallback to 80px.

21. **Filter count display**: Filter counts are shown in parentheses next to filter value labels when `show_filter_count` is truthy.

22. **Section ID usage**: Section ID is used for unique DOM targeting in filter group IDs.

23. **Price conversion**: Price range filters convert from cents to dollars by dividing by 100 (handled in `component-filters-price-range`).

24. **Accessibility considerations**:
    - Uses semantic `<details>` and `<summary>` elements
    - Proper label associations for checkboxes
    - Form structure with labels
    - Reset links for clearing filters
    - Keyboard navigation support via native details element

25. **Performance**: Inline styles prevent additional HTTP request but increase HTML size. Consider extracting to CSS file if used multiple times.

26. **Show more button**: Only appears when filter has more than 10 values and is not a price range filter.

27. **Caret icon rotation**: Caret icon rotates 180° when filter group is open via CSS `transform: rotate(180deg)`.

28. **No translation keys**: Filter labels come directly from Shopify filter objects, not translation files. "Show more"/"Show less" text is hardcoded in English.

29. **Scrollable sidebar**: When filter content exceeds max height, sidebar becomes scrollable independently of page scroll.

30. **Flex shrink**: Sidebar uses `flex-shrink: 0` to prevent compression in flex layouts.

31. **Border separation**: Each filter section has a top border for visual separation.

32. **Summary padding**: Summary elements have specific padding for consistent spacing.

33. **Show more button styling**: Button has hover effect with outline for better UX.

34. **Native details behavior**: Uses native HTML5 `<details>` element which provides:
    - Built-in keyboard navigation
    - Screen reader support
    - No JavaScript required for basic functionality
    - Alpine.js enhances with state management

35. **Filter group state sync**: Alpine.js state (`open`) is synced with details `open` attribute bidirectionally:
    - `x-bind:open="open"`: Alpine → HTML
    - `@toggle="open = $event.target.open"`: HTML → Alpine

