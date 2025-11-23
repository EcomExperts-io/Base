export class ProductCard extends HTMLElement {
  constructor() {
    super();
  }

  connectedCallback() {
    this.querySelectorAll('.color-swatch').forEach((s) => s.addEventListener('click', this.onSwatchClick.bind(this)));
  }

  onSwatchClick(event) {
    const swatch = event.target;
    const productImage = this.querySelector(`[data-product-image="${this.dataset.productId}"]`);
    const swatchImageElement = swatch.querySelector('.data-variant-image');
    let newImageUrl = swatchImageElement ? swatchImageElement.getAttribute('src') : null;
    let newSrcset = swatchImageElement ? swatchImageElement.getAttribute('srcset') : null;
    if (newImageUrl === null) {
      newImageUrl = swatch ? swatch.getAttribute('src') : null;
      newSrcset = swatch ? swatch.getAttribute('srcset') : null;
    }
    this.querySelectorAll('.color-swatch').forEach((s) => s.classList.remove('selected'));
    swatch.classList.add('selected');

    if (productImage && newImageUrl) {
      productImage.src = newImageUrl;
      productImage.srcset = newSrcset;
    }
  }
}

if (!customElements.get('product-card')) {
  customElements.define('product-card', ProductCard);
}