# ShareButton Web Component

`assets/component-product-share-button.js` exports the `ShareButton` class, which extends `HTMLElement` and is registered as the custom element `<share-button>`. This component provides native Web Share API support with a fallback to copy-to-clipboard functionality for sharing product URLs.

**Source:** [`assets/component-product-share-button.js`](../../assets/component-product-share-button.js)

## Overview

The `ShareButton` component:
- Uses native Web Share API when available (mobile devices)
- Falls back to copy-to-clipboard for browsers without native sharing
- Provides a details/summary dropdown for fallback sharing options
- Shows success feedback when URL is copied
- Automatically detects browser capabilities and sets up appropriate UI

## Class Structure

```javascript
export class ShareButton extends HTMLElement {
  constructor()
  getUrlToShare()
  initShareButton()
  setupNativeShare()
  setupFallbackShare()
  copyToClipboard(urlInput, successMessage, closeButton)
  showSuccessMessage(successMessage, closeButton)
  resetSuccessMessage(detailsElement, successMessage, closeButton)
}
```

## API Reference

| Method | Description |
|--------|-------------|
| `constructor()` | Initializes the component, gets URL to share, and sets up sharing UI |
| `getUrlToShare()` | Retrieves URL from input element or falls back to current page URL |
| `initShareButton()` | Detects browser capabilities and initializes appropriate sharing method |
| `setupNativeShare()` | Sets up native Web Share API sharing |
| `setupFallbackShare()` | Sets up copy-to-clipboard fallback with details dropdown |
| `copyToClipboard()` | Copies URL to clipboard using modern or legacy API |
| `showSuccessMessage()` | Displays success feedback when URL is copied |
| `resetSuccessMessage()` | Resets the success message and closes the dropdown |

## Method Details

### constructor()

```javascript
export class ShareButton extends HTMLElement {
  constructor() {
    super();
    this.urlToShare = this.getUrlToShare();
    this.initShareButton();
  }
}
```

**Initialization:**
- Gets the URL to share (from input or current page)
- Detects browser capabilities and initializes appropriate sharing method

### getUrlToShare()

```javascript
  getUrlToShare() {
    const urlInput = this.querySelector('input');
    return urlInput?.value || document.location.href;
  }
```

**Behavior:**
- Returns URL from input element if present
- Falls back to current page URL if no input found

### initShareButton()

```javascript
  initShareButton() {
    if (navigator.share) {
      this.setupNativeShare();
    } else {
      this.setupFallbackShare();
    }
  }
```

**Behavior:**
- Checks for `navigator.share` support
- Sets up native sharing if available, otherwise uses fallback

### setupNativeShare()

```javascript
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
```

**Behavior:**
- Hides the details dropdown (fallback UI)
- Shows the native share button
- Opens native share dialog when clicked
- Handles share cancellation gracefully

### setupFallbackShare()

```javascript
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
```

**Behavior:**
- Sets up details/summary dropdown toggle
- Closes dropdown when clicking outside
- Handles copy button click
- Handles close button click to reset state

### copyToClipboard()

```javascript
  copyToClipboard(urlInput, successMessage, closeButton) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(this.urlToShare).then(() => this.showSuccessMessage(successMessage, closeButton));
    } else {
      urlInput.select();
      document.execCommand('copy');
      this.showSuccessMessage(successMessage, closeButton);
    }
  }
```

**Behavior:**
- Uses modern Clipboard API if available
- Falls back to legacy `execCommand('copy')` for older browsers
- Shows success message after copying

## Custom Element Definition

```javascript
if (!customElements.get('share-button')) {
  customElements.define('share-button', ShareButton);
}
```

Ensures the element is registered only once across bundles or hot reload sessions.

## Integration with Shopify Liquid

### Native Share (Mobile)

```liquid
<share-button>
  <input type="hidden" value="{{ shop.url }}{{ product.url }}">
  <details hidden>
    <!-- Fallback UI hidden on mobile -->
  </details>
  <button>Share</button>
</share-button>
```

### Fallback Share (Desktop)

```liquid
<share-button>
  <input type="text" value="{{ shop.url }}{{ product.url }}" readonly>
  <details>
    <summary>Share</summary>
    <button class="share-button__copy">Copy link</button>
    <span id="ShareMessage" class="hidden"></span>
    <button class="share-button__close" class="hidden">Close</button>
  </details>
</share-button>
```

## Implementation Notes

- The component automatically detects browser capabilities and shows appropriate UI
- For native sharing, the details element is hidden and button is shown
- For fallback, the details dropdown is used with copy functionality
- URL input is optional—component falls back to `document.location.href` if not provided
- Success message element should have an ID starting with `ShareMessage`
- Copy and close buttons should have classes `.share-button__copy` and `.share-button__close`
- The component handles both modern Clipboard API and legacy `execCommand` for maximum compatibility
- Click-outside detection automatically closes the dropdown

