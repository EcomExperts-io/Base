# ModalOpener Web Component

`assets/component-modal-opener.js` exports the `ModalOpener` class, which extends `HTMLElement` and is registered as the custom element `<modal-opener>`. This component provides a unified way to open modals throughout the theme, used by quick-add modals, product monogram popups, and other modal types.

**Source:** [`assets/component-modal-opener.js`](../../assets/component-modal-opener.js)

## Overview

The `ModalOpener` component:
- Provides a reusable button/trigger for opening modals
- Works with any modal that implements a `show()` method
- Uses `data-modal` attribute to target the modal element
- Supports any button element as the trigger
- Simplifies modal opening across different modal types

## Class Structure

```javascript
export class ModalOpener extends HTMLElement {
  constructor()
}
```

## API Reference

| Method | Description |
|--------|-------------|
| `constructor()` | Initializes the component, finds button, and sets up click handler |

## Method Details

### constructor()

```javascript
export class ModalOpener extends HTMLElement {
  constructor() {
    super();

    const button = this.querySelector('button');

    if (!button) return;
    button.addEventListener('click', () => {
      const modal = document.querySelector(this.getAttribute('data-modal'));
      if (modal) {
        modal.show(button);
      }
    });
  }
}
```

**Behavior:**
1. Queries for a button element within the component
2. Returns early if no button found
3. Attaches click listener to button
4. Gets modal selector from `data-modal` attribute
5. Queries for modal element in document
6. Calls `show()` method on modal, passing the button as opener

**Note:** The modal must implement a `show(opener)` method that accepts the opener element.

## Custom Element Definition

```javascript
if (!customElements.get('modal-opener')) {
  customElements.define('modal-opener', ModalOpener);
}
```

Ensures the element is registered only once across bundles or hot reload sessions.

## Integration with Shopify Liquid

### Quick Add Modal

```liquid
<modal-opener data-modal="#QuickAddModal-{{ product.id }}">
  <button>
    Quick add
  </button>
</modal-opener>

<quick-add-modal id="QuickAddModal-{{ product.id }}">
  <!-- Modal content -->
</quick-add-modal>
```


## Implementation Notes

- The component requires a `<button>` element as a direct child
- The `data-modal` attribute must contain a valid CSS selector (e.g., `#ModalId` or `.modal-class`)
- The target modal must implement a `show(opener)` method
- The opener button is passed to the modal's `show()` method
- The component works with any modal type (quick-add, custom modals, etc.)
- If no button is found, the component silently fails (no error)
- If modal is not found, nothing happens (no error)
- The component is lightweight and has no dependencies
- Multiple modal openers can exist on the same page
- The same modal can be opened by multiple openers

