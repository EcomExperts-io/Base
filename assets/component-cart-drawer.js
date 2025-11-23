export class CartDrawer extends HTMLElement {
  constructor() {
    super();
    this.onCartRequestEnd = this.onCartRequestEnd.bind(this);
  }

  connectedCallback() {
    document.addEventListener('liquid-ajax-cart:request-end', this.onCartRequestEnd);
  }

  disconnectedCallback() {
    document.removeEventListener('liquid-ajax-cart:request-end', this.onCartRequestEnd);
  }

  onCartRequestEnd(event) {
    const { requestState } = event.detail || {};
    if (requestState?.requestType === 'add' && requestState?.responseData?.ok) {
      // Open cart drawer via Alpine on header
      window.dispatchEvent(new CustomEvent('cart-open'));
    }
  }
}

if (!customElements.get('cart-drawer')) {
  customElements.define('cart-drawer', CartDrawer);
}


