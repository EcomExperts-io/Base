class SalesBanner extends HTMLElement {
  constructor() {
    super();
    this.setExclusiveContent = this.setExclusiveContent.bind(this);
  }

  connectedCallback() {
    this.titleEl = this.querySelector('#exclusive-title');
    this.subtitleEl = this.querySelector('#exclusive-subtitle');
    this.btnEl = this.querySelector('#exclusive-btn');
    this.setExclusiveContent();
    window.addEventListener('resize', this.setExclusiveContent);
  }

  disconnectedCallback() {
    window.removeEventListener('resize', this.setExclusiveContent);
  }

  setExclusiveContent() {
    const mobile = window.innerWidth <= 750;
    // Background
    const bg = mobile ? this.dataset.bgMobile : this.dataset.bgDesktop;
    if (bg) this.style.backgroundImage = 'url(' + bg + ')';
    // Title
    const title = mobile ? this.dataset.titleMobile : this.dataset.titleDesktop;
    if (title && this.titleEl) this.titleEl.innerHTML = title;
    const titleColor = mobile ? this.dataset.titleColorMobile : this.dataset.titleColorDesktop;
    if (titleColor && this.titleEl) this.titleEl.style.color = titleColor;
    // Subtitle
    const subtitle = mobile ? this.dataset.subtitleMobile : this.dataset.subtitleDesktop;
    if (subtitle && this.subtitleEl) this.subtitleEl.innerHTML = subtitle;
    const subtitleColor = mobile ? this.dataset.subtitleColorMobile : this.dataset.subtitleColorDesktop;
    if (subtitleColor && this.subtitleEl) this.subtitleEl.style.color = subtitleColor;
    // Button
    const btn = mobile ? this.dataset.buttonMobile : this.dataset.buttonDesktop;
    if (btn && this.btnEl) this.btnEl.innerHTML = btn;
    const btnColor = mobile ? this.dataset.buttonColorMobile : this.dataset.buttonColorDesktop;
    if (btnColor && this.btnEl) this.btnEl.style.color = btnColor;
    const btnBg = mobile ? this.dataset.buttonBgMobile : this.dataset.buttonBgDesktop;
    if (btnBg && this.btnEl) this.btnEl.style.backgroundColor = btnBg;
  }
}

if (!customElements.get('sales-banner')) {
  customElements.define('sales-banner', SalesBanner);
}

// Shopify Theme Editor support: re-initialize on section load
if (window.Shopify && window.Shopify.designMode) {
  document.addEventListener('shopify:section:load', function (e) {
    const banners = e.target.querySelectorAll('sales-banner');
    banners.forEach(banner => {
      if (typeof banner.setExclusiveContent === 'function') {
        banner.setExclusiveContent();
      }
    });
  });
}
