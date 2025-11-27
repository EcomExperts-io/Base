# component-filters-drawer Snippet

`snippets/component-filters-drawer.liquid` renders a slide-in filters drawer for collection and search pages. It provides faceted filtering with nested drawer navigation, optional sorting, and Alpine.js-powered state management. The drawer includes persistent filter state, loading indicators, and responsive design for mobile and desktop use.

---

## What It Does

- Renders a slide-in drawer interface for product filtering and sorting.
- Displays filter facets (checkboxes) with nested drawer navigation for filter values.
- Supports price range filters via `component-filters-price-range` snippet.
- Includes optional sorting dropdown within the drawer.
- Uses Alpine.js for drawer open/close state and filter group persistence.
- Shows results count and loading states during filter updates.
- Prevents body scroll when drawer is open.
- Integrates with Section Rendering API for AJAX filter updates.

---

## Parameters

| Parameter          | Type    | Default      | Description                                                      |
|--------------------|---------|--------------|------------------------------------------------------------------|
| `results`          | object  | **required** | Collection or search object providing filters and sort options. |
| `enable_filtering` | boolean | **required** | Show filter facets in the drawer.                                |
| `enable_sorting`   | boolean | **required** | Show sorting dropdown in the drawer.                             |
| `color_scheme`     | string  | `'scheme-1'` | Color scheme for drawer styling.                                 |
| `section_id`       | string  | **required** | Unique section identifier for DOM IDs and JavaScript targeting. |
| `show_filter_count`| string  | optional     | Show product count next to each filter value.                    |
| `context`          | string  | optional     | Context identifier ('collection' or 'search') for results count display. |

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | Inline `{% style %}` block with comprehensive drawer styling |
| JavaScript | Alpine.js (required for state management), Section Rendering API integration |
| Snippets | `component-filters-price-range` (for price range filters) |
| Icons | `icon-filter.svg`, `icon-close.svg`, `icon-arrow.svg`, `icon-square.svg`, `icon-checkmark.svg` (inline via `inline_asset_content`) |
| Data | Requires `results` object with `filters`, `sort_options`, `sort_by`, `default_sort_by`, `products_count`, `all_products_count`, `results_count`, `terms` |

- Alpine.js powers drawer state (`x-data`, `:class`, `@click`).
- Inline styles provide all drawer-specific CSS (no external CSS file required).
- Section Rendering API handles filter updates via `data-render-section` attributes.

---

## Dynamic Styles

The snippet includes extensive inline styles for drawer behavior, animations, and responsive design:

```liquid
{%- style -%}
  .filters-drawer {
    width: calc(100% - 50px);
    max-width: 370px;
  }

  .drawer-main-wrapper:not(.drawer-active) .drawer-overlay {
    opacity: 0;
    transition: opacity 0.4s, width 0s linear 0.4s, visibility 0s linear 0.4s;
    visibility: hidden;
    width: 0;
    pointer-events: none;
  }

  .drawer-main-wrapper:not(.drawer-active) .drawer__wrapper {
    transform: translate(100%, 0px);
  }

  /* ... extensive styling for drawer components ... */

  body:has(.drawer-main-wrapper.drawer-active) {
    overflow: hidden;
  }

  @media screen and (max-width: 768px) {
    /* Mobile-specific font size adjustments */
  }
{%- endstyle -%}
```

- **Drawer width**: `calc(100% - 50px)` with `max-width: 370px` for responsive sizing.
- **Overlay animation**: Smooth fade in/out with delayed visibility changes.
- **Drawer slide**: Uses `transform: translate(100%, 0px)` to slide in from right.
- **Body scroll lock**: Prevents scrolling when drawer is open using `:has()` selector.
- **Responsive adjustments**: Mobile-specific font sizes at 768px breakpoint.

---

## Markup Structure

```liquid
<div
  x-data="{ open: false }"
  class="drawer-main-wrapper color-{{ color_scheme | default: 'scheme-1' }}"
  :class="{ 'drawer-active': open }"
  id="Details-{{ section_id }}"
>
  <!-- Trigger button -->
  <!-- Overlay -->
  <!-- Drawer content -->
</div>
```

