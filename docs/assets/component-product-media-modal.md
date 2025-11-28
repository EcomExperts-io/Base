# ProductMediaModal Web Component

`assets/component-product-media-modal.js` exports the `ProductMediaModal` class, which extends `HTMLElement` and is registered as the custom element `<product-media-modal>`. This component provides a full-screen modal view for product media images, allowing users to view product images in a larger format.

**Source:** [`assets/component-product-media-modal.js`](../../assets/component-product-media-modal.js)

## Overview

The `ProductMediaModal` component:
- Opens a modal dialog for viewing product media in full-screen
- Synchronizes with media gallery triggers (lightbox zoom buttons)
- Highlights the active media item when opened
- Supports keyboard navigation (ESC to close)
- Supports mouse click outside to close
- Manages body scroll lock when modal is open

## Class Structure

```javascript
export class ProductMediaModal extends HTMLElement {
  constructor()
  showModal(opener)
  hideModal()
  showActiveMedia()
}
```

## API Reference

| Method | Description |
|--------|-------------|
| `constructor()` | Initializes the component, sets up trigger listeners and close handlers |
| `showModal(opener)` | Opens the modal and displays the active media item |
| `hideModal()` | Closes the modal and unlocks body scroll |
| `showActiveMedia()` | Highlights and scrolls to the active media item in the modal |

## Method Details

### constructor()

```javascript
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
}
```

**Initialization:**
- Finds all lightbox zoom trigger elements in media gallery
- Attaches click listeners to each trigger
- Sets up close button handler
- Sets up pointer event handler for outside clicks (mouse only)

**Note:** The component queries triggers from the entire document, not just within itself, allowing triggers to be anywhere in the media gallery.

### showModal(opener)

```javascript
  showModal(opener) {
    this.openedBy = opener;
    document.body.classList.add('overflow-hidden');
    this.setAttribute('open', '');
    this.showActiveMedia();
  }
```

**Behavior:**
1. Stores reference to the opener element (trigger that opened modal)
2. Locks body scroll
3. Sets `open` attribute to show modal
4. Highlights and scrolls to active media

### showActiveMedia()

```javascript
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
```

**Behavior:**
- Removes `active` class from all media items
- Finds media item matching opener's `data-media-id`
- Adds `active` class to matching item
- Scrolls active item into view

### hideModal()

```javascript
  hideModal() {
    document.body.classList.remove('overflow-hidden');
    this.removeAttribute('open');
  }
```

**Behavior:**
- Unlocks body scroll
- Removes `open` attribute to hide modal

## Custom Element Definition

```javascript
if (!customElements.get('product-media-modal')) {
  customElements.define('product-media-modal', ProductMediaModal);
}
```

Ensures the element is registered only once across bundles or hot reload sessions.

## Integration with Shopify Liquid

```liquid
<!-- Media Gallery with Lightbox Triggers -->
<div class="media-gallery">
  {% for media in product.media %}
    <div class="light-box-zoom-trigger" 
         data-media-id="{{ media.id }}"
         data-modal="#ProductMediaModal">
      <img src="{{ media | image_url }}" alt="{{ media.alt }}">
    </div>
  {% endfor %}
</div>

<!-- Product Media Modal -->
<product-media-modal id="ProductMediaModal">
  <button id="ModalClose-{{ section.id }}">Close</button>
  
  {% for media in product.media %}
    <div data-media-id="{{ media.id }}">
      <img src="{{ media | image_url: width: 2000 }}" alt="{{ media.alt }}">
    </div>
  {% endfor %}
</product-media-modal>

<script src="{{ 'component-product-media-modal.js' | asset_url }}" type="module"></script>
```

## Implementation Notes

- Lightbox triggers must have class `.light-box-zoom-trigger` and be inside `.media-gallery`
- Triggers must have `data-modal` attribute pointing to modal selector (e.g., `#ProductMediaModal`)
- Triggers must have `data-media-id` attribute matching the media ID
- Modal media items must have `data-media-id` attributes matching trigger IDs
- Close button should have an ID starting with `ModalClose-`
- Active media items receive `.active` class for styling
- The component uses `pointerup` events but only responds to mouse clicks (not touch)
- Body scroll is automatically locked when modal is open
- ESC key support can be added via additional event listener if needed
- The modal queries triggers from the entire document, allowing flexible placement

