<<<<<<< HEAD
class FeaturedProducts extends HTMLElement {
    constructor() {
      super();
      this.swiper = null;
      this.sectionId = this.getAttribute('data-section-id');
      this.init = this.init.bind(this);
      this.destroy = this.destroy.bind(this);
    }
  
    connectedCallback() {
      this.init();
      document.addEventListener('shopify:section:load', this.onSectionLoad.bind(this));
      document.addEventListener('shopify:section:unload', this.onSectionUnload.bind(this));
    }
  
    disconnectedCallback() {
      this.destroy();
      document.removeEventListener('shopify:section:load', this.onSectionLoad.bind(this));
      document.removeEventListener('shopify:section:unload', this.onSectionUnload.bind(this));
    }
  
    init() {
      if (window.Swiper && this.sectionId) {
        const selector = `#featured-products-${this.sectionId}`;
        this.swiper = new Swiper(selector, {
          slidesPerView: 1.4,
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
=======
class FeaturedProducts extends HTMLElement {
    constructor() {
      super();
      this.swiper = null;
      this.sectionId = this.getAttribute('data-section-id');
      this.init = this.init.bind(this);
      this.destroy = this.destroy.bind(this);
    }
  
    connectedCallback() {
      this.init();
      document.addEventListener('shopify:section:load', this.onSectionLoad.bind(this));
      document.addEventListener('shopify:section:unload', this.onSectionUnload.bind(this));
    }
  
    disconnectedCallback() {
      this.destroy();
      document.removeEventListener('shopify:section:load', this.onSectionLoad.bind(this));
      document.removeEventListener('shopify:section:unload', this.onSectionUnload.bind(this));
    }
  
    init() {
      if (window.Swiper && this.sectionId) {
        const selector = `#featured-products-${this.sectionId}`;
        this.swiper = new Swiper(selector, {
          slidesPerView: 1.2,
          centeredSlides: true,
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
>>>>>>> 812a8d290ee5ac15db5ac89805c0f5a5f5683238
  }