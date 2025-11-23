export class FeaturedProducts extends HTMLElement {
  constructor() {
    super();
    this.swiper = null;
    this.sectionId = this.getAttribute('data-section-id');

    // Store bound methods so add/removeEventListener match
    this.onSectionLoad = this.onSectionLoad.bind(this);
    this.onSectionUnload = this.onSectionUnload.bind(this);
  }

  connectedCallback() {
    this.init();
    document.addEventListener('shopify:section:load', this.onSectionLoad);
    document.addEventListener('shopify:section:unload', this.onSectionUnload);
  }

  disconnectedCallback() {
    this.destroy();
    document.removeEventListener('shopify:section:load', this.onSectionLoad);
    document.removeEventListener('shopify:section:unload', this.onSectionUnload);
  }

  init() {
    if (window.Swiper && this.sectionId) {
      const selector = `#featured-products-${this.sectionId}`;
      const swiperEl = document.querySelector(selector);

      // Prevent duplicate swiper initialization
      if (!swiperEl || swiperEl.classList.contains('swiper-initialized')) return;

      this.swiper = new Swiper(selector, {
        slidesPerView: 1.8,
        spaceBetween: 16,
        autoHeight: true,
        navigation: {
          nextEl: `${selector} .featured-products__swiper-next`,
          prevEl: `${selector} .featured-products__swiper-prev`,
        },
        breakpoints: {
          750: { slidesPerView: 2, centeredSlides: false },
          990: { slidesPerView: 4, centeredSlides: false },
        },
        loop: false,
        watchOverflow: true,
      });
    }
  }

  destroy() {
    if (this.swiper) {
      this.swiper.destroy(true, true);
      this.swiper = null;
    }
  }

  onSectionLoad(e) {
    if (e.detail && e.detail.sectionId === this.sectionId) {
      this.destroy();
      this.init();
    }
  }

  onSectionUnload(e) {
    if (e.detail && e.detail.sectionId === this.sectionId) {
      this.destroy();
    }
  }
}

if (!customElements.get('featured-products')) {
  customElements.define('featured-products', FeaturedProducts);
}
