export class QuickAdd extends HTMLElement {
  constructor() {
    super();
    this.modal = null;
    this.modalContent = null;
    this.setupModal();
    this.bindEvents();
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
      document.body.classList.remove('overflow-hidden');

      document.querySelectorAll('quick-add-modal').forEach((modal) => {
        modal.removeAttribute('open');
        modal.modalContent.innerHTML = '';
      });
    }
  }

  setupModal() {
    this.modal = this.querySelector('[role="dialog"]');
    this.modalContent = this.querySelector('[id^="QuickAddInfo-"]');
    document.body.appendChild(this);
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

    // Only set aria-disabled and show spinner if it's a quick-add operation
    // with a loading spinner element
    if (opener && opener.querySelector('.loading__spinner')) {
      opener.setAttribute('aria-disabled', true);
      opener.querySelector('.loading__spinner').classList.remove('hidden');

      fetch(opener.getAttribute('data-product-url'))
        .then(response => response.text())
        .then(responseText => {
          const productElement = new DOMParser()
            .parseFromString(responseText, 'text/html')
            .querySelector('product-info');

          this.preprocessContent(productElement);
          this.setContent(productElement.outerHTML);

          document.body.classList.add('overflow-hidden');
          this.setAttribute('open', '');

          if (window.Shopify?.PaymentButton) Shopify.PaymentButton.init();
          if (window.ProductModel) window.ProductModel.loadShopifyXR();
        })
        .finally(() => {
          opener.removeAttribute('aria-disabled');
          opener.querySelector('.loading__spinner').classList.add('hidden');
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
    this.modalContent.innerHTML = '';
  }

  preprocessContent(element) {
    const uniqueSectionId = `${element.dataset.section}-modal-${Date.now()}`;
    element.innerHTML = element.innerHTML.replaceAll(element.dataset.section, uniqueSectionId);
    element.dataset.section = uniqueSectionId;
    element.dataset.updateUrl = 'false';
    element.querySelector('pickup-availability')?.remove();
    element.querySelector('script[src*="component-pickup-availability.js"]')?.remove();
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

