import { debounce } from './theme.js';

export class CollectionInfo extends HTMLElement {
  constructor() {
    super();
    this.debounceOnChange = debounce((event) => this.onChangeHandler(event), 800);
    this.addEventListener('change', this.debounceOnChange.bind(this));
    this.addEventListener('click', this.onClickHandler.bind(this));
  }

  onClickHandler = (event) => {
    if (event.target.matches('[data-render-section-url]')) {
      event.preventDefault();
      const searchParams = new URLSearchParams(event.target.dataset.renderSectionUrl.split('?')[1]).toString();
      this.fetchSection(searchParams);
    }
  };

  onChangeHandler = (event) => {
    if (!event.target.matches('[data-render-section]')) return;

    const form = event.target.closest('form') || document.querySelector('#filters-form') || document.querySelector('#filters-form-drawer');
    const formData = new FormData(form);
    const searchParams = new URLSearchParams(formData);
    const existingParams = new URLSearchParams(window.location.search);
    const qValue = existingParams.get('q');

    this.removeDefaultPriceFilters(searchParams, form);

    const finalParams = qValue ? `q=${encodeURIComponent(qValue)}&${searchParams}` : searchParams.toString();
    this.fetchSection(finalParams);
  };

  get form() {
    return this.querySelector('collection-info form');
  }

  updateSourceFromDestination = (html, id) => {
    const source = html.getElementById(`${id}`);
    const destination = this.querySelector(`#${id}`);
    if (source && destination) {
      destination.innerHTML = source.innerHTML;
    }
  };

  removeDefaultPriceFilters = (searchParams, form) => {
    const priceMin = searchParams.get('filter.v.price.gte');
    const priceMax = searchParams.get('filter.v.price.lte');
    const actualMaxPrice = form.querySelector('.max-range')?.getAttribute('max');

    const isMinAtDefault = priceMin === '0' || !priceMin;
    const isMaxAtDefault = !actualMaxPrice || priceMax === actualMaxPrice || !priceMax;

    if (isMinAtDefault && isMaxAtDefault) {
      searchParams.delete('filter.v.price.gte');
      searchParams.delete('filter.v.price.lte');
    }
  };

  updateURL(searchParams) {
    history.pushState({}, '', `${window.location.pathname}?${searchParams}`);
  }

  updateFilters = (html, className) => {
    const filtersFromFetch = html.querySelectorAll(`collection-info .${className}`);
    const filtersFromDom = document.querySelectorAll(`collection-info .${className}`);

    // Remove filters that are no longer returned from the server
    Array.from(filtersFromDom).forEach((currentElement) => {
      if (!Array.from(filtersFromFetch).some(({ id }) => currentElement.id === id)) {
        currentElement.remove();
      }
    });

    Array.from(filtersFromFetch).forEach((elementToRender, index) => {
      document.getElementById(elementToRender.id).innerHTML = elementToRender.innerHTML;
    });
  };

  showLoadingOverlay = () => {
    this.querySelector(`#loading-overlay-${this.dataset.section}`).style.display = 'flex';
    this.querySelector(`#loading-spinner-${this.dataset.section}`).style.display = 'block';
    this.querySelector(`#results-count-${this.dataset.section}`).style.display = 'none';
    this.querySelector(`#drawer-results-count-${this.dataset.section}`).style.display = 'none';
    this.querySelector(`#drawer-loading-spinner-${this.dataset.section}`).style.display = 'block';
  };

  hideLoadingOverlay = () => {
    this.querySelector(`#loading-overlay-${this.dataset.section}`).style.display = 'none';
    this.querySelector(`#loading-spinner-${this.dataset.section}`).style.display = 'none';
    this.querySelector(`#results-count-${this.dataset.section}`).style.display = 'block';
    this.querySelector(`#drawer-results-count-${this.dataset.section}`).style.display = 'block';
    this.querySelector(`#drawer-loading-spinner-${this.dataset.section}`).style.display = 'none';
  };

  fetchSection = (searchParams) => {
    this.showLoadingOverlay();
    fetch(`${window.location.pathname}?section_id=${this.dataset.section}&${searchParams}`)
      .then((response) => response.text())
      .then((responseText) => {
        let html = new DOMParser().parseFromString(responseText, 'text/html');
        this.updateURL(searchParams);
        this.updateSourceFromDestination(html, `product-grid-${this.dataset.section}`);
        this.updateSourceFromDestination(html, `results-count-${this.dataset.section}`);
        this.updateSourceFromDestination(html, `drawer-results-count-${this.dataset.section}`);
        this.updateSourceFromDestination(html, `active-filters-count-${this.dataset.section}`);
        this.updateSourceFromDestination(html, `active-filter-group-${this.dataset.section}`);
        this.updateSourceFromDestination(html, `sort-by-drawer-${this.dataset.section}`);
        this.updateSourceFromDestination(html, `sort-by-${this.dataset.section}`);
        this.updateSourceFromDestination(html, `filters-drawer-buttons-wrapper-id`);
        this.updateFilters(html, `js-filter`);
        this.hideLoadingOverlay();
        this.scrollToProductGrid();
      })
      .catch((error) => {
        console.error(error);
        this.hideLoadingOverlay();
      });
  };

  scrollToProductGrid = () => {
    const productGrid = this.querySelector(`#product-grid-${this.dataset.section}`);
    const headerId = document.querySelector('#main-header');
    const headerOffset = (headerId.offsetHeight + 10) || 80;

    if (productGrid) {
      const elementPosition = productGrid.getBoundingClientRect().top;
      const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

      window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
      });
    }
  };
}

if (!customElements.get('collection-info')) {
  customElements.define('collection-info', CollectionInfo);
}