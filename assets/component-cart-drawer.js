/**
 * Cart drawer — owns its open/close state (no Alpine), opens after
 * add-to-cart, and re-renders its wrapper from the section HTML that cart.js
 * bundles into every cart mutation ('cart:change' event).
 * @extends HTMLElement
 */
export class CartDrawer extends HTMLElement {
  constructor() {
    super();
    this.onCartChange = this.onCartChange.bind(this);
    this.onDocumentClick = this.onDocumentClick.bind(this);
    this.addEventListener('click', this.onInnerClick);
  }

  connectedCallback() {
    document.addEventListener('cart:change', this.onCartChange);
    document.addEventListener('click', this.onDocumentClick);
  }

  disconnectedCallback() {
    document.removeEventListener('cart:change', this.onCartChange);
    document.removeEventListener('click', this.onDocumentClick);
  }

  get sectionId() {
    return this.closest('.shopify-section')?.id.replace('shopify-section-', '');
  }

  open() {
    this.classList.add('cart-open');
  }

  close() {
    this.classList.remove('cart-open');
  }

  toggle() {
    this.classList.toggle('cart-open');
  }

  onDocumentClick(event) {
    const bubble = event.target.closest('#header-cart-bubble');
    if (bubble) {
      event.preventDefault();
      this.toggle();
    }
  }

  onInnerClick(event) {
    if (event.target.closest('.drawer-overlay, .cart-drawer__close')) {
      this.close();
      return;
    }

    const noteLabel = event.target.closest('.cart-note label');
    if (noteLabel) noteLabel.classList.toggle('note-open');
  }

  onCartChange(event) {
    const html = event.detail.sections?.[this.sectionId];
    if (html) this.render(html, event.detail.action);
    if (event.detail.action === 'add') this.open();
  }

  render(html, action) {
    const next = new DOMParser().parseFromString(html, 'text/html').querySelector('#cart-drawer .drawer__wrapper');
    const current = this.querySelector('.drawer__wrapper');
    if (!next || !current) return;

    const scrollTop = current.querySelector('.cart-items')?.scrollTop || 0;
    current.innerHTML = next.innerHTML;

    const items = current.querySelector('.cart-items');
    if (items) items.scrollTop = action === 'add' ? 0 : scrollTop;
  }
}

if (!customElements.get('cart-drawer')) {
  customElements.define('cart-drawer', CartDrawer);
}
