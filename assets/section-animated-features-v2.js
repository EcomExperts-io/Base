export class AnimatedFeaturesV2 extends HTMLElement {
  constructor() {
    super();
    this.observer = null;
  }

  connectedCallback() {
    this.setupScrollAnimation();
  }

  setupScrollAnimation() {
    this.observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');

          if (entry.target.classList.contains('animated-features-v2__heading')) {
            this.animateScrollingDigits(entry.target);
          }
        }
      });
    }, { threshold: 0.2 });

    const animatedElements = '.animated-features-v2__heading, .animated-features-v2__subheading, .animated-features-v2__feature, .animated-features-v2__disclaimer, .animated-features-v2__image-wrapper, .animated-features-v2__image-label';
    this.querySelectorAll(animatedElements).forEach((element) => this.observer.observe(element));
  }

  animateScrollingDigits(headingElement) {
    if (headingElement.dataset.animated) return;
    headingElement.dataset.animated = 'true';

    const percentageValue = headingElement.getAttribute('data-percentage');
    const percentageMatch = percentageValue.match(/(\d+)(.*)$/);

    if (!percentageMatch) {
      headingElement.textContent = percentageValue;
      return;
    }

    const percentageNumber = percentageMatch[1];
    const suffix = percentageMatch[2];
    const digits = percentageNumber.padStart(2, '0').split('');

    const animationSpeed = parseFloat(this.dataset.animationSpeed || '1.2');
    const digitAnimationDuration = animationSpeed * 1.5;
    const animationCompleteTime = digitAnimationDuration * 1000;

    let html = '<span class="animated-features-v2__counter-wrapper">';

    digits.forEach((targetDigit, index) => {
      html += '<span class="animated-features-v2__digit-container">';
      html += '<span class="animated-features-v2__digit-scroller">';

      for (let i = 0; i <= 10; i++) {
        html += `<span class="animated-features-v2__digit">${i % 10}</span>`;
      }

      html += '</span></span>';
    });

    html += `<span class="animated-features-v2__suffix">${suffix}</span>`;
    html += '</span>';

    headingElement.innerHTML = html;

    setTimeout(() => {
      const digitScrollers = headingElement.querySelectorAll('.animated-features-v2__digit-scroller');

      digitScrollers.forEach((digitScroller, index) => {
        const targetDigit = digits[index];
        const digitHeight = digitScroller.firstChild.offsetHeight;
        const scrollDistance = (targetDigit === '0' ? 10 : parseInt(targetDigit)) * digitHeight;

        digitScroller.style.transitionDelay = `${index * 0.1}s`;
        digitScroller.style.transform = `translateY(-${scrollDistance}px)`;
      });
    }, 50);

    setTimeout(() => {
      headingElement.textContent = percentageValue;
    }, animationCompleteTime);
  }

  disconnectedCallback() {
    if (this.observer) {
      this.observer.disconnect();
    }
  }
}

if (!customElements.get('animated-features-v2')) {
  customElements.define('animated-features-v2', AnimatedFeaturesV2);
}