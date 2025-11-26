# component-filters-price-range Snippet

`snippets/component-filters-price-range.liquid` renders a dual-range price filter component for collection and search pages. It provides both slider controls and number inputs for selecting minimum and maximum price ranges, with synchronized updates between inputs and visual slider track. The component uses the `<price-range>` custom element for interactive behavior.

---

## What It Does

- Renders a dual-range price filter with slider and number input controls.
- Synchronizes min/max range inputs with visual slider track.
- Displays currency symbol and formatted price inputs.
- Converts prices from cents (Shopify format) to dollars (display format).
- Integrates with Section Rendering API for AJAX filter updates.
- Provides real-time visual feedback as users adjust price range.

---

## Parameters

| Parameter     | Type   | Default | Description                                                      |
|---------------|--------|---------|------------------------------------------------------------------|
| `filter`      | object | **required** | Filter object with `type: 'price_range'` and price range data.  |
| `id_prefix`   | string | optional | Prefix for input IDs (typically `'Filter-'`).                   |
| `filter_type` | string | optional | Filter type identifier (documented but may not be used).        |

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | Inline `{% style %}` block with comprehensive price range styling |
| JavaScript | `component-filters-price-range.js` (defines `<price-range>` custom element) |
| Custom Elements | `<price-range>` (handles slider synchronization and UI updates) |
| Data | Requires `filter` object with `range_max`, `min_value`, `max_value`, and `cart.currency.symbol` |

- Custom element handles all interactive behavior and synchronization.
- Inline styles provide all price range-specific CSS (no external CSS file required).
- Section Rendering API handles filter updates via `data-render-section` attributes.

---

## Dynamic Styles

The snippet includes extensive inline styles for price range slider, inputs, and layout:

```liquid
{%- style -%}
  .slider-container {
    height: 4px;
    position: relative;
    background: #e4e4e4;
    border-radius: 5px;
  }

  .slider-container .price-slider {
    height: 100%;
    left: 0%;
    right: 0%;
    position: absolute;
    border-radius: 5px;
    background: #000;
    display: block;
  }

  .range-input input {
    position: absolute;
    width: 100%;
    height: 4px;
    background: none;
    top: 0px;
    left: 0px;
    pointer-events: none;
    cursor: pointer;
    -webkit-appearance: none;
    z-index: 2;
  }

  /* ... additional styling for inputs, labels, mobile ... */
{%- endstyle -%}
```

- **Slider track**: Visual representation of selected price range.
- **Dual range inputs**: Two overlapping range inputs for min/max selection.
- **Number inputs**: Text inputs for precise price entry.
- **Mobile responsive**: Adjustments for smaller screens at 768px breakpoint.

---

## Markup Structure

```liquid
<price-range>
  <div class="price-range-main" currency-symbol="{{ cart.currency.symbol }}">
    <div class="price-range-subcontainer">
      <div class="range-input">
        <!-- Min and max range inputs -->
      </div>
      <div class="price-input-container">
        <div class="slider-container">
          <div class="price-slider"></div>
        </div>
        <div class="price-input">
          <!-- Min and max number inputs -->
        </div>
      </div>
    </div>
  </div>
</price-range>
```

- **Custom element**: Uses `<price-range>` wrapper for JavaScript functionality.
- **Currency symbol**: Passed via `currency-symbol` attribute for display.
- **Dual controls**: Both slider and number inputs for flexible interaction.

### Range Inputs (Sliders)

```liquid
<div class="range-input">
  <input
    type="range"
    class="min-range"
    min="0"
    max="{{ filter.range_max | divided_by: 100 }}"
    {%- if filter.min_value.value -%}
      value="{{ filter.min_value.value | divided_by: 100 }}"
    {%- else -%}
      value="0"
    {%- endif -%}
    step="1"
    name="{{ filter.min_value.param_name }}"
    data-render-section
  >
  <input
    type="range"
    class="max-range"
    min="0"
    max="{{ filter.range_max | divided_by: 100 }}"
    {%- if filter.max_value.value -%}
      value="{{ filter.max_value.value | divided_by: 100 }}"
    {%- else -%}
      value="{{ filter.range_max | divided_by: 100 }}"
    {%- endif -%}
    step="1"
    name="{{ filter.max_value.param_name }}"
    data-render-section
  >
</div>
```

