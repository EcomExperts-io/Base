export class ProductRecommendations extends HTMLElement {
  constructor() {
    super();
    this.handleIntersection = this.handleIntersection.bind(this);
    this.observer = null;
  }

  connectedCallback() {
    this.observer = new IntersectionObserver(this.handleIntersection, {
      rootMargin: '0px 0px 200px 0px'
    });

    this.observer.observe(this);
  }

  handleIntersection(entries, observer) {
    if (!entries[0].isIntersecting) return;

    observer.unobserve(this);

    const url = this.dataset.url;

    fetch(url)
      .then(response => response.text())
      .then(text => {
        const html = document.createElement('div');
        html.innerHTML = text;
        const recommendations = html.querySelector('product-recommendations');

        if (recommendations && recommendations.innerHTML.trim().length) {
          this.innerHTML = recommendations.innerHTML;
        }
      })
      .catch(e => {
        console.error(e);
      });
  }
}

if (!customElements.get('product-recommendations')) {
  customElements.define('product-recommendations', ProductRecommendations);
} 
