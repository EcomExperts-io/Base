# SellingPlansWidget Web Component

`assets/component-selling-plans.js` exports the `SellingPlansWidget` class, which extends `HTMLElement` and is registered as the custom element `<selling-plans-widget>`. This component manages subscription selling plans, synchronizing plan selection with variant changes, updating prices, and handling purchase option inputs.

**Source:** [`assets/component-selling-plans.js`](../../assets/component-selling-plans.js)

## Overview

The `SellingPlansWidget` component:
- Manages subscription selling plan selection for products
- Synchronizes selling plan visibility with variant changes
- Updates product prices based on selected selling plan
- Appends selling plan inputs to add-to-cart forms
- Uses PerformanceObserver to detect variant fetch completion
- Handles both regular and sale prices for subscription plans

## Class Structure

```javascript
export class SellingPlansWidget extends HTMLElement {
  constructor()
  connectedCallback()
  // Getters
  rootElement
  variantIdInput
  priceElement
  comparedAtPrice
  visibleSellingPlanForm
  isVariantAvailable
  sellingPlanInput
  addToCartForms
  regularPriceElement
  salePriceElement
  salePriceValue
  regularPriceValue
  sellingPlanAllocationPrice
  selectedPurchaseOptionPrice
  selectedPurchaseOptionComparedAtPrice
  price
  sellingPlanInputs
  sellingPlanInputValue
  selectedPurchaseOption
  // Methods
  appendSellingPlanInputs()
  showSellingPlanForm(sellingPlanFormForSelectedVariant)
  hideSellingPlanForms(sellingPlanFormsForUnselectedVariants)
  handleSellingPlanFormVisibility()
  handleVariantChange()
  listenToVariantChange()
  listenToAddToCartForms()
  updatePrice()
  hideSalePrice()
  hideRegularPrice()
  showRegularPrice()
  showSalePrice()
  updateSellingPlanInputsValues()
  handleRadioButtonChange(selectedPurchaseOption)
  listenToSellingPlanFormRadioButtonChange()
  enablePerformanceObserver()
}
```

## API Reference

| Method / Property | Description |
|------------------|-------------|
| `constructor()` | Initializes the component |
| `connectedCallback()` | Sets up selling plan inputs, listeners, and price updates |
| `rootElement` | Getter for the closest `product-info` parent element |
| `variantIdInput` | Getter for the variant ID input in add-to-cart forms |
| `appendSellingPlanInputs()` | Clones and appends selling plan input to all add-to-cart forms |
| `handleVariantChange()` | Updates selling plan visibility and inputs when variant changes |
| `listenToVariantChange()` | Sets up MutationObserver and form change listeners |
| `updatePrice()` | Updates displayed price based on selected selling plan |
| `enablePerformanceObserver()` | Monitors fetch requests to update price after variant changes |

## Method Details

### connectedCallback()

```javascript
  connectedCallback() {
    this.enablePerformanceObserver();
    this.appendSellingPlanInputs();
    this.updateSellingPlanInputsValues();
    this.listenToVariantChange();
    this.listenToSellingPlanFormRadioButtonChange();
    this.updatePrice();
  }
```

**Initialization Steps:**
1. Enables PerformanceObserver to detect variant fetch completion
2. Appends selling plan inputs to all add-to-cart forms
3. Updates selling plan input values
4. Listens for variant changes
5. Listens for selling plan radio button changes
6. Updates initial price display

### appendSellingPlanInputs()

```javascript
  appendSellingPlanInputs() {
    this.addToCartForms.forEach((addToCartForm) => {
      addToCartForm.appendChild(this.sellingPlanInput.cloneNode());
    });
  }
```

**Behavior:**
- Clones the selling plan input (`.selected-selling-plan-id`) and appends to each add-to-cart form
- Ensures selling plan ID is submitted when adding to cart

### handleVariantChange()

```javascript
  handleVariantChange() {
    this.handleSellingPlanFormVisibility();
    this.updateSellingPlanInputsValues();
    this.listenToSellingPlanFormRadioButtonChange();
  }
```

**Behavior:**
- Shows/hides selling plan forms based on selected variant
- Updates selling plan input values
- Re-binds radio button listeners for the new visible form

