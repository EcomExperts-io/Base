/**
 * <cart-count> — renders the cart item count and keeps it current.
 *
 * Subscribes to the store rather than being re-rendered by the Section
 * Rendering API, so the header never needs to be part of a cart request.
 * Listens for 'cart:count' (optimistic and confirmed counts from
 * cart-store.js) and falls back to Cart.state on connect.
 * @extends HTMLElement
 */
export class CartCount extends HTMLElement {
  constructor() {
    super();
    this.onCount = this.onCount.bind(this);
  }

  connectedCallback() {
    document.addEventListener('cart:count', this.onCount);

    const count = window.Cart?.state?.item_count;
    if (count !== undefined) this.render(count);
  }

  disconnectedCallback() {
    document.removeEventListener('cart:count', this.onCount);
  }

  onCount(event) {
    this.render(event.detail.count);
  }

  render(count) {
    this.textContent = count;
    this.toggleAttribute('data-empty', count === 0);
  }
}

if (!customElements.get('cart-count')) {
  customElements.define('cart-count', CartCount);
}
