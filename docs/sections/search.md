# Search Section (`sections/search.liquid`)

`sections/search.liquid` renders the search results page with filtering, sorting, and pagination capabilities. It displays products, articles, and pages in a grid layout with support for infinite scroll, quick add functionality, and multiple filter types (horizontal, vertical, drawer). The section uses Alpine.js for search input state and integrates with predictive search when enabled.

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | `component-product-price.css`, `component-product-card.css`, `component-pagination.css`, `section-collection.css`, `section-search.css`, `component-quick-add.css` (conditional) |
| JavaScript | `section-collection.js`, `component-product-card.js`, `component-filters-price-range.js`, `component-infinite-scroll.js` (conditional), `component-quick-add.js` (conditional), `component-modal-opener.js` (conditional) |
| Custom Elements | `<collection-info>`, `<infinite-scroll>` |
| Snippets | `component-predictive-search`, `component-filters-sidebar`, `component-filters-drawer`, `component-filters-horizontal`, `component-product-card`, `component-article-card`, `component-pagination` |
| Icons | `icon-close.svg` (inline via `inline_asset_content`) |

- Many assets are conditionally loaded based on section settings.
- Section shares collection functionality via `section-collection.js` and `section-collection.css`.
- Predictive search integration when `settings.predictive_search_enabled` is true.

---

## Dynamic Styles

Dynamic styles are generated via an inline `{% style %}` block:

```liquid
{%- style -%}
  .collection-filters-wrapper {
    display: flex;
    {%- if section.settings.enable_filtering and section.settings.filter_type == "vertical" -%}
      flex-direction: row;
    {%- elsif section.settings.enable_filtering and section.settings.filter_type == "horizontal" -%}
      flex-direction: column;
    {% else %}
      flex-direction: column;
    {%- endif -%}
  }

  .product-grid {
    display: grid;
    grid-template-columns: repeat({{ section.settings.columns_desktop }}, 1fr);
    gap: 10px;
  }

  .section-{{ section.id }}-padding {
    padding-top: {{ section.settings.padding_top | times: 0.75 | round: 0 }}px;
    padding-bottom: {{ section.settings.padding_bottom | times: 0.75 | round: 0 }}px;
  }

  @media screen and (min-width: 769px) {
    .section-{{ section.id }}-padding {
      padding-top: {{ section.settings.padding_top }}px;
      padding-bottom: {{ section.settings.padding_bottom }}px;
    }
  }

  @media screen and (max-width: 990px) {
    .product-grid {
      grid-template-columns: repeat({{ section.settings.columns_mobile }}, 1fr);
    }
  }

  .product-grid-{{section.id}} .product-grid .quick-add__submit {
    color: {{ section.settings.button_text_color }};
    background-color: {{ section.settings.button_background_color }};
    border-color: {{ section.settings.button_border_color }};
    transition: all 0.2s ease;
  }

  .product-grid-{{section.id}} .quick-add__submit:hover {
    background-color: {{ section.settings.button_background_color | color_modify: 'alpha', 0.8 }};
  }
{%- endstyle -%}
```

- **Filter layout**: Flex direction changes based on filter type (vertical vs horizontal).
- **Grid columns**: Dynamic grid columns based on desktop and mobile settings.
- **Responsive padding**: Mobile padding is 75% of desktop padding.
- **Button styling**: Dynamic button colors for quick add functionality.
- **Hover effects**: Button background opacity changes on hover.

---

## Markup Structure

```liquid
<div class="template-search{% unless search.performed and search.results_count > 0 %} template-search--empty{% endunless %} section-{{ section.id }}-padding">
  <div class="template-search__header color-{{ section.settings.color_scheme }} page-width">
    <!-- Search title -->
    <!-- Predictive search form -->
    <!-- Results count / no results message -->
  </div>
  {%- if search.performed -%}
    <div class="collection-info-wrapper page-width">
      <collection-info data-section="{{ section.id }}">
        <!-- Filters, sorting, product grid -->
      </collection-info>
    </div>
  {%- endif -%}
</div>
```

- **Conditional classes**: Adds `template-search--empty` class when no search has been performed or no results exist.
- **Color scheme**: Header uses dynamic color scheme from settings.
- **Custom element**: Uses `<collection-info>` custom element for filter/sort functionality.

### Header Section

```liquid
<div class="template-search__header color-{{ section.settings.color_scheme }} page-width{% if settings.animations_reveal_on_scroll %} scroll-trigger animate--fade-in{% endif %}">
  <h1 class="h2 center">
    {%- if search.performed -%}
      {{- 'templates.search.title' | t -}}
    {%- else -%}
      {{- 'general.search.search' | t -}}
    {%- endif -%}
  </h1>
  <div class="template-search__search" x-data="{ searchTerm: '{{ search.terms | escape }}' }" @input="searchTerm = $event.target.value">
    {%- if settings.predictive_search_enabled -%}
      {%- render 'component-predictive-search', context: 'search-page' -%}
    {%- endif -%}
  </div>
  <!-- Results count / no results message -->
</div>
```

