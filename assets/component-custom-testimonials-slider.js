class CustomTestimonialsSlider extends HTMLElement {
  constructor() {
    super();
    this.swiper = null;
    this.sectionId = this.getAttribute('data-section-id');
    this.init = this.init.bind(this);
    this.destroy = this.destroy.bind(this);
    this.handleResize = this.handleResize.bind(this);
  }

  connectedCallback() {
    this.init();
    window.addEventListener('resize', this.handleResize);
    document.addEventListener('shopify:section:load', this.onSectionLoad.bind(this));
    document.addEventListener('shopify:section:unload', this.onSectionUnload.bind(this));
  }

  disconnectedCallback() {
    this.destroy();
    window.removeEventListener('resize', this.handleResize);
    document.removeEventListener('shopify:section:load', this.onSectionLoad.bind(this));
    document.removeEventListener('shopify:section:unload', this.onSectionUnload.bind(this));
  }

  shouldEnableSwiper() {
    const slidesCount = this.querySelectorAll('.swiper-slide').length;
    const width = window.innerWidth;
    if (width < 750) {
      return slidesCount > 1;
    } else if (width >= 990) {
      return slidesCount > 4;
    } else {
      // Tablet
      return slidesCount > 2;
    }
  }

  init() {
    if (window.Swiper && this.sectionId) {
      const selector = `#custom-testimonials-swiper-${this.sectionId}`;
      if (this.shouldEnableSwiper()) {
        if (!this.swiper) {
          this.swiper = new Swiper(selector, {
            slidesPerView: 1.2,
            spaceBetween: 16,
            navigation: {
              nextEl: `${selector} .custom-testimonials__swiper-next`,
              prevEl: `${selector} .custom-testimonials__swiper-prev`,
            },
            breakpoints: {
              750: { slidesPerView: 2, centeredSlides: false, loop: false, spaceBetween: 24 },
              990: {
                slidesPerView: 4,
                centeredSlides: false,
                loop: this.querySelectorAll('.swiper-slide').length > 4,
                spaceBetween: 24
              },
            },
            loop: (this.querySelectorAll('.swiper-slide').length > 4) ? false : true,
            watchOverflow: true,
            initialSlide: 0,
          });
        }
        this.toggleNav(true);
      } else {
        this.destroy();
        this.toggleNav(false);
      }
    }
  }

  destroy() {
    if (this.swiper) {
      this.swiper.destroy(true, true);
      this.swiper = null;
    }
    // Remove Swiper classes and inline styles from wrapper and slides
    const wrapper = this.querySelector('.swiper-wrapper');
    if (wrapper) {
      wrapper.classList.remove('swiper-wrapper');
      wrapper.removeAttribute('style');
    }
    this.querySelectorAll('.swiper-slide').forEach(slide => {
      slide.classList.remove('swiper-slide');
      slide.removeAttribute('style');
    });
  }

  toggleNav(show) {
    const prev = this.querySelector('.custom-testimonials__swiper-prev');
    const next = this.querySelector('.custom-testimonials__swiper-next');
    if (prev) prev.style.display = show ? '' : 'none';
    if (next) next.style.display = show ? '' : 'none';
  }

  handleResize() {
    this.init();
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

if (!customElements.get('custom-testimonials-slider')) {
  customElements.define('custom-testimonials-slider', CustomTestimonialsSlider);
} 