/**
 * ModalOpener component
 * 
 * A unified modal opener for all modal types in the theme.
 * Used by quick-add-modal, product-monogram-popup, and other modals.
 */
export class ModalOpener extends HTMLElement {
  constructor() {
    super();

    const button = this.querySelector('button');

    if (!button) return;
    button.addEventListener('click', (event) => {
      event.preventDefault();
      event.stopPropagation();
      
      this.toggleSpinner(button, true);
      
      const modal = document.querySelector(this.getAttribute('data-modal'));
      if (modal) modal.show(button);
    });
  }

  toggleSpinner(button, show) {
    const spinner = button.querySelector('.add-to-cart-icon-spinner');
    const icon = button.querySelector('.add-to-cart-icon');
    const text = button.querySelector('.add-to-cart-text__content');
    
    spinner?.classList.toggle('hidden', !show);
    icon?.classList.toggle('hidden', show);
    text?.classList.toggle('hidden', show);
  }
}

if (!customElements.get('modal-opener')) {
  customElements.define('modal-opener', ModalOpener);
}