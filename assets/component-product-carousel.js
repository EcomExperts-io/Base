class ProductCarousel extends HTMLElement {
  connectedCallback() {
    if (typeof Swiper !== 'undefined') {
      this.initSwiper();
    } else {
      const script = document.getElementById('swiper-script');
      if (script) {
        script.addEventListener('load', this.initSwiper.bind(this));
      }
    }
  }

  initSwiper() {
    const element = this.querySelector('.swiper');
    if (!element) return;
    this.swiper = new Swiper(element, {
      slidesPerView: 1,
      spaceBetween: 16,
      loop: true,
      pagination: {
        el: this.querySelector('.swiper-pagination'),
        clickable: true,
      },
      navigation: {
        nextEl: this.querySelector('.swiper-button-next'),
        prevEl: this.querySelector('.swiper-button-prev'),
      },
      breakpoints: {
        750: { slidesPerView: 2 },
        990: { slidesPerView: 4 },
      },
    });
  }
}

if (!customElements.get('product-carousel')) {
  customElements.define('product-carousel', ProductCarousel);
}
