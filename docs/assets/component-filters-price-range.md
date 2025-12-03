# PriceRange Web Component

`assets/component-filters-price-range.js` exports the `PriceRange` class, which extends `HTMLElement` and is registered as the custom element `<price-range>`. This component controls and synchronizes collection price range filters in Shopify themes.

**Source:** [`assets/component-filters-price-range.js`](../../assets/component-filters-price-range.js)

## Overview

The `PriceRange` component:
- Reads min/max values from URL filter parameters (`filter.v.price.gte` and `filter.v.price.lte`)
- Synchronizes dual range inputs, number inputs, and visual slider track
- Prevents invalid states (min > max) by constraining values appropriately
- Updates the UI in real-time as users interact with either range inputs or number inputs

## Class Structure

```javascript
export class PriceRange extends HTMLElement {
  constructor()
  connectedCallback()
  init()
  bindEvents()
  handleInputChange(source, event)
  updateUI(min, max)
}
```

## API Reference

| Method | Description |
|--------|-------------|
| `constructor()` | Calls `super()` to initialize the HTMLElement base class |
| `connectedCallback()` | Lifecycle hook that queries DOM elements, extracts currency symbol, and initializes the component |
| `init()` | Reads URL parameters, determines initial min/max values, updates UI, and binds event listeners |
| `bindEvents()` | Attaches `input` event listeners to range inputs and `change` event listeners to number inputs |
| `handleInputChange(source, event)` | Handles input changes from either range or number inputs, validates and constrains values, then updates UI |
| `updateUI(min, max)` | Updates range inputs, number inputs, and slider track position |

## Method Details

### constructor()

```javascript
export class PriceRange extends HTMLElement {
  constructor() {
    super();
  }
}
```

Initializes the custom element by calling `super()` to establish HTMLElement behavior. No additional setup is performed here.

### connectedCallback()

```javascript
  connectedCallback() {
    this.rangeInputs = this.querySelectorAll('.range-input input');
    this.numberInputs = this.querySelectorAll('.price-input input[type="number"]');
    this.rangeSlider = this.querySelector('.slider-container .price-slider');
    this.currencySymbol = this.querySelector('.price-range-main').getAttribute('currency-symbol');
    this.init();
  }
```

**DOM References:**
- `this.rangeInputs`: NodeList of both range inputs (min at index 0, max at index 1)
- `this.numberInputs`: NodeList of both number inputs (min at index 0, max at index 1)
- `this.rangeSlider`: The visual slider track element (`.slider-container .price-slider`)
- `this.currencySymbol`: Currency symbol retrieved from the `currency-symbol` attribute on the element itself (requires `.price-range-main` class)

**Note:** The currency symbol is retrieved from the element itself using `.querySelector('.price-range-main')`, so the `<price-range>` element must have the `price-range-main` class.

### init()

```javascript
  init() {
    const urlParams = new URLSearchParams(window.location.search);
    const urlMin = urlParams.get('filter.v.price.gte');
    const urlMax = urlParams.get('filter.v.price.lte');

    const minVal = urlMin ? parseInt(urlMin, 10) : parseInt(this.rangeInputs[0].value, 10);
    const maxVal = urlMax ? parseInt(urlMax, 10) : parseInt(this.rangeInputs[1].value, 10);

    this.updateUI(minVal, maxVal);
    this.bindEvents();
  }
```

**URL Parameters:**
- `filter.v.price.gte`: Minimum price value (greater than or equal)
- `filter.v.price.lte`: Maximum price value (less than or equal)

**Behavior:**
1. Parses URL search parameters to extract current filter values
2. Falls back to the default `value` attributes of the range inputs if URL params are missing
3. Converts all values to integers using `parseInt(value, 10)`
4. Updates the UI with the determined values
5. Binds event listeners for user interactions

### bindEvents()

```javascript
  bindEvents() {
    this.rangeInputs.forEach(() => {
      this.rangeInputs[0].addEventListener('input', (event) => this.handleInputChange('range', event));
      this.rangeInputs[1].addEventListener('input', (event) => this.handleInputChange('range', event));
    });

    this.numberInputs[0].addEventListener('change', (event) => this.handleInputChange('number', event));
    this.numberInputs[1].addEventListener('change', (event) => this.handleInputChange('number', event));
  }
```

