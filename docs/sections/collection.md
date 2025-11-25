# Collection Section (`sections/collection.liquid`)

This **Shopify** section renders a collection page with faceted filtering, sorting, pagination (or infinite scroll), and a responsive product grid. It leverages dynamic CSS, Liquid snippets for reusable components, and a custom Web Component (`<collection-info>`) for asynchronous updates.

---

## Dependencies & Assets

### CSS
- `component-product-price.css`
- `component-product-card.css`
- `component-pagination.css`
- `section-collection.css`
- `component-quick-add.css` *(only when quick add is enabled)*

### JavaScript
- `section-collection.js` – houses `<collection-info>` behavior
- `component-product-card.js`
- `component-filters-price-range.js`
- Optional: `component-quick-add.js`, `component-modal-opener.js`, `component-infinite-scroll.js`

### Snippets & Components
- Filter UIs: `component-filters-sidebar`, `component-filters-drawer`, `component-filters-horizontal`
- Cards & pagination: `component-product-card`, `component-pagination`, `component-quick-add`
- Custom element wrapper: `<collection-info>` defined in `assets/section-collection.js`

## Dynamic Styles

A `<style>` block at the top generates section-specific CSS based on admin settings.  
It controls layout directions, grid columns, padding, and button colors dynamically.  

```liquid
{%- style -%}
.collection-filters-wrapper {
  display: flex;
  {%- if section.settings.enable_filtering
      and section.settings.filter_type == "vertical" -%}
    flex-direction: row;
  {%- else -%}
    flex-direction: column;
  {%- endif -%}
}
.product-grid {
  display: grid;
  grid-template-columns: repeat({{ section.settings.columns_desktop }}, 1fr);
}
/* …additional responsive rules, padding, and button styling… */
{%- endstyle -%}
```
Source: Dynamic styles in `sections/collection.liquid` 

## Markup Structure

The HTML is organized into three main parts:

1. **Collection Hero**  
   Displays the collection title in a styled banner.
   ```liquid
   <div class="collection-hero color-{{ section.settings.color_scheme }}">
     <h1 class="collection-hero__title">{{ collection.title }}</h1>
   </div>
   ```

2. **Filters & Sorting**  
   Wraps filtering and sorting controls. Layout varies by `filter_type`:
   - **Vertical sidebar**:  
     `{% render 'component-filters-sidebar' %}`  
   - **Drawer** & **Horizontal**:  
     `{% render 'component-filters-drawer' %}` or  
     `{% render 'component-filters-horizontal' %}`  
   - **Mobile toggle** hides/shows drawers on small screens.  
   These snippets use Alpine.js for state management. 

3. **Product Grid & Pagination**  
   ```liquid
   <div id="product-grid-{{ section.id }}" class="product-grid" 
        {% if section.settings.enable_infinite_scroll %}data-product-grid{% endif %}>
     {%- if collection.products.size == 0 -%}
       <p>Nothing Here</p>
     {%- else -%}
       {%- for product in collection.products -%}
         {% render 'component-product-card',
             card_product: product,
             show_vendor: section.settings.show_vendor,
             enable_swatches: section.settings.enable_swatches,
             swatch_trigger: section.settings.swatch_trigger,
             swatch_type: section.settings.swatch_type,
             quick_add: section.settings.quick_add,
             section_id: section.id,
             button_text_color: section.settings.button_text_color,
             button_border_color: section.settings.button_border_color %}
       {%- endfor -%}
     {%- endif -%}
   </div>
   ```
   Product cards are rendered via the **Product Card** snippet .  
   - **Infinite scroll** wraps results in `<infinite-scroll>`;  
   - Otherwise uses `{% render 'component-pagination' %}`.

### Active Filters Badge Group

Below sorting, active filters appear as badges. Each badge has a “close” icon that re-renders the section with that filter removed:

```liquid
<div class="filter active-filter-item">
  <span>{{ f.label }}: {{ v.label }}</span>
  <div class="filter-close" data-render-section-url="{{ v.url_to_remove }}">
    {{ 'icon-close.svg' | inline_asset_content }}
  </div>
</div>
```

A **Clear all filters** badge resets all facets.

## JavaScript Behavior

Interaction is handled by a custom element `CollectionInfo` defined in `assets/section-collection.js`. Key responsibilities:

- **Debounced filter changes** (`change` events)  
- **Click handlers** for pagination, sorting, and badge removal  
- **AJAX fetch** of updated section HTML  
- **Dynamic DOM update** of grid, counts, and filters  
- **Loading overlays** during network requests

```js
class CollectionInfo extends HTMLElement {
  constructor() {
    super();
    this.debounceOnChange = debounce(this.onChangeHandler, 800);
    this.addEventListener('change', this.debounceOnChange.bind(this));
    this.addEventListener('click', this.onClickHandler.bind(this));
  }
  // …fetchSection, updateSourceFromDestination, show/hideLoadingOverlay…
}
customElements.define('collection-info', CollectionInfo);
```
Source: `assets/section-collection.js` 


## Settings Schema

At the end of the file a JSON schema defines editor controls. Key settings include:

| **ID**                    | **Type**         | **Default**  | **Purpose**                                |
|---------------------------|------------------|--------------|--------------------------------------------|
| `products_per_page`       | range            | 16           | Items per page                             |
| `columns_desktop`         | range            | 4            | Grid columns on desktop                    |
| `columns_mobile`          | select           | “2”          | Grid columns on mobile                     |
| `color_scheme`            | color_scheme     | “scheme-1”   | Section color palette                      |
| `enable_infinite_scroll`  | checkbox         | true         | Infinite scroll toggle                     |
| `enable_filtering`        | checkbox         | true         | Enable facet filters                       |
| `filter_type`             | select           | “horizontal” | Layout: horizontal, vertical, or drawer     |
| `enable_sorting`          | checkbox         | true         | Show Sort By dropdown                      |
| `quick_add`               | select           | “none”       | Quick Add button mode                      |
| `enable_swatches`         | checkbox         | true         | Show variant swatches                      |
| `swatch_type`             | select           | “image”      | Swatch display type: color or image        |
| `padding_top` / `bottom`  | range (px)       | 36           | Section vertical padding                   |
| `button_text_color`       | color            | `#838383`    | Quick-add button text color                |
| `button_background_color` | color            | `#ffffff`    | Quick-add button background                |
| `button_border_color`     | color            | `#838383`    | Quick-add button border                    |

These settings give merchants fine-grained control over layout, appearance, and interaction.