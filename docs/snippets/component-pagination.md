# component-pagination Snippet

`snippets/component-pagination.liquid` renders a set of pagination links for paginated results. It must be used within `{% paginate %}` tags and displays previous/next navigation buttons along with page numbers. The component integrates with the Section Rendering API for AJAX pagination updates and supports anchor links for scroll-to functionality.

---

## What It Does

- Renders pagination controls with previous/next buttons and page numbers.
- Displays clickable page numbers for direct navigation.
- Shows current page with special styling and `aria-current="page"`.
- Displays ellipsis (`...`) for non-clickable page separators.
- Integrates with Section Rendering API via `data-render-section-url` for AJAX updates.
- Supports anchor links for scroll-to functionality on page change.
- Provides accessible labels for screen readers.

---

## Parameters

| Parameter | Type   | Default | Description                                                      |
|-----------|--------|---------|------------------------------------------------------------------|
| `paginate`| object | **required** | Paginate object from `{% paginate %}` tags.                     |
| `anchor`  | string | optional | Anchor hash (e.g., `#product-grid`) to scroll to on page change. |

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | `component-pagination.css` (external stylesheet) |
| JavaScript | Section Rendering API integration (via `data-render-section-url` attributes) |
| Icons | `icon-caret.svg` (inline via `inline_asset_content` for previous/next arrows) |
| Data | Requires `paginate` object from `{% paginate %}` tags with `parts`, `previous`, `next`, `current_page` |

- Section Rendering API handles AJAX pagination updates.
- External CSS file provides pagination styling.
- Icons used for previous/next navigation arrows.

---

## Dynamic Styles

The snippet does not include inline styles. All styling is handled by the external `component-pagination.css` file.

---

## Markup Structure

```liquid
<div class="pagination pagination-wrapper">
  <ul class="pagination__list">
    {%- if paginate.parts.size > 0 -%}
      <!-- Previous button -->
      <!-- Page numbers -->
      <!-- Next button -->
    {%- endif -%}
  </ul>
</div>
```

- **Semantic structure**: Uses `<ul>` and `<li>` for list structure.
- **Conditional rendering**: Only renders if `paginate.parts.size > 0`.

### Previous Button

```liquid
{%- if paginate.previous -%}
  <li>
    <a
      href="{{ paginate.previous.url }}{{ anchor }}"
      class="pagination__item pagination__item--previous pagination__item-arrow"
      data-render-section-url="{{ paginate.previous.url }}"
      aria-label="{{ 'general.pagination.previous' | t }}"
    >
      <span class="svg-wrapper">{{ 'icon-caret.svg' | inline_asset_content }}</span>
    </a>
  </li>
{%- endif -%}
```

- **Conditional display**: Only shows if previous page exists (`paginate.previous`).
- **Section Rendering API**: Uses `data-render-section-url` for AJAX updates.
- **Anchor support**: Appends `anchor` parameter to URL for scroll-to functionality.
- **Accessibility**: Includes `aria-label` for screen readers.
- **Icon display**: Shows caret icon (rotated for previous direction).

### Page Numbers

```liquid
{%- for part in paginate.parts -%}
  {%- if part.is_link -%}
    <li>
      <a
        href="{{ part.url }}{{ anchor }}"
        class="pagination__item"
        data-render-section-url="{{ part.url }}"
        aria-label="{{ 'general.pagination.page' | t: number: part.title }}"
      >
        {{- part.title -}}
      </a>
    </li>
  {%- else -%}
    {%- if part.title == paginate.current_page -%}
      <li>
        <a
          class="pagination__item pagination__item--current"
          role="link"
          aria-disabled="true"
          aria-current="page"
          aria-label="{{ 'general.pagination.page' | t: number: part.title }}"
        >
          {{- part.title -}}
        </a>
      </li>
    {%- else -%}
      <li>
        <span class="pagination__item">{{ part.title }}</span>
      </li>
    {%- endif -%}
  {%- endif -%}
{%- endfor -%}
```

- **Three types of page parts**:
  1. **Clickable links** (`part.is_link`): Regular page numbers that are clickable.
  2. **Current page** (`part.title == paginate.current_page`): Current page with special styling and `aria-current="page"`.
  3. **Ellipsis** (neither link nor current): Non-clickable separators (typically `...`).

