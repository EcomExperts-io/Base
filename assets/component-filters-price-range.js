export class PriceRange extends HTMLElement {
  constructor() {
    super();
  }

  connectedCallback() {
    this.rangeInputs = this.querySelectorAll('.range-input input');
    this.numberInputs = this.querySelectorAll('.price-input input[type="number"]');
    this.rangeSlider = this.querySelector('.slider-container .price-slider');
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
    this.rangeInputs.forEach(() => {
      this.rangeInputs[0].addEventListener('input', (event) => this.handleInputChange('range', event));
      this.rangeInputs[1].addEventListener('input', (event) => this.handleInputChange('range', event));
    });

    this.numberInputs[0].addEventListener('change', (event) => this.handleInputChange('number', event));
    this.numberInputs[1].addEventListener('change', (event) => this.handleInputChange('number', event));
  }

  handleInputChange(source, event) {
    const minRangeVal = parseInt(this.rangeInputs[0].value, 10);
    const maxRangeVal = parseInt(this.rangeInputs[1].value, 10);
    const minNumberVal = parseInt(this.numberInputs[0].value, 10);
    const maxNumberVal = parseInt(this.numberInputs[1].value, 10);

    const maxAllowed = parseInt(this.rangeInputs[1].max, 10);
    const minAllowed = parseInt(this.rangeInputs[0].min, 10);

    let min = source === 'range' ? minRangeVal : minNumberVal;
    let max = source === 'range' ? maxRangeVal : maxNumberVal;

    if (isNaN(min) || isNaN(max)) return;

    min = Math.max(minAllowed, Math.min(min, maxAllowed));
    max = Math.max(minAllowed, Math.min(max, maxAllowed));

    const target = event?.target;

    if (target === this.rangeInputs[0] || target === this.numberInputs[0]) {
      min = Math.min(min, max - 1);
    } else if (target === this.rangeInputs[1] || target === this.numberInputs[1]) {
      max = Math.max(max, min + 1);
    }

    this.updateUI(min, max);
  }

  updateUI(min, max) {
    const maxRange = parseInt(this.rangeInputs[1].max, 10);

    min = Math.max(0, Math.min(min, maxRange));
    max = Math.max(0, Math.min(max, maxRange));

    this.rangeInputs[0].value = min;
    this.rangeInputs[1].value = max;
    this.numberInputs[0].value = min;
    this.numberInputs[1].value = max;

    this.rangeSlider.style.left = `${(min / maxRange) * 100}%`;
    this.rangeSlider.style.right = `${100 - (max / maxRange) * 100}%`;
  }
}

if (!customElements.get('price-range')) {
  customElements.define('price-range', PriceRange);
}