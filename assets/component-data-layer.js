export class DataLayer extends HTMLElement {
  constructor() {
    super();
    this.onCartRequestEnd = this.onCartRequestEnd.bind(this);
    this.trackViewItem = this.trackViewItem.bind(this);
    this.onProductClick = this.onProductClick.bind(this);
  }

  connectedCallback() {
    window.dataLayer = window.dataLayer || [];

    // add_to_cart: Track successful cart additions
    document.addEventListener('liquid-ajax-cart:request-end', this.onCartRequestEnd);

    // view_item: Track product page views
    if (this.dataset.template === 'product') {
      this.trackViewItem();
    }

    // select_item: Track product clicks
    document.addEventListener('click', this.onProductClick);
  }

  disconnectedCallback() {
    document.removeEventListener('liquid-ajax-cart:request-end', this.onCartRequestEnd);
    document.removeEventListener('click', this.onProductClick);
  }

  // =========================================================================
  // Helper Methods
  // =========================================================================

  pushToDataLayer(data) {
    window.dataLayer.push({ ecommerce: null });
    window.dataLayer.push(data);
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
      const sectionType =
        section.dataset.sectionType ||
        section.className.match(/section-([^\s]+)/)?.[1] ||
        'product_list';

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

  // =========================================================================
  // Event Handlers
  // =========================================================================

  onCartRequestEnd(event) {
    const { requestState } = event.detail || {};
    if (requestState?.requestType === 'add' && requestState?.responseData?.ok) {
      const productData = this.getProductData();
      const variantData = this.getSelectedVariantData();

      if (!productData || !variantData) {
        // Fallback to basic event if data not available
        this.pushToDataLayer({
          event: 'add_to_cart',
        });
        return;
      }

      const quantity = requestState?.responseData?.quantity || 1;
      const sellingPlanId = requestState?.responseData?.selling_plan_allocation?.selling_plan?.id || null;

      const item = this.formatGA4Item(productData, variantData, quantity, sellingPlanId);

      this.pushToDataLayer({
        event: 'add_to_cart',
        ecommerce: {
          currency: window.Shopify?.currency?.active || 'USD',
          value: item.price * quantity,
          items: [item],
        },
      });
    }
  }

  trackViewItem() {
    const productData = this.getProductData();
    const variantData = this.getSelectedVariantData();

    if (!productData || !variantData) {
      console.error('DataLayer: view_item - Missing product or variant data');
      return;
    }

    const item = this.formatGA4Item(productData, variantData);

    this.pushToDataLayer({
      event: 'view_item',
      ecommerce: {
        currency: window.Shopify?.currency?.active || 'USD',
        value: item.price,
        items: [item],
      },
    });
  }

  onProductClick(event) {
    const productCard = event.target.closest('product-card, .product-card');
    if (!productCard) {
      return;
    }

    const link = event.target.closest('a[href*="/products/"]');
    if (!link) {
      return;
    }

    // Skip quick-buy buttons (they trigger add_to_cart instead)
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

      this.pushToDataLayer({
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

if (!customElements.get('data-layer')) {
  customElements.define('data-layer', DataLayer);
}
