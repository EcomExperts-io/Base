# cart-discount Snippet

`snippets/cart-discount.liquid` renders a collapsible discount code form with applied discount pills. It uses custom elements (`<cart-discount-component>` and `<disclosure-custom>`) to handle discount application, removal, and accessible accordion behavior. The snippet automatically expands when discount codes are already applied to the cart.

---

## What It Does

- Renders a collapsible disclosure component for discount code entry.
- Provides a form to apply discount codes via AJAX to the cart.
- Displays applied discount codes as removable pills.
- Automatically expands when discounts are already applied.
- Shows error messages for invalid discount codes or shipping discount conflicts.
- Uses custom elements for interactive behavior and accessibility.

---

## Parameters

| Parameter     | Type   | Default            | Description                                                      |
|---------------|--------|--------------------|------------------------------------------------------------------|
| `section_id`  | string | `'cart-discount'` | The section ID used for JavaScript targeting and error display. |

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| JavaScript | `cart-discount.js` (defines `<cart-discount-component>` and `<disclosure-custom>` custom elements) |
| Icons | `icon-error.svg`, `icon-close.svg`, `icon-plus.svg`, `icon-minus.svg` (inline via `inline_asset_content`) |
| Data | Requires `cart` object with `cart_level_discount_applications` |

- Custom elements handle discount application/removal and disclosure toggle behavior.
- Icons are embedded inline via the `inline_asset_content` filter.
- Discount codes are extracted from `cart.cart_level_discount_applications` filtered by type `'discount_code'`.

---

## Markup Structure

```liquid
<disclosure-custom class="cart-discount">
  <button aria-controls="cart-discount-disclosure" aria-expanded="..." class="disclosure-trigger">
    <!-- Trigger button with label and icons -->
  </button>
  <div class="disclosure-content" {% unless disclosure_expanded %}inert{% endunless %}>
    <div id="cart-discount-disclosure">
      <cart-discount-component data-section-id="{{ section_id }}">
        <!-- Discount form and error messages -->
      </cart-discount-component>
      <ul class="cart-discount__codes">
        <!-- Applied discount pills -->
      </ul>
    </div>
  </div>
</disclosure-custom>
```

- **Disclosure wrapper**: Uses `<disclosure-custom>` custom element for accessible accordion behavior.
- **Conditional expansion**: Disclosure expands automatically when `disclosure_expanded` is `true` (when discounts exist).
- **Inert attribute**: Uses `inert` attribute when collapsed to prevent interaction with hidden content.

### Disclosure Trigger Button

```liquid
<button
  aria-controls="cart-discount-disclosure"
  aria-expanded="{% if disclosure_expanded %}true{% else %}false{% endif %}"
  aria-label="{% if disclosure_expanded %}{{ 'accessibility.close' | t }}{% else %}{{ 'accessibility.open' | t }}{% endif %} {{ 'accessibility.discount_menu' | t }}"
  class="disclosure-trigger"
  data-disclosure-open="{{ 'accessibility.open' | t }} {{ 'accessibility.discount_menu' | t }}"
  data-disclosure-close="{{ 'accessibility.close' | t }} {{ 'accessibility.discount_menu' | t }}"
  ref="disclosureTrigger"
  type="button"
>
  <span class="disclosure-trigger__label h6">{{ 'cart.discount' | t }}</span>
  <span class="disclosure-trigger__icons">
    <span class="svg-wrapper icon-plus">
      {{- 'icon-plus.svg' | inline_asset_content -}}
    </span>
    <span class="svg-wrapper icon-minus">
      {{- 'icon-minus.svg' | inline_asset_content -}}
    </span>
  </span>
</button>
```

- **ARIA attributes**: Full accessibility support with `aria-controls`, `aria-expanded`, and dynamic `aria-label`.
- **Data attributes**: Stores open/close labels for JavaScript to update `aria-label` dynamically.
- **Icon toggle**: Shows plus icon when closed, minus icon when open (handled by CSS/JS).
- **Ref attribute**: Uses `ref="disclosureTrigger"` for JavaScript targeting (likely Alpine.js or custom element).

### Discount Form