**Behavior:**
- Attaches `input` event listeners to both range inputs (min and max)
- Attaches `change` event listeners to both number inputs (min and max)
- All events are delegated to the `handleInputChange()` method with a source identifier ('range' or 'number')

### handleInputChange(source, event)

Handles input changes from either range inputs or number inputs, validates values, and updates the UI.

```javascript
handleInputChange(source, event) {
  const minRangeVal = parseInt(this.rangeInputs[0].value, 10);
  const maxRangeVal = parseInt(this.rangeInputs[1].value, 10);
  const minNumberVal = parseInt(this.numberInputs[0].value, 10);
  const maxNumberVal = parseInt(this.numberInputs[1].value, 10);

  const maxAllowed = parseInt(this.rangeInputs[1].max, 10);
  const minAllowed = parseInt(this.rangeInputs[0].min, 10);

  let min = source === 'range' ? minRangeVal : minNumberVal;
  let max = source === 'range' ? maxRangeVal : maxNumberVal;

  if (isNaN(min) || isNaN(max)) return;

  min = Math.max(minAllowed, Math.min(min, maxAllowed));
  max = Math.max(minAllowed, Math.min(max, maxAllowed));

  const target = event?.target;

  if (target === this.rangeInputs[0] || target === this.numberInputs[0]) {
    min = Math.min(min, max - 1);
  } else if (target === this.rangeInputs[1] || target === this.numberInputs[1]) {
    max = Math.max(max, min + 1);
  }

  this.updateUI(min, max);
}
```

**Parameters:**
- `source`: String indicating the input source - either `'range'` or `'number'`
- `event`: The event object containing the target element

**Behavior:**
1. Reads current values from both range and number inputs
2. Determines which values to use based on the `source` parameter
3. Validates that values are not NaN
4. Constrains values to the allowed min/max range
5. Ensures min < max by adjusting the changed value (min is capped at max - 1, max is floored at min + 1)
6. Calls `updateUI()` with the validated values

### updateUI(min, max)

Updates range inputs, number inputs, and slider track position.

```javascript
updateUI(min, max) {
  const maxRange = parseInt(this.rangeInputs[1].max, 10);

  min = Math.max(0, Math.min(min, maxRange));
  max = Math.max(0, Math.min(max, maxRange));

  console.log(min, max);

  this.rangeInputs[0].value = min;
  this.rangeInputs[1].value = max;
  this.numberInputs[0].value = min;
  this.numberInputs[1].value = max;

  this.rangeSlider.style.left = `${(min / maxRange) * 100}%`;
  this.rangeSlider.style.right = `${100 - (max / maxRange) * 100}%`;
}
```

**Behavior:**
1. Constrains min and max values to valid range (0 to maxRange)
2. Updates both range inputs with the new values
3. Updates both number inputs with the new values
4. Updates the slider track position using CSS `left` and `right` properties
5. Uses the maximum range value for calculating slider percentages

## Custom Element Definition

```javascript
if (!customElements.get('price-range')) {
  customElements.define('price-range', PriceRange);
}
```

Ensures the element is registered only once across bundles or hot reload sessions.

## Integration with Shopify Liquid

```liquid
<price-range class="price-range-main" currency-symbol="{{ cart.currency.symbol }}">
  <div class="range-input">
    <input type="range" min="0" max="1000" value="0">
    <input type="range" min="0" max="1000" value="1000">
  </div>

  <div class="price-input">
    <input type="number" min="0" max="1000" value="0">
    <input type="number" min="0" max="1000" value="1000">
  </div>

  <div class="slider-container">
    <div class="price-slider"></div>
  </div>
</price-range>

<script src="{{ 'component-filters-price-range.js' | asset_url }}" type="module"></script>
```

## Implementation Notes

- Include both range inputs inside `.range-input`.
- Include both number inputs inside `.price-input` with `type="number"`.
- Provide `.price-slider` to visualize the selected interval.
- Pass the correct `currency-symbol` attribute from Liquid.
- Load the module on any template using price filtering.
- The component synchronizes range inputs, number inputs, and the slider track automatically.
