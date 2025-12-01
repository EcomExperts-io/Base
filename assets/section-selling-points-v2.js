export class SellingPointsV2 extends HTMLElement {
  constructor() {
    super();
    this.swiper = null;
    this.sectionId = this.getAttribute('data-section-id');
    this.enableMobileSlider = this.getAttribute('data-enable-mobile-slider') === 'true';
    this.resizeTimeout = null;
  }

  get isMobile() {
    return window.matchMedia('(max-width: 749px)').matches;
  }

  get selector() {
    return `#selling-points-v2-${this.sectionId}`;
  }

  connectedCallback() {
    this.handleResize();

    this.resizeObserver = new ResizeObserver(() => this.handleResize());
    this.resizeObserver.observe(this);

    this.handleWindowResize = () => {
      clearTimeout(this.resizeTimeout);
      this.resizeTimeout = setTimeout(() => this.handleResize(), 100);
    };
    window.addEventListener('resize', this.handleWindowResize);
  }

  disconnectedCallback() {
    if (this.swiper) {
      this.swiper.destroy(true, true);
      this.swiper = null;
    }
    this.resizeObserver?.disconnect();
    window.removeEventListener('resize', this.handleWindowResize);
    clearTimeout(this.resizeTimeout);
  }

  handleResize() {
    if (this.isMobile && this.enableMobileSlider) {
      if (!this.swiper) this.init();
    } else if (this.swiper) {
      this.swiper.destroy(true, true);
      this.swiper = null;
    }
  }

  init() {
    if (!this.isMobile || !this.enableMobileSlider || !this.sectionId || !window.Swiper) {
      return;
    }

    const swiperEl = document.querySelector(this.selector);
    if (!swiperEl || swiperEl.classList.contains('swiper-initialized')) {
      return;
    }

    try {
      this.swiper = new Swiper(this.selector, {
        slidesPerView: 1,
        spaceBetween: 16,
        centeredSlides: true,
        pagination: {
          el: `${this.selector} .selling-points-v2__pagination`,
          clickable: true,
        },
        loop: false,
        watchOverflow: true,
        breakpoints: {
          750: { enabled: false },
        },
      });
    } catch (error) {
      console.error('Error initializing Swiper:', error);
    }
  }
}

if (!customElements.get('selling-points-v2')) {
  customElements.define('selling-points-v2', SellingPointsV2);
}
