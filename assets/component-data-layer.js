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

  /**
   * Get list context from section element or URL
   */
  static getListContext(element) {
    const section = element.closest('section, [data-section-type], [data-item-list-id]');

    if (section) {
      // Prefer explicit data attributes
      if (section.dataset.itemListId && section.dataset.itemListName) {
        return {
          id: section.dataset.itemListId,
          name: section.dataset.itemListName,
        };
      }

      // Fallback to section-based detection
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

    // Check if on collection page
    if (window.location.pathname.includes('/collections/')) {
      const collectionMatch = window.location.pathname.match(/\/collections\/([^\/\?#]+)/);
      const collectionHandle = collectionMatch ? collectionMatch[1] : 'unknown';
      return {
        id: `collection_${collectionHandle}`,
        name: 'Collection',
      };
    }

    // Check for homepage
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
      const listContext = DataLayerUtility.getListContext(productCard);

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
 * EVENT COMPONENT: VIEW ITEM LIST
 * ============================================================================
 */
class DataLayerViewItemList extends HTMLElement {
  constructor() {
    super();
    this.observer = null;
    this.mutationObserver = null;

    // Define selectors in one place to prevent mismatch bugs
    this.listSelectors = ['.product-grid', 'ul.grid', '[data-product-list]'];
  }

  connectedCallback() {
    this.initializeObserver();
    this.observeProductLists();
    this.setupMutationObserver();
  }

  disconnectedCallback() {
    // Disconnect IntersectionObserver
    if (this.observer) {
      this.observer.disconnect();
      this.observer = null;
    }

    // Disconnect MutationObserver
    if (this.mutationObserver) {
      this.mutationObserver.disconnect();
      this.mutationObserver = null;
    }
  }

  initializeObserver() {
    // Check if IntersectionObserver is supported
    if (!('IntersectionObserver' in window)) {
      return;
    }

    // Create IntersectionObserver with 10% threshold
    this.observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          // Check if element is intersecting and hasn't been tracked yet
          if (entry.isIntersecting && !entry.target.hasAttribute('data-gtm-list-viewed')) {
            // Mark as viewed to prevent duplicate tracking
            entry.target.setAttribute('data-gtm-list-viewed', 'true');

            // Track the view_item_list event
            this.trackViewItemList(entry.target);

            // Stop observing this element
            this.observer.unobserve(entry.target);
          }
        });
      },
      {
        threshold: 0.1, // Trigger when 10% of the list is visible
        rootMargin: '0px',
      },
    );
  }

  observeProductLists() {
    if (!this.observer) {
      return;
    }

    // Select all potential product list containers
    const productLists = document.querySelectorAll(this.listSelectors.join(', '));

    productLists.forEach((list) => {
      // Only observe if list has products and hasn't been observed yet
      const hasProducts = list.querySelectorAll('[data-product-item-data]').length > 0;
      const notYetObserved = !list.hasAttribute('data-gtm-observer-attached');

      if (hasProducts && notYetObserved) {
        list.setAttribute('data-gtm-observer-attached', 'true');
        this.observer.observe(list);
      }
    });
  }

  setupMutationObserver() {
    // Check if MutationObserver is supported
    if (!('MutationObserver' in window)) {
      return;
    }

    // Create MutationObserver to watch for dynamically loaded content
    this.mutationObserver = new MutationObserver((mutations) => {
      let shouldReobserve = false;

      mutations.forEach((mutation) => {
        // Check if new nodes were added
        if (mutation.addedNodes.length > 0) {
          mutation.addedNodes.forEach((node) => {
            // Check if the added node is an element and contains product lists
            if (node.nodeType === 1) {
              // Check if the added node matches any of the list selectors
              const isMatch = this.listSelectors.some((selector) => node.matches(selector) || node.querySelector(selector));

              // If the added node matches any of the list selectors, re-observe the product lists
              if (isMatch) {
                shouldReobserve = true;
              }
            }
          });
        }
      });

      // Re-scan for product lists if new content was added
      if (shouldReobserve) {
        this.observeProductLists();
      }
    });

    const targetNode = document.getElementById('MainContent') || document.body;

    // Start observing the document for changes
    this.mutationObserver.observe(targetNode, {
      childList: true,
      subtree: true,
    });
  }

  getProductListItems(listElement) {
    const productCards = listElement.querySelectorAll('[data-product-item-data]');
    return Array.from(productCards)
      .map((card) => {
        try {
          return JSON.parse(card.innerHTML);
        } catch (e) {
          console.error('DataLayer: Failed to parse product item', e);
          return null;
        }
      })
      .filter(Boolean);
  }

  trackViewItemList(listElement) {
    const listContext = DataLayerUtility.getListContext(listElement);

    // Get all product items in the list
    const items = this.getProductListItems(listElement);

    if (items.length === 0) {
      console.error('DataLayer: view_item_list - No valid product data found');
      return;
    }

    // Push to dataLayer
    DataLayerUtility.pushToDataLayer({
      event: 'view_item_list',
      ecommerce: {
        currency: window.Shopify?.currency?.active || 'USD',
        item_list_id: listContext.id,
        item_list_name: listContext.name,
        items: items,
      },
    });
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
    // Skip form inputs (radio, checkbox, input, select, etc.)
    if (event.target.tagName === 'INPUT' || event.target.tagName === 'SELECT' || event.target.tagName === 'TEXTAREA') {
      return;
    }

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
      button.type === 'submit' ||
      (button.href && button.href.includes('/cart')) ||
      (button.href && button.href.includes('/checkout'))
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
    this.onCartClick = this.onCartClick.bind(this);
  }

  connectedCallback() {
    document.addEventListener('click', this.onCartClick);
  }

  disconnectedCallback() {
    document.removeEventListener('click', this.onCartClick);
  }

  onCartClick(event) {
    const cartTrigger = event.target.closest('#header-cart-bubble, [data-cart-trigger], .cart-trigger');
    if (cartTrigger) {
      setTimeout(this.trackViewCart.bind(this), 100);
    }
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
 * EVENT COMPONENT: PRODUCT OPTION SELECTED
 * ============================================================================
 */
class DataLayerProductOption extends HTMLElement {
  constructor() {
    super();
    this.onOptionChange = this.onOptionChange.bind(this);
  }

  connectedCallback() {
    document.addEventListener('change', this.onOptionChange);
  }

  disconnectedCallback() {
    document.removeEventListener('change', this.onOptionChange);
  }

  onOptionChange(event) {
    // Check if change event is from variant-selector
    const variantSelector = event.target.closest('variant-selector');
    if (!variantSelector) {
      return;
    }

    // Determine picker type and extract option data
    const pickerType = variantSelector.dataset.pickerType;
    let optionName, optionValue;

    if (pickerType === 'button') {
      // Extract from radio input
      const input = event.target;
      if (input.type !== 'radio' || !input.checked) {
        return;
      }

      const fieldset = input.closest('fieldset');
      const legend = fieldset?.querySelector('legend');
      optionName = legend?.textContent?.trim() || '';
      optionValue = input.value;
    }

    if (!optionName || !optionValue) {
      return;
    }

    // Get product context
    const productData = DataLayerUtility.getProductData();
    const variantData = DataLayerUtility.getSelectedVariantData();

    if (!productData) {
      return;
    }

    // Push to data layer
    DataLayerUtility.pushToDataLayer({
      event: 'product_option_selected',
      option_name: optionName,
      option_value: optionValue,
      product_id: productData.id?.toString(),
      product_name: productData.title,
      variant_id: variantData?.id?.toString() || '',
      variant_sku: variantData?.sku || '',
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
      DataLayerUtility.pushToDataLayer({
        event: 'search',
        search_term: searchTerm,
      });
    }
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
 * EVENT COMPONENT: SELECT CONTENT
 * ============================================================================
 */
class DataLayerSelectContent extends HTMLElement {
  constructor() {
    super();
    this.onClick = this.onClick.bind(this);
    this.onChange = this.onChange.bind(this);
  }

  connectedCallback() {
    document.addEventListener('click', this.onClick);
    document.addEventListener('change', this.onChange);
  }

  disconnectedCallback() {
    document.removeEventListener('click', this.onClick);
    document.removeEventListener('change', this.onChange);
  }

  onClick(event) {
    // Find element with data-track-content-type
    const element = event.target.closest('[data-track-content-type]');
    if (!element) {
      return;
    }

    // Skip select elements (handled by onChange)
    if (element.tagName === 'SELECT') {
      return;
    }

    // Extract content_type and item_id from data attributes
    const contentType = element.dataset.trackContentType;
    const itemId = element.dataset.trackItemId;
    const itemName = element.dataset.trackItemName || element.textContent?.trim();

    // Validate required attributes
    if (!contentType || !itemId) {
      console.warn('DataLayer: select_content - Missing required data attributes');
      return;
    }

    // Push to dataLayer
    DataLayerUtility.pushToDataLayer({
      event: 'select_content',
      content_type: contentType,
      item_id: itemId,
      item_name: itemName,
    });
  }

  onChange(event) {
    // Handle change events on select elements with data-track-content-type="sort"
    const select = event.target.closest('select[data-track-content-type="sort"]');
    if (!select) {
      return;
    }

    const selectedOption = select.options[select.selectedIndex];
    const itemId = selectedOption.dataset.trackItemId || select.value;
    const itemName = selectedOption.dataset.trackItemName || selectedOption.textContent?.trim();

    // Validate required attributes
    if (!itemId) {
      console.warn('DataLayer: select_content - Missing required data attributes on sort select');
      return;
    }

    // Push to dataLayer
    DataLayerUtility.pushToDataLayer({
      event: 'select_content',
      content_type: 'sort',
      item_id: itemId,
      item_name: itemName,
    });
  }
}

/**
 * ============================================================================
 * EVENT COMPONENT: LOGIN
 * ============================================================================
 */
class DataLayerLogin extends HTMLElement {
  constructor() {
    super();
    this.handleLoginSubmit = this.handleLoginSubmit.bind(this);
  }

  connectedCallback() {
    this.checkForRecentLogin();

    const loginForm = document.querySelector('form[action*="/account/login"]');
    if (loginForm) {
      loginForm.addEventListener('submit', this.handleLoginSubmit);
    }
  }

  disconnectedCallback() {
    const loginForm = document.querySelector('form[action*="/account/login"]');
    if (loginForm) {
      loginForm.removeEventListener('submit', this.handleLoginSubmit);
    }
  }

  handleLoginSubmit(event) {
    const loginForm = event.target;

    if (!loginForm.action?.includes('/account/login') || !loginForm.querySelector('input[name="customer[email]"]')) {
      return;
    }

    const emailInput = loginForm.querySelector('#CustomerEmail');
    const email = emailInput ? emailInput.value : '';

    try {
      sessionStorage.setItem('login_provider', 'email');
      sessionStorage.setItem('login_email', email);
      sessionStorage.setItem('login_timestamp', new Date().toISOString());
      sessionStorage.setItem('just_logged_in', 'true');
    } catch (error) {
      console.error('DataLayer: Failed to set login tracking flags', error);
    }
  }

  checkForRecentLogin() {
    // Check sessionStorage for just_logged_in flag
    const justLoggedIn = sessionStorage.getItem('just_logged_in');
    const loginProvider = sessionStorage.getItem('login_provider') || 'email';
    const loginEmail = sessionStorage.getItem('login_email');

    if (justLoggedIn === 'true') {
      this.handleSuccessfulLogin(loginProvider, loginEmail);

      // Clear flags after tracking
      sessionStorage.removeItem('just_logged_in');
      sessionStorage.removeItem('login_timestamp');
      sessionStorage.removeItem('login_provider');
      sessionStorage.removeItem('login_email');
    }
  }

  handleSuccessfulLogin(loginProvider, loginEmail) {
    DataLayerUtility.pushToDataLayer({
      event: 'login',
      method: loginProvider || 'email',
      customer_email: loginEmail,
      timestamp: new Date().toISOString(),
    });
  }
}

/**
 * ============================================================================
 * EVENT COMPONENT: SIGN UP
 * ============================================================================
 */
class DataLayerSignUp extends HTMLElement {
  constructor() {
    super();
    this.handleSignupSubmit = this.handleSignupSubmit.bind(this);
  }

  connectedCallback() {
    document.addEventListener('submit', this.handleSignupSubmit);
    this.checkForRecentSignup();
  }

  disconnectedCallback() {
    document.removeEventListener('submit', this.handleSignupSubmit);
  }

  handleSignupSubmit(event) {
    const form = event.target;

    if (!form.action?.includes('/account') || !form.querySelector('input[name="customer[email]"]')) {
      return;
    }

    const firstNameInput = form.querySelector('#RegisterForm-FirstName');
    const emailInput = form.querySelector('#RegisterForm-email');

    const firstName = firstNameInput ? firstNameInput.value : '';
    const email = emailInput ? emailInput.value : '';

    if (!email) {
      return;
    }

    sessionStorage.setItem('just_signed_up', 'true');
    sessionStorage.setItem('signup_email', email);
    sessionStorage.setItem('signup_first_name', firstName);
  }

  checkForRecentSignup() {
    const justSignedUp = sessionStorage.getItem('just_signed_up');
    const signupEmail = sessionStorage.getItem('signup_email');
    const signupFirstName = sessionStorage.getItem('signup_first_name');

    if (justSignedUp === 'true') {
      this.handleSuccessfulSignup(signupEmail, signupFirstName);

      // Clear flags after tracking
      sessionStorage.removeItem('just_signed_up');
      sessionStorage.removeItem('signup_timestamp');
      sessionStorage.removeItem('signup_email');
      sessionStorage.removeItem('signup_first_name');
    }
  }

  handleSuccessfulSignup(signupEmail, signupFirstName) {
    DataLayerUtility.pushToDataLayer({
      event: 'sign_up',
      method: 'email',
      customer_id: window.customer?.id,
      customer_email: window.customer?.email || signupEmail,
      customer_name: window.customer?.name || signupFirstName,
      timestamp: new Date().toISOString(),
    });
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
  'data-layer-view-item-list': DataLayerViewItemList,
  'data-layer-add-to-cart': DataLayerAddToCart,
  'data-layer-view-cart': DataLayerViewCart,
  'data-layer-remove-from-cart': DataLayerRemoveFromCart,
  // Cart Operations
  'data-layer-update-cart': DataLayerUpdateCart,
  // User Engagement Events
  'data-layer-cta-click': DataLayerCtaClick,
  'data-layer-faq-toggle': DataLayerFaqToggle,
  'data-layer-search': DataLayerSearch,
  'data-layer-select-content': DataLayerSelectContent,
  'data-layer-carousel': DataLayerCarousel,
  'data-layer-product-option': DataLayerProductOption,
  // Authentication Events
  'data-layer-login': DataLayerLogin,
  'data-layer-sign-up': DataLayerSignUp,
  // System & Status Events
  'data-layer-error-404': DataLayerError404,
  'data-layer-out-of-stock': DataLayerOutOfStock,
};

Object.entries(dataLayerComponents).forEach(([tagName, componentClass]) => {
  if (!customElements.get(tagName)) {
    customElements.define(tagName, componentClass);
  }
});