- **Section Rendering API**: Clickable links use `data-render-section-url` for AJAX updates.
- **Anchor support**: All links append `anchor` parameter for scroll-to functionality.
- **Accessibility**: All links include `aria-label` with page number.

### Next Button

```liquid
{%- if paginate.next -%}
  <li>
    <a
      href="{{ paginate.next.url }}{{ anchor }}"
      class="pagination__item pagination__item--next pagination__item-arrow"
      data-render-section-url="{{ paginate.next.url }}"
      aria-label="{{ 'general.pagination.next' | t }}"
    >
      <span class="svg-wrapper"> {{ 'icon-caret.svg' | inline_asset_content }}</span>
    </a>
  </li>
{%- endif -%}
```

- **Conditional display**: Only shows if next page exists (`paginate.next`).
- **Section Rendering API**: Uses `data-render-section-url` for AJAX updates.
- **Anchor support**: Appends `anchor` parameter to URL for scroll-to functionality.
- **Accessibility**: Includes `aria-label` for screen readers.
- **Icon display**: Shows caret icon (normal direction for next).

---

## Behavior

- **Pagination navigation**: Clicking page numbers or previous/next buttons navigates to that page.
- **AJAX updates**: When Section Rendering API is enabled, pagination updates content without full page reload.
- **Anchor scrolling**: If `anchor` parameter provided, page scrolls to anchor element after navigation.
- **Current page indication**: Current page is visually distinct and marked with `aria-current="page"`.
- **Ellipsis display**: Non-clickable page separators (ellipsis) displayed as plain text.

---

## Usage Example

Basic usage:

```liquid
{% paginate collection.products by 12 %}
  <!-- Product grid -->
  {% render 'component-pagination', paginate: paginate %}
{% endpaginate %}
```

With anchor for scroll-to:

```liquid
{% paginate search.results by 20 %}
  <!-- Search results -->
  {% render 'component-pagination', paginate: paginate, anchor: '#search-results' %}
{% endpaginate %}
```

With conditional rendering (only show if multiple pages):

```liquid
{% paginate blog.articles by 6 %}
  <!-- Article grid -->
  {%- if paginate.pages > 1 -%}
    {% render 'component-pagination', paginate: paginate %}
  {%- endif -%}
{% endpaginate %}
```

Typically used in:
- Collection pages (`sections/collection.liquid`)
- Search pages (`sections/search.liquid`)
- Blog pages (`sections/blog.liquid`)
- Article pages (`sections/article.liquid`)

---

## Implementation Notes

1. **Paginate tag requirement**: Must be used within `{% paginate %}` tags. The `paginate` object is only available within the paginate block.

2. **Section Rendering API integration**: All pagination links include `data-render-section-url` attribute for AJAX updates. This allows pagination to update content without full page reload when integrated with collection/search components.

3. **Anchor parameter**: The optional `anchor` parameter appends a hash anchor to pagination URLs. This is useful for scrolling to a specific element (e.g., product grid) after page change.

4. **Paginate object structure**: The `paginate` object contains:
    - `paginate.parts`: Array of page parts (links, current page, ellipsis)
    - `paginate.previous`: Previous page object (or null)
    - `paginate.next`: Next page object (or null)
    - `paginate.current_page`: Current page number
    - `paginate.pages`: Total number of pages

5. **Page part types**: Each `part` in `paginate.parts` can be:
    - **Link** (`part.is_link == true`): Clickable page number
    - **Current page** (`part.title == paginate.current_page`): Current page (not clickable)
    - **Ellipsis** (neither): Non-clickable separator (typically `...`)

6. **Icon dependency**: Requires `icon-caret.svg` in the `assets/` folder for previous/next navigation arrows.

7. **CSS class dependencies**: Snippet relies on CSS classes:
    - `.pagination`
    - `.pagination-wrapper`
    - `.pagination__list`
    - `.pagination__item`
    - `.pagination__item--previous`
    - `.pagination__item--next`
    - `.pagination__item--current`
    - `.pagination__item-arrow`
    - `.svg-wrapper`

