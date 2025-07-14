if (!customElements.get('bulk-product-atc')) {
  class BulkProductAtc extends HTMLElement {
    constructor() {
      super();
      this.form = null;
      this.bulkRows = [];
      this.variantInputs = [];
    }

    connectedCallback() {
      this.initializeBulkSelector();
      this.updateBulkTotal()
    }

    initializeBulkSelector() {
      this.findForm();
      this.findElements();
      this.setupEventListeners();
      this.updateBulkSelector();
    }

    findForm() {
      const form1 = document.querySelector('.product-form__buttons form[action*="/cart/add"]');
      const form2 = document.querySelector('form[action*="/cart/add"]');
      const form3 = document.querySelector('form[action*="/cart"]');
      this.form = form1 || form2 || form3;

      if (!this.form) {
        console.warn('BulkProductAtc: No form found');
        return;
      }

      // Clone and replace form to ensure clean event listeners
      const newForm = this.form.cloneNode(true);
      this.form.parentNode.replaceChild(newForm, this.form);
      this.form = newForm;
    }

    findElements() {
      this.variantInputs = document.querySelectorAll('input[type="radio"], select');
      this.bulkRows = document.querySelectorAll('.bulk-quantity-row');
    }

    setupEventListeners() {
      if (!this.form) return;

      // Listen for variant changes
      document.addEventListener('change', (e) => {
        if (e.target.matches('input[type="radio"], select')) {
          this.updateBulkSelector();
          this.updateBulkTotal();
        }
        if (e.target.matches('.bulk-quantity-input')) {
          this.updateBulkTotal();
        }
      });

      // Handle form submission
      this.form.addEventListener('submit', this.handleFormSubmit.bind(this), true);

      // Handle submit button clicks
      const submitButtons = this.form.querySelectorAll('button[type="submit"], input[type="submit"]');
      submitButtons.forEach(button => {
        button.addEventListener('click', this.handleButtonClick.bind(this), true);
      });
    }

    updateBulkSelector() {
      if (this.variantInputs.length === 0 || this.bulkRows.length === 0) return;

      const currentVariantKey = this.getCurrentVariantKey();

      this.bulkRows.forEach(row => {
        const rowVariantKey = row.getAttribute('data-variant-key');
        if (rowVariantKey === currentVariantKey) {
          row.style.display = 'flex';
          const input = row.querySelector('input[type="number"]');
          if (input) input.value = 0;
        } else {
          row.style.display = 'none';
          const input = row.querySelector('input[type="number"]');
          if (input) input.value = 0;
        }
      });
    }

    getCurrentVariantKey() {
      let currentVariantKey = '';
      const variantSelectors = document.querySelectorAll('input[type="radio"]:checked, select');

      variantSelectors.forEach(input => {
        const optionName = input.name || input.getAttribute('name');
        if (optionName && !optionName.toLowerCase().includes('size')) {
          currentVariantKey += input.value + '-';
        }
      });

      return currentVariantKey;
    }

    hasBulkQuantities() {
      const bulkInputs = document.querySelectorAll('input[name^="bulk_qty["]');
      let totalQuantity = 0;
      bulkInputs.forEach(input => {
        totalQuantity += parseInt(input.value) || 0;
      });
      return totalQuantity > 0;
    }

    getSelectedQuantities() {
      const bulkInputs = document.querySelectorAll('.bulk-quantity-input');
      const selectedQuantities = [];

      bulkInputs.forEach(input => {
        const quantity = parseInt(input.value) || 0;
        if (quantity > 0) {
          const variantRow = input.closest('.bulk-quantity-row');
          const variantId = variantRow ? variantRow.getAttribute('data-variant-id') : null;
          if (variantId) {
            selectedQuantities.push({
              id: parseInt(variantId),
              quantity: quantity,
              input: input
            });
          }
        }
      });

      return selectedQuantities;
    }

    handleButtonClick(e) {
      if (!this.hasBulkQuantities()) {
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
        return false;
      }
    }

    handleFormSubmit(e) {

      const selectedQuantities = this.getSelectedQuantities();

      if (selectedQuantities.length === 0) {
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
        return false;
      }



      if (selectedQuantities.length === 1) {
        // Single item: just update hidden input and let form submit normally
        const hiddenVariantInput = this.form.querySelector('input[name="id"]');
        if (hiddenVariantInput) {
          hiddenVariantInput.value = selectedQuantities[0].id;
        }
        // Don't return - let the form submit normally
      }


      // Multiple items: use single AJAX request
      e.preventDefault();
      e.stopPropagation();
      e.stopImmediatePropagation();

      this.addMultipleItemsToCart(selectedQuantities);
    }

    addMultipleItemsToCart(selectedQuantities) {
      
      const itemsToAdd = selectedQuantities.map(item => ({
        id: item.id,
        quantity: item.quantity
      }));

      fetch('/cart/add.js', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({ items: itemsToAdd })
      })
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status} - ${response.statusText}`);
        }
        return response.json();
      })
      .then(data => {
        console.log('Successfully added items to cart:', data);
        window.location.href = '/cart';
      })
      .catch(error => {
        console.error('Failed to add items:', error);
        alert('There was an error adding items to the cart. Please try again.');
      });
    }

    updateBulkTotal() {
      // Find all visible bulk-quantity-rows
      const rows = document.querySelectorAll('.bulk-quantity-row');
      let total = 0;
      rows.forEach(row => {
        if (row.style.display !== 'none') {
          const qtyInput = row.querySelector('.bulk-quantity-input');
          const qty = parseInt(qtyInput.value) || 0;
          // Try to get price from a data attribute, fallback to 0
          let price = 0;
          if (row.dataset.price) {
            price = parseInt(row.dataset.price);
          } else {
            // Try to get price from a hidden input or global object if needed
            const priceInput = row.querySelector('input[type="hidden"][name^="variant_price_"]');
            if (priceInput) price = parseInt(priceInput.value);
          }
          total += qty * price;
        }
      });
      // Update the Add to Cart button
      const addToCartTotal = document.querySelector('.add-to-cart-total');
      if (addToCartTotal) {
        if (window.Shopify && Shopify.formatMoney) {
          addToCartTotal.textContent = `TOTAL ${Shopify.formatMoney(total, Shopify.money_format)}`;
        } else {
          addToCartTotal.textContent = `TOTAL $${(total / 100).toFixed(2)}`;
        }
      }
    }
  }

  customElements.define('bulk-product-atc', BulkProductAtc);
} 