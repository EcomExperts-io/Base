export class LocalizationForm extends HTMLElement {
  constructor() {
    super();
    this.elements = {
      input: this.querySelector('input[name="language_code"], input[name="country_code"]'),
    };

    this.querySelectorAll('a').forEach((item) => item.addEventListener('click', this.onItemClick.bind(this)));
  }

  onItemClick(event) {
    event.preventDefault();
    const form = this.querySelector('form');
    this.elements.input.value = event.currentTarget.dataset.value;
    if (form) form.submit();
  }
}

if (!customElements.get('localization-form')) {
  customElements.define('localization-form', LocalizationForm);
}