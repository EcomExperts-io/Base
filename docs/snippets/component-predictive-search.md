# component-predictive-search Snippet

`snippets/component-predictive-search.liquid` renders a predictive search form with real-time search suggestions. It uses the `<predictive-search>` custom element for JavaScript functionality, Alpine.js for form state management, and integrates with Shopify's predictive search API. The component displays search results dynamically as the user types and supports both header and page contexts.

---

## What It Does

- Renders a search form with input, clear button, and submit button.
- Uses Alpine.js for search term state management and input focus handling.
- Integrates with `<predictive-search>` custom element for API requests.
- Displays loading state during search requests.
- Shows clear button when search term has content.
- Supports header context with overlay for mobile/desktop search modals.
- Provides accessible search form with proper ARIA attributes.
- Populates results container dynamically via JavaScript.

---

## Parameters

| Parameter | Type   | Default | Description                                                      |
|----------|--------|---------|------------------------------------------------------------------|
| `context`| string | optional | If `'header'`, renders overlay for search modal. Otherwise, standard search form. |

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | `component-predictive-search.css` (external stylesheet, loaded conditionally in theme layout) |
| JavaScript | `component-predictive-search.js` (defines `<predictive-search>` custom element, loaded conditionally in theme layout), Alpine.js (required for form state) |
| Icons | `icon-search.svg`, `icon-close.svg`, `icon-loader.svg` (inline via `inline_asset_content`) |
| Data | Requires `search.terms` object, `routes.search_url` for form action |
| Sections | `sections/predictive-results.liquid` (rendered dynamically via JavaScript) |

- Custom element handles predictive search API requests and result rendering.
- Alpine.js powers form state (`x-model`, `x-show`, `@click`, `@focus`).
- External CSS and JavaScript loaded conditionally when `settings.predictive_search_enabled` is true.

---

## Dynamic Styles

The snippet does not include inline styles. All styling is handled by the external `component-predictive-search.css` file. However, the header overlay uses inline style binding for opacity:

```liquid
:style="{ opacity: searchOpen ? 1 : 0 }"
```

- **Dynamic opacity**: Overlay opacity controlled by Alpine.js `searchOpen` state.

---

## Markup Structure

```liquid
<predictive-search x-ref="predictiveSearch">
  <form action="{{ routes.search_url }}" method="get" role="search">
    <!-- Search input and buttons -->
  </form>
  <div id="predictive-search-wrapper">
    <!-- Loading indicator -->
    <!-- Results container -->
  </div>
  {% if context == 'header' %}
    <!-- Overlay -->
  {% endif %}
</predictive-search>
```

- **Custom element**: Wrapped in `<predictive-search>` custom element for JavaScript functionality.
- **Alpine.js reference**: Uses `x-ref="predictiveSearch"` for method access from Alpine.js.

### Search Form

```liquid
<form action="{{ routes.search_url }}" method="get" role="search">
  <input
    type="search"
    name="q"
    value="{{ search.terms | escape }}"
    aria-owns="predictive-search-results"
    aria-controls="predictive-search-results"
    aria-haspopup="listbox"
    aria-autocomplete="list"
    placeholder="Search"
    x-model="searchTerm"
    x-ref="searchInput"
    @focus="$event.target.select()"
  >
  <input name="options[prefix]" type="hidden" value="last">
  <!-- Buttons -->
</form>
```

- **Form action**: Submits to `routes.search_url` for standard search fallback.
- **Search input**: Uses `type="search"` for native search input features.
- **Alpine.js binding**: `x-model="searchTerm"` binds input value to Alpine.js state.
- **Focus handling**: `@focus="$event.target.select()"` selects all text on focus.
- **ARIA attributes**: Comprehensive ARIA attributes for accessibility:
    - `aria-owns`: Links to results container
    - `aria-controls`: Indicates controlled element
    - `aria-haspopup`: Indicates popup listbox
    - `aria-autocomplete`: Indicates autocomplete behavior
- **Prefix option**: Hidden input sets `options[prefix]` to `'last'` for search behavior.

### Clear Button

```liquid
<button
  type="reset"
  class="reset__button"
  aria-label="Clear search term"
  @click="searchTerm = ''; $refs.predictiveSearch.clearSearch($event)"
  x-show="searchTerm.length > 0"
  x-transition
  x-cloak
>
  {{- 'icon-close.svg' | inline_asset_content -}}
</button>
```

