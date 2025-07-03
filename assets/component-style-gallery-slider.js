class CustomStyleGallerySlider extends HTMLElement {
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

  init() {
    if (window.Swiper && this.sectionId) {
      const selector = `#style-gallery-swiper-${this.sectionId}`;
      if (!this.swiper) {
        this.swiper = new Swiper(selector, {
          slidesPerView: 1,
          centeredSlides: false,
          spaceBetween: 0,
          autoHeight: true,
          navigation: {
            nextEl: `${selector} .style-gallery__swiper-next`,
            prevEl: `${selector} .style-gallery__swiper-prev`,
          },
          breakpoints: {
            750: { slidesPerView: 2, centeredSlides: false, loop: false, spaceBetween: 24 },
            990: {
              slidesPerView: 6,
              centeredSlides: false,
              loop: true,
              spaceBetween: 24
            },
          },
          loop: window.innerWidth >= 990 ? true : false,
          watchOverflow: true,
          initialSlide: 0,
        });
      }
      this.toggleNav(true);
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
    const prev = this.querySelector('.style-gallery__swiper-prev');
    const next = this.querySelector('.style-gallery__swiper-next');
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

if (!customElements.get('custom-style-gallery-slider')) {
  customElements.define('custom-style-gallery-slider', CustomStyleGallerySlider);
} 