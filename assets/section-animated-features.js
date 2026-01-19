export class AnimatedFeatures extends HTMLElement {
  constructor() {
    super();
    this.observer = null;
  }

  connectedCallback() {
    const cards = this.querySelectorAll('.animated-features__card');
    cards.forEach((card) => {
      card.addEventListener('click', this.handleCardClick.bind(this));
    });

    this.initScrollAnimations();
  }

  initScrollAnimations() {
    this.observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
        }
      });
    }, { threshold: 0.2 });

    const elements = this.querySelectorAll('[class*="animated-features__"]');
    elements.forEach((el) => this.observer.observe(el));
  }

  handleCardClick(event) {
    const card = event.currentTarget;
    if (card.querySelector('.animated-features__card-back')) {
      card.classList.toggle('is-flipped');
    }
  }

  disconnectedCallback() {
    const cards = this.querySelectorAll('.animated-features__card');
    cards.forEach((card) => {
      card.removeEventListener('click', this.handleCardClick);
    });

    if (this.observer) {
      this.observer.disconnect();
    }
  }
}

if (!customElements.get('animated-features')) {
  customElements.define('animated-features', AnimatedFeatures);
}