- **Conditional display**: Only shows when `searchTerm.length > 0` via `x-show`.
- **Clear functionality**: Clears Alpine.js state and calls custom element method.
- **Smooth transition**: Uses `x-transition` for show/hide animation.
- **Accessibility**: Includes `aria-label` for screen readers.

### Submit Button

```liquid
<button aria-label="Search">
  {{- 'icon-search.svg' | inline_asset_content -}}
</button>
```

- **Icon-only button**: Uses search icon with `aria-label` for accessibility.
- **Form submission**: Submits form to search results page.

### Results Container

```liquid
<div id="predictive-search-wrapper" tabindex="-1">
  <div class="predictive-search__loading hidden">
    {{ 'icon-loader.svg' | inline_asset_content }}
  </div>
  <div id="predictive-search"></div>
</div>
```

- **Loading indicator**: Shows spinner during search requests (toggled by JavaScript).
- **Results target**: `#predictive-search` is where results are dynamically inserted.
- **Tabindex**: Uses `tabindex="-1"` for programmatic focus management.

### Header Overlay (Conditional)

```liquid
{% if context == 'header' %}
  <div
    id="predictive-search-overlay"
    x-on:click="searchOpen = false"
    x-transition
    x-cloak
    x-show="searchOpen"
    :style="{ opacity: searchOpen ? 1 : 0 }"
    class="predictive-search-overlay"
  ></div>
{% endif %}
```

- **Conditional rendering**: Only renders when `context == 'header'`.
- **Click to close**: Clicking overlay closes search (`searchOpen = false`).
- **Dynamic opacity**: Opacity controlled by `searchOpen` state.
- **Smooth transition**: Uses `x-transition` for fade animation.

---

## Behavior

- **Real-time search**: As user types, predictive search API is called (debounced) to fetch suggestions.
- **Loading state**: Loading indicator shows during API requests.
- **Results display**: Search results dynamically inserted into `#predictive-search` container.
- **Clear functionality**: Clear button resets search term and clears results.
- **Form submission**: Submitting form navigates to full search results page.
- **Focus handling**: Selecting input selects all text for easy replacement.
- **Overlay interaction**: In header context, clicking overlay closes search modal.

---

## Usage Example

Basic usage:

```liquid
{% render 'component-predictive-search' %}
```

In header context:

```liquid
{% render 'component-predictive-search', context: 'header' %}
```

Typically used in:
- Header (`sections/header.liquid`) when `settings.predictive_search_enabled` is true
- Search pages (`sections/search.liquid`) when predictive search is enabled

---

## Implementation Notes

1. **Custom element requirement**: Snippet requires `component-predictive-search.js` to be loaded, which defines the `<predictive-search>` custom element.

2. **Alpine.js requirement**: Snippet requires Alpine.js to be loaded for form state management.

3. **Conditional asset loading**: CSS and JavaScript files are loaded conditionally in `layout/theme.liquid` when `settings.predictive_search_enabled` is true.

4. **Predictive search API**: The custom element makes requests to Shopify's predictive search API endpoint and renders `sections/predictive-results.liquid` dynamically.

5. **Debounced input**: The custom element debounces input events (700ms) to avoid excessive API requests.

6. **Search term state**: Alpine.js `searchTerm` variable is bound to input via `x-model="searchTerm"`.

7. **Clear method**: Custom element provides `clearSearch()` method called by clear button.

8. **Icon dependencies**: Requires the following icons in `assets/`:
    - `icon-search.svg` (search icon)
    - `icon-close.svg` (clear button icon)
    - `icon-loader.svg` (loading spinner)

9. **CSS class dependencies**: Snippet relies on CSS classes:
    - `.reset__button`
    - `.predictive-search__loading`
    - `.hidden`
    - `.predictive-search-overlay`
    - `#predictive-search-wrapper`
    - `#predictive-search`

10. **Alpine.js directives**:
    - `x-ref="predictiveSearch"`: References custom element for method access
    - `x-model="searchTerm"`: Binds input value to Alpine.js state
    - `x-ref="searchInput"`: References input for focus management
    - `@focus="$event.target.select()"`: Selects all text on focus
    - `@click="searchTerm = ''; $refs.predictiveSearch.clearSearch($event)"`: Clears search
    - `x-show="searchTerm.length > 0"`: Shows clear button when term exists
    - `x-transition`: Provides smooth show/hide animations
    - `x-cloak`: Prevents flash of unstyled content
    - `x-show="searchOpen"`: Shows overlay when search is open (header context)
    - `:style="{ opacity: searchOpen ? 1 : 0 }"`: Controls overlay opacity
    - `x-on:click="searchOpen = false"`: Closes search on overlay click

