# PickupAvailability Web Components

`assets/component-pickup-availability.js` exports two classes: `PickupAvailability` and `PickupAvailabilityDrawer`, registered as `<pickup-availability>` and `<pickup-availability-drawer>` custom elements. These components handle local pickup availability display and drawer interface for viewing pickup locations.

**Source:** [`assets/component-pickup-availability.js`](../../assets/component-pickup-availability.js)

## Overview

The `PickupAvailability` component:
- Fetches pickup availability data for product variants
- Displays pickup availability preview
- Opens drawer with detailed pickup location information
- Handles variant changes and updates availability
- Shows error state with retry functionality

The `PickupAvailabilityDrawer` component:
- Provides a drawer interface for viewing pickup locations
- Handles open/close state management
- Supports keyboard navigation (ESC to close)
- Manages body scroll lock

## Class Structure

### PickupAvailability

```javascript
export class PickupAvailability extends HTMLElement {
  constructor()
  fetchAvailability(variantId)
  onClickRefreshList()
  update(variant)
  renderError()
  renderPreview(sectionInnerHTML)
}
```

### PickupAvailabilityDrawer

```javascript
export class PickupAvailabilityDrawer extends HTMLElement {
  constructor()
  handleBodyClick(evt)
  hide()
  show(focusElement)
}
```

## API Reference

### PickupAvailability

| Method | Description |
|--------|-------------|
| `constructor()` | Initializes component, checks availability attribute, and fetches data |
| `fetchAvailability(variantId)` | Fetches pickup availability from Shopify API |
| `onClickRefreshList()` | Retry handler for failed requests |
| `update(variant)` | Updates availability when variant changes |
| `renderError()` | Displays error state with retry button |
| `renderPreview(sectionInnerHTML)` | Renders availability preview and sets up drawer |

### PickupAvailabilityDrawer

| Method | Description |
|--------|-------------|
| `constructor()` | Sets up close button and keyboard handlers |
| `handleBodyClick(evt)` | Closes drawer when clicking outside |
| `hide()` | Hides drawer and unlocks body scroll |
| `show(focusElement)` | Shows drawer and locks body scroll |

## Method Details

### PickupAvailability.constructor()

```javascript
export class PickupAvailability extends HTMLElement {
  constructor() {
    super();

    if (!this.hasAttribute('available')) return;

    this.errorHtml = this.querySelector('template').content.firstElementChild.cloneNode(true);
    this.onClickRefreshList = this.onClickRefreshList.bind(this);
    this.fetchAvailability(this.dataset.variantId);
  }
}
```

**Behavior:**
- Only initializes if `available` attribute is present
- Clones error template for error state
- Fetches availability for initial variant

### PickupAvailability.fetchAvailability(variantId)

```javascript
  fetchAvailability(variantId) {
    if (!variantId) return;

    let rootUrl = this.dataset.rootUrl;
    if (!rootUrl.endsWith('/')) {
      rootUrl = rootUrl + '/';
    }
    const variantSectionUrl = `${rootUrl}variants/${variantId}/?section_id=pickup-availability`;

    fetch(variantSectionUrl)
      .then((response) => response.text())
      .then((text) => {
        const sectionInnerHTML = new DOMParser()
          .parseFromString(text, 'text/html')
          .querySelector('.shopify-section');
        this.renderPreview(sectionInnerHTML);
      })
      .catch((e) => {
        const button = this.querySelector('button');
        if (button) button.removeEventListener('click', this.onClickRefreshList);
        this.renderError();
      });
  }
```

**Behavior:**
1. Validates variant ID
2. Constructs API URL from `data-root-url` and variant ID
3. Fetches pickup availability section
4. Renders preview or error state

### PickupAvailability.update(variant)

```javascript
  update(variant) {
    if (variant?.available) {
      this.fetchAvailability(variant.id);
    } else {
      this.removeAttribute('available');
      this.innerHTML = '';
    }
  }
```