- **Price conversion**: Divides by 100 to convert from cents (Shopify) to dollars (display).
- **Min range**: Defaults to 0 if no min value set.
- **Max range**: Defaults to `range_max` if no max value set.
- **Section Rendering API**: `data-render-section` triggers AJAX updates.
- **Overlapping inputs**: Both inputs positioned absolutely for dual-range functionality.

### Visual Slider Track

```liquid
<div class="slider-container">
  <div class="price-slider"></div>
</div>
```

- **Visual indicator**: Shows selected price range as filled portion of track.
- **Dynamic positioning**: JavaScript updates `left` and `right` CSS properties based on min/max values.

### Number Inputs

```liquid
<div class="price-input">
  <div class="price-field">
    <span>From</span>
    <label>
      <span class="currency-symbol">{{ cart.currency.symbol }}</span>
      <input
        type="number"
        class="min-number"
        min="0"
        max="{{ filter.range_max | divided_by: 100 }}"
        {%- if filter.min_value.value -%}
          value="{{ filter.min_value.value | divided_by: 100 }}"
        {%- else -%}
          value="0"
        {%- endif -%}
        step="1"
        data-render-section
      >
    </label>
  </div>
  <div class="price-field">
    <span>To</span>
    <label>
      <span class="currency-symbol">{{ cart.currency.symbol }}</span>
      <input
        type="number"
        class="max-number"
        min="0"
        max="{{ filter.range_max | divided_by: 100 }}"
        {%- if filter.max_value.value -%}
          value="{{ filter.max_value.value | divided_by: 100 }}"
        {%- else -%}
          value="{{ filter.range_max | divided_by: 100 }}"
        {%- endif -%}
        step="1"
        data-render-section
      >
    </label>
  </div>
</div>
```

- **Currency display**: Shows currency symbol before number input.
- **Synchronized values**: Values match range inputs (converted from cents).
- **Section Rendering API**: `data-render-section` triggers AJAX updates.
- **Labels**: "From" and "To" labels for clarity.

---

## Behavior

- **Dual-range selection**: Users can set both minimum and maximum price.
- **Synchronized inputs**: Range sliders and number inputs stay in sync.
- **Visual feedback**: Slider track updates to show selected range.
- **Price conversion**: Automatically converts between cents (Shopify) and dollars (display).
- **Real-time updates**: Changes trigger Section Rendering API requests.
- **Validation**: JavaScript prevents invalid states (min > max).
- **Currency display**: Shows appropriate currency symbol from cart.

---

## Usage Example

```liquid
{% if f.type == 'price_range' %}
  {% render 'component-filters-price-range',
    filter: f,
    id_prefix: 'Filter-',
    filter_type: 'horizontal'
  %}
{% endif %}
```

Typically used within:
- `component-filters-horizontal.liquid`
- `component-filters-drawer.liquid`
- `component-filters-sidebar.liquid`

---

## Implementation Notes

1. **Custom element requirement**: Requires `component-filters-price-range.js` to be loaded which defines the `<price-range>` custom element.

2. **Price conversion**: Shopify stores prices in cents, but the component displays in dollars:
   - `filter.range_max | divided_by: 100` converts max price
   - `filter.min_value.value | divided_by: 100` converts min value
   - `filter.max_value.value | divided_by: 100` converts max value

3. **Dual range inputs**: Two overlapping `<input type="range">` elements create the dual-range slider:
   - Min range: `.min-range` class
   - Max range: `.max-range` class
   - Both positioned absolutely in `.range-input` container

4. **Visual slider track**: The `.price-slider` element visually represents the selected range:
   - JavaScript updates `left` and `right` CSS properties
   - `left` = (min / maxRange) * 100%
   - `right` = 100 - (max / maxRange) * 100%