### handleSellingPlanFormVisibility()

```javascript
  handleSellingPlanFormVisibility() {
    const sellingPlanFormForSelectedVariant = this.rootElement.querySelector(`div[data-variant-id="${this.variantIdInput.value}"]`);
    const sellingPlanFormsForUnselectedVariants = this.rootElement.querySelectorAll(
      `.selling_plan_theme_integration:not([data-variant-id="${this.variantIdInput.value}"])`,
    );
    this.showSellingPlanForm(sellingPlanFormForSelectedVariant);
    this.hideSellingPlanForms(sellingPlanFormsForUnselectedVariants);
  }
```

**Behavior:**
- Finds selling plan form matching current variant ID
- Hides all other variant's selling plan forms
- Only shows the form for the selected variant

### updatePrice()

```javascript
  updatePrice() {
    if (!this.selectedPurchaseOptionComparedAtPrice || this.selectedPurchaseOptionComparedAtPrice === this.selectedPurchaseOptionPrice) {
      this.showRegularPrice();
      this.hideSalePrice();
      this.priceElement.classList.remove('price--on-sale');
    } else {
      this.showSalePrice();
      this.hideRegularPrice();
      this.priceElement.classList.add('price--on-sale');
    }
  }
```

**Behavior:**
- Compares regular price with compared-at price
- Shows sale price if discount exists, otherwise shows regular price
- Updates CSS classes for styling

### enablePerformanceObserver()

```javascript
  enablePerformanceObserver() {
    const performanceObserver = new PerformanceObserver((list) => {
      list.getEntries().forEach((entry) => {
        if (entry.initiatorType !== 'fetch') return;

        const url = new URL(entry.name);
        /*
          When a buyer selects a product variant, a fetch request is initiated.
          Upon completion of this fetch request, we update the price to reflect the correct value.
        */
        if (url.search.includes('variant') || url.search.includes('variants')) {
          this.updatePrice();
        }
      });
    });

    performanceObserver.observe({ entryTypes: ['resource'] });
  }
```

**Behavior:**
- Monitors network requests for variant-related fetches
- Updates price after variant fetch completes
- Ensures price reflects correct selling plan pricing

## Custom Element Definition

```javascript
if (!customElements.get('selling-plans-widget')) {
  customElements.define('selling-plans-widget', SellingPlansWidget);
}
```

Ensures the element is registered only once across bundles or hot reload sessions.

## Integration with Shopify Liquid

```liquid
<selling-plans-widget>
  <input type="hidden" class="selected-selling-plan-id" name="selling_plan" value="">
  
  {% for variant in product.variants %}
    <div class="selling_plan_theme_integration" data-variant-id="{{ variant.id }}">
      {% for selling_plan_group in product.selling_plan_groups %}
        {% for selling_plan in selling_plan_group.selling_plans %}
          <label>
            <input 
              type="radio" 
              name="selling_plan_{{ variant.id }}"
              data-selling-plan-id="{{ selling_plan.id }}"
              data-selling-plan-group-id="{{ selling_plan_group.id }}"
              data-variant-price="{{ selling_plan.price | money }}"
              data-variant-compare-at-price="{{ selling_plan.compare_at_price | money }}"
            >
            {{ selling_plan.name }}
          </label>
        {% endfor %}
      {% endfor %}
    </div>
  {% endfor %}
</selling-plans-widget>

<script src="{{ 'component-selling-plans.js' | asset_url }}" type="module"></script>
```

## Implementation Notes

- The component must be nested inside a `<product-info>` element
- Selling plan forms must have `data-variant-id` attributes matching variant IDs
- Radio inputs must have `data-selling-plan-id`, `data-selling-plan-group-id`, `data-variant-price`, and `data-variant-compare-at-price` attributes
- The hidden input `.selected-selling-plan-id` is cloned to all add-to-cart forms
- Forms for unselected variants are hidden using `.selling_plan_theme_integration--hidden` class
- The component uses PerformanceObserver to detect when variant fetches complete
- Price elements must have classes `.price`, `.price__regular`, `.price__sale`, `.price-item--sale`, and `.price-item--regular`
- The component automatically handles both one-time purchase and subscription pricing

