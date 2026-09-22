/**
 * <cart-line-item data-key> — one cart line's stepper, quantity input and
 * remove link. Intercepts the /cart/change links rendered by
 * component-cart-line-item.liquid and routes them through Cart.change by key.
 *
 * Rapid +/- clicks are debounced into one request carrying the final
 * quantity. Errors render into the line's .cart-item__error and the input is
 * reset to the last server-rendered value.
 * @extends HTMLElement
 */
const DEBOUNCE_MS = 250;

export class CartLineItem extends HTMLElement {
  timer = null;

  constructor() {
    super();
    this.onClick = this.onClick.bind(this);
    this.onChange = this.onChange.bind(this);
    this.onError = this.onError.bind(this);
  }

  connectedCallback() {
    this.addEventListener('click', this.onClick);
    this.addEventListener('change', this.onChange);
    document.addEventListener('cart:error', this.onError);
  }

  disconnectedCallback() {
    clearTimeout(this.timer);
    this.removeEventListener('click', this.onClick);
    this.removeEventListener('change', this.onChange);
    document.removeEventListener('cart:error', this.onError);
  }

  get key() {
    return this.dataset.key;
  }

  get input() {
    return this.querySelector('.cart-quantity input');
  }

  get errorEl() {
    return this.querySelector('.cart-item__error');
  }

  onClick(event) {
    const remove = event.target.closest('[data-remove]');

    if (remove) {
      event.preventDefault();
      this.submit(0);
      return;
    }

    const step = event.target.closest('[data-step]');
    if (!step || !this.input) return;

    event.preventDefault();
    const increment = Number(this.input.step) || 1;
    const direction = Number(step.dataset.step) || 1;
    const current = Number(this.input.value) || 0;

    this.setQuantity(current + direction * increment);
  }

  onChange(event) {
    if (event.target !== this.input) return;
    this.setQuantity(Number(this.input.value) || 0);
  }

  /**
   * Clamps to the variant's quantity rule and schedules the request.
   * Anything below `min` becomes 0 (remove) — matching Shopify's own cart.
   */
  setQuantity(requested) {
    const min = Number(this.input.min) || 1;
    const max = Number(this.input.max) || Infinity;
    let quantity = Math.min(requested, max);
    if (quantity < min) quantity = 0;

    this.input.value = quantity;
    if (this.errorEl) this.errorEl.textContent = '';

    clearTimeout(this.timer);
    this.timer = setTimeout(() => this.submit(quantity), DEBOUNCE_MS);
  }

  submit(quantity) {
    this.setAttribute('aria-busy', 'true');
    window.Cart.change(this.key, quantity, { source: this }).catch(() => {
      // cart:error handler renders the message; nothing else to do here.
    });
  }

  onError(event) {
    if (event.detail.source !== this) return;

    this.removeAttribute('aria-busy');
    if (this.errorEl) this.errorEl.textContent = event.detail.error.description;
    if (this.input) this.input.value = this.input.defaultValue;
  }
}

if (!customElements.get('cart-line-item')) {
  customElements.define('cart-line-item', CartLineItem);
}
