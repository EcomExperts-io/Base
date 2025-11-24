/**
 * Docs: docs/assets/component-cart-notification.md
 * @extends HTMLElement
 */
export class CartNotification extends HTMLElement {
  /**
   * Sets up button handlers and subscribes to AJAX cart updates.
   */
  constructor() {
    super();
    this.hideNotification = this.hideNotification.bind(this);
    this.querySelector('.cart-notification-continue_shopping').addEventListener('click', () => this.hideNotification());
    this.querySelector('.cart-notification__close').addEventListener('click', () => this.hideNotification());
    document.addEventListener('liquid-ajax-cart:request-end', this.onCartUpdate.bind(this));
  }

  /**
   * Removes listeners when the element detaches from the DOM.
   */
  disconnectedCallback() {
    this.querySelector('.cart-notification-continue_shopping').removeEventListener('click', this.hideNotification);
    this.querySelector('.cart-notification__close').removeEventListener('click', this.hideNotification);
    document.removeEventListener('liquid-ajax-cart:request-end', this.onCartUpdate.bind(this));
  }

  /**
   * Handles Liquid Ajax Cart responses and updates the UI after successful adds.
   * @param {CustomEvent} event - Liquid Ajax Cart completion event.
   */
  onCartUpdate(event) {
    const { requestState } = event.detail;
    if (requestState?.requestType === 'add' && requestState.responseData?.ok) {
      this.updateNotification(requestState.responseData.body)
    }
  }

  /**
   * Renders the latest product info inside the notification drawer.
   * @param {Object} updatedCartNotification - JSON payload returned from the cart request.
   */
  updateNotification(updatedCartNotification) {
    const productElement = this.querySelector('#cart-notification-product');
    const optionsHTML = updatedCartNotification.options_with_values
      .map((option) => `<div class="product-option"><dt>${option.name}: </dt><dd>${option.value}</dd></div>`)
      .join('');

    const productHTML = `
        <div class="cart-notification-product__image">
          <img src="${updatedCartNotification.image}" alt="${updatedCartNotification.featured_image.alt}" width="70" height="70">
        </div>
        <div>
          <p class="caption-with-letter-spacing">Shopify</p>
          <h3 class="cart-notification-product__name h4">${updatedCartNotification.product_title}</h3>
          <dl>${optionsHTML}</dl>
        </div>
      `;

    productElement.innerHTML = productHTML;
    this.showNotification();
  }

  /**
   * Displays the cart notification drawer.
   */
  showNotification() {
    this.querySelector('#cart-notification').classList.add('cart-notification-open');
  }

  /**
   * Hides the cart notification drawer.
   */
  hideNotification() {
    this.querySelector('#cart-notification').classList.remove('cart-notification-open');
  }
}

if (!customElements.get('cart-notification')) {
  customElements.define('cart-notification', CartNotification);
}