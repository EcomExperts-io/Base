export class AnimatedFeatures extends HTMLElement {
  constructor() {
    super();
    this.observer = null;
  }

  connectedCallback() {
    this.initCardClickHandlers();
    this.initScrollAnimations();
  }

  initCardClickHandlers() {
    const animatedCards = this.querySelectorAll('.animated-features__card');
    animatedCards.forEach((animatedCard) => {
      animatedCard.addEventListener('click', this.handleCardClick.bind(this));
    });
  }

  initScrollAnimations() {
    this.observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
        }
      });
    }, { threshold: 0.2 });

    const animatedElements = this.querySelectorAll('[class*="animated-features__"]');
    animatedElements.forEach((element) => this.observer.observe(element));
  }

  handleCardClick(event) {
    const animatedCard = event.currentTarget;
    if (animatedCard.querySelector('.animated-features__card-back')) {
      animatedCard.classList.toggle('is-flipped');
    }
  }

  disconnectedCallback() {
    if (this.observer) {
      this.observer.disconnect();
    }
  }
}

if (!customElements.get('animated-features')) {
  customElements.define('animated-features', AnimatedFeatures);
}