- **Alpine.js state**: Uses `x-data="{ open: false }"` for drawer open/close state.
- **Dynamic class**: Applies `drawer-active` class when `open` is true.
- **Color scheme**: Applies theme color scheme for consistent styling.

### Trigger Button

```liquid
<button type="button" @click="open = !open" class="drawer__facet-button-trigger">
  <div class="svg-wrapper">
    {{ 'icon-filter.svg' | inline_asset_content }}
  </div>
  <div class="desktop-facet-text-wrapper small-hide">
    {%- if enable_filtering -%}
      <span>{{ 'products.facets.filter_button' | t }}</span>
    {%- elsif enable_sorting -%}
      <span>{{ 'products.facets.sort_button' | t }}</span>
    {%- endif -%}
  </div>
  <div class="mobile-facet-text-wrapper large-up-hide">
    {%- if enable_filtering and enable_sorting -%}
      <span>{{ 'products.facets.filter_and_sort' | t }}</span>
    {%- elsif enable_filtering -%}
      <span>{{ 'products.facets.filter_button' | t }}</span>
    {%- elsif enable_sorting -%}
      <span>{{ 'products.facets.sort_button' | t }}</span>
    {%- endif -%}
  </div>
</button>
```

- **Responsive text**: Different button text for desktop vs mobile.
- **Conditional text**: Changes based on filtering/sorting enabled.
- **Icon display**: Shows filter icon alongside text.

### Drawer Header

```liquid
<div class="facets__header-drawer">
  <div class="child-facets__header-wrapper">
    <div class="mobile-facets__header-inner">
      <h2 class="mobile-facets__heading">...</h2>
      <div class="drawer__count-wrapper">
        <p class="mobile-facets__count" id="drawer-results-count-{{ section_id }}">
          <!-- Results count -->
        </p>
        <div id="drawer-loading-spinner-{{ section_id }}" class="loading-overlay__spinner"></div>
      </div>
    </div>
    <div class="drawer-close-icon" @click="open = !open">
      <!-- Close icon -->
    </div>
  </div>
</div>
```

- **Sticky header**: Header stays at top when scrolling filter values.
- **Results count**: Displays product count with context-aware formatting.
- **Loading spinner**: Shows loading state during filter updates.
- **Close button**: Allows closing drawer from header.

### Filter Facets

```liquid
<div class="drawer__facets-wrapper" x-data="{ openFilter: $persist(true).as('openFilter') }">
  <div class="drawer__child-facets-wrapper">
    {%- for f in results.filters -%}
      <div id="Details-{{ f.param_name | escape }}-{{ section_id }}-Drawer" class="single-facet__link js-filter">
        <div class="mobile-facets__block" @click="openFilter = openFilter === {{ forloop.index }} ? null : {{ forloop.index }}">
          <span>{{ f.label }}</span>
          <span class="mobile-facets__arrow">
            <!-- Arrow icon -->
          </span>
        </div>
        <div class="facets__values-drawer" :class="{ 'child-drawer-active': openFilter === {{ forloop.index }} }">
          <!-- Filter values (checkboxes or price range) -->
        </div>
      </div>
    {%- endfor -%}
  </div>
</div>
```

- **Persistent state**: Uses Alpine.js `$persist()` to remember last opened filter.
- **Nested drawers**: Each filter group opens its own drawer for values.
- **Toggle behavior**: Clicking filter label toggles its drawer open/closed.
- **Price range support**: Renders `component-filters-price-range` for price filters.

### Filter Values

```liquid
{%- for v in f.values -%}
  <label class="facet-checkbox">
    <input
      id="{{ input_id }}"
      type="checkbox"
      name="{{ v.param_name }}"
      value="{{ v.value }}"
      data-render-section="filters-form-drawer"
      {% if v.active %}checked{% endif %}
      {% if v.count == 0 and v.active == false %}disabled{% endif %}
    >
    {{- 'icon-square.svg' | inline_asset_content -}}
    <div class="svg-wrapper">
      {{- 'icon-checkmark.svg' | inline_asset_content -}}
    </div>
    {{- v.label }}
    {% if show_filter_count != blank %} ({{ v.count }}){% endif %}
  </label>
{%- endfor -%}
```

