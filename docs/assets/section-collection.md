# CollectionInfo Web Component 🗂️

`assets/section-collection.js` defines `<collection-info>`, a custom element that powers dynamic filtering, sorting, pagination, and URL updates on collection pages without a full reload.

**Source:** [`assets/section-collection.js`](../../assets/section-collection.js)

---

## What It Does

- Debounces filter changes so rapid input doesn’t spam the network.
- Listens for clicks on pagination, sorting, and filter badges via `data-render-section-url`.
- Fetches fresh HTML from Shopify’s Section Rendering API and swaps specific DOM fragments.
- Keeps filters, counts, and drawers synchronized across desktop and mobile layouts.
- Toggles loading overlays and scrolls shoppers back to the product grid after updates.

---

## API Overview

| Method / Property              | Purpose                                                                 |
|--------------------------------|-------------------------------------------------------------------------|
| `constructor()`                | Binds debounced change + click handlers.                                |
| `onClickHandler(event)`        | Intercepts links with `data-render-section-url` for AJAX pagination.     |
| `onChangeHandler(event)`       | Serializes filter forms into query params and triggers fetches.         |
| `fetchSection(searchParams)`   | Calls the Section Rendering API, updates DOM, URL, and scroll position. |
| `updateSourceFromDestination()`| Copies HTML fragments (grid, counts, etc.) from the fetched document.   |
| `updateFilters()`              | Syncs facet markup between main view and drawers.                       |
| `showLoadingOverlay()`         | Displays section-level loading overlays and hides result counts.        |
| `hideLoadingOverlay()`         | Reverts the overlay state once the response is applied.                 |
| `updateURL(searchParams)`      | Pushes the latest query string into browser history.                    |
| `scrollToProductGrid()`        | Smooth-scrolls the viewport to the updated product grid.                |
| `get form()`                   | Convenience getter for the component’s inner `<form>`.                  |

---

## Detailed Method Documentation

### constructor()

```js
constructor() {
  super();
  this.debounceOnChange = debounce(
    (event) => this.onChangeHandler(event),
    800
  );
  this.addEventListener('change', this.debounceOnChange.bind(this));
  this.addEventListener('click', this.onClickHandler.bind(this));
}
```

- Creates an `800ms` debounced wrapper around `onChangeHandler`.
- Registers `change` and `click` listeners on the component root.

### onClickHandler(event)

```js
onClickHandler = (event) => {
  if (!event.target.matches('[data-render-section-url]')) return;
  event.preventDefault();
  const query = event.target.dataset.renderSectionUrl.split('?')[1];
  const searchParams = new URLSearchParams(query).toString();
  this.fetchSection(searchParams);
};
```

- Captures clicks on pagination links, “clear filter” badges, and other controls that expose the next URL via `data-render-section-url`.

### onChangeHandler(event)

```js
onChangeHandler = (event) => {
  if (!event.target.matches('[data-render-section]')) return;

  const form =
    event.target.closest('form') ||
    document.querySelector('#filters-form') ||
    document.querySelector('#filters-form-drawer');
  const formData = new FormData(form);
  let searchParams = new URLSearchParams(formData).toString();
  const existing = new URLSearchParams(window.location.search);
  const qValue = existing.get('q');

  if (qValue) {
    searchParams = `q=${encodeURIComponent(qValue)}&${searchParams}`;
  }

  this.fetchSection(searchParams);
};
```

- Serializes whichever filter form is available (inline, drawer, or fallback) and preserves the `q` search parameter.

### fetchSection(searchParams)

```js
fetchSection = (searchParams) => {
  this.showLoadingOverlay();
  fetch(
    `${window.location.pathname}?section_id=${this.dataset.section}&${searchParams}`
  )
    .then((res) => res.text())
    .then((text) => {
      const html = new DOMParser().parseFromString(text, 'text/html');
      this.updateURL(searchParams);
      this.updateSourceFromDestination(html, `product-grid-${this.dataset.section}`);
      this.updateSourceFromDestination(html, `active-facets-${this.dataset.section}`);
      this.updateFilters(html, 'facets-toggle');
      this.hideLoadingOverlay();
      this.scrollToProductGrid();
    })
    .catch((err) => {
      console.error(err);
      this.hideLoadingOverlay();
    });
};
```

