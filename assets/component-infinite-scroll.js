export class InfiniteScroll extends HTMLElement {
  constructor() {
    super();
    this.anchor = this.querySelector("a");
    if (!this.anchor) return;

    this.observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          this.loadNextPage();
        }
      });
    });

    this.observer.observe(this);
  }

  async loadNextPage() {
    this.observer.disconnect();

    this.anchor.style.display = "flex";
    this.anchor.innerText = "Loading...";

    const url = this.anchor.getAttribute("href");
    if (!url) return;

    try {
      const response = await fetch(url);
      const text = await response.text();
      const html = new DOMParser().parseFromString(text, "text/html");

      // Grab the product grid from the next page
      const newGrid = html.querySelector("[data-product-grid]");
      const grid = document.querySelector("[data-product-grid]");

      if (newGrid && grid) {
        Array.from(newGrid.children).forEach((child) => {
          grid.appendChild(child);
        });
      }

      // Handle next infinite scroll
      const newInfinite = html.querySelector("infinite-scroll");
      if (newInfinite) {
        this.replaceWith(newInfinite);
      } else {
        this.remove();
      }
    } catch (err) {
      console.error("InfiniteScroll error:", err);
    }

    this.anchor.style.display = "none";
    this.anchor.innerText = "";
  }
}

if (!customElements.get("infinite-scroll")) {
  customElements.define("infinite-scroll", InfiniteScroll);
}