import { debounce } from './theme.js';

export class PredictiveSearch extends HTMLElement {
  constructor() {
    super();

    this.input = this.querySelector('input[type="search"]');
    this.predictiveSearchResults = this.querySelector('#predictive-search');
    this.resetButton = this.querySelector('.reset__button');
    this.searchTerm = this.input.value.trim();
    this.isOpen = false;
    this.abortController = new AbortController();
    this.input.addEventListener('input', debounce((e) => this.onChange(e), 700));
    this.input.addEventListener('focus', (e) => this.onChange(e));
    this.handleClickOutside = this.handleClickOutside.bind(this);
    document.addEventListener('click', this.handleClickOutside);
  }

  onChange(e) {
    console.log(e);
    const newSearchTerm = this.input.value.trim();
    this.searchTerm = newSearchTerm;

    if (!this.searchTerm.length) {
      const resultsElement = this.querySelector('#predictive-search-results');
      if (resultsElement) resultsElement.remove();
      this.close();
      return;
    }

    if (!this.isOpen) {
      this.toggleLoading(true);
    }
    this.getSearchResults(this.searchTerm);
  }

  getSearchResults(searchTerm) {
    fetch(`/search/suggest?q=${encodeURIComponent(searchTerm)}&section_id=predictive-results`, {
      signal: this.abortController.signal,
    })
      .then(response => {
        if (!response.ok) {
          this.close();
          return Promise.reject(new Error(`Failed to fetch: ${response.status}`));
        }
        return response.text();
      })
      .then(text => {
        const parser = new DOMParser();
        const doc = parser.parseFromString(text, 'text/html');
        const resultsMarkup = doc.querySelector('#shopify-section-predictive-results')?.innerHTML || '';
        this.updateResults(resultsMarkup);
      })
      .catch(error => {
        console.error('Error fetching search results:', error);
        this.close();
      });
  }

  updateResults(resultsMarkup) {
    this.predictiveSearchResults.innerHTML = resultsMarkup;
    this.open();
  }
  
  open() {
    this.toggleLoading(false);
    this.predictiveSearchResults.style.display = 'block';
    this.isOpen = true;
  }

  close() {
    this.predictiveSearchResults.style.display = 'none';
    this.isOpen = false;
  }

  clearSearch(e) {
    e.preventDefault();
    this.input.value = '';
    this.onChange();
  }

  handleClickOutside(event) {
    // Check if the click is outside the predictive search component
    if (this.isOpen && !this.contains(event.target)) {
      this.close();
    }
  }

  disconnectedCallback() {
    // Clean up event listeners when component is removed
    document.removeEventListener('click', this.handleClickOutside);
  }

  toggleLoading(show) {
    this.querySelector('.predictive-search__loading')?.classList.toggle('hidden', !show);
  }
}

if (!customElements.get('predictive-search')) {
  customElements.define('predictive-search', PredictiveSearch);
}