- Calls the Section Rendering API using the current section ID.
- Parses the HTML with `DOMParser` so individual fragments can be queried.
- Updates the URL, DOM fragments, loaders, and scroll position.

### updateSourceFromDestination(html, id)

```js
updateSourceFromDestination = (html, id) => {
  const source = html.getElementById(id);
  const dest = this.querySelector(`#${id}`);
  if (source && dest) dest.innerHTML = source.innerHTML;
};
```

- Replaces the contents of matching IDs (product grid, result counts, toolbar blocks, etc.).

### updateFilters(html, className)

```js
updateFilters = (html, className) => {
  const fromFetch = html.querySelectorAll(`collection-info .${className}`);
  const fromDom = document.querySelectorAll(`collection-info .${className}`);

  fromDom.forEach((element) => {
    const id = element.getAttribute('id');
    const updated = Array.from(fromFetch).find((item) => item.getAttribute('id') === id);
    if (!updated) {
      element.remove();
      return;
    }
    element.innerHTML = updated.innerHTML;
  });
};
```

- Keeps sidebar, drawer, and sticky filter elements in sync by mirroring markup from the fetched response.

### showLoadingOverlay() / hideLoadingOverlay()

```js
showLoadingOverlay = () => {
  this.querySelector(`#loading-overlay-${this.dataset.section}`).style.display = 'flex';
  // Hide result count, show spinner, etc.
};

hideLoadingOverlay = () => {
  this.querySelector(`#loading-overlay-${this.dataset.section}`).style.display = 'none';
  // Restore result count visibility
};
```

- Toggles the loading overlay that sits on top of the grid and drawers.

### updateURL(searchParams)

```js
updateURL(searchParams) {
  history.pushState({}, '', `${window.location.pathname}?${searchParams}`);
}
```

- Keeps the browser URL shareable by mirroring the current filter/sort state.

### scrollToProductGrid()

```js
scrollToProductGrid = () => {
  const grid = this.querySelector(`#product-grid-${this.dataset.section}`);
  const header = document.querySelector('#main-header');
  const offset = (header?.offsetHeight || 70) + 10;
  if (grid) {
    const top = grid.getBoundingClientRect().top + window.pageYOffset - offset;
    window.scrollTo({ top, behavior: 'smooth' });
  }
};
```

- Smooth-scrolls users back to the grid after filters reload so context is preserved.

### Getter: `form`

```js
get form() {
  return this.querySelector('form');
}
```

- Convenience accessor used by other scripts to reference the active filter form.

---

## Custom Element Definition

```js
if (!customElements.get('collection-info')) {
  customElements.define('collection-info', CollectionInfo);
}
```

The guard prevents duplicate registrations when Shopify hot reloads assets in the theme editor.

---

## Integration with Shopify Liquid

Wrap your collection layout with the custom element and include the script:

```liquid
<collection-info data-section="{{ section.id }}">
  <!-- Filters, sorting, badges, grid, pagination -->
</collection-info>

{{ 'section-collection.js' | asset_url | script_tag }}
```

Each interactive control should expose either `data-render-section` (inputs) or `data-render-section-url` (links and buttons) so the component can react.

---

## Usage Checklist

1. Render IDs like `product-grid-\{\{ section.id \}\}` and `active-facets-\{\{ section.id \}\}` so `updateSourceFromDestination` can target them.
2. Mirror filter controls inside drawers and inline toolbars; `updateFilters` keeps them synchronized.
3. Keep `loading-overlay-\{\{ section.id \}\}` in the markup for the spinner state.
4. Preserve the `<collection-info>` wrapper whenever filters or grids are moved into new sections/snippets.

