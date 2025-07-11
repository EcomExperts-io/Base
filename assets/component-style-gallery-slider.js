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
          slidesPerView: 2,
          centeredSlides: true,
          spaceBetween: 10,
          autoHeight: false,
          loop: true,
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
          watchOverflow: true,
          initialSlide: 0,
        });
        
        // Set responsive height directly on Swiper container and slides
        const swiperContainer = this.querySelector('.swiper');
        const swiperWrapper = this.querySelector('.swiper-wrapper');
        const swiperSlides = this.querySelectorAll('.swiper-slide');
        
        // Set responsive height based on screen size
        let slideHeight = '200px'; // Default for mobile
        if (window.innerWidth >= 750) {
          slideHeight = '250px'; // Medium screens
        }
        if (window.innerWidth >= 990) {
          slideHeight = '284px'; // Desktop
        }
        
        if (swiperContainer) {
          swiperContainer.style.height = slideHeight;
        }
        if (swiperWrapper) swiperWrapper.style.height = slideHeight;
        swiperSlides.forEach(slide => {
          slide.style.height = slideHeight;
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