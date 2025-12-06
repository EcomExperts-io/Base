const STORAGE_KEY_FALLBACK = 'firstVisitSeen';

class FirstVisitOverlay extends HTMLElement {
  constructor() {
    super();
    this.hideDelay = Number(this.dataset.hideDelay || '600');
    this.storageKey = this.dataset.storageKey || STORAGE_KEY_FALLBACK;
    this._handleLoad = this._handleLoad.bind(this);
  }

  connectedCallback() {
    this.root = document.documentElement;

    if (this.root.classList.contains('first-visit-returning')) {
      this.remove();
      return;
    }

    window.addEventListener('load', this._handleLoad, { once: true });
  }

  disconnectedCallback() {
    window.removeEventListener('load', this._handleLoad);
  }

  _markSeen() {
    try {
      sessionStorage.setItem(this.storageKey, '1');
    } catch (_error) {
      // Storage might be unavailable; ignore
    }
  }

  _handleLoad() {
    window.setTimeout(() => this._hideOverlay(), this.hideDelay);
  }

  _hideOverlay() {
    this.setAttribute('data-hidden', 'true');
    this._markSeen();
    this.root.classList.add('first-visit-returning');

    window.setTimeout(() => {
      this.remove();
    }, 250);
  }
}

if (!customElements.get('first-visit-overlay')) {
  customElements.define('first-visit-overlay', FirstVisitOverlay);
}

