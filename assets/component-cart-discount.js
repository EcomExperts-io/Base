/**
 * <cart-discount-form data-codes> — applies and removes discount codes through
 * Cart.update({ discount }). The pills, totals and line prices all come back
 * as rendered HTML in the same request, so this element renders nothing
 * itself except an error message.
 *
 * `data-codes` is the comma-separated list of codes Liquid found applied.
 * After a successful apply, the store re-renders this element, so the check
 * for "did Shopify actually accept the code" reads the new cart state.
 * @extends HTMLElement
 */
export class CartDiscountForm extends HTMLElement {
  constructor() {
    super();
    this.onSubmit = this.onSubmit.bind(this);
    this.onClick = this.onClick.bind(this);
  }

  connectedCallback() {
    this.addEventListener('submit', this.onSubmit);
    this.addEventListener('click', this.onClick);
  }

  disconnectedCallback() {
    this.removeEventListener('submit', this.onSubmit);
    this.removeEventListener('click', this.onClick);
  }

  get codes() {
    return (this.dataset.codes || '').split(',').filter(Boolean);
  }

  get input() {
    return this.querySelector('input[name="discount_code"]');
  }

  /** The element is replaced when its section re-renders; find the live one. */
  get live() {
    return this.isConnected ? this : document.querySelector('cart-discount-form') || this;
  }

  showError(message) {
    const box = this.querySelector('[data-discount-error]');
    const text = this.querySelector('[data-discount-error-text]');
    if (!box || !text) return;

    text.textContent = message;
    box.hidden = false;
  }

  setBusy(busy) {
    this.toggleAttribute('aria-busy', busy);
    for (const control of this.querySelectorAll('input, button')) control.disabled = busy;
  }

  hasCode(code) {
    return this.codes.some((existing) => existing.toUpperCase() === code.toUpperCase());
  }

  /**
   * Shopify accepts any string in `discount` and simply ignores invalid codes,
   * so acceptance is checked against the cart that comes back.
   */
  static isApplied(cart, code) {
    const upper = code.toUpperCase();

    if (cart.cart_level_discount_applications?.some((app) => app.title?.toUpperCase() === upper)) return true;

    return cart.items?.some((item) =>
      item.line_level_discount_allocations?.some((allocation) => allocation.discount_application?.title?.toUpperCase() === upper)
    );
  }

  async onSubmit(event) {
    event.preventDefault();

    const code = this.input?.value.trim();
    if (!code || this.hasCode(code)) return;

    this.setBusy(true);

    try {
      const response = await window.Cart.update({ discount: [...this.codes, code].join(',') }, { source: this });
      const cart = window.Cart.state || response;

      if (!CartDiscountForm.isApplied(cart, code)) this.live.showError(this.dataset.errorInvalid);
    } catch (error) {
      this.live.showError(error.description || this.dataset.errorGeneric);
    } finally {
      this.setBusy(false);
    }
  }

  async onClick(event) {
    const button = event.target.closest('[data-remove-discount]');
    if (!button) return;

    const code = button.closest('[data-discount-code]')?.dataset.discountCode;
    if (!code) return;

    this.setBusy(true);

    try {
      const remaining = this.codes.filter((existing) => existing.toUpperCase() !== code.toUpperCase());
      await window.Cart.update({ discount: remaining.join(',') }, { source: this });
    } catch (error) {
      this.live.showError(error.description || this.dataset.errorGeneric);
    } finally {
      this.setBusy(false);
    }
  }
}

if (!customElements.get('cart-discount-form')) {
  customElements.define('cart-discount-form', CartDiscountForm);
}
