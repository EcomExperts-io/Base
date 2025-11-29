export class FeaturedProducts extends HTMLElement {
  constructor() {
    super();
    this.swiper = null;
    this.sectionId = this.getAttribute('data-section-id');
  }

  connectedCallback() {
    this.init();
  }

  disconnectedCallback() {
    this.destroy();
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

}

if (!customElements.get('featured-products')) {
  customElements.define('featured-products', FeaturedProducts);
}
