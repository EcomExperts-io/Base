# QuickAdd Web Component

`assets/component-quick-add.js` exports the `QuickAdd` class, which extends `HTMLElement` and is registered as the custom element `<quick-add-modal>`. This component provides a modal interface for quick product viewing and adding to cart, commonly used in product grids and collection pages.

**Source:** [`assets/component-quick-add.js`](../../assets/component-quick-add.js)

## Overview

The `QuickAdd` component:
- Opens a modal dialog for quick product viewing
- Fetches product information dynamically via AJAX
- Preprocesses content to prevent ID conflicts in modal contexts
- Listens for the cart engine's `cart:change` event and automatically closes modals after a successful add
- Shows the quick-add icon spinner while an add-to-cart form submits
- Supports keyboard navigation (ESC to close)
- Manages body scroll lock when modal is open
- Reinjects scripts from fetched content to ensure functionality

## Class Structure

```javascript
export class QuickAdd extends HTMLElement {
  constructor()
  connectedCallback()
  disconnectedCallback()
  setupAjaxCartButtons()
  toggleSpinner(button, show)
  onCartRequestEnd(event)
  resetAllSpinners()
  setupModal()
  bindEvents()
  show(opener)
  hide()
  preprocessContent(element)
  setContent(html)
}
```

## API Reference

| Method | Description |
|--------|-------------|
| `constructor()` | Initializes the component, sets up modal, binds events, and wires the add-to-cart submit hook |
| `connectedCallback()` | Lifecycle hook that appends the component to body and listens for `cart:change` |
| `disconnectedCallback()` | Lifecycle hook that removes the `cart:change` listener |
| `setupAjaxCartButtons()` | Document-level submit hook on `form[action*="/cart/add"]` to show button spinners |
| `toggleSpinner(button, show)` | Toggles spinner/icon/text visibility inside a quick-add button |
| `onCartRequestEnd(event)` | Handles `cart:change` add actions: closes modals and resets spinners |
| `resetAllSpinners()` | Restores all quick-add icon buttons to their idle state |
| `setupModal()` | Queries modal elements |
| `bindEvents()` | Attaches click, keyboard, and outside-click event listeners |
| `show(opener)` | Fetches product data and displays modal |
| `hide()` | Closes modal and clears content |
| `preprocessContent(element)` | Modifies product info to prevent ID conflicts in modal |
| `setContent(html)` | Sets modal content and reinjects scripts |

## Method Details

### constructor()

```javascript
export class QuickAdd extends HTMLElement {
  constructor() {
    super();
    this.modal = null;
    this.modalContent = null;
    this.setupModal();
    this.bindEvents();
    this.onCartRequestEnd = this.onCartRequestEnd.bind(this);
    this.setupAjaxCartButtons();
  }
}
```

**Initialization:**
- Sets up modal references
- Binds events
- Prepares cart event handler
- Wires the document-level add-to-cart submit hook

### setupAjaxCartButtons()

```javascript
  setupAjaxCartButtons() {
    document.addEventListener('submit', (event) => {
      const form = event.target;
      if (!(form instanceof HTMLFormElement)) return;
      if (!(form.getAttribute('action') || '').includes('/cart/add')) return;

      const button = form.querySelector('.quick-add__icon-button');
      if (button) this.toggleSpinner(button, true);
    });
  }
```

**Behavior:**
- Matches submits on any `form[action*="/cart/add"]` — the same selector the cart engine uses (there is no wrapper element around product forms anymore)
- Shows the spinner on the form's `.quick-add__icon-button` while the add request runs

### setupModal()

```javascript
  setupModal() {
    this.modal = this.querySelector('[role="dialog"]');
    this.modalContent = this.querySelector('[id^="QuickAddInfo-"]');
  }
```

**Behavior:**
- Finds modal dialog element
- Finds modal content container (ID starting with `QuickAddInfo-`)
- `connectedCallback()` then moves the component to `document.body` for proper z-index stacking and subscribes to `cart:change`

### show(opener)

```javascript
  show(opener) {
    this.openedBy = opener;

    if (opener && opener.getAttribute('data-product-url')) {
      opener.setAttribute('aria-disabled', true);

      fetch(opener.getAttribute('data-product-url'))
        .then(response => response.text())
        .then(responseText => {
          const productElement = new DOMParser()
            .parseFromString(responseText, 'text/html')
            .querySelector('product-info');

          if (!productElement) {
            console.error('Product info not found in response');
            return;
          }

          this.preprocessContent(productElement);
          this.setContent(productElement.outerHTML);

          document.body.classList.add('overflow-hidden');
          this.setAttribute('open', '');

          this.resetAllSpinners();

          if (window.Shopify?.PaymentButton) Shopify.PaymentButton.init();
          if (window.ProductModel) window.ProductModel.loadShopifyXR();
        })
        .catch(error => {
          console.error('Error loading product:', error);
        })
        .finally(() => {
          opener.removeAttribute('aria-disabled');
        });
    } else {
      // For other modals (like monogram popup) that don't need fetch
      document.body.classList.add('overflow-hidden');
      this.setAttribute('open', '');
    }
  }
```

