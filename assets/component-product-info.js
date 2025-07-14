if (!customElements.get('product-info')) {
  class ProductInfo extends HTMLElement {
    abortController = undefined;

    constructor() {
      super();
    }

    setupEventListeners() {
      this.variantSelector?.addEventListener('change', this.onVariantChange.bind(this));
      if(this.quantitySelector){
        this.quantitySelector.addEventListener('change', this.onQuantitySelectorEvent.bind(this));
        this.quantitySelector.querySelector('button[name="plus"]').addEventListener('click', this.onQuantitySelectorEvent.bind(this));
        this.quantitySelector.querySelector('button[name="minus"]').addEventListener('click', this.onQuantitySelectorEvent.bind(this));
      }
      document.getElementById('swiper-script').addEventListener('load', this.initSwiper.bind(this));
      document.addEventListener('liquid-ajax-cart:request-end', this.onCartUpdate.bind(this));
    }

    connectedCallback() {
      this.setupEventListeners();
      if (typeof Swiper !== 'undefined') {
        this.initSwiper();
      }
    }

    initSwiper() {
      const thumbsSwiperEl = this.querySelector('.thumbs-gallery');
      const mainSwiperEl = this.querySelector('.main-gallery');
      
      // Initialize thumbnail swiper if it exists
      if (thumbsSwiperEl) {
        this.thumbsSwiper = new Swiper(thumbsSwiperEl, {
          spaceBetween: 15,
          slidesPerView: 5,
          freeMode: false,
          watchSlidesProgress: true,
          slideToClickedSlide: true,
          simulateTouch: true,
          breakpoints: {
            600: { slidesPerView: 6 },
            900: { slidesPerView: 6 }
          }
        });
      }

      // Initialize main swiper with thumbnail support if available
      if (mainSwiperEl) {
        this.swiper = new Swiper(mainSwiperEl, {
          slidesPerView: 1,
          spaceBetween: 10,
          
          thumbs: this.thumbsSwiper ? {
            swiper: this.thumbsSwiper,
          } : undefined,
          simulateTouch: true,
        });
      } else {
        // Fallback to original swiper initialization if no main-gallery
        this.swiper = new Swiper('.swiper', {
          autoHeight: true,
          direction: 'horizontal',
          pagination: {
            el: '.swiper-pagination',
          },
          navigation: {
            prevEl: '.swiper-button-prev',
            nextEl: '.swiper-button-next',
          },
        });
      }
    }

    onCartUpdate(e) {
      if (!window.location.pathname.includes('/products/')) return;
      const { requestState } = e.detail;
      // If the "add to cart" request is successful
      if (requestState.requestType === 'add' && requestState.responseData?.ok) {
        // Add the CSS class to the "body" tag
        document.body.classList.add('js-show-ajax-cart');
        // dispatch a custom event
        document.dispatchEvent(
          new CustomEvent('item-added-to-cart', {
            detail: requestState?.responseData?.body,
          })
        );
      }
    }

    get variantSelector() {
      return this.querySelector('variant-selector');
    }

    get quantitySelector() {
      return this.querySelector('quantity-selector');
    }

    get selectedOptionValues() {
      if (this.variantSelector.dataset.pickerType === 'dropdown') {
        const list = Array.from(this.variantSelector.querySelectorAll('select')).map(
          (select) => select.options[select.selectedIndex].dataset.optionValueId
        );
        return list;
      } else {
        const list = Array.from(this.variantSelector.querySelectorAll('fieldset input:checked')).map(
          ({ dataset }) => dataset.optionValueId
        );
        return list;
      }
    }

    getSelectedVariant(html) {
      const selectedVariant = html.querySelector('[data-selected-variant]')?.innerHTML;
      return !!selectedVariant ? JSON.parse(selectedVariant) : null;
    }

    onVariantChange(e) {
      const hasDifferentProductUrl = e.target?.dataset?.productUrl ? (e.target?.dataset?.productUrl !== this.dataset.url) : false;
      const productUrl = e.target?.dataset?.productUrl || this.dataset.url;
      this.renderSection(hasDifferentProductUrl, productUrl);
      
      // Update bulk quantity total if bulk selector exists
      this.updateBulkQuantityTotal();
    }

    onQuantitySelectorEvent(e) {
      const quantityInput = this.quantitySelector.querySelector('input[type="number"]');
      let currentValue = parseInt(quantityInput.value);
      const minValue = parseInt(quantityInput.getAttribute('min')) || 0;
      const maxValue = parseInt(quantityInput.getAttribute('max')) || Infinity;

      if (e.target.name === 'minus' && currentValue > minValue) {
        quantityInput.value = currentValue - 1;
      } else if (e.target.name === 'plus' && currentValue < maxValue) {
        quantityInput.value = currentValue + 1;
      } else if (e.type === 'change') {
        if (currentValue < minValue) {
          quantityInput.value = minValue;
        } else if (currentValue > maxValue) {
          quantityInput.value = maxValue;
        }
      }

      // Update the Add to Cart button total price
      const addToCartTotal = this.querySelector(`#add-to-cart-container-${this.dataset.section} .add-to-cart-total`);
      const variantDataScript = this.querySelector('script[data-selected-variant]');
      let variant = null;
      if (variantDataScript) {
        try {
          variant = JSON.parse(variantDataScript.textContent);
        } catch (err) {}
      }
      const qty = parseInt(quantityInput.value) || 1;
      if (addToCartTotal && variant && typeof variant.price === 'number') {
        debugger
        const total = variant.price * qty;
        if (window.Shopify && Shopify.formatMoney) {
          addToCartTotal.textContent = `TOTAL ${Shopify.formatMoney(total, Shopify.money_format)}`;
        } else {
          addToCartTotal.textContent = `TOTAL $${(total / 100).toFixed(2)}`;
        }
      }
    }

    updateMedia(variantFeaturedMediaId) {
      if (!variantFeaturedMediaId) return;
      const slideElement = this.querySelector(`.swiper-slide[data-media-id="${variantFeaturedMediaId}"]`);
      if (slideElement) {
        const index = slideElement.dataset.mediaIndex;
        this.swiper?.slideTo(index);
      }
    }

    updateBulkQuantityTotal() {
      const bulkSelector = this.querySelector('bulk-product-atc');
      if (!bulkSelector) return;

      const bulkInputs = bulkSelector.querySelectorAll('.bulk-quantity-input');
      const addToCartTotal = this.querySelector(`#add-to-cart-container-${this.dataset.section} .add-to-cart-total`);
      
      if (!addToCartTotal || !bulkInputs.length) return;

      let totalQuantity = 0;
      let totalPrice = 0;

      bulkInputs.forEach(input => {
        const quantity = parseInt(input.value) || 0;
        const variantId = input.closest('.bulk-quantity-row').dataset.variantId;
        const variantPrice = parseInt(input.closest('.bulk-quantity-row').dataset.price) || 0;
        
        totalQuantity += quantity;
        totalPrice += quantity * variantPrice;
      });

      // If no quantities are selected, show 0
      if (totalQuantity === 0) {
        addToCartTotal.textContent = 'TOTAL $0.00';
      } else if (window.Shopify && Shopify.formatMoney) {
        addToCartTotal.textContent = `TOTAL ${Shopify.formatMoney(totalPrice, Shopify.money_format)}`;
      } else {
        addToCartTotal.textContent = `TOTAL $${(totalPrice / 100).toFixed(2)}`;
      }
    }

    updateURL(variantId) {
      // this.querySelector('share-button')?.updateUrl(
      //   `${window.shopUrl}${url}${variantId ? `?variant=${variantId}` : ''}`
      // );
      if (!window.location.pathname.includes('/products/')) return;
      window.history.replaceState({}, '', `${this.dataset.url}${variantId ? `?variant=${variantId}` : ''}`);
    }

    updateSourceFromDestination = (html, id) => {
      const source = html.getElementById(`${id}`);
      const destination = this.querySelector(`#${id}`);
      if (source && destination) {
        destination.innerHTML = source.innerHTML;
      }
    };

    updateVariantInputs(variantId) {
      this.querySelectorAll(`#product-form-${this.dataset.section}, #product-form-installment-${this.dataset.section}`).forEach(
        (productForm) => {
          const input = productForm.querySelector('input[name="id"]');
          input.value = variantId ?? '';
        }
      );
    }

    renderSection(hasDifferentProductUrl, productUrl) {
      this.abortController?.abort();
      this.abortController = new AbortController();

      fetch(`${productUrl}?option_values=${this.selectedOptionValues}&section_id=${this.dataset.section}`, {
        signal: this.abortController.signal,
      })
        .then((response) => response.text())
        .then((responseText) => {
          const html = new DOMParser().parseFromString(responseText, 'text/html');
          const variant = this.getSelectedVariant(html);
          if (hasDifferentProductUrl) {
            const productInfo = html.querySelector('product-info');
            this.replaceWith(productInfo);
            productInfo.updateURL(variant?.id);
          } else {
            this.updateMedia(variant?.featured_media?.id);
            this.updateURL(variant?.id);
            this.updateVariantInputs(variant?.id);
            this.updateSourceFromDestination(html, `add-to-cart-container-${this.dataset.section}`);
            // Update the Add to Cart button price dynamically
            const addToCartTotal = this.querySelector(`#add-to-cart-container-${this.dataset.section} .add-to-cart-total`);
            if (addToCartTotal && variant && typeof variant.price === 'number') {
              if (window.Shopify && Shopify.formatMoney) {
                addToCartTotal.textContent = `TOTAL ${Shopify.formatMoney(variant.price, Shopify.money_format)}`;
              } else {
                // fallback if Shopify.formatMoney is not available
                addToCartTotal.textContent = `TOTAL $${(variant.price / 100).toFixed(2)}`;
              }
            }
            this.updateSourceFromDestination(html, `variant-selector-${this.dataset.section}`);
            this.updateSourceFromDestination(html, `price-${this.dataset.section}`);
            this.updateSourceFromDestination(html, `sku-${this.dataset.section}`);
            this.updateSourceFromDestination(html, `inventory-${this.dataset.section}`);
            
            // Update bulk quantity total after section update
            this.updateBulkQuantityTotal();
          }
        })
        .catch((error) => {
          if (error.name === 'AbortError') {
            console.log('Fetch aborted by user');
          } else {
            console.error(error);
          }
        });
    }
  }

  customElements.define('product-info', ProductInfo);
}