```liquid
<cart-discount-component data-section-id="{{ section_id }}">
  <div class="cart-discount__content">
    <form class="cart-discount__form">
      <label for="cart-discount" class="visually-hidden">
        {{- 'accessibility.discount' | t -}}
      </label>
      <input
        id="cart-discount"
        class="cart-discount__input"
        type="text"
        name="discount"
        placeholder="{{ 'cart.discount_code' | t }}"
        required
      >
      <button type="submit" class="button button--primary cart-discount__button">
        {{ 'cart.apply' | t }}
      </button>
    </form>
  </div>
  <!-- Error messages -->
</cart-discount-component>
```

- **Custom element**: Uses `<cart-discount-component>` to handle form submission and discount application.
- **Accessible label**: Label is visually hidden but available to screen readers.
- **Required input**: Input field is marked as `required` for HTML5 validation.
- **Section ID**: Passes `section_id` via `data-section-id` attribute for JavaScript targeting.

### Error Messages

```liquid
<div class="cart-discount__error hidden" role="alert">
  <span class="svg-wrapper">
    {{- 'icon-error.svg' | inline_asset_content -}}
  </span>
  <small class="cart-discount__error-text cart-discount__error-text--discount-code cart-primary-typography hidden">
    {{ 'cart.discount_code_error' | t }}
  </small>
  <small class="cart-discount__error-text cart-discount__error-text--shipping cart-primary-typography hidden">
    {{ 'cart.shipping_discount_error' | t }}
  </small>
</div>
```

- **Two error types**: Separate error messages for invalid discount codes and shipping discount conflicts.
- **Hidden by default**: All error elements use `hidden` class and are shown via JavaScript when needed.
- **ARIA role**: Uses `role="alert"` for screen reader announcements.
- **Error classes**: Uses modifier classes (`--discount-code`, `--shipping`) for specific error targeting.

### Applied Discount Pills

```liquid
<ul class="cart-discount__codes">
  {% for discount_code in discount_codes %}
    <li
      class="cart-discount__pill"
      data-discount-code="{{ discount_code }}"
      aria-label="{{ 'accessibility.discount_applied' | t }} {{ discount_code | escape }}"
    >
      <p class="cart-discount__pill-code">
        {{ discount_code }}
      </p>
      <button
        type="button"
        class="cart-discount__pill-remove svg-wrapper svg-wrapper--smaller button-unstyled"
        aria-label="{{ 'cart.remove_discount' | t }} {{ discount_code | escape }}"
      >
        {{- 'icon-close.svg' | inline_asset_content -}}
      </button>
    </li>
  {% endfor %}
</ul>
```

- **Discount list**: Displays all applied discount codes as pills.
- **Data attribute**: Each pill uses `data-discount-code` for JavaScript targeting.
- **Remove button**: Each pill includes a remove button with proper ARIA label.
- **Accessibility**: Full ARIA support with descriptive labels for screen readers.

---

## Behavior

- **Automatic expansion**: Disclosure expands automatically when `discount_codes.size > 0`.
- **Discount application**: Form submission triggers `applyDiscount()` method in `<cart-discount-component>` which:
  - Validates and normalizes the discount code (trim, uppercase)
  - Checks for duplicates
  - POSTs to `/cart/update.js` with all discount codes
  - Reloads page on success or shows error on failure
- **Discount removal**: Clicking remove button triggers `removeDiscount()` method which:
  - Removes the specific discount code
  - Reapplies remaining discounts
  - Reloads page to reflect changes
- **Error handling**: Shows appropriate error message based on error type (invalid code vs shipping conflict).
- **Disclosure toggle**: Button toggles disclosure open/closed with proper ARIA state updates.

---

## Usage Example

```liquid
{% render 'cart-discount', section_id: section.id %}
```

Or with default section ID:

```liquid
{% render 'cart-discount' %}
```

Typically used in:
- Cart page (`sections/cart.liquid`)
- Cart drawer (`snippets/component-cart-drawer.liquid`)
- Cart notification (`snippets/component-cart-notification.liquid`)

---

## Implementation Notes