8. **Translation keys**: Uses translation keys from `locales/en.default.json`:
    - `general.pagination.previous`
    - `general.pagination.next`
    - `general.pagination.page` (with `number` variable)

9. **Accessibility features**:
    - `aria-label` on all navigation links
    - `aria-current="page"` on current page
    - `aria-disabled="true"` on current page link
    - Semantic HTML structure (`<ul>`, `<li>`)

10. **Current page styling**: Current page uses `pagination__item--current` class and is not clickable (has `aria-disabled="true"`).

11. **Ellipsis handling**: Ellipsis (non-clickable separators) are rendered as `<span>` elements, not links.

12. **Previous/next icons**: Previous and next buttons use caret icons. CSS should rotate previous icon 180° for proper direction.

13. **Conditional rendering**: Previous and next buttons only render when those pages exist (`paginate.previous` and `paginate.next`).

14. **URL structure**: Pagination URLs are generated by Shopify's `paginate` object and include query parameters for page number.

15. **Anchor appending**: Anchor parameter is appended to all pagination URLs using string concatenation: `\{\{ paginate.previous.url \}\}\{\{ anchor \}\}`.

16. **No JavaScript file**: Snippet doesn't require a separate JavaScript file - Section Rendering API integration handled by collection/search components.

17. **External CSS**: All styling handled by external `component-pagination.css` file, not inline styles.

18. **List structure**: Uses semantic `<ul>` and `<li>` elements for proper list structure.

19. **Empty state**: Only renders if `paginate.parts.size > 0` to avoid empty pagination on single-page results.

20. **Translation interpolation**: Page number translation uses variable interpolation: `'general.pagination.page' | t: number: part.title`.

21. **Icon wrapper**: Icons wrapped in `<span class="svg-wrapper">` for styling purposes.

22. **Role attribute**: Current page link uses `role="link"` even though it's not clickable, for semantic consistency.

23. **URL escaping**: Pagination URLs are generated by Shopify and don't require manual escaping.

24. **Multiple pagination instances**: Can be used multiple times on the same page if multiple paginate blocks exist.

25. **Responsive design**: Pagination styling should be responsive (handled by CSS file).

26. **Loading states**: Section Rendering API integration may show loading states during pagination updates (handled by collection/search components).

27. **Browser history**: When using Section Rendering API, browser history may be updated via JavaScript (handled by collection/search components).

28. **Focus management**: After pagination update, focus should be managed appropriately (handled by collection/search components or can be added via anchor).

29. **Keyboard navigation**: Pagination links are keyboard accessible via standard link navigation.

30. **Screen reader support**: All pagination links have descriptive `aria-label` attributes for screen reader users.

31. **Current page semantics**: Current page is marked with both `aria-current="page"` and `aria-disabled="true"` to indicate it's the current page and not clickable.

32. **Ellipsis display**: Ellipsis are typically displayed as `...` or similar separator text to indicate skipped pages.

33. **Page number display**: Page numbers are displayed as text (`part.title`) which is typically the page number (1, 2, 3, etc.).

34. **URL parameters**: Pagination URLs include Shopify's pagination query parameters (e.g., `?page=2`).

35. **Section Rendering API format**: The `data-render-section-url` attribute contains the full URL for the Section Rendering API request.

36. **Anchor hash**: Anchor parameter should include the `#` symbol (e.g., `#product-grid`) for proper anchor linking.

37. **No conditional logic for single page**: Snippet doesn't check if pagination is needed - that should be done in the parent template (e.g., `{% if paginate.pages > 1 %}`).

38. **Icon rotation**: Previous button icon should be rotated 180° via CSS to point left instead of right.

39. **Spacing**: Icon has space before it in next button (`<span class="svg-wrapper"> {{ 'icon-caret.svg' | inline_asset_content }}</span>`) but not in previous button - this may be intentional or a minor inconsistency.

40. **Translation file structure**: Translation keys should be structured in `locales/en.default.json`:
    ```json
    {
      "general": {
        "pagination": {
          "previous": "Previous page",
          "next": "Next page",
          "page": "Page {{ number }}"
        }
      }
    }
    ```

