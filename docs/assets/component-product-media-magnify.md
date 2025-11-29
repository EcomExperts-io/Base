# ProductMediaMagnifier Web Component

`assets/component-product-media-magnify.js` exports the `ProductMediaMagnifier` class, which extends `HTMLElement` and is registered as the custom element `<product-media-magnify>`. This component provides an image magnification feature that shows a zoomed view of product images on hover/click.

**Source:** [`assets/component-product-media-magnify.js`](../../assets/component-product-media-magnify.js)

## Overview

The `ProductMediaMagnifier` component:
- Creates a magnified overlay of product images
- Tracks mouse position to show corresponding zoomed area
- Uses a configurable zoom ratio (default 2x)
- Shows loading spinner while image loads
- Removes overlay on click or mouse leave
- Calculates zoom position based on image aspect ratio

## Class Structure

```javascript
export class ProductMediaMagnifier extends HTMLElement {
  constructor()
  connectedCallback()
  createOverlay(image)
  prepareOverlay(container, image)
  toggleLoadingSpinner(image)
  moveWithHover(image, event)
  magnify(image, event)
}
```

## API Reference

| Method | Description |
|--------|-------------|
| `constructor()` | Initializes the component with zoom ratio and overlay reference |
| `connectedCallback()` | Lifecycle hook that sets up click handler on image |
| `createOverlay(image)` | Creates the magnified overlay element and handles image loading |
| `prepareOverlay(container, image)` | Sets up overlay styling and background image |
| `toggleLoadingSpinner(image)` | Shows/hides loading spinner during image load |
| `moveWithHover(image, event)` | Calculates and updates overlay position based on mouse position |
| `magnify(image, event)` | Main method that creates overlay and sets up interaction handlers |

## Method Details

### constructor()

```javascript
export class ProductMediaMagnifier extends HTMLElement {
  constructor() {
    super();
    this.zoomRatio = 2;
    this.overlay = null;
  }
}
```

**Initialization:**
- Sets default zoom ratio to 2x
- Initializes overlay reference as null

### connectedCallback()

```javascript
  connectedCallback() {
    const image = this.querySelector('img');
    image.onclick = (event) => {
      this.magnify(image, event);
    };
    
  }
```

**Behavior:**
- Finds the image element within the component
- Attaches click handler to trigger magnification

### magnify(image, event)

```javascript
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
```

**Behavior:**
1. Creates the magnified overlay
2. Sets up click handler to remove overlay
3. Sets up mousemove handler to track cursor position
4. Sets up mouseleave handler to remove overlay
5. Sets initial position if event provided

### createOverlay(image)

```javascript
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
```

**Behavior:**
- Creates overlay div and image element
- Prepares overlay styling
- Shows loading spinner
- Inserts overlay before image when loaded
- Returns overlay element

### moveWithHover(image, event)

```javascript
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
```

**Behavior:**
- Calculates image aspect ratio
- Gets mouse position relative to image container
- Converts position to percentages
- Updates overlay background position to show corresponding zoomed area
- Sets background size based on zoom ratio

### prepareOverlay(container, image)

```javascript
  prepareOverlay(container, image) {
    container.setAttribute('class', 'image-magnify-full-size');
    container.setAttribute('aria-hidden', 'true');
    container.style.backgroundImage = `url('${image.src}')`;
    container.style.backgroundColor = 'var(--gradient-background)';
  }
```

**Behavior:**
- Sets overlay class for styling
- Marks as aria-hidden for accessibility
- Sets background image to same source as original
- Sets background color from CSS variable

## Custom Element Definition

```javascript
if (!customElements.get('product-media-magnify')) {
  customElements.define('product-media-magnify', ProductMediaMagnifier);
}
```

Ensures the element is registered only once across bundles or hot reload sessions.

## Integration with Shopify Liquid

```liquid
<product-media-magnify>
  <img 
    src="{{ product.featured_image | image_url: width: 800 }}" 
    alt="{{ product.featured_image.alt }}"
  >
  <div class="loading__spinner hidden">
    <!-- Loading spinner -->
  </div>
</product-media-magnify>

<script src="{{ 'component-product-media-magnify.js' | asset_url }}" type="module"></script>
```

## CSS Requirements

```css
.image-magnify-full-size {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  background-repeat: no-repeat;
  background-size: cover;
  pointer-events: auto;
  z-index: 10;
}

.loading__spinner {
  /* Loading spinner styles */
}
```

## Implementation Notes

- The component requires a single `<img>` element as a direct child
- Loading spinner should be a sibling of the image with class `.loading__spinner`
- The overlay uses the same image source as the original for zooming
- Zoom ratio is configurable via `this.zoomRatio` (default: 2)
- Overlay is positioned absolutely and covers the entire image area
- Background position is calculated based on mouse position and image aspect ratio
- The component automatically handles image loading states
- Overlay is removed on click or mouse leave
- The component uses CSS custom properties for background color (`--gradient-background`)
- Image opacity is managed during overlay creation (currently commented out in code)

