export class AnimatedFeaturesV2 extends HTMLElement {
  connectedCallback() {
    this.setupScrollAnimation();
  }

  setupScrollAnimation() {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');

          if (entry.target.classList.contains('animated-features-v2__heading')) {
            this.animateScrollingDigits(entry.target);
          }
        }
      });
    }, { threshold: 0.2 });

    const elements = '.animated-features-v2__heading, .animated-features-v2__subheading, .animated-features-v2__feature, .animated-features-v2__disclaimer, .animated-features-v2__image-wrapper, .animated-features-v2__image-label';
    this.querySelectorAll(elements).forEach(el => observer.observe(el));
  }

  animateScrollingDigits(heading) {
    if (heading.dataset.animated) return;
    heading.dataset.animated = 'true';

    const text = heading.getAttribute('data-percentage');
    const match = text.match(/(\d+)(.*)$/);

    if (!match) {
      heading.textContent = text;
      return;
    }

    const number = match[1];
    const suffix = match[2];
    const digits = number.padStart(2, '0').split('');

   
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

    heading.innerHTML = html;

    setTimeout(() => {
      const scrollers = heading.querySelectorAll('.animated-features-v2__digit-scroller');

      scrollers.forEach((scroller, index) => {
        const targetDigit = digits[index];
        const digitHeight = scroller.firstChild.offsetHeight;
        const scrollDistance = (targetDigit === '0' ? 10 : parseInt(targetDigit)) * digitHeight;

        scroller.style.transitionDelay = `${index * 0.1}s`;
        scroller.style.transform = `translateY(-${scrollDistance}px)`;
      });
    }, 50);

    setTimeout(() => {
      heading.textContent = text;
    }, animationCompleteTime);
  }
}

if (!customElements.get('animated-features-v2')) {
  customElements.define('animated-features-v2', AnimatedFeaturesV2);
}