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
    window.dataLayer.push({ ecommerce: null }); // Clear previous ecommerce object
    window.dataLayer.push(data);
  }

  /**
   * Get product data from DOM
   */
  static getProductData() {
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

  /**
   * Get selected variant data from DOM
   */
  static getSelectedVariantData() {
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
    this.trackViewItem();
  }

  formatGA4Item(productData, variantData, quantity = 1, sellingPlanId = null) {
    const item = {
      item_id: variantData.sku || variantData.id.toString(),
      item_name: productData.title,
      item_brand: productData.vendor,
      item_category: productData.type,
      item_variant: variantData.title,
      price: variantData.price / 100,
      quantity: quantity,
    };

    if (sellingPlanId) {
      item.selling_plan_id = sellingPlanId;
      item.purchase_type = 'subscription';
    } else {
      item.purchase_type = 'one-time';
    }

    return item;
  }

  trackViewItem() {
    const productData = DataLayerUtility.getProductData();
    const variantData = DataLayerUtility.getSelectedVariantData();

    if (!productData || !variantData) {
      console.error('DataLayer: view_item - Missing product or variant data');
      return;
    }

    const item = this.formatGA4Item(productData, variantData, 1);

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

    // Skip carousel navigation buttons (handled by carousel component)
    if (button.classList.contains('swiper-button-next') || button.classList.contains('swiper-button-prev') || button.closest('.swiper')) {
      return;
    }

    // Skip product-related buttons (handled by other components)
    if (
      button.closest('product-card') ||
      button.closest('.quick-add') ||
      button.closest('form[action*="/cart"]') ||
      button.closest('ajax-cart-product-form') ||
      button.closest('ajax-cart-quantity') ||
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
    this.trackOutOfStock();
  }

  trackOutOfStock() {
    const productData = DataLayerUtility.getProductData();
    const variantData = DataLayerUtility.getSelectedVariantData();

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
}

/**
 * ============================================================================
 * EVENT COMPONENT: VIEW CART
 * ============================================================================
 */
class DataLayerViewCart extends HTMLElement {
  constructor() {
    super();
  }

  connectedCallback() {
    // Track cart page loads
    if (window.location.pathname.includes('/cart')) {
      this.trackViewCart();
    }

    // Listen for clicks on cart icon/button
    this.setupCartIconListener();
  }

  setupCartIconListener() {
    document.addEventListener('click', (event) => {
      const cartTrigger = event.target.closest('#header-cart-bubble, [data-cart-trigger], .cart-trigger');
      if (cartTrigger) {
        setTimeout(() => {
          this.trackViewCart();
        }, 100);
      }
    });
  }

  formatCartItems(cartState) {
    if (!cartState?.items) {
      return [];
    }

    return cartState.items.map((item) => ({
      item_id: item.sku || item.id.toString(),
      item_name: item.product_title,
      item_brand: item.vendor,
      item_category: item.product_type,
      item_variant: item.variant_title,
      price: item.price / 100,
      quantity: item.quantity,
    }));
  }

  trackViewCart() {
    const cartState = window.liquidAjaxCart?.cart;

    if (!cartState || !cartState.items || cartState.item_count === 0) {
      return;
    }

    const items = this.formatCartItems(cartState);
    const cartValue = cartState.total_price / 100;

    DataLayerUtility.pushToDataLayer({
      event: 'view_cart',
      ecommerce: {
        currency: window.Shopify?.currency?.active || 'USD',
        value: cartValue,
        items: items,
      },
    });
  }
}

/**
 * ============================================================================
 * EVENT COMPONENT: REMOVE FROM CART
 * ============================================================================
 */
class DataLayerRemoveFromCart extends HTMLElement {
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

    // Only track change requests that result in removals
    if (requestState?.requestType !== 'change' || !requestState?.responseData?.ok) {
      return;
    }

    const removedItems = requestState.responseData.body?.items_removed;
    const currentCartItems = requestState.responseData.body?.items;

    // Only proceed if there are items removed
    if (!removedItems || removedItems.length === 0) {
      return;
    }

    // Filter to only items that are COMPLETELY removed (not in the current cart)
    const completelyRemovedItems = removedItems.filter((removedItem) => {
      // Check if this item still exists in the cart
      const stillInCart = currentCartItems?.some(
        (cartItem) => cartItem.variant_id === removedItem.variant_id || cartItem.key === removedItem.view_key,
      );
      // Only include if NOT still in cart (completely removed)
      return !stillInCart;
    });

    if (completelyRemovedItems.length > 0) {
      this.trackRemoveFromCart(completelyRemovedItems);
    }
  }

  trackRemoveFromCart(removedItems) {
    let totalRemovedValue = 0;
    const itemsForGA4 = removedItems.map((item) => {
      const itemPrice = parseFloat(item.price) || 0;
      totalRemovedValue += itemPrice * item.quantity;

      return {
        item_id: item.sku || item.variant_id?.toString(),
        item_name: item.product_title,
        item_variant: item.variant_title,
        item_brand: item.vendor,
        price: itemPrice,
        quantity: item.quantity,
        item_category: item.product_type,
      };
    });

    DataLayerUtility.pushToDataLayer({
      event: 'remove_from_cart',
      ecommerce: {
        currency: window.Shopify?.currency?.active || 'USD',
        value: totalRemovedValue,
        items: itemsForGA4,
      },
    });
  }
}

/**
 * ============================================================================
 * EVENT COMPONENT: UPDATE CART
 * ============================================================================
 */
class DataLayerUpdateCart extends HTMLElement {
  constructor() {
    super();
    this.onCartRequestEnd = this.onCartRequestEnd.bind(this);
    this.cartStateBeforeUpdate = null;
  }

  connectedCallback() {
    document.addEventListener('liquid-ajax-cart:request-start', (event) => {
      const { requestState } = event.detail || {};
      if (requestState?.requestType === 'change') {
        this.cartStateBeforeUpdate = window.liquidAjaxCart?.cart;
      }
    });

    document.addEventListener('liquid-ajax-cart:request-end', this.onCartRequestEnd);
  }

  disconnectedCallback() {
    document.removeEventListener('liquid-ajax-cart:request-end', this.onCartRequestEnd);
  }

  onCartRequestEnd(event) {
    const { requestState } = event.detail || {};

    // Only track change requests
    if (requestState?.requestType !== 'change' || !requestState?.responseData?.ok) {
      return;
    }

    // Get updated items from response
    const updatedItems = requestState.responseData.body?.items;

    // If there are no updated items or the previous cart state is not available, return
    if (!updatedItems || !this.cartStateBeforeUpdate?.items) {
      return;
    }

    // Compare previous cart state with current state to find quantity changes
    updatedItems.forEach((currentItem) => {
      const previousItem = this.cartStateBeforeUpdate.items.find(
        (prev) => prev.key === currentItem.key || prev.variant_id === currentItem.variant_id,
      );

      // If item exists in previous state and quantity changed
      if (previousItem && previousItem.quantity !== currentItem.quantity) {
        DataLayerUtility.pushToDataLayer({
          event: 'update_cart',
          item_id: currentItem.sku || currentItem.variant_id?.toString(),
          item_name: currentItem.product_title,
          previous_quantity: previousItem.quantity,
          new_quantity: currentItem.quantity,
        });
      }
    });
  }
}

/**
 * ============================================================================
 * EVENT COMPONENT: SEARCH
 * ============================================================================
 */
class DataLayerSearch extends HTMLElement {
  constructor() {
    super();
    this.onSearchSubmit = this.onSearchSubmit.bind(this);
  }

  connectedCallback() {
    // Track search form submissions
    document.addEventListener('submit', this.onSearchSubmit);

    // Track search page loads with query parameter
    if (window.location.pathname.includes('/search')) {
      this.trackSearchFromUrl();
    }
  }

  disconnectedCallback() {
    document.removeEventListener('submit', this.onSearchSubmit);
  }

  onSearchSubmit(event) {
    const form = event.target;

    // Check if it's a search form
    if (!form.action?.includes('/search') && !form.querySelector('input[name="q"]') && !form.classList.contains('search')) {
      return;
    }

    const searchInput = form.querySelector('input[name="q"], input[type="search"]');
    if (!searchInput) {
      return;
    }

    const searchTerm = searchInput.value?.trim();
    if (searchTerm) {
      this.trackSearch(searchTerm);
    }
  }

  trackSearchFromUrl() {
    const urlParams = new URLSearchParams(window.location.search);
    const searchTerm = urlParams.get('q');

    if (searchTerm) {
      this.trackSearch(searchTerm);
    }
  }

  trackSearch(searchTerm) {
    DataLayerUtility.pushToDataLayer({
      event: 'search',
      search_term: searchTerm,
    });
  }
}

/**
 * ============================================================================
 * EVENT COMPONENT: CAROUSEL INTERACTION
 * ============================================================================
 */
class DataLayerCarousel extends HTMLElement {
  constructor() {
    super();
    this.onCarouselClick = this.onCarouselClick.bind(this);
  }

  connectedCallback() {
    document.addEventListener('click', this.onCarouselClick);
  }

  disconnectedCallback() {
    document.removeEventListener('click', this.onCarouselClick);
  }

  onCarouselClick(event) {
    // Support Swiper's div[role="button"] navigation buttons
    const button = event.target.closest('div[role="button"]');
    if (!button) {
      return;
    }

    // Check for Swiper navigation buttons
    const isSwiperNext = button.classList.contains('swiper-button-next');
    const isSwiperPrev = button.classList.contains('swiper-button-prev');

    if (!isSwiperNext && !isSwiperPrev) {
      return;
    }

    // Check if button is inside a swiper container
    const swiperContainer = button.closest('.swiper');

    if (swiperContainer) {
      const carouselId = swiperContainer.id || swiperContainer.dataset.carouselId || 'swiper';
      const slideDirection = isSwiperPrev ? 'previous' : 'next';

      DataLayerUtility.pushToDataLayer({
        event: 'carousel_interaction',
        interaction_type: 'arrow_click',
        slide_direction: slideDirection,
        carousel_id: carouselId,
      });
    }
  }
}

/**
 * ============================================================================
 * COMPONENT REGISTRATION
 * ============================================================================
 */

const dataLayerComponents = {
  'data-layer': DataLayer, // Register parent first
  // Core E-commerce Events
  'data-layer-select-item': DataLayerSelectItem,
  'data-layer-view-item': DataLayerViewItem,
  'data-layer-add-to-cart': DataLayerAddToCart,
  'data-layer-view-cart': DataLayerViewCart,
  'data-layer-remove-from-cart': DataLayerRemoveFromCart,
  // Cart Operations
  'data-layer-update-cart': DataLayerUpdateCart,
  // User Engagement Events
  'data-layer-cta-click': DataLayerCtaClick,
  'data-layer-faq-toggle': DataLayerFaqToggle,
  'data-layer-search': DataLayerSearch,
  'data-layer-carousel': DataLayerCarousel,
  // System & Status Events
  'data-layer-error-404': DataLayerError404,
  'data-layer-out-of-stock': DataLayerOutOfStock,
};

Object.entries(dataLayerComponents).forEach(([tagName, componentClass]) => {
  if (!customElements.get(tagName)) {
    customElements.define(tagName, componentClass);
  }
});
