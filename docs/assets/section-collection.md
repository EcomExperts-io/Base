# CollectionInfo Component 🗂️

The `section-collection.js` file defines a **custom Web Component** `<collection-info>` that powers dynamic filtering, sorting, pagination, and URL updates on Shopify collection pages without full reloads .

## Overview  
The `CollectionInfo` class extends `HTMLElement` to:  
- Listen for **filter changes** and **navigation clicks**.  
- Fetch updated section HTML via Shopify’s Section Rendering API.  
- Update page fragments (product grid, counts, filters).  
- Manage browser history and smooth scrolling.  

## Dependencies  
- **`debounce(fn, wait)`**: Delays handler execution to prevent rapid requests .  
- **`URLSearchParams`, `FormData`, `DOMParser`**: Native APIs for URL and HTML manipulation.  

## Usage  
Include the component script and wrap your collection markup:

```liquid
<collection-info data-section="{{ section.id }}">
  <!-- filters, grid, pagination… -->
</collection-info>
<script src="{{ 'section-collection.js' | asset_url }}" type="module"></script>
```  
This integrates `<collection-info>` into your theme’s **main-collection** section .

---

## Function Summary 📋

| Method                                     | Purpose                                                                          |
|--------------------------------------------|----------------------------------------------------------------------------------|
| `constructor()`                            | Binds event listeners and debounced change handler.                              |
| `onClickHandler(event)`                    | Handles clicks on elements with `data-render-section-url`.                       |
| `onChangeHandler(event)`                   | Captures filter input changes (`data-render-section`) and builds query params.   |
| `fetchSection(searchParams)`               | Fetches new HTML, updates sections, URL, overlays, and scrolls to grid.          |
| `updateSourceFromDestination(html, id)`    | Replaces innerHTML of target element with fetched content.                      |
| `updateFilters(html, className)`           | Synchronizes filter facets—removes stale and updates existing ones.              |
| `showLoadingOverlay()`<br>`hideLoadingOverlay()` | Toggles loading spinner and results count visibility.                           |
| `updateURL(searchParams)`                  | Pushes new query string into browser history.                                   |
| `scrollToProductGrid()`                    | Smooth-scrolls viewport to the product grid top.                                 |
| `get form()`                               | Getter for the component’s `<form>`.                                             |

---

## Detailed API

### constructor()  
Initializes the component by:  
- Calling `super()`.  
- Creating a **debounced** version of `onChangeHandler` (800 ms) via `debounce(fn, wait)` .  
- Attaching:  
  - `change` → debounced handler  
  - `click` → `onClickHandler`  

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

### onClickHandler(event)  
Fires when any click occurs inside `<collection-info>`.  
- **Targets**: Elements matching `[data-render-section-url]`.  
- **Behavior**:  
  1. Prevents default link action.  
  2. Extracts query string from `data-render-section-url`.  
  3. Calls `fetchSection(searchParams)`.

```js
onClickHandler = (event) => {
  if (!event.target.matches('[data-render-section-url]')) return;
  event.preventDefault();
  const query = event.target.dataset.renderSectionUrl
    .split('?')[1];
  const searchParams = new URLSearchParams(query).toString();
  this.fetchSection(searchParams);
};
```

### onChangeHandler(event)  
Handles input changes for filters.  
- **Guard**: Only elements with `data-render-section`.  
- **Flow**:  
  1. Finds nearest `<form>` (or drawer/sidebar).  
  2. Serializes form into `URLSearchParams`.  
  3. Preserves any existing `q` (search) parameter.  
  4. Calls `fetchSection(searchParams)`.

```js
onChangeHandler = (event) => {

  if (!event.target.matches('[data-render-section]')) return;

  const form = event.target.closest('form') || document.querySelector('#filters-form') || document.querySelector('#filters-form-drawer');
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

### fetchSection(searchParams)  
Central method to update page content.  
1. **Show** loading overlay.  
2. **Fetch** HTML from `?section_id={section}&{searchParams}`.  
3. **Parse** response into a `Document`.  
4. **Update**:  
   - Browser URL (`updateURL`)  
   - Grid, counts, filters, sorting elements (`updateSourceFromDestination`, `updateFilters`)  
5. **Hide** overlay and **scroll** to grid.  
6. **Error**: Logs and hides overlay.

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
      // Multiple updates…
      this.hideLoadingOverlay();
      this.scrollToProductGrid();
    })
    .catch((err) => {
      console.error(err);
      this.hideLoadingOverlay();
    });
};
```

### updateSourceFromDestination(html, id)  
Replaces a target fragment’s HTML with fetched content.  
- **Inputs**:  
  - `html`: Parsed Document  
  - `id`: Element ID to update  
- **Action**: If both source and destination exist, copy `innerHTML`.

```js
updateSourceFromDestination = (html, id) => {
  const source = html.getElementById(id);
  const dest = this.querySelector(`#${id}`);
  if (source && dest) dest.innerHTML = source.innerHTML;
};
```

### updateFilters(html, className)  
Keeps filter lists in sync:  
1. **Removes** stale filter facets no longer returned.  
2. **Updates** existing filters’ content.

```js
updateFilters = (html, className) => {
  const fromFetch = html.querySelectorAll(`collection-info .${className}`);
  const fromDom   = document.querySelectorAll(`collection-info .${className}`);
  // Remove missing…
  // Update matched…
};
```

### showLoadingOverlay() & hideLoadingOverlay()  
Toggles visibility of spinners vs. results counts for both main and drawer views:

```js
showLoadingOverlay = () => {
  this.querySelector(`#loading-overlay-${this.dataset.section}`).style.display = 'flex';
  // …toggle spinner/result-count elements
};
hideLoadingOverlay = () => {
  this.querySelector(`#loading-overlay-${this.dataset.section}`).style.display = 'none';
  // …revert visibility
};
```

### updateURL(searchParams)  
Pushes a new history entry with updated query string:

```js
updateURL(searchParams) {
  history.pushState({}, '', `${window.location.pathname}?${searchParams}`);
}
```

### scrollToProductGrid()  
Smoothly scrolls viewport to the top of the product grid, accounting for header height:

```js
scrollToProductGrid = () => {
  const grid = this.querySelector(`#product-grid-${this.dataset.section}`);
  const header = document.querySelector('#main-header');
  const offset = (header.offsetHeight + 10) || 80;
  if (grid) {
    const top = grid.getBoundingClientRect().top + window.pageYOffset - offset;
    window.scrollTo({ top, behavior: 'smooth' });
  }
};
```

### Getter: `form`  
Returns the component’s `<form>` element:

```js
get form() {
  return this.querySelector('collection-info form');
}
```

---

**Key Takeaways**  
- **Debounced Filtering**: Prevents UI thrash on rapid input.  
- **Partial Updates**: Only specific DOM regions reload, improving performance.  
- **History & Scroll**: Maintains shareable URLs and user-friendly scrolling.  

This component encapsulates the collection page’s dynamic behavior into a reusable, maintainable Web Component.