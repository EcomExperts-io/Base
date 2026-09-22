/**
 * <cart-drawer> — owns open/close state, opens after add-to-cart, and swaps
 * .drawer__wrapper from the section HTML that cart-store.js bundles into every
 * mutation. Never fetches.
 *
 * Opens on any click of `[data-cart-open]` (the header cart bubble carries
 * it) and closes on `[data-drawer-close]`, Escape, or the overlay.
 * @extends HTMLElement
 */
export class CartDrawer extends HTMLElement {
  unsubscribe = null;

  constructor() {
    super();
    this.onCart = this.onCart.bind(this);
    this.onNoteChange = this.onNoteChange.bind(this);
    this.onDocumentClick = this.onDocumentClick.bind(this);
    this.onKeydown = this.onKeydown.bind(this);
    this.onInnerClick = this.onInnerClick.bind(this);
  }

  connectedCallback() {
    this.unsubscribe = window.Cart.subscribe(this.onCart);
    this.addEventListener('change', this.onNoteChange);
    document.addEventListener('click', this.onDocumentClick);
    document.addEventListener('keydown', this.onKeydown);
    this.addEventListener('click', this.onInnerClick);
  }

  disconnectedCallback() {
    this.unsubscribe?.();
    this.removeEventListener('change', this.onNoteChange);
    document.removeEventListener('click', this.onDocumentClick);
    document.removeEventListener('keydown', this.onKeydown);
    this.removeEventListener('click', this.onInnerClick);
  }

  /** Saves the order note without re-rendering (nothing visible changes). */
  onNoteChange(event) {
    if (!event.target.matches('[data-cart-note]')) return;
    window.Cart.update({ note: event.target.value }, { source: event.target, withSections: false }).catch(() => {});
  }

  get sectionId() {
    return this.closest('.shopify-section')?.id.replace('shopify-section-', '');
  }

  get isOpen() {
    return this.classList.contains('cart-open');
  }

  open() {
    this.classList.add('cart-open');
    document.body.classList.add('overflow-hidden');
    this.querySelector('.drawer__wrapper')?.focus();
  }

  close() {
    this.classList.remove('cart-open');
    document.body.classList.remove('overflow-hidden');
  }

  toggle() {
    if (this.isOpen) {
      this.close();
    } else {
      this.open();
    }
  }

  onDocumentClick(event) {
    const opener = event.target.closest('[data-cart-open]');
    if (!opener) return;

    event.preventDefault();
    this.toggle();
  }

  onKeydown(event) {
    if (event.key === 'Escape' && this.isOpen) this.close();
  }

  onInnerClick(event) {
    if (event.target.closest('[data-drawer-close]')) this.close();
  }

  onCart({ action, sections }) {
    const html = sections?.[this.sectionId];
    if (html) this.render(html, action);
    if (action === 'add') this.open();
  }

  render(html, action) {
    const next = new DOMParser().parseFromString(html, 'text/html').querySelector('cart-drawer .drawer__wrapper');
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