- **Alpine.js integration**: Uses Alpine.js for search input state management.
- **Predictive search**: Conditionally renders predictive search component.
- **Dynamic title**: Changes based on whether search has been performed.

### Filters and Sorting

The section supports three filter types:

#### Vertical Filters
```liquid
{%- if section.settings.enable_filtering and section.settings.filter_type == 'vertical' -%}
  {% render 'component-filters-sidebar',
    results: search,
    collapse_filters: section.settings.collapse_filters,
    show_filter_count: section.settings.show_filter_count
  %}
{% endif %}
```

- **Sidebar layout**: Filters appear in a sidebar alongside results.
- **Mobile drawer**: Includes mobile filter drawer for smaller screens.

#### Horizontal Filters
```liquid
{%- if section.settings.enable_filtering and section.settings.filter_type == 'horizontal' -%}
  <div class="horizontal-filters__parent-wrapper">
    {% render 'component-filters-horizontal',
      results: search,
      show_filter_count: section.settings.show_filter_count
    %}
    <!-- Mobile drawer -->
  </div>
{% endif %}
```

- **Top layout**: Filters appear above the product grid.
- **Mobile drawer**: Includes mobile filter drawer for smaller screens.

#### Drawer Filters
```liquid
{% elsif section.settings.enable_filtering and section.settings.filter_type == 'drawer' %}
  <div class="horizontal-filters__parent-wrapper">
    {% render 'component-filters-drawer', ... %}
  </div>
{% endif %}
```

- **Drawer-only**: All filters contained in a drawer interface.

### Active Filters Display

```liquid
<div id="active-filter-group-{{ section.id }}" class="active-filter-group__item-wrapper">
  {%- for f in search.filters -%}
    <!-- Price range filters -->
    <!-- Active value filters -->
  {%- endfor -%}
  <!-- Clear all filters link -->
</div>
```

- **Active filter chips**: Displays selected filters as removable chips.
- **Price range display**: Shows selected price range with min/max values.
- **Clear all**: Provides link to clear all active filters at once.

### Product Grid

```liquid
<div class="product-grid-wrapper product-grid-{{ section.id }}" id="product-grid-{{ section.id }}">
  <div id="loading-overlay-{{ section.id }}" class="loading-overlay"></div>
  <div class="product-grid" {% if section.settings.enable_infinite_scroll %} data-product-grid {% endif %}>
    {%- for item in search.results -%}
      {%- case item.object_type -%}
        {%- when 'product' -%}
          {% render 'component-product-card', ... %}
        {%- when 'article' -%}
          {% render 'component-article-card', ... %}
        {%- when 'page' -%}
          <!-- Page card markup -->
      {%- endcase -%}
    {%- endfor -%}
  </div>
  <!-- Pagination or infinite scroll -->
</div>
```

- **Multiple result types**: Handles products, articles, and pages.
- **Lazy loading**: Images lazy load after the first two items.
- **Infinite scroll**: Optional infinite scroll when enabled.
- **Loading overlay**: Shows loading state during filter/sort updates.

### Pagination

```liquid
{% if section.settings.enable_infinite_scroll %}
  <infinite-scroll style="display: flex; justify-content: center;">
    {%- if paginate.next -%}
      <a href="{{ paginate.next.url }}&section_id={{ section.id }}"></a>
    {%- endif -%}
  </infinite-scroll>
{% else %}
  {%- if paginate.pages > 1 -%}
    {% render 'component-pagination', paginate: paginate, anchor: '' %}
  {%- endif -%}
{% endif %}
```

- **Two modes**: Supports either infinite scroll or traditional pagination.
- **Section ID**: Includes section ID in infinite scroll URLs for proper rendering.

---

## Behavior

- **Search results**: Displays products, articles, and pages from search query.
- **Filtering**: Supports multiple filter types with AJAX updates via Section Rendering API.
- **Sorting**: Dropdown sort selector updates results via AJAX.
- **Infinite scroll**: Loads more results automatically when scrolling (when enabled).
- **Quick add**: Product cards support quick add to cart when enabled.
- **Predictive search**: Integrates with predictive search component when enabled.
- **Loading states**: Shows loading overlay during filter/sort updates.
- **Active filters**: Displays and allows removal of active filters.

---

## Schema

The section includes extensive settings for layout, filtering, sorting, and display options. Key settings include:

### Display Settings
- **Products per page**: `products_per_page` (8-36, default: 16)
- **Columns desktop**: `columns_desktop` (1-6, default: 4)
- **Columns mobile**: `columns_mobile` (1-2, default: 2)
- **Color scheme**: `color_scheme`
- **Image ratio**: `image_ratio` (adapt, portrait, square)