- **Custom checkboxes**: Uses icon-based checkboxes for styling.
- **Active state**: Pre-checks active filters.
- **Disabled state**: Disables filters with 0 results (unless already active).
- **Section Rendering API**: `data-render-section="filters-form-drawer"` triggers AJAX updates.
- **Filter count**: Optionally shows product count next to each value.

### Sorting Dropdown

```liquid
{%- if enable_sorting -%}
  <div class="drawer__child-sorting-wrapper">
    <div id="sort-by-drawer-{{ section_id }}" class="facet-filters__field large-up-hide">
      <h2 class="facet-filters__label">
        <label for="SortBy">{{ 'products.facets.sort_by_label' | t }}</label>
      </h2>
      <select
        data-render-section="filters-form-drawer"
        name="sort_by"
        id="SortBy"
        class="facet-filters__sort"
      >
        {%- for option in results.sort_options -%}
          <option value="{{ option.value | escape }}" {% if option.value == sort_by %}selected="selected"{% endif %}>
            {{ option.name | escape }}
          </option>
        {%- endfor -%}
      </select>
    </div>
  </div>
{%- endif -%}
```

- **Mobile-only**: Sorting shown only on mobile (`large-up-hide`).
- **Section Rendering API**: Sort changes trigger AJAX updates.
- **Current selection**: Pre-selects current sort option.

---

## Behavior

- **Drawer toggle**: Button opens/closes drawer via Alpine.js state.
- **Overlay click**: Clicking overlay closes drawer.
- **Filter group toggle**: Clicking filter label opens nested drawer for that group's values.
- **Persistent state**: Last opened filter group persists between page loads via `$persist()`.
- **Filter updates**: Checkbox changes trigger Section Rendering API requests to update product grid.
- **Sort updates**: Sort dropdown changes trigger Section Rendering API requests.
- **Loading states**: Shows spinner during filter/sort updates.
- **Results count**: Updates dynamically after filter changes.
- **Body scroll lock**: Prevents background scrolling when drawer is open.
- **Nested navigation**: Filter values slide in from right, back button returns to main list.

---

## Usage Example

```liquid
{% render 'component-filters-drawer',
  results: collection,
  enable_filtering: section.settings.enable_filtering,
  enable_sorting: section.settings.enable_sorting,
  color_scheme: section.settings.color_scheme,
  section_id: section.id,
  show_filter_count: section.settings.show_filter_count,
  context: 'collection'
%}
```

Or for search pages:

```liquid
{% render 'component-filters-drawer',
  results: search,
  enable_filtering: section.settings.enable_filtering,
  enable_sorting: section.settings.enable_sorting,
  color_scheme: section.settings.color_scheme,
  section_id: section.id,
  show_filter_count: section.settings.show_filter_count,
  context: 'search'
%}
```

Typically used in:
- Collection pages (`sections/collection.liquid`)
- Search pages (`sections/search.liquid`)
- As mobile filter option for horizontal/vertical filter layouts

---

## Implementation Notes

1. **Alpine.js requirement**: Snippet requires Alpine.js to be loaded in the theme for state management.

2. **Section Rendering API**: Filter and sort changes use `data-render-section="filters-form-drawer"` to trigger AJAX updates. The form ID is `filters-form-drawer`.

3. **Persistent filter state**: Uses Alpine.js `$persist()` plugin to remember which filter group was last opened:
   ```liquid
   x-data="{ openFilter: $persist(true).as('openFilter') }"
   ```

4. **Filter group IDs**: Each filter group uses unique ID: `Details-\{\{ f.param_name | escape \}\}-\{\{ section_id \}\}-Drawer`