11. **Search terms escaping**: Search terms are escaped using `escape` filter for security.

12. **Form action**: Form submits to `routes.search_url` for standard search fallback when JavaScript is disabled.

13. **Prefix option**: Hidden input `options[prefix]` set to `'last'` affects search behavior (searches from end of words).

14. **Accessibility features**:
    - `role="search"` on form
    - `aria-owns` and `aria-controls` linking input to results
    - `aria-haspopup="listbox"` indicating popup
    - `aria-autocomplete="list"` indicating autocomplete
    - `aria-label` on buttons
    - Proper semantic HTML

15. **Results container**: Results are dynamically inserted into `#predictive-search` div by the custom element.

16. **Loading state**: Loading indicator toggled via `hidden` class by custom element JavaScript.

17. **Header context**: When `context == 'header'`, overlay is rendered for search modal functionality.

18. **Overlay state**: Overlay visibility controlled by Alpine.js `searchOpen` variable (must be defined in parent scope).

19. **Focus management**: Input text selected on focus for easy replacement.

20. **Clear functionality**: Clear button both resets Alpine.js state and calls custom element method for complete cleanup.

21. **No translation keys**: Placeholder text and button labels are hardcoded in English. Consider adding translation support.

22. **Search URL**: Uses `routes.search_url` for form action, which is Shopify's standard search route.

23. **Input type**: Uses `type="search"` which provides native search input features (clear button in some browsers).

24. **Tabindex on wrapper**: Results wrapper uses `tabindex="-1"` for programmatic focus management.

25. **Custom element methods**: Custom element provides methods accessible via `$refs.predictiveSearch`:
    - `clearSearch(event)`: Clears search term and results

26. **API integration**: Custom element handles:
    - Debouncing input events
    - Making API requests to predictive search endpoint
    - Rendering results section dynamically
    - Managing loading states
    - Handling errors

27. **Results section**: Results are rendered from `sections/predictive-results.liquid` which displays:
    - Search suggestions (queries and collections)
    - Articles and pages
    - Products with pricing

28. **No inline styles**: All styling handled by external CSS file (except overlay opacity binding).

29. **Overlay click handling**: Overlay click closes search, providing intuitive UX for modal search.

30. **Smooth transitions**: Clear button and overlay use `x-transition` for smooth animations.

31. **Icon-only buttons**: Both clear and submit buttons are icon-only, requiring `aria-label` for accessibility.

32. **Form method**: Form uses `method="get"` for standard search submission.

33. **Input name**: Search input uses `name="q"` which is Shopify's standard search query parameter.

34. **Value binding**: Input value bound to both Liquid (`value="\{\{ search.terms | escape \}\}"`) and Alpine.js (`x-model="searchTerm"`).

35. **Focus select**: `@focus="$event.target.select()"` selects all text when input is focused, making it easy to replace.

36. **Hidden class**: Loading indicator uses `hidden` class which should be toggled by JavaScript to show/hide.

37. **Results ID**: Results container uses `id="predictive-search"` which must match the ID expected by the custom element.

38. **Wrapper ID**: Results wrapper uses `id="predictive-search-wrapper"` for styling and JavaScript targeting.

39. **Overlay ID**: Overlay uses `id="predictive-search-overlay"` for styling and JavaScript targeting.

40. **Context parameter**: `context` parameter allows different behavior/styling for header vs page contexts.

41. **No conditional rendering for empty state**: Snippet doesn't handle empty search state - that's handled by the results section.

42. **Debounce timing**: Custom element debounces input by 700ms to balance responsiveness and API efficiency.

43. **Abort controller**: Custom element uses `AbortController` to cancel in-flight requests when new input is entered.

44. **Click outside handling**: Custom element handles clicking outside to close results (not shown in snippet but handled by JavaScript).

45. **Keyboard navigation**: Results should support keyboard navigation (handled by results section and custom element).

46. **Escape key handling**: Escape key should close results (handled by custom element JavaScript).

47. **Focus trap**: Results container may implement focus trap for keyboard accessibility (handled by custom element).

48. **Loading state management**: Loading indicator visibility managed by custom element's `toggleLoading()` method.

49. **Results rendering**: Custom element fetches and renders `sections/predictive-results.liquid` section dynamically.

50. **Search term persistence**: Search term persists in input value and Alpine.js state for consistent behavior.

