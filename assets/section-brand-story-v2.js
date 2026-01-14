export class BrandStoryV2 extends HTMLElement {
  constructor() {
    super();
    this.items = this.querySelectorAll('.brand-story-v2__item');
    this.mediaElements = this.querySelectorAll('.brand-story-v2__media');
  }

  connectedCallback() {
    this.items.forEach((item, index) => {
      const button = item.querySelector('.brand-story-v2__heading-button');
      if (button) {
        button.addEventListener('click', (e) => {
          e.preventDefault();
          if (window.innerWidth <= 900) {
            this.handleItemClick(index);
          } else {
            this.updateImage(index);
          }
        });
        item.addEventListener('mouseenter', () => {
          if (window.innerWidth > 900) {
            this.updateImage(index);
          }
        });
        item.addEventListener('focus', () => {
          if (window.innerWidth > 900) {
            this.updateImage(index);
          }
        });
      }
    });
  }

  handleItemClick = (index) => {
    const targetItem = this.items[index];
    if (!targetItem) return;

    const button = targetItem.querySelector('.brand-story-v2__heading-button');
    const isActive = targetItem.classList.contains('is-active');

    if (isActive) {
      targetItem.classList.remove('is-active');
      if (button) button.setAttribute('aria-expanded', 'false');
    } else {
      this.items.forEach((item, i) => {
        const itemButton = item.querySelector('.brand-story-v2__heading-button');
        if (i === index) {
          item.classList.add('is-active');
          if (itemButton) itemButton.setAttribute('aria-expanded', 'true');
        } else {
          item.classList.remove('is-active');
          if (itemButton) itemButton.setAttribute('aria-expanded', 'false');
        }
      });
    }
  };

  updateImage = (index) => {
    const targetItem = this.items[index];
    if (!targetItem) return;

    this.items.forEach((item, i) => {
      const button = item.querySelector('.brand-story-v2__heading-button');
      if (i === index) {
        item.classList.add('is-active');
        if (button) button.setAttribute('aria-expanded', 'true');
      } else {
        item.classList.remove('is-active');
        if (button) button.setAttribute('aria-expanded', 'false');
      }
    });

    const targetElement = Array.from(this.mediaElements).find(el => el.dataset.blockIndex === String(index));
    const currentElement = Array.from(this.mediaElements).find(el => !el.classList.contains('is-hidden'));

    if (currentElement === targetElement && targetElement) {
      targetElement.classList.remove('slide-up');
      targetElement.classList.add('slide-up-out');
      setTimeout(() => {
        targetElement.classList.remove('slide-up-out');
        targetElement.classList.add('slide-up');
      }, 300);
      return;
    }

    this.mediaElements.forEach((el) => {
      if (!el.classList.contains('is-hidden')) {
        el.classList.remove('slide-up');
        el.classList.add('slide-up-out');
        setTimeout(() => {
          el.classList.add('is-hidden');
          el.classList.remove('slide-up-out');
        }, 300);
      }
    });

    if (targetElement) {
      setTimeout(() => {
        targetElement.classList.remove('is-hidden', 'slide-up-out', 'slide-up');
        targetElement.classList.add('slide-up');
      }, currentElement ? 300 : 0);
    }
  };
}

if (!customElements.get('brand-story-v2')) {
  customElements.define('brand-story-v2', BrandStoryV2);
}
