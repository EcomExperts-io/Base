/**
 * <cart-page> — swaps its contents from the section HTML that cart-store.js
 * bundles into every mutation. Never fetches.
 * @extends HTMLElement
 */
export class CartPage extends HTMLElement {
  unsubscribe = null;

  constructor() {
    super();
    this.onCart = this.onCart.bind(this);
    this.onNoteChange = this.onNoteChange.bind(this);
  }

  connectedCallback() {
    this.unsubscribe = window.Cart.subscribe(this.onCart);
    this.addEventListener('change', this.onNoteChange);
  }

  disconnectedCallback() {
    this.unsubscribe?.();
    this.removeEventListener('change', this.onNoteChange);
  }

  /** Saves the order note without re-rendering (nothing visible changes). */
  onNoteChange(event) {
    if (!event.target.matches('[data-cart-note]')) return;
    window.Cart.update({ note: event.target.value }, { source: event.target, withSections: false }).catch(() => {});
  }

  get sectionId() {
    return this.closest('.shopify-section')?.id.replace('shopify-section-', '');
  }

  onCart({ sections }) {
    const html = sections?.[this.sectionId];
    if (!html) return;

    const next = new DOMParser().parseFromString(html, 'text/html').querySelector('cart-page');
    if (next) this.innerHTML = next.innerHTML;
  }
}

if (!customElements.get('cart-page')) {
  customElements.define('cart-page', CartPage);
}