### Product Card Settings
- **Show vendor**: `show_vendor`
- **Show rating**: `show_rating`
- **Quick add**: `quick_add` (none, standard)
- **Enable swatches**: `enable_swatches`
- **Swatch type**: `swatch_type` (color, image)
- **Swatch trigger**: `swatch_trigger` (option name for swatches)

### Filtering Settings
- **Enable filtering**: `enable_filtering`
- **Filter type**: `filter_type` (horizontal, vertical, drawer)
- **Collapse filters**: `collapse_filters`
- **Show filter count**: `show_filter_count`

### Sorting Settings
- **Enable sorting**: `enable_sorting`

### Article Settings
- **Article show date**: `article_show_date`
- **Article show author**: `article_show_author`

### Pagination Settings
- **Enable infinite scroll**: `enable_infinite_scroll`

### Button Styling
- **Button text color**: `button_text_color`
- **Button border color**: `button_border_color`
- **Button background color**: `button_background_color`

### Padding Settings
- **Padding top**: `padding_top` (0-100px, default: 36)
- **Padding bottom**: `padding_bottom` (0-100px, default: 36)

---

## Implementation Notes

1. **Search object**: Uses Shopify's `search` object which contains `results`, `results_count`, `performed`, `terms`, `filters`, `sort_by`, `sort_options`, etc.

2. **Result types**: Search results can include multiple object types:
   - Products (`item.object_type == 'product'`)
   - Articles (`item.object_type == 'article'`)
   - Pages (`item.object_type == 'page'`)

3. **Pagination**: Uses `{% paginate search.results by section.settings.products_per_page %}` to paginate results.

4. **Filter integration**: Filters use Section Rendering API to update results without page reload. Filter components (`component-filters-sidebar`, `component-filters-horizontal`, `component-filters-drawer`) handle the AJAX requests.

5. **Sort integration**: Sort dropdown uses `data-render-section="filters-form"` attribute to trigger Section Rendering API updates.

6. **Active filters**: Active filters are calculated by checking:
   - Price range filters: `f.min_value.value > 0` or `f.max_value.value < f.range_max`
   - Other filters: `f.active_values.size > 0`

7. **Clear all filters**: Generates URL with search terms only: `?q=\{\{ search.terms | escape \}\}`.

8. **Lazy loading**: Images lazy load after the first two items (`forloop.index > 2`).

9. **Infinite scroll**: Uses `<infinite-scroll>` custom element which loads next page via AJAX when user scrolls near bottom.

10. **Loading overlay**: Shows loading state during filter/sort updates via `loading-overlay-\{\{ section.id \}\}` element.

11. **Results count**: Displays results count with search terms: `'templates.search.results_with_count' | t: terms: search.terms, count: search.results_count`.

12. **Empty state**: Shows "no results" message when `search.results_count == 0` and no filters are active.

13. **Predictive search**: Integrates with `component-predictive-search` snippet when `settings.predictive_search_enabled` is true.

14. **Alpine.js**: Uses Alpine.js for search input state management (`x-data`, `@input`).

15. **Translation keys**: All user-facing text uses translation filters (`templates.search.*`, `general.search.*`).

16. **Custom element**: Uses `<collection-info>` custom element (shared with collection pages) for filter/sort functionality.

17. **Section Rendering API**: Filter and sort changes trigger Section Rendering API requests to update the product grid without full page reload.

18. **Button styling**: Quick add buttons use dynamic colors from section settings with hover effects.

19. **Responsive grid**: Grid columns adjust based on `columns_desktop` and `columns_mobile` settings with media query breakpoint at 990px.

20. **Animation support**: Header includes scroll-trigger animation classes when `settings.animations_reveal_on_scroll` is enabled.

21. **Page cards**: Pages are rendered with custom markup (not using a snippet) with badge indicating "Page" type.

22. **Article cards**: Articles use `component-article-card` snippet with configurable date and author display.

23. **Product cards**: Products use `component-product-card` snippet with full configuration options (swatches, quick add, vendor, etc.).

24. **Filter form IDs**: Sort dropdown uses different form IDs based on filter type:
    - `filters-form-drawer` for drawer type
    - `filters-form` for horizontal/vertical types

25. **Mobile filter drawer**: All filter types include mobile drawer version for smaller screens (`large-up-hide` class).

26. **Price range filter**: Price range filters display min/max values formatted with `money` filter.

27. **Filter removal**: Active filters can be removed by clicking the close icon, which triggers Section Rendering API request to `f.url_to_remove` or `v.url_to_remove`.

28. **Sort options**: Sort dropdown populated from `search.sort_options` with current selection from `search.sort_by`.

29. **Section ID in URLs**: Infinite scroll URLs include `section_id=\{\{ section.id \}\}` parameter for proper Section Rendering API requests.

30. **CSS class dependencies**: Section relies on many CSS classes from shared collection and search stylesheets.

