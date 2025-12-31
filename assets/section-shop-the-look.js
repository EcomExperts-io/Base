/**
 * Shop The Look Section Component
 * 
 * Initializes Swiper slider for shop the look section with image hotspots
 * and product recommendations.
 */
export class ShopTheLook extends HTMLElement {
  constructor() {
    super();
    this.swiper = null;
    this.sectionId = this.getAttribute('data-section-id');
    this.handleHotspotClick = this.handleHotspotClick.bind(this);
    this.handleOutsideClick = this.handleOutsideClick.bind(this);
  }

  connectedCallback() {
    this.init();
    this.initHotspots();
    setTimeout(() => { 
      this.updateProgressBar(); }, 100);
  }

  disconnectedCallback() {
    this.destroy();
    this.destroyHotspots();
  }

  init() {
    if (!window.Swiper || !this.sectionId) {
      console.error('Swiper library not loaded or section ID missing');
      return;
    }
    const selector = `#shop-the-look-${this.sectionId}`;
    const swiperEl = document.querySelector(selector);
    // Prevent duplicate swiper initialization
    if (!swiperEl || swiperEl.classList.contains('swiper-initialized')) {
      return;
    }
    try {
      this.swiper = new Swiper(selector, {
        slidesPerView: 1,
        spaceBetween: 24,
        navigation: {
          nextEl: `${selector} .shop-the-look__nav-button--next`,
          prevEl: `${selector} .shop-the-look__nav-button--prev`,
        },
        loop: false,
        watchOverflow: true,
        autoHeight: false,
        on: {
          init: () => {
            this.updateNavigationState();
            this.updateProgressBar();
          },
          slideChange: () => {
            this.updateNavigationState();
            this.updateProgressBar();
            this.closeAllTooltips();
          },
        },
      });
    } catch (error) {
      console.error('Error initializing Shop The Look Swiper:', error);
    }
  }

  toggleHotspotListeners(action) {
    const hotspotTriggers = this.querySelectorAll('.shop-the-look__hotspot-trigger');

    hotspotTriggers.forEach(trigger => {
      trigger[action]('click', this.handleHotspotClick);
    });

    document[action]('click', this.handleOutsideClick);
  }

  initHotspots() {
    this.toggleHotspotListeners('addEventListener');
  }

  destroyHotspots() {
    this.toggleHotspotListeners('removeEventListener');
  }

  handleHotspotClick(event) {
    event.stopPropagation();
    const trigger = event.currentTarget;
    const hotspot = trigger.closest('.shop-the-look__hotspot');
    const isActive = hotspot.classList.contains('is-active');

    // Close all other tooltips first
    this.closeAllTooltips();

    // Toggle current tooltip
    if (!isActive) {
      hotspot.classList.add('is-active');
      trigger.setAttribute('aria-expanded', 'true');
    }
  }

  handleOutsideClick(event) {
    const isInsideHotspot = event.target.closest('.shop-the-look__hotspot');
    if (!isInsideHotspot) {
      this.closeAllTooltips();
    }
  }

  closeTooltip(hotspot) {
    if (hotspot) {
      hotspot.classList.remove('is-active');
      const trigger = hotspot.querySelector('.shop-the-look__hotspot-trigger');
      if (trigger) {
        trigger.setAttribute('aria-expanded', 'false');
      }
    }
  }

  closeAllTooltips() {
    const activeHotspots = this.querySelectorAll('.shop-the-look__hotspot.is-active');
    activeHotspots.forEach(hotspot => this.closeTooltip(hotspot));
  }

  updateNavigationState() {
    if (!this.swiper) return;
    const prevButton = this.querySelector('.shop-the-look__nav-button--prev');
    const nextButton = this.querySelector('.shop-the-look__nav-button--next');

    if (prevButton) {
      prevButton.disabled = this.swiper.isBeginning;
    }

    if (nextButton) {
      nextButton.disabled = this.swiper.isEnd;
    }
  }

  updateProgressBar() {
    if (!this.swiper) return;

    const progressFill = this.querySelector('.shop-the-look__progress-fill');
    if (!progressFill) return;

    const totalSlides = this.swiper.slides.length;
    const currentIndex = this.swiper.activeIndex;
    const progress = ((currentIndex + 1) / totalSlides) * 100;

    progressFill.style.width = `${progress}%`;
  }

  destroy() {
    if (this.swiper) {
      this.swiper.destroy(true, true);
      this.swiper = null;
    }
  }
}

if (!customElements.get('shop-the-look')) {
  customElements.define('shop-the-look', ShopTheLook);
}