1. **Discount code extraction**: Discount codes are extracted using:
   ```liquid
   cart.cart_level_discount_applications | where: 'type', 'discount_code' | map: 'title'
   ```
   This filters for discount code type and extracts the title (code).

2. **Disclosure state**: The `disclosure_expanded` variable is set based on whether discount codes exist, controlling initial expansion state.

3. **Inert attribute**: When disclosure is collapsed, the content uses `inert` attribute to prevent keyboard and screen reader interaction with hidden content.

4. **Custom element requirements**: Requires `cart-discount.js` to be loaded which defines:
   - `<cart-discount-component>`: Handles discount form submission and removal
   - `<disclosure-custom>`: Handles accordion toggle behavior

5. **Error message display**: JavaScript shows/hides error messages by toggling the `hidden` class on error elements. Two error types:
   - `cart-discount__error-text--discount-code`: Invalid discount code
   - `cart-discount__error-text--shipping`: Shipping discount conflict

6. **Discount code normalization**: JavaScript normalizes codes to uppercase and trims whitespace before submission.

7. **Duplicate prevention**: JavaScript checks for duplicate codes before submission and clears input if duplicate is detected.

8. **Multiple discounts**: The form supports multiple discount codes by joining them with commas in the POST request.

9. **Page reload**: On successful discount application/removal, the page reloads to reflect cart changes. This ensures all cart totals and discounts are properly updated.

10. **Translation keys**: All user-facing text uses translation filters:
    - `cart.discount`
    - `cart.discount_code`
    - `cart.apply`
    - `cart.discount_code_error`
    - `cart.shipping_discount_error`
    - `cart.remove_discount`
    - `accessibility.discount`
    - `accessibility.discount_applied`
    - `accessibility.discount_menu`
    - `accessibility.open`
    - `accessibility.close`

11. **Icon dependencies**: Requires the following icons in `assets/`:
    - `icon-error.svg`
    - `icon-close.svg`
    - `icon-plus.svg`
    - `icon-minus.svg`

12. **CSS class dependencies**: Section relies on CSS classes for styling:
    - `.cart-discount`
    - `.disclosure-trigger`
    - `.disclosure-content`
    - `.cart-discount__form`
    - `.cart-discount__input`
    - `.cart-discount__button`
    - `.cart-discount__error`
    - `.cart-discount__codes`
    - `.cart-discount__pill`
    - `.cart-discount__pill-remove`
    - `.visually-hidden`
    - `.hidden`

13. **Ref attributes**: Uses `ref="disclosureTrigger"` and `ref="disclosureContent"` which are likely used by the `<disclosure-custom>` custom element for JavaScript targeting (similar to Alpine.js `x-ref`).

14. **Data attributes for JavaScript**:
    - `data-section-id`: Section identifier for error targeting
    - `data-discount-code`: Discount code value for removal
    - `data-disclosure-open`: Open state label
    - `data-disclosure-close`: Close state label

15. **Form submission**: Form submission is handled by JavaScript (not native form submission) to enable AJAX updates without full page reload for error display.

16. **Accessibility features**:
    - Proper ARIA roles and attributes
    - Visually hidden labels for screen readers
    - Dynamic `aria-label` updates
    - `aria-expanded` state management
    - `role="alert"` for error announcements
    - Descriptive button labels

17. **Discount code display**: Applied discount codes are displayed exactly as entered (case-preserved in display, but normalized in submission).

18. **Error icon**: Error messages include an icon for visual indication alongside text.

19. **Button styling**: Apply button uses `button button--primary` classes for consistent theme styling.

20. **Responsive design**: Disclosure component works on all screen sizes with proper touch targets for mobile.

21. **No form validation**: HTML5 `required` attribute provides basic validation, but detailed validation happens server-side via Shopify's cart API.

22. **Cart object dependency**: Snippet requires `cart` object to be available in Liquid context. This is automatically available on cart pages and in cart-related snippets.

23. **Section ID usage**: The `section_id` parameter is used to namespace error messages and JavaScript targeting, allowing multiple discount forms on the same page if needed (though typically only one is used).

24. **Disclosure content ID**: The disclosure content uses `id="cart-discount-disclosure"` which is referenced by the trigger button's `aria-controls` attribute for proper accessibility association.

