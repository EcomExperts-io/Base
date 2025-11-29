# QuickAdd Web Component

`assets/component-quick-add.js` exports the `QuickAdd` class, which extends `HTMLElement` and is registered as the custom element `<quick-add-modal>`. This component provides a modal interface for quick product viewing and adding to cart, commonly used in product grids and collection pages.

**Source:** [`assets/component-quick-add.js`](../../assets/component-quick-add.js)

## Overview

The `QuickAdd` component:
- Opens a modal dialog for quick product viewing
- Fetches product information dynamically via AJAX
- Preprocesses content to prevent ID conflicts in modal contexts
- Handles cart add events and automatically closes modal on success
- Supports keyboard navigation (ESC to close)
- Manages body scroll lock when modal is open
- Reinjects scripts from fetched content to ensure functionality

## Class Structure

```javascript
export class QuickAdd extends HTMLElement {
  constructor()
  connectedCallback()
  disconnectedCallback()
  onCartRequestEnd(event)
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
| `constructor()` | Initializes the component, sets up modal, binds events, and prepares cart listener |
| `connectedCallback()` | Lifecycle hook that listens for cart request end events |
| `disconnectedCallback()` | Lifecycle hook that removes cart event listener |
| `onCartRequestEnd(event)` | Handles cart add completion and closes modal |
| `setupModal()` | Queries modal elements and appends component to body |
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
  }
}
```

**Initialization:**
- Sets up modal references
- Appends component to document body
- Binds events
- Prepares cart event handler

### setupModal()

```javascript
  setupModal() {
    this.modal = this.querySelector('[role="dialog"]');
    this.modalContent = this.querySelector('[id^="QuickAddInfo-"]');
    document.body.appendChild(this);
  }
```

**Behavior:**
- Finds modal dialog element
- Finds modal content container (ID starting with `QuickAddInfo-`)
- Moves component to body for proper z-index stacking

### show(opener)

```javascript
  show(opener) {
    this.openedBy = opener;

    // Only set aria-disabled and show spinner if it's a quick-add operation
    // with a loading spinner element
    if (opener && opener.querySelector('.loading__spinner')) {
      opener.setAttribute('aria-disabled', true);
      opener.querySelector('.loading__spinner').classList.remove('hidden');

      fetch(opener.getAttribute('data-product-url'))
        .then(response => response.text())
        .then(responseText => {
          const productElement = new DOMParser()
            .parseFromString(responseText, 'text/html')
            .querySelector('product-info');

          this.preprocessContent(productElement);
          this.setContent(productElement.outerHTML);

          document.body.classList.add('overflow-hidden');
          this.setAttribute('open', '');

          if (window.Shopify?.PaymentButton) Shopify.PaymentButton.init();
          if (window.ProductModel) window.ProductModel.loadShopifyXR();
        })
        .finally(() => {
          opener.removeAttribute('aria-disabled');
          opener.querySelector('.loading__spinner').classList.add('hidden');
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
2. If opener has loading spinner, shows loading state
3. Fetches product HTML from `data-product-url` attribute
4. Parses response and extracts `product-info` element
5. Preprocesses content to prevent ID conflicts
6. Sets modal content and reinjects scripts
7. Locks body scroll and opens modal
8. Initializes Shopify PaymentButton and ProductModel if available
9. Hides loading spinner when complete

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
    const { requestState } = event.detail || {};
    if (requestState?.requestType === 'add' && requestState?.responseData?.ok) {
      document.body.classList.remove('overflow-hidden');

      document.querySelectorAll('quick-add-modal').forEach((modal) => {
        modal.removeAttribute('open');
        modal.modalContent.innerHTML = '';
      });
    }
  }
```

**Behavior:**
- Listens for liquid-ajax-cart add-to-cart completion
- Closes all quick-add modals when add succeeds
- Unlocks body scroll
- Clears modal content

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
- Loading spinner element should have class `.loading__spinner` and be hidden by default
- The component automatically handles liquid-ajax-cart integration
- Modal is appended to body for proper z-index stacking
- Content is preprocessed to prevent ID conflicts with main page
- Scripts are automatically reinjected to ensure functionality
- Body scroll is locked when modal is open
- ESC key and outside clicks close the modal
- The component supports both quick-add (with fetch) and static modals (without fetch)

