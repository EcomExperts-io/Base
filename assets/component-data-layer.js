/**
 * ============================================================================
 * DATA LAYER UTILITY CLASS
 * ============================================================================
 */
class DataLayerUtility {
  /**
   * Push to dataLayer with ecommerce reset
   */
  static pushToDataLayer(data) {
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({ ecommerce: null }); // Clear previous ecommerce object
    window.dataLayer.push(data);
  }
}

/**
 * ============================================================================
 * DATA LAYER PARENT COMPONENT
 * ============================================================================
 */
class DataLayer extends HTMLElement {
  connectedCallback() {
    // Initialize global dataLayer array once when component mounts
    window.dataLayer = window.dataLayer || [];
  }
}

/**
 * ============================================================================
 * EVENT COMPONENT: SELECT ITEM
 * ============================================================================
 */
class DataLayerSelectItem extends HTMLElement {
  constructor() {
    super();
    this.onProductClick = this.onProductClick.bind(this);
  }

  connectedCallback() {
    document.addEventListener('click', this.onProductClick);
  }

  disconnectedCallback() {
    document.removeEventListener('click', this.onProductClick);
  }

  getListContext(element) {
    const section = element.closest('section, [data-section-type], [data-item-list-id]');
    if (section) {
      if (section.dataset.itemListId && section.dataset.itemListName) {
        return {
          id: section.dataset.itemListId,
          name: section.dataset.itemListName,
        };
      }

      const sectionId = section.id || section.dataset.sectionId || 'unknown';
      const sectionType = section.dataset.sectionType || section.className.match(/section-([^\s]+)/)?.[1] || 'product_list';

      return {
        id: sectionId,
        name: sectionType
          .replace(/_/g, ' ')
          .replace(/-/g, ' ')
          .replace(/\b\w/g, (l) => l.toUpperCase()),
      };
    }

    if (window.location.pathname.includes('/collections/')) {
      const collectionMatch = window.location.pathname.match(/\/collections\/([^\/\?#]+)/);
      const collectionHandle = collectionMatch ? collectionMatch[1] : 'unknown';
      return {
        id: `collection_${collectionHandle}`,
        name: 'Collection',
      };
    }

    if (window.location.pathname === '/') {
      return {
        id: 'homepage',
        name: 'Homepage',
      };
    }

    return {
      id: 'unknown',
      name: 'Product List',
    };
  }

  onProductClick(event) {
    const productCard = event.target.closest('product-card, .product-card');
    if (!productCard) {
      return;
    }

    // Get the link to the product page to check if it's a product page to trigger select_item
    const link = event.target.closest('a[href*="/products/"]');
    if (!link) {
      return;
    }

    // Skip quick-buy buttons (they trigger add_to_cart instead of select_item)
    if (link.closest('.quick-add') || link.closest('form')) {
      return;
    }

    const dataElement = productCard.querySelector('[data-product-item-data]');
    if (!dataElement) {
      return;
    }

    try {
      const itemData = JSON.parse(dataElement.innerHTML);
      const listContext = this.getListContext(productCard);

      DataLayerUtility.pushToDataLayer({
        event: 'select_item',
        ecommerce: {
          item_list_id: listContext.id,
          item_list_name: listContext.name,
          items: [itemData],
        },
      });
    } catch (e) {
      console.error('DataLayer: Failed to parse product item data', e);
    }
  }
}

/**
 * ============================================================================
 * EVENT COMPONENT: VIEW ITEM
 * ============================================================================
 */
class DataLayerViewItem extends HTMLElement {
  connectedCallback() {
    // Get parent data-layer element to check template
    const parentDataLayer = this.closest('data-layer');
    if (!parentDataLayer || parentDataLayer.dataset.template !== 'product') {
      return;
    }

    this.trackViewItem();
  }

  getProductData() {
    const productElement = document.querySelector('[data-product]');
    if (!productElement) {
      return null;
    }

    try {
      return JSON.parse(productElement.innerHTML);
    } catch (e) {
      console.error('DataLayer: Failed to parse product data', e);
      return null;
    }
  }

  getSelectedVariantData() {
    const variantElement = document.querySelector('[data-selected-variant]');
    if (!variantElement) {
      return null;
    }

    try {
      return JSON.parse(variantElement.innerHTML);
    } catch (e) {
      console.error('DataLayer: Failed to parse variant data', e);
      return null;
    }
  }

  formatGA4ViewItem(productData, variantData) {
    return {
      item_id: variantData.sku || variantData.id.toString(),
      item_name: productData.title,
      item_brand: productData.vendor,
      item_category: productData.type,
      item_variant: variantData.title,
      price: variantData.price / 100,
      quantity: 1,
    };
  }

  trackViewItem() {
    const productData = this.getProductData();
    const variantData = this.getSelectedVariantData();

    if (!productData || !variantData) {
      console.error('DataLayer: view_item - Missing product or variant data');
      return;
    }

    const item = this.formatGA4ViewItem(productData, variantData);

    DataLayerUtility.pushToDataLayer({
      event: 'view_item',
      ecommerce: {
        currency: window.Shopify?.currency?.active || 'USD',
        value: item.price,
        items: [item],
      },
    });
  }
}

/**
 * ============================================================================
 * EVENT COMPONENT: ADD TO CART
 * ============================================================================
 */
class DataLayerAddToCart extends HTMLElement {
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

    // Only track successful add requests
    if (requestState?.requestType !== 'add' || !requestState?.responseData?.ok) {
      return;
    }

    const { sku, id, product_title, vendor, product_type, variant_title, price, quantity } = requestState?.responseData?.body;
    const sellingPlanId = requestState?.responseData?.body?.selling_plan_allocation?.selling_plan?.id || null;

    const item = {
      item_id: sku || id.toString(),
      item_name: product_title,
      item_brand: vendor,
      item_category: product_type,
      item_variant: variant_title,
      price: price / 100,
      quantity: quantity,
    };

    if (sellingPlanId) {
      item.selling_plan_id = sellingPlanId;
      item.purchase_type = 'subscription';
    } else {
      item.purchase_type = 'one-time';
    }

    const cartValue = item.price * quantity;

    DataLayerUtility.pushToDataLayer({
      event: 'add_to_cart',
      ecommerce: {
        currency: window.Shopify?.currency?.active || 'USD',
        value: cartValue,
        cart_value_text: `${cartValue.toFixed(2)}`,
        items: [item],
      },
    });
  }
}

/**
 * ============================================================================
 * EVENT COMPONENT: CTA CLICK
 * ============================================================================
 */
class DataLayerCtaClick extends HTMLElement {
  constructor() {
    super();
    this.onButtonClick = this.onButtonClick.bind(this);
  }

  connectedCallback() {
    document.addEventListener('click', this.onButtonClick);
  }

  disconnectedCallback() {
    document.removeEventListener('click', this.onButtonClick);
  }

  onButtonClick(event) {
    // Find the clicked button or link styled as button
    const button = event.target.closest('button, a.button, .button, [class*="button"]');
    if (!button) {
      return;
    }

    // Skip product-related buttons (handled by other components)
    if (
      button.closest('product-card') ||
      button.closest('.quick-add') ||
      button.closest('form[action*="/cart"]') ||
      button.closest('ajax-cart-product-form') ||
      button.type === 'submit'
    ) {
      return;
    }

    // Get button text and URL
    const linkText = button.textContent?.trim();
    const linkUrl = button.href || window.location.href;
    const ctaLocation = this.getCtaLocation(button);

    DataLayerUtility.pushToDataLayer({
      event: 'cta_click',
      link_text: linkText,
      link_url: linkUrl,
      cta_location: ctaLocation,
    });
  }

  getCtaLocation(button) {
    // Try to find section or container context
    const section = button.closest('section, [data-section-type]');
    if (section) {
      const sectionId = section.id || section.dataset.sectionId || 'unknown-section';
      return sectionId;
    }

    // Check for common locations
    if (button.closest('header')) {
      return 'header';
    }
    if (button.closest('footer')) {
      return 'footer';
    }
    if (button.closest('.hero')) {
      return 'hero';
    }
    if (button.closest('.banner')) {
      return 'banner';
    }

    return 'unidentified-cta-location';
  }
}

/**
 * ============================================================================
 * EVENT COMPONENT: FAQ TOGGLE
 * ============================================================================
 */
class DataLayerFaqToggle extends HTMLElement {
  constructor() {
    super();
    this.onSummaryClick = this.onSummaryClick.bind(this);
  }

  connectedCallback() {
    document.addEventListener('click', this.onSummaryClick, true);
  }

  disconnectedCallback() {
    document.removeEventListener('click', this.onSummaryClick, true);
  }

  onSummaryClick(event) {
    const summary = event.target.closest('summary');
    if (!summary) {
      return;
    }

    const details = summary.parentElement;
    if (!details || details.tagName !== 'DETAILS') {
      return;
    }

    const faqQuestion = summary.textContent?.trim() || 'FAQ';

    DataLayerUtility.pushToDataLayer({
      event: 'faq_toggle',
      faq_question: faqQuestion,
    });
  }
}

/**
 * ============================================================================
 * EVENT COMPONENT: ERROR 404
 * ============================================================================
 */
class DataLayerError404 extends HTMLElement {
  connectedCallback() {
    // Check if this is a 404 page
    const parentDataLayer = this.closest('data-layer');
    if (!parentDataLayer || parentDataLayer.dataset.template !== '404') {
      return;
    }

    this.track404();
  }

  track404() {
    DataLayerUtility.pushToDataLayer({
      event: 'error_404',
      page_referrer: document.referrer || 'direct',
      page_location: window.location.href,
    });
  }
}

/**
 * ============================================================================
 * EVENT COMPONENT: OUT OF STOCK VIEW
 * ============================================================================
 */
class DataLayerOutOfStock extends HTMLElement {
  connectedCallback() {
    // Get parent data-layer element to check template
    const parentDataLayer = this.closest('data-layer');
    if (!parentDataLayer || parentDataLayer.dataset.template !== 'product') {
      return;
    }

    this.trackOutOfStock();
  }

  trackOutOfStock() {
    const productData = this.getProductData();
    const variantData = this.getSelectedVariantData();

    if (!productData || !variantData) {
      return;
    }

    if (variantData.available) {
      return;
    }

    DataLayerUtility.pushToDataLayer({
      event: 'out_of_stock_view',
      item_id: variantData.sku || variantData.id.toString(),
      item_name: productData.title,
    });
  }

  getProductData() {
    const productElement = document.querySelector('[data-product]');
    if (!productElement) {
      return null;
    }

    try {
      return JSON.parse(productElement.innerHTML);
    } catch (e) {
      console.error('DataLayer: Failed to parse product data', e);
      return null;
    }
  }

  getSelectedVariantData() {
    const variantElement = document.querySelector('[data-selected-variant]');
    if (!variantElement) {
      return null;
    }

    try {
      return JSON.parse(variantElement.innerHTML);
    } catch (e) {
      console.error('DataLayer: Failed to parse variant data', e);
      return null;
    }
  }
}

/**
 * ============================================================================
 * COMPONENT REGISTRATION
 * ============================================================================
 */

// Always register parent component
if (!customElements.get('data-layer')) {
  customElements.define('data-layer', DataLayer);
}

// Check if select_item component exists in DOM
if (document.querySelector('data-layer-select-item') && !customElements.get('data-layer-select-item')) {
  customElements.define('data-layer-select-item', DataLayerSelectItem);
}

// Check if view_item component exists in DOM
if (document.querySelector('data-layer-view-item') && !customElements.get('data-layer-view-item')) {
  customElements.define('data-layer-view-item', DataLayerViewItem);
}

// Check if add_to_cart component exists in DOM
if (document.querySelector('data-layer-add-to-cart') && !customElements.get('data-layer-add-to-cart')) {
  customElements.define('data-layer-add-to-cart', DataLayerAddToCart);
}

// Check if cta_click component exists in DOM
if (document.querySelector('data-layer-cta-click') && !customElements.get('data-layer-cta-click')) {
  customElements.define('data-layer-cta-click', DataLayerCtaClick);
}

// Check if faq_toggle component exists in DOM
if (document.querySelector('data-layer-faq-toggle') && !customElements.get('data-layer-faq-toggle')) {
  customElements.define('data-layer-faq-toggle', DataLayerFaqToggle);
}

// Check if error_404 component exists in DOM
if (document.querySelector('data-layer-error-404') && !customElements.get('data-layer-error-404')) {
  customElements.define('data-layer-error-404', DataLayerError404);
}

// Check if out_of_stock component exists in DOM
if (document.querySelector('data-layer-out-of-stock') && !customElements.get('data-layer-out-of-stock')) {
  customElements.define('data-layer-out-of-stock', DataLayerOutOfStock);
}
