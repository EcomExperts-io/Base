export class ProductMediaMagnifier extends HTMLElement {
  constructor() {
    super();
    this.zoomRatio = 2;
    this.overlay = null;
  }

  createOverlay(image) {
    const overlayImage = document.createElement('img');
    overlayImage.setAttribute('src', `${image.src}`);
    this.overlay = document.createElement('div');
    this.prepareOverlay(this.overlay, overlayImage);

    // image.style.opacity = '50%';
    this.toggleLoadingSpinner(image);

    overlayImage.onload = () => {
      this.toggleLoadingSpinner(image);
      image.parentElement.insertBefore(this.overlay, image);
      image.style.opacity = '100%';
    };

    return this.overlay;
  }

  prepareOverlay(container, image) {
    container.setAttribute('class', 'image-magnify-full-size');
    container.setAttribute('aria-hidden', 'true');
    container.style.backgroundImage = `url('${image.src}')`;
    container.style.backgroundColor = 'var(--gradient-background)';
  }

  toggleLoadingSpinner(image) {
    const loadingSpinner = image.parentElement.parentElement.querySelector(`.loading__spinner`);
    if (!loadingSpinner) return;
    loadingSpinner.classList.toggle('hidden');
  }

  moveWithHover(image, event) {
    // calculate mouse position
    const ratio = image.height / image.width;
    const container = event.target.getBoundingClientRect();
    const xPosition = event.clientX - container.left;
    const yPosition = event.clientY - container.top;
    const xPercent = `${xPosition / (image.clientWidth / 100)}%`;
    const yPercent = `${yPosition / ((image.clientWidth * ratio) / 100)}%`;

    // determine what to show in the frame
    this.overlay.style.backgroundPosition = `${xPercent} ${yPercent}`;
    this.overlay.style.backgroundSize = `${image.width * this.zoomRatio}px`;
  }

  magnify(image, event) {
    const overlay = this.createOverlay(image);

    overlay.onclick = () => overlay.remove();
    overlay.onmousemove = (e) => this.moveWithHover(image, e);
    overlay.onmouseleave = () => overlay.remove();

    // Initial position
    if (event) {
      this.moveWithHover(image, event);
    }
  }

  connectedCallback() {
    const image = this.querySelector('img');
    image.onclick = (event) => {
      this.magnify(image, event);
    };
    
  }
}


if (!customElements.get('product-media-magnify')) {
  customElements.define('product-media-magnify', ProductMediaMagnifier);
}