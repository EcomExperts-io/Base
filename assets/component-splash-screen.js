const STORAGE_KEY_FALLBACK = 'splashScreenSeen';
const FADE_DURATION_FALLBACK = 4000;
const BUFFER_OFFSET = 600;

class SplashScreen extends HTMLElement {
  constructor() {
    super();
    this.hideDelay = Number(this.dataset.hideDelay || '600');
    this.storageKey = this.dataset.storageKey || STORAGE_KEY_FALLBACK;
    this.fadeDuration = Number(this.dataset.fadeDuration || FADE_DURATION_FALLBACK);
    this._handleLoad = this._handleLoad.bind(this);
  }

  connectedCallback() {
    this.root = document.documentElement;

    if (this.root.classList.contains('splash-screen-returning')) {
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
    window.setTimeout(() => this._hideSplash(), this.hideDelay);
  }

  _hideSplash() {
    this.setAttribute('data-hidden', 'true');
    this._markSeen();
    this.root.classList.add('splash-screen-returning');

    window.setTimeout(() => {
      this.remove();
    }, this.fadeDuration + BUFFER_OFFSET);
  }
}

if (!customElements.get('splash-screen')) {
  customElements.define('splash-screen', SplashScreen);
}

