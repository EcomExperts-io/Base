export class QuickAdd extends HTMLElement {
  constructor() {
    super();
    this.modal = null;
    this.modalContent = null;
    this.setupModal();
    this.bindEvents();
    this.onCartRequestEnd = this.onCartRequestEnd.bind(this);
    this.setupAjaxCartButtons();
  }

  connectedCallback() {
    if (!this.initialized) {
      this.initialized = true;
      document.body.appendChild(this);
      document.addEventListener('liquid-ajax-cart:request-end', this.onCartRequestEnd);
    }
  }

  setupAjaxCartButtons() {
    document.addEventListener('submit', (event) => {
      const form = event.target.closest('ajax-cart-product-form');
      if (!form) return;

      const button = form.querySelector('.quick-add__icon-button');
      if (button) this.toggleSpinner(button, true);
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

  disconnectedCallback() {
    if (this.initialized) {
      document.removeEventListener('liquid-ajax-cart:request-end', this.onCartRequestEnd);
    }
  }

  onCartRequestEnd(event) {
    const { requestState } = event.detail || {};
    if (requestState?.requestType === 'add' && requestState?.responseData?.ok) {
      document.body.classList.remove('overflow-hidden');

      document.querySelectorAll('quick-add-modal').forEach((modal) => {
        modal.removeAttribute('open');
        if (modal.modalContent) {
          modal.modalContent.innerHTML = '';
        }
      });

      this.resetAllSpinners();
    }
  }

  resetAllSpinners() {
    document.querySelectorAll('.quick-add__icon-button').forEach((button) => {
      this.toggleSpinner(button, false);
    });
  }

  setupModal() {
    this.modal = this.querySelector('[role="dialog"]');
    this.modalContent = this.querySelector('[id^="QuickAddInfo-"]');
  }

  bindEvents() {
    this.querySelector('[id^="ModalClose-"]')?.addEventListener('click', () => this.hide());
    this.addEventListener('keyup', (event) => {
      if (event.code.toUpperCase() === 'ESCAPE') this.hide();
    });
    this.addEventListener('click', (event) => {
      if (event.target === this) this.hide();
    });

  }

  show(opener) {
    this.openedBy = opener;

    if (opener && opener.getAttribute('data-product-url')) {
      opener.setAttribute('aria-disabled', true);

      fetch(opener.getAttribute('data-product-url'))
        .then(response => response.text())
        .then(responseText => {
          const productElement = new DOMParser()
            .parseFromString(responseText, 'text/html')
            .querySelector('product-info');

          if (!productElement) {
            console.error('Product info not found in response');
            return;
          }

          this.preprocessContent(productElement);
          this.setContent(productElement.outerHTML);

          document.body.classList.add('overflow-hidden');
          this.setAttribute('open', '');

          this.resetAllSpinners();

          if (window.Shopify?.PaymentButton) Shopify.PaymentButton.init();
          if (window.ProductModel) window.ProductModel.loadShopifyXR();
        })
        .catch(error => {
          console.error('Error loading product:', error);
        })
        .finally(() => {
          opener.removeAttribute('aria-disabled');
        });
    } else {
      // For other modals (like monogram popup) that don't need fetch
      document.body.classList.add('overflow-hidden');
      this.setAttribute('open', '');
    }
  }

  hide() {
    document.body.classList.remove('overflow-hidden');
    this.removeAttribute('open');
    if (this.modalContent) {
      this.modalContent.innerHTML = '';
    }
  }

  preprocessContent(element) {
    const uniqueSectionId = `${element.dataset.section}-modal-${Date.now()}`;
    element.innerHTML = element.innerHTML.replaceAll(element.dataset.section, uniqueSectionId);
    element.dataset.section = uniqueSectionId;
    element.dataset.updateUrl = 'false';
    element.querySelector('pickup-availability')?.remove();
    element.querySelector('script[src*="component-pickup-availability.js"]')?.remove();
    element.querySelector('product-media-modal')?.remove();
    element.querySelector('script[src*="component-product-media-modal.js"]')?.remove();
    element.querySelector('product-recommendations')?.remove();
    element.querySelector('script[src*="product-recommendations.js"]')?.remove();
  }

  setContent(html) {
    this.modalContent.innerHTML = html;
    // Reinject scripts
    this.modalContent.querySelectorAll('script').forEach(oldScript => {
      const newScript = document.createElement('script');
      Array.from(oldScript.attributes).forEach(attr => {
        newScript.setAttribute(attr.name, attr.value);
      });
      newScript.textContent = oldScript.textContent;
      oldScript.parentNode.replaceChild(newScript, oldScript);
    });
  }

}

if (!customElements.get('quick-add-modal')) {
  customElements.define('quick-add-modal', QuickAdd);
}