**Behavior:**
1. Stores reference to opener element
2. If opener has a `data-product-url`, marks it `aria-disabled` while loading
3. Fetches product HTML from `data-product-url` attribute
4. Parses response and extracts `product-info` element
5. Preprocesses content to prevent ID conflicts
6. Sets modal content and reinjects scripts
7. Locks body scroll and opens modal
8. Resets any active quick-add button spinners
9. Initializes Shopify PaymentButton and ProductModel if available

### preprocessContent(element)

```javascript
  preprocessContent(element) {
    const uniqueSectionId = `${element.dataset.section}-modal-${Date.now()}`;
    element.innerHTML = element.innerHTML.replaceAll(element.dataset.section, uniqueSectionId);
    element.dataset.section = uniqueSectionId;
    element.dataset.updateUrl = 'false';
    element.querySelector('pickup-availability')?.remove();
    element.querySelector('script[src*="component-pickup-availability.js"]')?.remove();
    element.querySelector('product-recommendations')?.remove();
    element.querySelector('script[src*="product-recommendations.js"]')?.remove();
  }
```

**Behavior:**
- Creates unique section ID with timestamp to prevent conflicts
- Replaces all section ID references in HTML
- Sets `data-update-url="false"` to prevent URL updates in modal
- Removes pickup availability and product recommendations (not needed in quick-add)

### setContent(html)

```javascript
  setContent(html) {
    this.modalContent.innerHTML = html;
    // Reinject scripts
    this.modalContent.querySelectorAll('script').forEach(oldScript => {
      const newScript = document.createElement('script');
      Array.from(oldScript.attributes).forEach(attr => {
        newScript.setAttribute(attr.name, attr.value);
      });
      newScript.textContent = oldScript.textContent;
      oldScript.parentNode.replaceChild(newScript, oldScript);
    });
  }
```

**Behavior:**
- Sets modal content HTML
- Reinjects all script elements (scripts don't execute when set via innerHTML)
- Preserves all script attributes and content

### onCartRequestEnd(event)

```javascript
  onCartRequestEnd(event) {
    if (event.detail?.action === 'add') {
      document.body.classList.remove('overflow-hidden');

      document.querySelectorAll('quick-add-modal').forEach((modal) => {
        modal.removeAttribute('open');
        if (modal.modalContent) {
          modal.modalContent.innerHTML = '';
        }
      });

      this.resetAllSpinners();
    }
  }
```

**Behavior:**
- Listens for the cart engine's `cart:change` event (which only fires on success) and reacts to `action === 'add'`
- Closes all quick-add modals when an add succeeds
- Unlocks body scroll
- Clears modal content
- Resets all quick-add button spinners

## Custom Element Definition

```javascript
if (!customElements.get('quick-add-modal')) {
  customElements.define('quick-add-modal', QuickAdd);
}
```

Ensures the element is registered only once across bundles or hot reload sessions.

## Integration with Shopify Liquid

```liquid
<!-- Quick Add Button -->
<modal-opener data-modal="#QuickAddModal-{{ product.id }}">
  <button data-product-url="{{ product.url }}">
    <span class="loading__spinner hidden">Loading...</span>
    Quick add
  </button>
</modal-opener>

<!-- Quick Add Modal -->
<quick-add-modal id="QuickAddModal-{{ product.id }}">
  <div role="dialog">
    <button id="ModalClose-{{ product.id }}">Close</button>
    <div id="QuickAddInfo-{{ product.id }}">
      <!-- Product info will be loaded here -->
    </div>
  </div>
</quick-add-modal>

<script src="{{ 'component-quick-add.js' | asset_url }}" type="module"></script>
```

## Implementation Notes

- The modal must have a `[role="dialog"]` element
- Modal content container must have an ID starting with `QuickAddInfo-`
- Close button should have an ID starting with `ModalClose-`
- Quick-add buttons should have `data-product-url` attribute with product URL
- Quick-add icon buttons use `.add-to-cart-icon-spinner`, `.add-to-cart-icon`, and `.add-to-cart-text__content` spans for the spinner toggle
- The component integrates with the native cart engine: it hooks `form[action*="/cart/add"]` submits for spinners and listens for `cart:change` to close modals
- Modal is appended to body for proper z-index stacking
- Content is preprocessed to prevent ID conflicts with main page
- Scripts are automatically reinjected to ensure functionality
- Body scroll is locked when modal is open
- ESC key and outside clicks close the modal
- The component supports both quick-add (with fetch) and static modals (without fetch)

