class FeaturedCollectionsV2 extends HTMLElement {
  constructor() {
    super();
    this.swipers = []; 
    this.sectionId = this.getAttribute('data-section-id');
    this.radios = this.querySelectorAll("input[type='radio']");
    
    this.handleTabChange = this.handleTabChange.bind(this);
  }

  connectedCallback() {
    this.radios.forEach(radio => {
      radio.addEventListener('change', this.handleTabChange);
    });

    this.swiperInit();
  }

  disconnectedCallback() {
    this.swiperDestroy();
  }

  handleTabChange(event) {
    const selectedRadio = event.target;
    const targetSwiperId = selectedRadio.dataset.targetSwiper;
    
    const allSwiperContainers = this.querySelectorAll('.featured-collections-v2__swiper');

    allSwiperContainers.forEach(container => {
      if (container.id === targetSwiperId) {
        container.classList.remove('hidden');
      } else {
        container.classList.add('hidden');
      }
    });
  }

  swiperInit() {
    const swiperElements = this.querySelectorAll('.swiper');
    
    swiperElements.forEach(swiperEl => {
      if (swiperEl.classList.contains('swiper-initialized')) return;
      
      const productGridGap = parseInt(swiperEl.dataset.productGridGap);
      const productsOnDesktop = parseInt(swiperEl.dataset.productsOnDesktop);
      const productsOnMobile = parseInt(swiperEl.dataset.productsOnMobile);
      const swiperInstance = new Swiper(swiperEl, {
        slidesPerView: 1.8,
        spaceBetween: productGridGap,
        autoHeight: true,
        // IMPORTANT: These two lines allow Swiper to work when un-hidden
        observer: true,
        observeParents: true,
        navigation: {
          nextEl: swiperEl.querySelector('.featured-collections-v2__swiper-next'),
          prevEl: swiperEl.querySelector('.featured-collections-v2__swiper-prev'),
        },
        breakpoints: {
          750: { slidesPerView: productsOnMobile, centeredSlides: false },
          990: { slidesPerView: productsOnDesktop, centeredSlides: false },
        },
        loop: false,
        watchOverflow: true,
      });

      this.swipers.push(swiperInstance);
    });
  }

  swiperDestroy() {
    if (this.swipers.length > 0) {
      this.swipers.forEach(swiper => swiper.destroy(true, true));
      this.swipers = [];
    }
  }
}

if (!customElements.get('featured-collections-v2')) {
  customElements.define('featured-collections-v2', FeaturedCollectionsV2);
}