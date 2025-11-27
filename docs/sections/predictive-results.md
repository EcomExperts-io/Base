# Predictive Results Section (`sections/predictive-results.liquid`)

`sections/predictive-results.liquid` displays search results from Shopify's predictive search API. It renders suggestions, collections, articles, pages, and products in organized sections with proper ARIA attributes for accessibility. The section only renders when a predictive search has been performed.

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | `component-predictive-search.css` (loaded in theme layout when predictive search is enabled) |
| JavaScript | `component-predictive-search.js` (loaded in theme layout when predictive search is enabled) |
| Snippets | `component-product-price` (for product pricing display) |
| Icons | `icon-arrow.svg` (inline via `inline_asset_content`) |
| Data | Relies on `predictive_search` object (resources: queries, collections, articles, pages, products) |

- Section only renders when `predictive_search.performed` is `true`.
- CSS and JavaScript are loaded conditionally in `layout/theme.liquid` based on `settings.predictive_search_enabled`.
- Product results use the `component-product-price` snippet for consistent pricing display.
- Section respects theme settings: `settings.predictive_search_show_vendor` and `settings.predictive_search_show_price`.

---

## Markup Structure

```liquid
{%- if predictive_search.performed -%}
  <div id="predictive-search-results">
    <div id="predictive-results__wrapper">
      <!-- Suggestions (queries and collections) -->
      <!-- Articles and Pages -->
      <!-- Products -->
    </div>
    <!-- View all results link -->
  </div>
{%- endif -%}
```

- **Conditional rendering**: Section only displays when predictive search has been performed.
- **Container IDs**: Uses `id="predictive-search-results"` and `id="predictive-results__wrapper"` for JavaScript targeting.
- **Accessibility**: All lists use proper ARIA roles (`role="listbox"`, `role="option"`).

### Suggestions Section

```liquid
{%- if predictive_search.resources.queries.size > 0 or predictive_search.resources.collections.size > 0 -%}
  <div>
    <h3>Suggestions</h3>
    <ul role="listbox" aria-labelledby="predictive-search-suggestions">
      {%- for query in predictive_search.resources.queries -%}
        <li role="option">
          <a href="{{ query.url }}" class="predictive-search__item" tabindex="-1">
            {{ query.styled_text }}
          </a>
        </li>
      {%- endfor -%}
      {%- for collection in predictive_search.resources.collections -%}
        <li role="option">
          <a href="{{ collection.url }}" class="predictive-search__item" tabindex="-1">
            {{ collection.title }}
          </a>
        </li>
      {%- endfor -%}
    </ul>
  </div>
{%- endif -%}
```

- **Query suggestions**: Displays styled text from search queries (e.g., "shoes" with matching terms highlighted).
- **Collection links**: Shows matching collections by title.
- **ARIA attributes**: Uses `role="listbox"` and `role="option"` for screen reader support.
- **Tabindex**: Links use `tabindex="-1"` to allow programmatic focus management by JavaScript.

### Articles and Pages Section

```liquid
{%- if predictive_search.resources.articles.size > 0 or predictive_search.resources.pages.size > 0 -%}
  <div>
    <h3>Articles and Pages</h3>
    <ul role="listbox" aria-labelledby="predictive-search-articles">
      {%- for page in predictive_search.resources.pages -%}
        <li role="option">
          <a href="{{ page.url }}" class="predictive-search__item" tabindex="-1">
            {{ page.title | escape }}
          </a>
        </li>
      {%- endfor -%}
      {%- for article in predictive_search.resources.articles -%}
        <li role="option">
          <a href="{{ article.url }}" class="predictive-search__item" tabindex="-1">
            {{ article.title | escape }}
          </a>
        </li>
      {%- endfor -%}
    </ul>
  </div>
{%- endif -%}
```

- **Content pages**: Displays matching pages and blog articles.
- **Title escaping**: All titles are escaped for security.
- **Consistent structure**: Same ARIA pattern as suggestions section.

### Products Section

```liquid
{%- if predictive_search.resources.products.size > 0 -%}
  <div class="predictive-search__products">
    <h3>Products</h3>
    <ul role="listbox" aria-labelledby="predictive-search-products">
      {%- for product in predictive_search.resources.products -%}
        <li role="option">
          <a href="{{ product.url }}">
            {%- if product.featured_media != blank -%}
              <img
                class="predictive-search__image"
                src="{{ product.featured_media | image_url: width: 150 }}"
                alt="{{ product.featured_media.alt | escape }}"
                width="50"
                height="{{ 50 | divided_by: product.featured_media.preview_image.aspect_ratio }}"
              >
            {%- endif -%}
            <div class="predictive-search__item-content">
              {%- if settings.predictive_search_show_vendor -%}
                <small class="predictive-search__item-vendor">
                  {{ product.vendor }}
                </small>
              {%- endif -%}
              <p class="predictive-search__item-heading">{{ product.title | escape }}</p>
              {%- if settings.predictive_search_show_price -%}
                {% render 'component-product-price', product: product, use_variant: true, show_badges: false %}
              {%- endif -%}
            </div>
          </a>
        </li>
      {%- endfor -%}
    </ul>
  </div>
{%- endif -%}
```

