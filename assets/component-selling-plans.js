export class SellingPlansWidget extends HTMLElement {
  constructor() {
    super();
  }

  connectedCallback() {
    this.enablePerformanceObserver();
    this.appendSellingPlanInputs();
    this.updateSellingPlanInputsValues();
    this.listenToVariantChange();
    this.listenToSellingPlanFormRadioButtonChange();
    this.updatePrice();
  }

  get rootElement() {
    return this.closest('product-info');
  }

  /*
    We are careful to target the correct form, as there are instances when we encounter an installment form that we specifically aim to avoid interacting with.
  */
  get variantIdInput() {
    const forms = this.addToCartForms;
    return (
      forms[1]?.querySelector(`input[name="id"]`) ||
      forms[1]?.querySelector(`select[name="id"]`) ||
      forms[0]?.querySelector(`input[name="id"]`) ||
      forms[0]?.querySelector(`select[name="id"]`)
    );
  }

  get priceElement() {
    return this.rootElement.querySelector('.price');
  }

  get comparedAtPrice() {
    return this.rootElement.querySelector('.price__sale');
  }

  get visibleSellingPlanForm() {
    return this.querySelector(`div[data-variant-id^="${this.variantIdInput?.value}"]`);
  }

  get isVariantAvailable() {
    return this.selectedPurchaseOption?.getAttributeNames().includes('disabled');
  }

  get sellingPlanInput() {
    return this.rootElement.querySelector('.selected-selling-plan-id');
  }

  get addToCartForms() {
    return this.rootElement.querySelectorAll('[action*="/cart/add"]');
  }

  /*
    To enable the addition of a selling plan to a cart, it's necessary to include an input with the name "selling_plan", which will carry the selling ID as its value. When a buyer clicks on 'add to cart', the appropriate selling plan ID is added to their cart.
  */
  appendSellingPlanInputs() {
    this.addToCartForms.forEach((addToCartForm) => {
      addToCartForm.appendChild(this.sellingPlanInput.cloneNode());
    });
  }

  showSellingPlanForm(sellingPlanFormForSelectedVariant) {
    sellingPlanFormForSelectedVariant?.classList?.remove('selling_plan_theme_integration--hidden');
  }

  hideSellingPlanForms(sellingPlanFormsForUnselectedVariants) {
    sellingPlanFormsForUnselectedVariants.forEach((element) => {
      element.classList.add('selling_plan_theme_integration--hidden');
    });
  }

  /*
    Each product variant comes with a selling plan selection box that the buyer can interact with.
    When a buyer chooses a different variant, we ensure that only the relevant selling plan selection box is displayed.
    This guarantees that only the selling plan associated with the selected variant is shown.
  */
  handleSellingPlanFormVisibility() {
    const sellingPlanFormForSelectedVariant = this.rootElement.querySelector(`div[data-variant-id="${this.variantIdInput.value}"]`);
    const sellingPlanFormsForUnselectedVariants = this.rootElement.querySelectorAll(
      `.selling_plan_theme_integration:not([data-variant-id="${this.variantIdInput.value}"])`,
    );
    this.showSellingPlanForm(sellingPlanFormForSelectedVariant);
    this.hideSellingPlanForms(sellingPlanFormsForUnselectedVariants);
  }

  handleVariantChange() {
    this.handleSellingPlanFormVisibility();
    this.updateSellingPlanInputsValues();
    this.listenToSellingPlanFormRadioButtonChange();
  }

  /*
    The functions listenToVariantChange() and listenToAddToCartForms() are implemented to track when a product variant is altered or when the product form is updated.
    The identification of the variant is crucial as it dictates which selling plan box should be displayed.
  */
  listenToVariantChange() {
    this.listenToAddToCartForms();
    if (this.variantIdInput?.tagName === 'INPUT') {
      const variantIdObserver = new MutationObserver((mutationList) => {
        mutationList.forEach((mutationRecord) => {
          this.handleVariantChange(mutationRecord.target.value);
        });
      });

      variantIdObserver.observe(this.variantIdInput, {
        attributes: true,
      });
    }
  }

  listenToAddToCartForms() {
    this.addToCartForms.forEach((addToCartForm) => {
      addToCartForm.addEventListener('change', () => {
        this.handleVariantChange();
      });
    });
  }

  get regularPriceElement() {
    return this.rootElement.querySelector('.price__regular');
  }

  get salePriceElement() {
    return this.rootElement.querySelector('.price__sale');
  }

  get salePriceValue() {
    return this.salePriceElement?.querySelector('.price-item--sale');
  }

  get regularPriceValue() {
    return this.salePriceElement?.querySelector('.price-item--regular');
  }

  get sellingPlanAllocationPrice() {
    return document.getElementById(`${this.selectedPurchaseOption.dataset.sellingPlanGroupId}_allocation_price`);
  }

  get selectedPurchaseOptionPrice() {
    return this.selectedPurchaseOption?.dataset.variantPrice;
  }

  get selectedPurchaseOptionComparedAtPrice() {
    return this.selectedPurchaseOption?.dataset.variantCompareAtPrice;
  }

  get price() {
    return this.sellingPlanAllocationPrices?.price ?? null;
  }

  /*
    We aim to ascertain whether a compared price exists, which would indicate that the currently selected input has a discount applied to it.
    If a discount is detected, the discounted price is displayed; otherwise, the regular price is shown.
  */
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

  hideSalePrice() {
    this.salePriceElement.style.display = 'none';
  }

  hideRegularPrice() {
    this.regularPriceElement.style.display = 'none';
  }

  showRegularPrice() {
    this.regularPriceElement.style.display = 'block';
    this.rootElement.querySelector('.price__sale').style.display = 'none';
  }

  showSalePrice() {
    this.salePriceElement.style.display = 'block';
    this.regularPriceValue.innerHTML = this.selectedPurchaseOptionComparedAtPrice;
    this.salePriceValue.innerHTML = this.selectedPurchaseOptionPrice;
  }

  get sellingPlanInputs() {
    return this.rootElement.querySelectorAll('.selected-selling-plan-id');
  }

  updateSellingPlanInputsValues() {
    this.sellingPlanInputs.forEach((sellingPlanInput) => {
      sellingPlanInput.value = this.sellingPlanInputValue;
    });
  }

  get sellingPlanInputValue() {
    return this.selectedPurchaseOption?.dataset.sellingPlanId ?? null;
  }

  get selectedPurchaseOption() {
    return this.visibleSellingPlanForm?.querySelector('input[type="radio"]:checked');
  }

  set selectedPurchaseOption(selectedPurchaseOption) {
    this._selectedPurchaseOption = selectedPurchaseOption;
  }

  handleRadioButtonChange(selectedPurchaseOption) {
    this.selectedPurchaseOption = selectedPurchaseOption;
    this.updateSellingPlanInputsValues();
    this.updatePrice();
  }

  listenToSellingPlanFormRadioButtonChange() {
    this.visibleSellingPlanForm?.querySelectorAll('input[type="radio"]').forEach((radio) => {
      radio.addEventListener('change', (event) => {
        this.handleRadioButtonChange(event.target);
      });
    });
  }

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
}

if (!customElements.get('selling-plans-widget')) {
  customElements.define('selling-plans-widget', SellingPlansWidget);
}
