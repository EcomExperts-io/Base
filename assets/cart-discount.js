class CartDiscount extends HTMLElement {
  constructor() {
    super();
    this.form = null;
    this.discountInput = null;
    this.cartDiscountError = null;
    this.cartDiscountErrorDiscountCode = null;
    this.cartDiscountErrorShipping = null;
    this.boundApplyDiscount = this.applyDiscount.bind(this);
    this.boundRemoveDiscount = this.removeDiscount.bind(this);
  }

  connectedCallback() {
    this.form = this.querySelector('.cart-discount__form');
    this.discountInput = this.querySelector('input[name="discount"]');
    this.cartDiscountError = this.querySelector('.cart-discount__error');
    this.cartDiscountErrorDiscountCode = this.querySelector('.cart-discount__error-text--discount-code');
    this.cartDiscountErrorShipping = this.querySelector('.cart-discount__error-text--shipping');

    if (!this.form) {
      console.error('CartDiscount: Form not found');
      return;
    }

    this.form.addEventListener('submit', this.boundApplyDiscount);
    document.addEventListener('click', this.boundRemoveDiscount);
  }

  disconnectedCallback() {
    if (this.form) {
      this.form.removeEventListener('submit', this.boundApplyDiscount);
    }
    document.removeEventListener('click', this.boundRemoveDiscount);
  }

  async applyDiscount(event) {
    event.preventDefault();

    const code = this.discountInput?.value.trim().toUpperCase();
    if (!code) return;

    const existingDiscounts = this.getExistingDiscounts();
    
    if (existingDiscounts.some(c => c.toUpperCase() === code)) {
      this.discountInput.value = '';
      return;
    }

    this.hideErrors();

    const allDiscounts = [...existingDiscounts, code].join(',');

    try {
      const response = await fetch(window.Shopify.routes.root + 'cart/update.js', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ discount: allDiscounts })
      });

      const cart = await response.json();
      
      const applied = cart.cart_level_discount_applications?.some(
        app => app?.title?.toUpperCase() === code
      ) || (cart.cart_level_discount_applications?.length > existingDiscounts.length);

      if (applied) {
        window.location.reload();
      } else {
        this.showError(code);
      }
      
    } catch (error) {
      console.error('Error applying discount:', error);
      this.showError(code);
    }
  }

  async removeDiscount(event) {
    const removeButton = event.target.closest('.cart-discount__pill-remove');
    if (!removeButton) return;

    const pill = removeButton.closest('.cart-discount__pill');
    const codeToRemove = pill?.dataset.discountCode;
    if (!codeToRemove) return;

    event.preventDefault();

    const existingDiscounts = this.getExistingDiscounts();
    const remaining = existingDiscounts.filter(c => c.toUpperCase() !== codeToRemove.toUpperCase());

    try {
      await fetch(window.Shopify.routes.root + 'cart/update.js', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ discount: '' })
      });

      if (remaining.length > 0) {
        const url = new URL(window.location.href);
        const returnUrl = encodeURIComponent(url.pathname + url.search);
        const discountPath = remaining.map(encodeURIComponent).join(',');
        window.location.href = `${window.Shopify.routes.root}discount/${discountPath}?return_to=${returnUrl}`;
      } else {
        window.location.reload();
      }
    } catch (error) {
      console.error('Error removing discount:', error);
      window.location.reload();
    }
  }

  hideErrors() {
    this.cartDiscountError?.classList.add('hidden');
    this.cartDiscountErrorDiscountCode?.classList.add('hidden');
    this.cartDiscountErrorShipping?.classList.add('hidden');
  }

  showError(code) {
    if (!this.cartDiscountError) return;
    
    const isShipping = code.toLowerCase().includes('ship') || code.toLowerCase().includes('free');
    const errorEl = isShipping ? this.cartDiscountErrorShipping : this.cartDiscountErrorDiscountCode;
    
    this.cartDiscountError.classList.remove('hidden');
    errorEl?.classList.remove('hidden');
  }

  getExistingDiscounts() {
    return Array.from(document.querySelectorAll('.cart-discount__pill'))
      .map(pill => pill.dataset.discountCode)
      .filter(Boolean);
  }
}

if (!customElements.get('cart-discount-component')) {
  customElements.define('cart-discount-component', CartDiscount);
}

class DisclosureCustom extends HTMLElement {
  constructor() {
    super();
    this.trigger = null;
    this.content = null;
  }

  connectedCallback() {
    this.trigger = this.querySelector('[ref="disclosureTrigger"]');
    this.content = this.querySelector('[ref="disclosureContent"]');

    if (!this.trigger || !this.content) {
      console.error('DisclosureCustom: Required elements not found');
      return;
    }

    this.boundToggleDisclosure = this.toggleDisclosure.bind(this);
    this.trigger.addEventListener('click', this.boundToggleDisclosure);
  }

  disconnectedCallback() {
    if (this.trigger && this.boundToggleDisclosure) {
      this.trigger.removeEventListener('click', this.boundToggleDisclosure);
    }
  }

  toggleDisclosure() {
    if (!this.trigger || !this.content) return;

    const expanded = this.trigger.matches('[aria-expanded="true"]');
    this.trigger.setAttribute('aria-expanded', String(!expanded));
    this.trigger.setAttribute(
      'aria-label',
      expanded ? this.trigger.dataset.disclosureOpen : this.trigger.dataset.disclosureClose
    );
    this.content.inert = expanded;
  }
}

if (!customElements.get('disclosure-custom')) {
  customElements.define('disclosure-custom', DisclosureCustom);
}
