/**
 * Cart page wrapper — re-renders itself from the section HTML that cart.js
 * bundles into every cart mutation ('cart:change' event).
 * @extends HTMLElement
 */
export class CartPage extends HTMLElement {
  constructor() {
    super();
    this.onCartChange = this.onCartChange.bind(this);
  }

  connectedCallback() {
    document.addEventListener('cart:change', this.onCartChange);
  }

  disconnectedCallback() {
    document.removeEventListener('cart:change', this.onCartChange);
  }

  get sectionId() {
    return this.closest('.shopify-section')?.id.replace('shopify-section-', '');
  }

  onCartChange(event) {
    const html = event.detail.sections?.[this.sectionId];
    if (!html) return;

    const next = new DOMParser().parseFromString(html, 'text/html').querySelector('cart-page');
    if (next) this.innerHTML = next.innerHTML;
  }
}

if (!customElements.get('cart-page')) {
  customElements.define('cart-page', CartPage);
}
