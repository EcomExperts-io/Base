# LocalizationForm Web Component

`assets/component-localization-form.js` exports the `LocalizationForm` class, which extends `HTMLElement` and is registered as the custom element `<localization-form>`. This component handles language and country selection for Shopify store localization, automatically submitting the form when a selection is made.

**Source:** [`assets/component-localization-form.js`](../../assets/component-localization-form.js)

## Overview

The `LocalizationForm` component:
- Handles language and country code selection
- Automatically submits form when selection is made
- Prevents default link navigation
- Updates hidden input values before submission
- Supports both language and country localization

## Class Structure

```javascript
export class LocalizationForm extends HTMLElement {
  constructor()
  onItemClick(event)
}
```

## API Reference

| Method | Description |
|--------|-------------|
| `constructor()` | Initializes the component, queries form elements, and sets up click listeners |
| `onItemClick(event)` | Handles selection clicks, updates input value, and submits form |

## Method Details

### constructor()

```javascript
export class LocalizationForm extends HTMLElement {
  constructor() {
    super();
    this.elements = {
      input: this.querySelector('input[name="language_code"], input[name="country_code"]'),
    };

    this.querySelectorAll('a').forEach((item) => item.addEventListener('click', this.onItemClick.bind(this)));
  }
}
```

**Initialization:**
- Queries for language or country code input
- Finds all anchor elements within the component
- Attaches click listeners to each anchor

### onItemClick(event)

```javascript
  onItemClick(event) {
    event.preventDefault();
    const form = this.querySelector('form');
    this.elements.input.value = event.currentTarget.dataset.value;
    if (form) form.submit();
  }
```

**Behavior:**
1. Prevents default link navigation
2. Finds form element
3. Updates input value from anchor's `data-value` attribute
4. Submits form if found

## Custom Element Definition

```javascript
if (!customElements.get('localization-form')) {
  customElements.define('localization-form', LocalizationForm);
}
```

Ensures the element is registered only once across bundles or hot reload sessions.

## Integration with Shopify Liquid

### Language Selection

```liquid
<localization-form>
  <form action="{{ routes.cart_url }}" method="post">
    <input type="hidden" name="language_code" value="{{ request.locale.iso_code }}">
    
    <ul>
      {% for locale in shop.published_locales %}
        <li>
          <a href="#" data-value="{{ locale.iso_code }}">
            {{ locale.endonym_name }}
          </a>
        </li>
      {% endfor %}
    </ul>
  </form>
</localization-form>
```

### Country Selection

```liquid
<localization-form>
  <form action="{{ routes.cart_url }}" method="post">
    <input type="hidden" name="country_code" value="{{ localization.country.iso_code }}">
    
    <ul>
      {% for country in localization.available_countries %}
        <li>
          <a href="#" data-value="{{ country.iso_code }}">
            {{ country.name }}
          </a>
        </li>
      {% endfor %}
    </ul>
  </form>
</localization-form>
```

### Combined Language and Country

```liquid
<localization-form>
  <form action="{{ routes.cart_url }}" method="post">
    <input type="hidden" name="language_code" value="{{ request.locale.iso_code }}">
    <input type="hidden" name="country_code" value="{{ localization.country.iso_code }}">
    
    <div class="language-selector">
      <span>Language:</span>
      {% for locale in shop.published_locales %}
        <a href="#" data-value="{{ locale.iso_code }}">{{ locale.endonym_name }}</a>
      {% endfor %}
    </div>
    
    <div class="country-selector">
      <span>Country:</span>
      {% for country in localization.available_countries %}
        <a href="#" data-value="{{ country.iso_code }}">{{ country.name }}</a>
      {% endfor %}
    </div>
  </form>
</localization-form>
```

## Implementation Notes

- The component requires a form element with a hidden input (`name="language_code"` or `name="country_code"`)
- Selection links must have `data-value` attribute with the code to set
- The component automatically submits the form when a selection is made
- Form action should point to a route that handles localization (typically `routes.cart_url`)
- The component supports both language and country selection (but only one input per form)
- Clicking a link prevents default navigation and submits the form instead
- The component works with Shopify's built-in localization features
- Multiple localization forms can exist on the same page
- The component is lightweight and has no dependencies
- If no form is found, the component silently fails (no error)