- **Product images**: Shows featured media at 150px width, displayed at 50px width with calculated height for aspect ratio.
- **Vendor display**: Conditionally shows vendor based on `settings.predictive_search_show_vendor`.
- **Price display**: Uses `component-product-price` snippet when `settings.predictive_search_show_price` is enabled.
- **Image aspect ratio**: Calculates height dynamically to maintain proper aspect ratio.

### View All Results Link

```liquid
<a href="{{ routes.search_url }}?q={{ predictive_search.terms }}">
  <span>Search for "{{ predictive_search.terms }}"</span>
  {{- 'icon-arrow.svg' | inline_asset_content -}}
</a>
```

- **Full search page**: Links to the full search results page with the search query.
- **Icon**: Uses inline SVG arrow icon for visual indication.
- **Query parameter**: Passes search terms via `q` query parameter.

---

## Behavior

- **Conditional rendering**: Section only renders when `predictive_search.performed` is `true`.
- **Dynamic content**: All content is server-rendered based on predictive search API results.
- **Accessibility**: Full ARIA support with proper roles and labels for screen readers.
- **Keyboard navigation**: Links use `tabindex="-1"` to allow JavaScript to manage focus programmatically.
- **Theme settings integration**: Respects `settings.predictive_search_show_vendor` and `settings.predictive_search_show_price` for conditional display.

---

## Schema

This section does not include a `{% schema %}` block, meaning:

- No customizable settings in the theme editor.
- All configuration comes from theme settings (`settings.predictive_search_show_vendor`, `settings.predictive_search_show_price`).
- Section is typically rendered via AJAX by the predictive search JavaScript component.

**Note**: This section is designed to be dynamically loaded into a container (typically `#predictive-search`) by the `component-predictive-search.js` custom element.

---

## Implementation Notes

1. **Predictive search integration**: This section is loaded via AJAX by the `<predictive-search>` custom element when users type in the search input. The JavaScript fetches this section with the search query and renders it into the results container.

2. **Translation keys**: Section headings ("Suggestions", "Articles and Pages", "Products") are hardcoded and not localized. Consider using translation filters if internationalization is needed.

3. **Image optimization**: Product images are requested at 150px width but displayed at 50px, allowing for high-DPI displays while keeping file sizes reasonable.

4. **Aspect ratio calculation**: Product image height is calculated using `50 | divided_by: product.featured_media.preview_image.aspect_ratio` to maintain proper proportions.

5. **Query styled text**: Search query suggestions use `query.styled_text` which includes HTML markup for highlighting matching terms (e.g., `<strong>` tags).

6. **Collection display**: Collections are shown by title only, without images or additional metadata.

7. **Content escaping**: All user-generated content (titles, vendor names) are escaped using the `escape` filter for security.

8. **Tabindex management**: All result links use `tabindex="-1"` to allow the predictive search JavaScript to manage keyboard navigation programmatically.

9. **ARIA labels**: Each list uses `aria-labelledby` to reference the heading (though the IDs are not explicitly set in the headings - this may need adjustment).

10. **View all link**: The "View all results" link appears at the bottom of all results, providing a clear path to the full search page.

11. **No empty states**: The section doesn't render if no results are found (handled by the outer conditional).

12. **CSS class dependencies**: Section relies on CSS classes like `predictive-search__item`, `predictive-search__image`, `predictive-search__item-content`, `predictive-search__item-vendor`, `predictive-search__item-heading`, etc. Ensure these are defined in `component-predictive-search.css`.

13. **JavaScript integration**: The `component-predictive-search.js` custom element handles:
    - Fetching this section via AJAX
    - Managing focus and keyboard navigation
    - Showing/hiding the results container
    - Debouncing search input

14. **Theme settings**: Section respects two theme settings:
    - `settings.predictive_search_show_vendor`: Controls vendor display in product results
    - `settings.predictive_search_show_price`: Controls price display in product results

15. **Product price snippet**: Uses `component-product-price` with `use_variant: true` and `show_badges: false` for consistent pricing display without sale badges.

16. **Icon dependency**: Requires `icon-arrow.svg` in the `assets/` folder for the "View all results" link.

17. **Search terms display**: The "View all results" link displays the actual search terms in quotes for clarity.

18. **No pagination**: Predictive search results are limited (typically 4-5 items per category) and don't include pagination.

