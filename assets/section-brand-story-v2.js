class BrandStoryV2 extends HTMLElement {
  constructor() {
    super();
    this.items = this.querySelectorAll('.brand-story-v2__item');
    this.featuredImage = this.querySelector('.brand-story-v2__featured-image');
  }

  connectedCallback() {
    this.items.forEach((item, index) => {
      const button = item.querySelector('.brand-story-v2__heading-button');
      if (button) {
        button.addEventListener('click', (e) => {
          e.preventDefault();
          if (window.innerWidth <= 900) {
            this.handleItemClick(index);
          }
        });
        item.addEventListener('mouseenter', () => {
          if (window.innerWidth > 900) {
            this.handleItemHover(index);
          }
        });
        item.addEventListener('focus', () => {
          if (window.innerWidth > 900) {
            this.handleItemHover(index);
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

  handleItemHover = (index) => {
    if (window.innerWidth <= 900) return;

    const targetItem = this.items[index];
    if (!targetItem) return;

    const isAlreadyActive = targetItem.classList.contains('is-active');
    const imageUrl = targetItem.dataset.imageUrl;

    if (imageUrl && this.featuredImage && !isAlreadyActive) {
      this.featuredImage.classList.remove('slide-up', 'slide-up-out');
      this.featuredImage.classList.add('slide-up-out');
      setTimeout(() => {
        const handleImageLoad = () => {
          this.featuredImage.classList.remove('slide-up-out');
          this.featuredImage.classList.add('slide-up');
          this.featuredImage.removeEventListener('load', handleImageLoad);
        };
        this.featuredImage.addEventListener('load', handleImageLoad);
        this.featuredImage.src = imageUrl;
        if (this.featuredImage.complete) {
          handleImageLoad();
        }
      }, 300); 
    }

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
  };
}

if (!customElements.get('brand-story-v2')) {
  customElements.define('brand-story-v2', BrandStoryV2);
}
