export class ProductMediaModal extends HTMLElement {
  constructor() {
    super();
    const mediaSlides = document.querySelectorAll('media-gallery .light-box-zoom-trigger');
    if (!mediaSlides.length) return;
    mediaSlides.forEach((slide) => {
      slide.addEventListener('click', () => {
        const modal = document.querySelector(slide.getAttribute('data-modal'));
        if (modal) modal.showModal(slide);
      });
    });
    this.querySelector('[id^="ModalClose-"]').addEventListener('click', this.hideModal.bind(this, false));
    this.addEventListener('pointerup', (event) => {
      if (event.pointerType === 'mouse') this.hideModal();
    });
  }

  showModal(opener) {
    this.openedBy = opener;
    document.body.classList.add('overflow-hidden');
    this.setAttribute('open', '');
    this.showActiveMedia();
  }

  hideModal() {
    document.body.classList.remove('overflow-hidden');
    this.removeAttribute('open');
  }

  showActiveMedia() {
    this.querySelectorAll(
      `[data-media-id]:not([data-media-id="${this.openedBy.getAttribute('data-media-id')}"])`
    ).forEach((element) => {
      element.classList.remove('active');
    });
    const activeMedia = this.querySelector(`[data-media-id="${this.openedBy.getAttribute('data-media-id')}"]`);
    activeMedia.classList.add('active');
    activeMedia.scrollIntoView();
  }
}

if (!customElements.get('product-media-modal')) {
  customElements.define('product-media-modal', ProductMediaModal);
}