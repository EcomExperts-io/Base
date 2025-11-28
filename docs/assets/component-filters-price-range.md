# PriceRange Web Component

`assets/component-filters-price-range.js` exports the `PriceRange` class, which extends `HTMLElement` and is registered as the custom element `<price-range>`. This component controls and synchronizes collection price range filters in Shopify themes.

**Source:** [`assets/component-filters-price-range.js`](../../assets/component-filters-price-range.js)

## Overview

The `PriceRange` component:
- Reads min/max values from URL filter parameters (`filter.v.price.gte` and `filter.v.price.lte`)
- Synchronizes dual range inputs, visual slider track, and price display labels
- Prevents invalid states (min > max) by only updating when values are valid
- Updates the UI in real-time as users interact with the range inputs

## Class Structure

```javascript
export class PriceRange extends HTMLElement {
  constructor()
  connectedCallback()
  init()
  bindEvents()
  updateUI(min, max)
}
```

## API Reference

| Method | Description |
|--------|-------------|
| `constructor()` | Calls `super()` to initialize the HTMLElement base class |
| `connectedCallback()` | Lifecycle hook that queries DOM elements, extracts currency symbol, and initializes the component |
| `init()` | Reads URL parameters, determines initial min/max values, updates UI, and binds event listeners |
| `bindEvents()` | Attaches `input` event listeners to both range inputs for real-time updates |
| `updateUI(min, max)` | Updates price display labels, slider track position, and input values |

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
    this.rangeSlider = this.querySelector('.slider-container .price-slider');
    this.minPriceText = this.querySelector('.min_price');
    this.maxPriceText = this.querySelector('.max_price');
    this.currencySymbol = this.querySelector('.price-range-main').getAttribute('currency-symbol');
    this.init();
  }
```

**DOM References:**
- `this.rangeInputs`: NodeList of both range inputs (min at index 0, max at index 1)
- `this.rangeSlider`: The visual slider track element (`.slider-container .price-slider`)
- `this.minPriceText`: Element displaying the minimum price (`.min_price`)
- `this.maxPriceText`: Element displaying the maximum price (`.max_price`)
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
    this.rangeInputs.forEach((input) => {
      input.addEventListener('input', () => {
        const newMin = parseInt(this.rangeInputs[0].value, 10);
        const newMax = parseInt(this.rangeInputs[1].value, 10);

        if (newMin <= newMax) {
          this.updateUI(newMin, newMax);
        }
      });
    });
  }
```

**Behavior:**
- Attaches `input` event listeners to both range inputs
- On each input change, reads the current values from both inputs (always reads from `rangeInputs[0]` and `rangeInputs[1]`, not the event target)
- Only calls `updateUI()` if `newMin <= newMax` to prevent invalid states
- If min > max, the UI remains unchanged until a valid state is achieved

### updateUI(min, max)

Updates the displayed labels with currency formatting.

Moves the slider track using CSS left & right.

Reflects updated values back into the two range inputs.

```javascript
updateUI(min, max) {
  this.minPriceText.textContent = `${this.currencySymbol}${min}.00`;
  this.maxPriceText.textContent = `${this.currencySymbol}${max}.00`;
  this.rangeSlider.style.left = `${(min / this.rangeInputs[0].max) * 100}%`;
  this.rangeSlider.style.right = `${100 - (max / this.rangeInputs[1].max) * 100}%`;
  this.rangeInputs[0].value = min;
  this.rangeInputs[1].value = max;
}
```

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

  <div class="slider-container">
    <div class="price-slider"></div>
  </div>

  <div class="price-display">
    <span class="min_price"></span>
    <span class="max_price"></span>
  </div>
</price-range>

<script src="{{ 'component-filters-price-range.js' | asset_url }}" type="module"></script>
```

## Implementation Notes

- Include both range inputs inside `.range-input`.
- Provide `.price-slider` to visualize the selected interval.
- Include `.min_price` and `.max_price` elements for UI text.
- Pass the correct `currency-symbol` attribute from Liquid.
- Load the module on any template using price filtering.
