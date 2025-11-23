export class ShareButton extends HTMLElement {
  constructor() {
    super();
    this.urlToShare = this.getUrlToShare();
    this.initShareButton();
  }

  getUrlToShare() {
    const urlInput = this.querySelector('input');
    return urlInput?.value || document.location.href;
  }

  initShareButton() {
    if (navigator.share) {
      this.setupNativeShare();
    } else {
      this.setupFallbackShare();
    }
  }

  setupNativeShare() {
    const detailsElement = this.querySelector('details');
    const button = this.querySelector('button');
    detailsElement.setAttribute('hidden', 'hidden');
    button.classList.remove('hidden');

    button.addEventListener('click', (event) => {
      event.preventDefault();
      navigator
        .share({
          url: this.urlToShare,
          title: document.title,
        })
        .catch((error) => console.error('Sharing failed', error));
    });
  }

  setupFallbackShare() {
    const detailsElement = this.querySelector('details');
    const copyButton = this.querySelector('.share-button__copy');
    const closeButton = this.querySelector('.share-button__close');
    const summary = this.querySelector('summary');
    const successMessage = this.querySelector('[id^="ShareMessage"]');
    const urlInput = this.querySelector('input');

    summary.addEventListener('click', (event) => {
      event.preventDefault();
      detailsElement.open = !detailsElement.open;
    });

    document.addEventListener('click', (event) => {
      if (!detailsElement.contains(event.target) && detailsElement.open) {
        detailsElement.open = false;
      }
    });

    copyButton.addEventListener('click', (event) => {
      event.preventDefault();
      this.copyToClipboard(urlInput, successMessage, closeButton);
    });

    closeButton.addEventListener('click', (event) => {
      event.preventDefault();
      this.resetSuccessMessage(detailsElement, successMessage, closeButton);
    });
  }

  copyToClipboard(urlInput, successMessage, closeButton) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(this.urlToShare).then(() => this.showSuccessMessage(successMessage, closeButton));
    } else {
      urlInput.select();
      document.execCommand('copy');
      this.showSuccessMessage(successMessage, closeButton);
    }
  }

  showSuccessMessage(successMessage, closeButton) {
    successMessage.textContent = 'Link copied!';
    successMessage.classList.remove('hidden');
    closeButton.classList.remove('hidden');
    closeButton.focus();
  }

  resetSuccessMessage(detailsElement, successMessage, closeButton) {
    detailsElement.open = false;
    successMessage.classList.add('hidden');
    successMessage.textContent = '';
    closeButton.classList.add('hidden');
  }
}

if (!customElements.get('share-button')) {
  customElements.define('share-button', ShareButton);
}