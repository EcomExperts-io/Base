class ShopByCategory extends HTMLElement {
  constructor() {
    super();
    this.collections = this.querySelectorAll(".shop-by-category__collection-item");
    this.currentFeaturedImage = this.querySelector(".shop-by-category__featured-image");

    this.handleImageChangeOnHover = this.handleImageChangeOnHover.bind(this);
  }

  connectedCallback() {
    this.collections.forEach(collection => {
      collection.addEventListener("mouseover", this.handleImageChangeOnHover);
      collection.addEventListener('focus', this.handleImageChangeOnHover);
    });
  }

  handleImageChangeOnHover(event) {
    if (window.innerWidth <= 1080) return;
    console.log("still working");
    const collection = event.currentTarget;
    const featuredImage = collection.dataset.featuredImage;

    if (!featuredImage || !this.currentFeaturedImage)
      return;
    if (this.currentFeaturedImage.src.includes(featuredImage))
      return;

    this.currentFeaturedImage.srcset = "";
    this.currentFeaturedImage.removeAttribute("srcset");
    this.currentFeaturedImage.src = featuredImage;
  }

  disconnectedCallback() {
    this.collections.forEach(collection => {
      collection.removeEventListener("mouseover", this.handleImageChangeOnHover);
      collection.removeEventListener('focus', this.handleImageChangeOnHover);
    });
  }
}

if (!customElements.get("shop-by-category")) {
  customElements.define("shop-by-category", ShopByCategory);
}