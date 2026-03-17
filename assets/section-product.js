export class ProductInfo extends HTMLElement {
  abortController = undefined;
  swiper = undefined;

  constructor() {
    super();
  }

  setupEventListeners() {
    this.variantSelector?.addEventListener('change', this.onVariantChange.bind(this));
    this.quantitySelector.addEventListener('change', this.onQuantitySelectorEvent.bind(this));
    this.quantitySelector.querySelector('button[name="plus"]').addEventListener('click', this.onQuantitySelectorEvent.bind(this));
    this.quantitySelector.querySelector('button[name="minus"]').addEventListener('click', this.onQuantitySelectorEvent.bind(this));
  }

  connectedCallback() {
    this.setupEventListeners();
    this.initSwiper();
  }

  initSwiper() {
    const thumbnailGalleryEl = this.querySelector('.product-media-gallery__thumbnails');
    const thumbnailWrapperEl = this.querySelector('.product-media-gallery__thumbnails-wrapper');
    if (thumbnailGalleryEl) {

      const mainGalleryEl = this.querySelector('.product-media-gallery__main');
      if (mainGalleryEl) {
        this.swiper = new Swiper(mainGalleryEl, {
          spaceBetween: 0,
          thumbs: {
            swiper: new Swiper(thumbnailGalleryEl, {
              spaceBetween: 12,
              slidesPerView: 'auto',
              freeMode: true,
              watchSlidesProgress: true,
              slideToClickedSlide: true,
              navigation: {
                prevEl: thumbnailWrapperEl?.querySelector('.swiper-button-prev') || thumbnailGalleryEl.querySelector('.swiper-button-prev'),
                nextEl: thumbnailWrapperEl?.querySelector('.swiper-button-next') || thumbnailGalleryEl.querySelector('.swiper-button-next'),
              },
              breakpoints: {
                768: {
                  spaceBetween: 14,
                },
                1024: {
                  spaceBetween: 16,
                }
              }
            }),
          },
        });
      }
    }

    const carouselGalleryEl = this.querySelector('.product-media-gallery__carousel');
    if (carouselGalleryEl) {
      this.swiper = new Swiper(carouselGalleryEl, {
        autoHeight: true,
        direction: 'horizontal',
        pagination: {
          el: carouselGalleryEl.querySelector('.swiper-pagination'),
        },
        navigation: {
          prevEl: carouselGalleryEl.querySelector('.swiper-button-prev'),
          nextEl: carouselGalleryEl.querySelector('.swiper-button-next'),
        },
      });
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
    const productUrlChanged = e.target?.dataset?.productUrl ? (e.target?.dataset?.productUrl !== this.dataset.url) : false;
    const productUrl = e.target?.dataset?.productUrl || this.dataset.url;
    this.renderSection(productUrlChanged, productUrl);
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
  }

  updateMedia(variantFeaturedMediaId) {
    if (!variantFeaturedMediaId) return;
    const mediaSlide = this.querySelector(`.swiper-slide[data-media-id="${variantFeaturedMediaId}"]`);
    if (!mediaSlide) return;

    const slideIndex = parseInt(mediaSlide.dataset.mediaIndex);
    this.swiper?.slideTo(slideIndex);
  }

  updateURL(variantId) {
    // this.querySelector('share-button')?.updateUrl(
    //   `${window.shopUrl}${url}${variantId ? `?variant=${variantId}` : ''}`
    // );

    // Don't update URL if this is in a modal/quick-add context
    if (this.dataset.updateUrl === 'false') return;

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

  renderSection(productUrlChanged, productUrl) {
    this.abortController?.abort();
    this.abortController = new AbortController();

    // If the section is in a modal, use the original section id without the modal suffix
    const sectionId = this.dataset.updateUrl === 'false' ? this.dataset.section.split('-modal')[0] : this.dataset.section;
    fetch(`${productUrl}?option_values=${this.selectedOptionValues}&section_id=${sectionId}`, {
      signal: this.abortController.signal,
    })
      .then((response) => response.text())
      .then((responseText) => {
        // If the section is in a modal, replace the original section id with the modal section id
        if (this.dataset.updateUrl === 'false') {
          responseText = responseText.replaceAll(this.dataset.section.split('-modal')[0], this.dataset.section);
        }

        // Parse the response text into an HTML document
        const html = new DOMParser().parseFromString(responseText, 'text/html');
        const variant = this.getSelectedVariant(html);
        if (productUrlChanged) {
          // If the product url has changed, replace the current section with the new section
          const productInfo = html.querySelector('product-info');
          this.replaceWith(productInfo);
          productInfo.updateURL(variant?.id);
        } else {
          this.updateMedia(variant?.featured_media?.id);
          this.updateURL(variant?.id);
          this.updateVariantInputs(variant?.id);
          this.updateSourceFromDestination(html, `add-to-cart-container-${this.dataset.section}`);
          this.updateSourceFromDestination(html, `variant-selector-${this.dataset.section}`);
          this.updateSourceFromDestination(html, `price-${this.dataset.section}`);
          this.updateSourceFromDestination(html, `sku-${this.dataset.section}`);
          this.updateSourceFromDestination(html, `inventory-${this.dataset.section}`);
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

if (!customElements.get('product-info')) {
  customElements.define('product-info', ProductInfo);
}