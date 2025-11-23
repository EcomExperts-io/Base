export class PriceRange extends HTMLElement {
  constructor() {
    super();
  }

  connectedCallback() {
    this.rangeInputs = this.querySelectorAll('.range-input input');
    this.rangeSlider = this.querySelector('.slider-container .price-slider');
    this.minPriceText = this.querySelector('.min_price');
    this.maxPriceText = this.querySelector('.max_price');
    this.currencySymbol = this.querySelector('.price-range-main').getAttribute('currency-symbol');
    this.init();
  }

  init() {
    const urlParams = new URLSearchParams(window.location.search);
    const urlMin = urlParams.get('filter.v.price.gte');
    const urlMax = urlParams.get('filter.v.price.lte');

    const minVal = urlMin ? parseInt(urlMin, 10) : parseInt(this.rangeInputs[0].value, 10);
    const maxVal = urlMax ? parseInt(urlMax, 10) : parseInt(this.rangeInputs[1].value, 10);

    this.updateUI(minVal, maxVal);
    this.bindEvents();
  }

  bindEvents() {
    this.rangeInputs.forEach((input) => {
      input.addEventListener('input', () => {
        const newMin = parseInt(this.rangeInputs[0].value, 10);
        const newMax = parseInt(this.rangeInputs[1].value, 10);

        if (newMin <= newMax) {
          this.updateUI(newMin, newMax);
        }
      });
    });
  }

  updateUI(min, max) {
    this.minPriceText.textContent = `${this.currencySymbol}${min}.00`;
    this.maxPriceText.textContent = `${this.currencySymbol}${max}.00`;
    this.rangeSlider.style.left = `${(min / this.rangeInputs[0].max) * 100}%`;
    this.rangeSlider.style.right = `${100 - (max / this.rangeInputs[1].max) * 100}%`;
    this.rangeInputs[0].value = min;
    this.rangeInputs[1].value = max;
  }
}

if (!customElements.get('price-range')) {
  customElements.define('price-range', PriceRange);
}