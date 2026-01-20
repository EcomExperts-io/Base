/**
 * Shop Categories Section Component
 * 
 * Initializes Swiper slider for shop categories section.
 */

export class ShopCategories extends HTMLElement {
  constructor() {
    super();
    this.swiper = null;
    this.sectionId = this.getAttribute('data-section-id');
  }

  connectedCallback() {
    this.init();
    setTimeout(() => {
      this.updateProgressBar();
    }, 100);
  }

  disconnectedCallback() {
    this.destroy();
  }

  init() {
    if (!window.Swiper || !this.sectionId) {
      console.error('Swiper library not loaded or section ID missing');
      return;
    }
    const selector = `#shop-categories-${this.sectionId}`;
    const swiperEl = document.querySelector(selector);
    // Prevent duplicate swiper initialization
    if (!swiperEl || swiperEl.classList.contains('swiper-initialized')) {
      return;
    }
    try {
      this.swiper = new Swiper(selector, {
        slidesPerView: 4,
        spaceBetween: 24,
        navigation: {
          nextEl: `${selector} .shop-categories__nav-button--next`,
          prevEl: `${selector} .shop-categories__nav-button--prev`,
        },
        loop: false,
        watchOverflow: true,
        autoHeight: false,
        breakpoints: {
          0: {
            slidesPerView: 1.5,
            spaceBetween: 24,
          },
          749: {
            slidesPerView: 4,
            spaceBetween: 24,
          },
        },
        on: {
          init: () => {
            this.updateNavigationState();
            this.updateProgressBar();
          },
          slideChange: () => {
            this.updateNavigationState();
            this.updateProgressBar();
          },
        },
      });
    } catch (error) {
      console.error('Error initializing Shop Categories Swiper:', error);
    }
  }

  updateNavigationState() {
    if (!this.swiper) return;
    const prevButton = this.querySelector('.shop-categories__nav-button--prev');
    const nextButton = this.querySelector('.shop-categories__nav-button--next');

    if (prevButton) {
      prevButton.disabled = this.swiper.isBeginning;
    }

    if (nextButton) {
      nextButton.disabled = this.swiper.isEnd;
    }
  }

  updateProgressBar() {
    const progressFill = this.querySelector('.shop-categories__progress-fill');
    if (!this.swiper || !progressFill) return;

    const totalSlides = this.swiper.slides.length;
    if (totalSlides === 0) return;

    const slidesPerView = this.swiper.params.slidesPerView || 1;
    const currentIndex = this.swiper.activeIndex;
    const lastVisibleIndex = currentIndex + slidesPerView - 1;
    const maxIndex = totalSlides - 1;

    if (lastVisibleIndex >= maxIndex) {
      progressFill.style.width = '100%';
    } else {
      const progress = ((lastVisibleIndex + 1) / totalSlides) * 100;
      progressFill.style.width = `${progress}%`;
    }
  }

  destroy() {
    if (this.swiper) {
      this.swiper.destroy(true, true);
      this.swiper = null;
    }
  }
}

if (!customElements.get('shop-categories')) {
  customElements.define('shop-categories', ShopCategories);
}
