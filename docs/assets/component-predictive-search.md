# PredictiveSearch Web Component

`assets/component-predictive-search.js` exports the `PredictiveSearch` class, which extends `HTMLElement` and is registered as the custom element `<predictive-search>`. This component provides real-time search suggestions as users type, fetching results from Shopify's predictive search API.

**Source:** [`assets/component-predictive-search.js`](../../assets/component-predictive-search.js)

## Overview

The `PredictiveSearch` component:
- Provides real-time search suggestions as users type
- Debounces input to reduce API calls (700ms delay)
- Fetches results from Shopify's predictive search endpoint
- Shows loading state during fetch
- Handles click-outside to close results
- Supports clearing search input
- Uses AbortController to cancel in-flight requests

## Class Structure

```javascript
export class PredictiveSearch extends HTMLElement {
  constructor()
  connectedCallback()
  disconnectedCallback()
  onChange(e)
  getSearchResults(searchTerm)
  updateResults(resultsMarkup)
  open()
  close()
  clearSearch(e)
  handleClickOutside(event)
  toggleLoading(show)
}
```

## API Reference

| Method | Description |
|--------|-------------|
| `constructor()` | Initializes the component, sets up input listeners and click-outside handler |
| `connectedCallback()` | Lifecycle hook (no additional setup needed) |
| `disconnectedCallback()` | Lifecycle hook that removes click-outside listener |
| `onChange(e)` | Handles input changes, debounced with 700ms delay |
| `getSearchResults(searchTerm)` | Fetches search results from Shopify API |
| `updateResults(resultsMarkup)` | Updates the results container with fetched markup |
| `open()` | Shows the results container |
| `close()` | Hides the results container |
| `clearSearch(e)` | Clears the search input and closes results |
| `handleClickOutside(event)` | Closes results when clicking outside component |
| `toggleLoading(show)` | Shows/hides loading spinner |

## Method Details

### constructor()

```javascript
export class PredictiveSearch extends HTMLElement {
  constructor() {
    super();

    this.input = this.querySelector('input[type="search"]');
    this.predictiveSearchResults = this.querySelector('#predictive-search');
    this.resetButton = this.querySelector('.reset__button');
    this.searchTerm = this.input.value.trim();
    this.isOpen = false;
    this.abortController = new AbortController();
    this.input.addEventListener('input', debounce((e) => this.onChange(e), 700));
    this.input.addEventListener('focus', (e) => this.onChange(e));
    this.handleClickOutside = this.handleClickOutside.bind(this);
    document.addEventListener('click', this.handleClickOutside);
  }
}
```

**Initialization:**
- Queries required DOM elements (input, results container, reset button)
- Sets up debounced input listener (700ms delay)
- Sets up focus listener for immediate search on focus
- Creates AbortController for request cancellation
- Binds click-outside handler

**Note:** Imports `debounce` function from `theme.js`.

### onChange(e)

```javascript
  onChange(e) {
    console.log(e);
    const newSearchTerm = this.input.value.trim();
    this.searchTerm = newSearchTerm;

    if (!this.searchTerm.length) {
      const resultsElement = this.querySelector('#predictive-search-results');
      if (resultsElement) resultsElement.remove();
      this.close();
      return;
    }

    if (!this.isOpen) {
      this.toggleLoading(true);
    }
    this.getSearchResults(this.searchTerm);
  }
```

**Behavior:**
1. Gets trimmed search term from input
2. If empty, removes results and closes
3. If not open, shows loading spinner
4. Fetches search results

### getSearchResults(searchTerm)

```javascript
  getSearchResults(searchTerm) {
    fetch(`/search/suggest?q=${encodeURIComponent(searchTerm)}&section_id=predictive-results`, {
      signal: this.abortController.signal,
    })
      .then(response => {
        if (!response.ok) {
          this.close();
          return Promise.reject(new Error(`Failed to fetch: ${response.status}`));
        }
        return response.text();
      })
      .then(text => {
        const parser = new DOMParser();
        const doc = parser.parseFromString(text, 'text/html');
        const resultsMarkup = doc.querySelector('#shopify-section-predictive-results')?.innerHTML || '';
        this.updateResults(resultsMarkup);
      })
      .catch(error => {
        console.error('Error fetching search results:', error);
        this.close();
      });
  }
```

**Behavior:**
- Fetches from Shopify's predictive search endpoint
- Uses AbortController to cancel previous requests
- Parses HTML response and extracts results section
- Updates results or closes on error

### updateResults(resultsMarkup)

```javascript
  updateResults(resultsMarkup) {
    this.predictiveSearchResults.innerHTML = resultsMarkup;
    this.open();
  }
```

**Behavior:**
- Sets results container HTML
- Opens results container

### handleClickOutside(event)

```javascript
  handleClickOutside(event) {
    // Check if the click is outside the predictive search component
    if (this.isOpen && !this.contains(event.target)) {
      this.close();
    }
  }
```

**Behavior:**
- Closes results if click is outside component
- Only acts when results are open

## Custom Element Definition

```javascript
if (!customElements.get('predictive-search')) {
  customElements.define('predictive-search', PredictiveSearch);
}
```

Ensures the element is registered only once across bundles or hot reload sessions.

## Integration with Shopify Liquid

```liquid
<predictive-search>
  <form action="{{ routes.search_url }}" method="get">
    <input 
      type="search" 
      name="q" 
      placeholder="Search..."
      autocomplete="off"
    >
    <button type="button" class="reset__button">Clear</button>
  </form>

  <div id="predictive-search" style="display: none;">
    <div class="predictive-search__loading hidden">Loading...</div>
    <div id="predictive-search-results">
      <!-- Results will be loaded here -->
    </div>
  </div>
</predictive-search>

<script src="{{ 'component-predictive-search.js' | asset_url }}" type="module"></script>
```

## Shopify Section Setup

Create a section file `sections/predictive-results.liquid`:

```liquid
<div id="shopify-section-predictive-results">
  {% if predictive_search.performed %}
    <!-- Products -->
    {% if predictive_search.resources.products.size > 0 %}
      <div class="predictive-search__products">
        {% for product in predictive_search.resources.products %}
          {% render 'component-product-card', product: product %}
        {% endfor %}
      </div>
    {% endif %}

    <!-- Collections, Pages, Articles can be added similarly -->
  {% endif %}
</div>
```

## Implementation Notes

- The component requires `theme.js` with `debounce` function exported
- Search input must have `type="search"` attribute
- Results container must have ID `#predictive-search`
- Loading spinner should have class `.predictive-search__loading` and be hidden by default
- Reset button should have class `.reset__button`
- The component uses Shopify's `/search/suggest` endpoint with `section_id` parameter
- Results section must have ID `#shopify-section-predictive-results`
- Input is debounced with 700ms delay to reduce API calls
- Focus event triggers immediate search
- AbortController cancels previous requests when new input is entered
- Click-outside detection automatically closes results
- The component handles empty search terms by closing results
- Error handling closes results and logs to console