**Behavior:**
- Fetches availability if variant is available
- Clears content if variant unavailable

### PickupAvailability.renderPreview(sectionInnerHTML)

```javascript
  renderPreview(sectionInnerHTML) {
    const drawer = document.querySelector('pickup-availability-drawer');
    // if (drawer) drawer.remove();
    if (!sectionInnerHTML.querySelector('pickup-availability-preview')) {
      this.innerHTML = '';
      this.removeAttribute('available');
      return;
    }

    this.innerHTML = sectionInnerHTML.querySelector('pickup-availability-preview').outerHTML;
    this.setAttribute('available', '');

    document.body.appendChild(sectionInnerHTML.querySelector('pickup-availability-drawer'));
    const colorClassesToApply = this.dataset.productPageColorScheme.split(' ');
    colorClassesToApply.forEach((colorClass) => {
      document.querySelector('pickup-availability-drawer').classList.add(colorClass);
    });

    const button = this.querySelector('button');
    if (button)
      button.addEventListener('click', (evt) => {
        document.querySelector('pickup-availability-drawer').show(evt.target);
      });
  }
```

**Behavior:**
- Extracts preview markup from fetched section
- Updates component HTML
- Appends drawer to body
- Applies color scheme classes
- Sets up drawer open button

### PickupAvailabilityDrawer.show(focusElement)

```javascript
  show(focusElement) {
    this.focusElement = focusElement;
    this.setAttribute('open', '');
    document.body.addEventListener('click', this.onBodyClick);
    document.body.classList.add('overflow-hidden');
  }
```

**Behavior:**
- Stores focus element reference
- Sets `open` attribute
- Adds click-outside listener
- Locks body scroll

## Custom Element Definitions

```javascript
if (!customElements.get('pickup-availability')) {
  customElements.define('pickup-availability', PickupAvailability);
}
```

```javascript
if (!customElements.get('pickup-availability-drawer')) {
  customElements.define('pickup-availability-drawer', PickupAvailabilityDrawer);
}
```

## Integration with Shopify Liquid

```liquid
<pickup-availability
  data-variant-id="{{ product.selected_or_first_available_variant.id }}"
  data-root-url="{{ routes.root_url }}"
  data-product-page-color-scheme="{{ section.settings.color_scheme }}"
  {% if product.selected_or_first_available_variant.available %}available{% endif %}
>
  <template>
    <div class="pickup-availability__error">
      <p>Unable to load pickup availability</p>
      <button>Try again</button>
    </div>
  </template>
</pickup-availability>

<script src="{{ 'component-pickup-availability.js' | asset_url }}" type="module"></script>
```

## Shopify Section Setup

Create `sections/pickup-availability.liquid`:

```liquid
<div class="shopify-section">
  <pickup-availability-preview>
    <button id="ShowPickupAvailabilityDrawer">
      Check availability
    </button>
  </pickup-availability-preview>

  <pickup-availability-drawer>
    <button>Close</button>
    {% for location in pickup_locations %}
      <div class="pickup-location">
        <h3>{{ location.name }}</h3>
        <p>{{ location.address }}</p>
      </div>
    {% endfor %}
  </pickup-availability-drawer>
</div>
```

## Implementation Notes

- `PickupAvailability` requires `available` attribute to initialize
- Component needs `data-variant-id` and `data-root-url` attributes
- Error template must be provided in `<template>` element
- Drawer is appended to body for proper z-index stacking
- Color scheme classes are applied from `data-product-page-color-scheme`
- Drawer button must have ID `ShowPickupAvailabilityDrawer` for click-outside detection
- The component automatically handles variant changes via `update()` method
- Fetch URL format: `{rootUrl}/variants/{variantId}/?section_id=pickup-availability`
- Preview element must be `<pickup-availability-preview>`
- Drawer element must be `<pickup-availability-drawer>`
- Body scroll is locked when drawer is open
- ESC key closes the drawer
- Click-outside detection closes the drawer

