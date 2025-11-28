export class CartDiscountForm extends HTMLElement {
  connectedCallback() {
    this.form = this.querySelector('#cart-discount-form');
    this.input = this.querySelector('#discount-code-input');
    this.errorEl = this.querySelector('.cart-discount__error');
    this.codesList = this.querySelector('.cart-discount__codes');
    this.submitBtn = this.form?.querySelector('button[type="submit"]');
    this.originalButtonText = this.submitBtn?.textContent.trim();

    if (!this.form) return;

    this.form.addEventListener('submit', this.handleSubmit.bind(this));
    this.codesList?.addEventListener('click', this.handleRemoveClick.bind(this));
  }

  disconnectedCallback() {
    this.form?.removeEventListener('submit', this.handleSubmit.bind(this));
    this.codesList?.removeEventListener('click', this.handleRemoveClick.bind(this));
  }

  showError(msg) {
    const errorText = this.errorEl?.querySelector('.cart-discount__error-text');
    if (errorText) {
      errorText.textContent = msg;
      this.errorEl.style.display = 'flex';
    }
  }

  hideError() {
    if (this.errorEl) {
      this.errorEl.style.display = 'none';
      const errorText = this.errorEl.querySelector('.cart-discount__error-text');
      if (errorText) errorText.textContent = '';
    }
  }

  setLoading(loading) {
    if (this.submitBtn) {
      this.submitBtn.disabled = loading;
      this.submitBtn.textContent = loading ? 'Applying...' : this.originalButtonText;
    }
    if (this.input) this.input.disabled = loading;
  }

  async applyDiscount(codes) {
    const res = await fetch(`${window.Shopify.routes.root}cart/update.js`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ discount: codes })
    });

    if (!res.ok) throw new Error(`Discount update failed: ${res.status}`);
    return res.json();
  }

  getExistingCodes() {
    return Array.from(this.querySelectorAll('.cart-discount__pill'))
      .map(pill => pill.dataset.discountCode)
      .filter(Boolean);
  }

  getCartDiscountCodes(cart) {
    const codes = (cart.cart_level_discount_applications || [])
      .filter(app => app.type === 'discount_code')
      .map(app => app.title);

    (cart.items || []).forEach(item => {
      if (item.discounts) {
        item.discounts.forEach(d => d.title && codes.push(d.title));
      }
      if (item.line_level_discount_allocations) {
        item.line_level_discount_allocations.forEach(a => {
          if (a.discount_application?.title) codes.push(a.discount_application.title);
        });
      }
    });

    return [...new Set(codes)];
  }

  createPill(code) {
    const li = document.createElement('li');
    li.className = 'cart-discount__pill';
    li.dataset.discountCode = code;

    const codeP = document.createElement('p');
    codeP.className = 'cart-discount__pill-code';
    codeP.textContent = code;

    const removeBtn = document.createElement('button');
    removeBtn.type = 'button';
    removeBtn.className = 'cart-discount__pill-remove';
    removeBtn.setAttribute('aria-label', `Remove discount ${code}`);

    const existingIcon = this.querySelector('.cart-discount__pill-remove')?.innerHTML;
    removeBtn.innerHTML = existingIcon || '<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 4L4 12M4 4l8 8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>';

    li.appendChild(codeP);
    li.appendChild(removeBtn);
    return li;
  }

  updatePills(cart) {
    if (!this.codesList) return;

    const allDiscountCodes = this.getCartDiscountCodes(cart);
    const currentCodes = this.getExistingCodes();
    const currentPills = Array.from(this.codesList.querySelectorAll('.cart-discount__pill'));

    currentPills.forEach(pill => {
      const code = pill.dataset.discountCode;
      if (!allDiscountCodes.some(c => c.toUpperCase() === code.toUpperCase())) {
        pill.remove();
      }
    });

    allDiscountCodes.forEach(code => {
      if (!currentCodes.some(c => c.toUpperCase() === code.toUpperCase())) {
        this.codesList.appendChild(this.createPill(code));
      }
    });
  }

  async handleSubmit(event) {
    event.preventDefault();
    this.hideError();

    const code = this.input?.value.trim();
    if (!code) {
      this.showError('Please enter a discount code.');
      return;
    }

    const existing = this.getExistingCodes();
    if (existing.some(c => c.toUpperCase() === code.toUpperCase())) {
      this.input.value = '';
      return;
    }

    this.setLoading(true);
    try {
      const allCodes = [...existing, code].join(',');
      await this.applyDiscount(allCodes);

      const cart = await fetch(`${window.Shopify.routes.root}cart.js`).then(r => r.json());
      const cartCodes = this.getCartDiscountCodes(cart);
      const isApplied = cartCodes.some(c => c.toUpperCase() === code.toUpperCase());

      if (isApplied) {
        this.input.value = '';
        this.updatePills(cart);

        if (window.liquidAjaxCart?.update) {
          window.liquidAjaxCart.update({}, {});
        }
      } else {
        this.showError('That discount code is not valid.');
      }
    } catch (err) {
      console.error(err);
      this.showError('Something went wrong while applying the code.');
    } finally {
      this.setLoading(false);
    }
  }

  async handleRemoveClick(event) {
    const removeBtn = event.target.closest('.cart-discount__pill-remove');
    if (!removeBtn) return;

    const pill = removeBtn.closest('.cart-discount__pill');
    const codeToRemove = pill?.dataset.discountCode;
    if (!codeToRemove) return;

    event.preventDefault();
    this.hideError();

    pill.classList.add('cart-discount__pill--removing');
    removeBtn.disabled = true;

    try {
      const existing = this.getExistingCodes();
      const remaining = existing.filter(c => c.toUpperCase() !== codeToRemove.toUpperCase());
      const codes = remaining.length > 0 ? remaining.join(',') : '';

      await this.applyDiscount(codes);

      const cart = await fetch(`${window.Shopify.routes.root}cart.js`).then(r => r.json());
      this.updatePills(cart);

      if (window.liquidAjaxCart?.update) {
        window.liquidAjaxCart.update({}, {});
      }
    } catch (err) {
      console.error(err);
      pill.classList.remove('cart-discount__pill--removing');
      removeBtn.disabled = false;
      this.showError('Something went wrong while removing the discount.');
      const cart = await fetch(`${window.Shopify.routes.root}cart.js`).then(r => r.json());
      this.updatePills(cart);
    }
  }
}

if (!customElements.get('cart-discount-form')) {
  customElements.define('cart-discount-form', CartDiscountForm);
}
