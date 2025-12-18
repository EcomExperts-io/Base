/**
 * Related Products Carousel Component
 * 
 * Initializes Swiper carousel for related products section when layout is set to carousel.
 * Waits for product recommendations to load via AJAX before initialization.
 */
export class RelatedProductsCarousel extends HTMLElement {
  constructor() {
    super();
    this.swiper = null;
    this.observer = null;
  }

  connectedCallback() {
    if (this.querySelector('.swiper-slide')) {
      this.initCarousel();
      return;
    }

    this.observer = new MutationObserver(() => {
      if (this.querySelector('.swiper-slide') && !this.swiper) {
        this.initCarousel();
        this.observer.disconnect();
      }
    });

    this.observer.observe(this, {
      childList: true,
      subtree: true
    });
  }

  disconnectedCallback() {
    if (this.observer) {
      this.observer.disconnect();
    }
    this.destroyCarousel();
  }

  initCarousel() {
    if (!window.Swiper) {
      console.error('Swiper library not loaded');
      return;
    }

    const carouselEl = this.querySelector('.related-products__carousel');
    if (!carouselEl) return;

    if (this.swiper || carouselEl.classList.contains('swiper-initialized')) {
      return;
    }

    const wrapper = this.querySelector('.related-products__carousel-wrapper');
    if (!wrapper) return;

    const prevButton = wrapper.querySelector('.swiper-button-prev');
    const nextButton = wrapper.querySelector('.swiper-button-next');

    this.swiper = new Swiper(carouselEl, {
      slidesPerView: 1.2,
      spaceBetween: 16,
      navigation: {
        nextEl: nextButton,
        prevEl: prevButton,
      },
      breakpoints: {
        480: {
          slidesPerView: 2,
          spaceBetween: 12,
        },
        750: {
          slidesPerView: 3,
          spaceBetween: 16,
        },
        990: {
          slidesPerView: 4,
          spaceBetween: 20,
        },
      },
      watchOverflow: true,
    });
  }

  destroyCarousel() {
    if (this.swiper) {
      this.swiper.destroy(true, true);
      this.swiper = null;
    }
  }
}

if (!customElements.get('related-products-carousel')) {
  customElements.define('related-products-carousel', RelatedProductsCarousel);
}