5. **Nested drawer animation**: Filter value drawers slide in from right using `transform: translate(100%)` and `transform: translate(0px)` when active.

6. **Price range filters**: Price range filters are handled by `component-filters-price-range` snippet, not standard checkboxes.

7. **Disabled filters**: Filters with 0 results are disabled unless already active (to allow removing active filters with 0 results).

8. **Results count display**: Results count format differs for collection vs search:
   - Collection: `products.facets.results_count` or `products.facets.results_count_of`
   - Search: `templates.search.results_with_count`

9. **Loading spinner**: Spinner shows/hides via JavaScript during Section Rendering API requests.

10. **Body scroll lock**: Uses CSS `:has()` selector to prevent body scrolling when drawer is open. Requires modern browser support.

11. **Responsive visibility**: Drawer trigger button hidden on desktop when filtering is disabled (`large-up-hide` class).

12. **Form structure**: All filters are within `<form id="filters-form-drawer">` for proper form submission handling.

13. **Checkbox styling**: Uses custom icon-based checkboxes (`icon-square.svg` and `icon-checkmark.svg`) instead of native checkboxes for consistent styling.

14. **Filter value IDs**: Each checkbox uses unique ID: `Filter-Drawer-\{\{ f.param_name | escape \}\}-\{\{ forloop.index \}\}`

15. **Translation keys**: All user-facing text uses translation filters:
    - `products.facets.filter_button`
    - `products.facets.sort_button`
    - `products.facets.filter_and_sort`
    - `products.facets.results_count`
    - `products.facets.results_count_of`
    - `products.facets.sort_by_label`
    - `templates.search.results_with_count`
    - `accessibility.close`

16. **Icon dependencies**: Requires the following icons in `assets/`:
    - `icon-filter.svg`
    - `icon-close.svg`
    - `icon-arrow.svg`
    - `icon-square.svg`
    - `icon-checkmark.svg`

17. **Color scheme integration**: Drawer uses theme color scheme via `color-\{\{ color_scheme \}\}` class.

18. **Mobile-first design**: Drawer is primarily designed for mobile use, though it can be used on desktop as well.

19. **Accessibility considerations**:
    - Proper button labels
    - Form structure with labels
    - Hidden close text for screen readers
    - Semantic HTML structure

20. **Performance**: Inline styles prevent additional HTTP request but increase HTML size. Consider extracting to CSS file if drawer is used multiple times per page.

21. **Filter count display**: Filter counts are shown in parentheses next to filter value labels when `show_filter_count` is not blank.

22. **Sort dropdown visibility**: Sort dropdown is only shown on mobile (`large-up-hide`) to avoid duplication with desktop sort controls.

23. **Overlay behavior**: Overlay fades in/out with smooth transitions and prevents interaction when drawer is closed.

24. **Nested drawer close**: Back button in nested drawer uses `@click.stop` to prevent event bubbling and closes only the nested drawer.

25. **Filter group state**: Each filter group can be independently opened/closed, with only one open at a time (controlled by `openFilter` variable).

26. **Section ID usage**: Section ID is used throughout for unique DOM targeting:
    - Drawer wrapper: `Details-\{\{ section_id \}\}`
    - Results count: `drawer-results-count-\{\{ section_id \}\}`
    - Loading spinner: `drawer-loading-spinner-\{\{ section_id \}\}`
    - Sort dropdown: `sort-by-drawer-\{\{ section_id \}\}`
    - Filter groups: `Details-\{\{ f.param_name \}\}-\{\{ section_id \}\}-Drawer`

27. **Context parameter**: The `context` parameter determines which results count format to use (collection vs search).

28. **Filter form submission**: Form doesn't use traditional submission - all updates happen via Section Rendering API triggered by `data-render-section` attributes.

29. **Animation timing**: Drawer slide animation uses 0.3s ease transition, overlay uses 0.4s with delayed visibility changes.

30. **Z-index management**: Drawer uses z-index values (2 for header, 9 for footer, 10 for nested drawers) to ensure proper layering.