5. **Section Rendering API**: All inputs use `data-render-section` attribute (without value) to trigger AJAX updates when values change.

6. **Currency symbol**: Retrieved from `cart.currency.symbol` and passed via `currency-symbol` attribute to custom element.

7. **Input synchronization**: The `<price-range>` custom element synchronizes:
   - Range inputs ↔ Number inputs
   - Range inputs ↔ Visual slider track
   - Number inputs ↔ Visual slider track

8. **Default values**:
   - Min defaults to 0 if `filter.min_value.value` is not set
   - Max defaults to `filter.range_max` if `filter.max_value.value` is not set

9. **Input names**: Range inputs use Shopify filter parameter names:
   - Min: `filter.min_value.param_name` (typically `filter.v.price.gte`)
   - Max: `filter.max_value.param_name` (typically `filter.v.price.lte`)

10. **Number input styling**: Number inputs are styled to look like labels with currency symbol, creating a cohesive design.

11. **Mobile responsive**: Styles adjust at 768px breakpoint:
    - Price input flex direction changes
    - Field margins adjusted
    - Layout optimized for smaller screens

12. **WebKit styling**: Custom styles for range input thumbs in WebKit browsers:
    - Removes default appearance
    - Custom thumb size (10px × 10px)
    - Black circular thumb

13. **Spin button removal**: Number inputs have spin buttons removed via CSS for cleaner appearance.

14. **Z-index layering**: Range inputs use `z-index: 2` to appear above slider track for interaction.

15. **Pointer events**: Range inputs use `pointer-events: none` on container, `pointer-events: auto` on thumbs for proper interaction.

16. **Step value**: All inputs use `step="1"` for whole dollar increments.

17. **CSS class dependencies**: Snippet relies on CSS classes:
    - `.price-range-main`
    - `.price-range-subcontainer`
    - `.range-input`
    - `.min-range`
    - `.max-range`
    - `.price-input-container`
    - `.slider-container`
    - `.price-slider`
    - `.price-input`
    - `.price-field`
    - `.min-number`
    - `.max-number`
    - `.currency-symbol`

18. **JavaScript integration**: The `<price-range>` custom element:
    - Reads URL parameters on init
    - Binds event listeners to all inputs
    - Updates UI in real-time
    - Prevents invalid states (min > max)
    - Handles synchronization between inputs

19. **URL parameter format**: JavaScript reads filter values from URL:
    - `filter.v.price.gte` for minimum
    - `filter.v.price.lte` for maximum

20. **No translation keys**: Price range labels ("From", "To") are hardcoded in English. Consider using translation filters if internationalization is needed.

21. **Filter object structure**: Requires filter object with:
    - `type: 'price_range'`
    - `range_max`: Maximum price in cents
    - `min_value.value`: Current min value in cents (optional)
    - `max_value.value`: Current max value in cents (optional)
    - `min_value.param_name`: Parameter name for min (e.g., `filter.v.price.gte`)
    - `max_value.param_name`: Parameter name for max (e.g., `filter.v.price.lte`)

22. **Cart currency**: Requires `cart.currency.symbol` to be available for currency display.

23. **Accessibility considerations**:
    - Proper label associations
    - Number inputs for keyboard entry
    - Range inputs for mouse/touch interaction
    - Semantic HTML structure

24. **Performance**: Inline styles prevent additional HTTP request but increase HTML size. Consider extracting to CSS file if used multiple times.

25. **Validation**: JavaScript in custom element validates that min ≤ max and adjusts values if needed.

26. **Real-time updates**: All input changes trigger immediate UI updates and Section Rendering API requests.

27. **Visual feedback**: Slider track provides immediate visual feedback as users adjust range.

28. **Input constraints**: All inputs respect min/max constraints based on `filter.range_max`.

29. **Currency symbol display**: Currency symbol is displayed before number inputs for clarity.

30. **Mobile optimization**: Layout adjusts for mobile with flex direction changes and spacing adjustments.

