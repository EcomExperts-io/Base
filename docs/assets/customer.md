# CustomerAddresses Utility

`assets/customer.js` exports the `CustomerAddresses` class, which manages customer address forms in account pages. This utility handles address creation, editing, deletion, and country/province selector integration with Shopify's native functionality.

**Source:** [`assets/customer.js`](../../assets/customer.js)

## Overview

The `CustomerAddresses` utility:
- Manages customer address form interactions (add, edit, delete)
- Integrates with Shopify's `CountryProvinceSelector` for address forms
- Handles form expansion/collapse via ARIA attributes
- Provides delete confirmation dialogs
- Supports multiple address forms on the same page

## Class Structure

```javascript
class CustomerAddresses {
  constructor()
  _getElements()
  _setupCountries()
  _setupEventListeners()
  _toggleExpanded(target)
  _handleAddEditButtonClick(currentTarget)
  _handleCancelButtonClick(currentTarget)
  _handleDeleteButtonClick(currentTarget)
}
```

## API Reference

| Method | Description |
|--------|-------------|
| `constructor()` | Initializes the utility, gets DOM elements, sets up countries, and binds events |
| `_getElements()` | Queries and returns all required DOM elements |
| `_setupCountries()` | Initializes Shopify CountryProvinceSelector for all address forms |
| `_setupEventListeners()` | Attaches click event listeners to all interactive elements |
| `_toggleExpanded(target)` | Toggles the `aria-expanded` attribute on a target element |
| `_handleAddEditButtonClick()` | Handles add/edit button clicks to expand/collapse forms |
| `_handleCancelButtonClick()` | Handles cancel button clicks to close forms |
| `_handleDeleteButtonClick()` | Handles delete button clicks with confirmation dialog |

## Method Details

### constructor()

```javascript
class CustomerAddresses {
  constructor() {
    this.elements = this._getElements();
    if (Object.keys(this.elements).length === 0) return;
    this._setupCountries();
    this._setupEventListeners();
  }
}
```

**Behavior:**
1. Gets all required DOM elements
2. Returns early if no elements found (page doesn't have address forms)
3. Sets up country/province selectors
4. Binds event listeners

### _getElements()

```javascript
  _getElements() {
    const container = document.querySelector(selectors.customerAddresses);
    return container
      ? {
        container,
        addressContainer: container.querySelector(selectors.addressContainer),
        toggleButtons: document.querySelectorAll(selectors.toggleAddressButton),
        cancelButtons: container.querySelectorAll(selectors.cancelAddressButton),
        deleteButtons: container.querySelectorAll(selectors.deleteAddressButton),
        countrySelects: container.querySelectorAll(selectors.addressCountrySelect),
      }
      : {};
  }
```

**Returns:**
- `container`: Main customer addresses container
- `addressContainer`: Address form container
- `toggleButtons`: All add/edit buttons
- `cancelButtons`: All cancel buttons
- `deleteButtons`: All delete buttons
- `countrySelects`: All country select elements

### _setupCountries()

```javascript
  _setupCountries() {
    if (Shopify && Shopify.CountryProvinceSelector) {
      // eslint-disable-next-line no-new
      new Shopify.CountryProvinceSelector('AddressCountryNew', 'AddressProvinceNew', {
        hideElement: 'AddressProvinceContainerNew',
      });
      this.elements.countrySelects.forEach((select) => {
        const formId = select.dataset.formId;
        // eslint-disable-next-line no-new
        new Shopify.CountryProvinceSelector(`AddressCountry_${formId}`, `AddressProvince_${formId}`, {
          hideElement: `AddressProvinceContainer_${formId}`,
        });
      });
    }
  }
```

**Behavior:**
- Initializes Shopify's CountryProvinceSelector for the "new address" form
- Initializes selectors for all existing address forms (using `data-form-id` attribute)
- Requires Shopify's global `Shopify.CountryProvinceSelector` to be available

### _handleDeleteButtonClick()

```javascript
  _handleDeleteButtonClick = ({ currentTarget }) => {
    // eslint-disable-next-line no-alert
    if (confirm(currentTarget.getAttribute(attributes.confirmMessage))) {
      Shopify.postLink(currentTarget.dataset.target, {
        parameters: { _method: 'delete' },
      });
    }
  };
```

**Behavior:**
- Shows confirmation dialog using the button's `data-confirm-message` attribute
- If confirmed, uses Shopify's `postLink` to submit DELETE request
- Requires `data-target` attribute with the delete URL

## Selectors and Attributes

The utility uses the following selectors and attributes:

**Selectors:**
- `[data-customer-addresses]`: Main container
- `[data-address-country-select]`: Country select elements
- `[data-address]`: Address form container
- `button[aria-expanded]`: Toggle buttons
- `button[type="reset"]`: Cancel buttons
- `button[data-confirm-message]`: Delete buttons

**Attributes:**
- `aria-expanded`: Controls form visibility (true/false)
- `data-confirm-message`: Confirmation message for delete actions
- `data-form-id`: Form identifier for country/province selectors
- `data-target`: Delete URL for address deletion

## Integration with Shopify Liquid

```liquid
<div data-customer-addresses>
  <!-- New Address Form -->
  <div data-address>
    <button aria-expanded="false">Add new address</button>
    <form id="AddressFormNew">
      <select id="AddressCountryNew" data-address-country-select></select>
      <div id="AddressProvinceContainerNew">
        <select id="AddressProvinceNew"></select>
      </div>
      <button type="reset">Cancel</button>
    </form>
  </div>

  <!-- Existing Address Forms -->
  {% for address in customer.addresses %}
    <div data-address>
      <button aria-expanded="false">Edit</button>
      <form id="AddressForm_{{ address.id }}">
        <select id="AddressCountry_{{ address.id }}" data-address-country-select data-form-id="{{ address.id }}"></select>
        <div id="AddressProvinceContainer_{{ address.id }}">
          <select id="AddressProvince_{{ address.id }}"></select>
        </div>
        <button type="reset">Cancel</button>
        <button data-confirm-message="Delete this address?" data-target="{{ address.url }}">Delete</button>
      </form>
    </div>
  {% endfor %}
</div>

<script src="{{ 'customer.js' | asset_url }}"></script>
```

## Implementation Notes

- The utility requires Shopify's global `Shopify` object with `CountryProvinceSelector` and `postLink` methods
- All address forms must follow Shopify's standard naming conventions for country/province selectors
- Toggle buttons must have `aria-expanded` attribute for accessibility
- Delete buttons must have `data-confirm-message` and `data-target` attributes
- The utility automatically handles multiple address forms on the same page
- Country/province selectors are initialized automatically for all forms
- The utility gracefully handles pages without address forms (returns early if no elements found)

