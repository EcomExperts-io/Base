# component-cart-discount Snippet

`snippets/component-cart-discount.liquid` renders a discount code form with applied discount pills. It uses the `<cart-discount-form>` custom element to handle discount application, removal, and dynamic UI updates without page reloads.

---

## What It Does

- Renders a discount code input form
- Displays applied discount codes as removable pills
- Shows error messages for invalid discount codes
- Updates dynamically via Liquid Ajax Cart integration
- Provides loading states during API calls

---

## Parameters

This snippet does not accept any parameters. It uses the global `cart` object available in Liquid context.

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| JavaScript | `component-cart-discount.js` (defines `<cart-discount-form>` custom element) |
| CSS | `cart.css` (contains discount form styles) |
| Icons | `icon-error.svg`, `icon-close.svg` (inline via `inline_asset_content`) |
| Data | Requires `cart` object with `cart_level_discount_applications` |
| External | Liquid Ajax Cart library for cart updates |

---

## Markup Structure

```liquid
<cart-discount-form>
  <div class="cart-discount">
    <form id="cart-discount-form" class="cart-discount__form">
      <input
        id="discount-code-input"
        name="discount_code"
        type="text"
        class="cart-discount__input"
        placeholder="{{ 'cart.discount_code' | t }}"
        required
      >
      <button type="submit" class="cart-discount__button">
        {{ 'cart.apply' | t }}
      </button>
    </form>

    <ul class="cart-discount__codes">
      {%- for discount_application in cart.cart_level_discount_applications -%}
        {%- if discount_application.type == 'discount_code' -%}
          <li class="cart-discount__pill" data-discount-code="{{ discount_application.title | escape }}">
            <p class="cart-discount__pill-code">{{ discount_application.title | escape }}</p>
            <button type="button" class="cart-discount__pill-remove" aria-label="{{ 'cart.remove_discount' | t }} {{ discount_application.title | escape }}">
              {{- 'icon-close.svg' | inline_asset_content -}}
            </button>
          </li>
        {%- endif -%}
      {%- endfor -%}
    </ul>

    <div class="cart-discount__error" style="display: none;" role="alert">
      <span class="svg-wrapper">
        {{- 'icon-error.svg' | inline_asset_content -}}
      </span>
      <p class="cart-discount__error-text"></p>
    </div>
  </div>
</cart-discount-form>
```

---

## Component Structure

### Custom Element Wrapper

```liquid
<cart-discount-form>
```

The `<cart-discount-form>` custom element wraps the entire component and handles all JavaScript functionality.

### Form Element

```liquid
<form id="cart-discount-form" class="cart-discount__form">
```

- **ID requirement**: Must be `cart-discount-form` for JavaScript targeting
- **Class**: `cart-discount__form` for styling
- Contains input and submit button

### Input Field

```liquid
<input
  id="discount-code-input"
  name="discount_code"
  type="text"
  class="cart-discount__input"
  placeholder="{{ 'cart.discount_code' | t }}"
  required
>
```

- **ID requirement**: Must be `discount-code-input` for JavaScript targeting
- **Required attribute**: HTML5 validation
- **Placeholder**: Uses translation key `cart.discount_code`

### Submit Button

```liquid
<button type="submit" class="cart-discount__button">
  {{ 'cart.apply' | t }}
</button>
```

- Button text changes to "Applying..." during loading
- Disabled during API calls
- Uses translation key `cart.apply`

### Discount Codes List

```liquid
<ul class="cart-discount__codes">
  {%- for discount_application in cart.cart_level_discount_applications -%}
    {%- if discount_application.type == 'discount_code' -%}
      <li class="cart-discount__pill" data-discount-code="{{ discount_application.title | escape }}">
        <!-- Pill content -->
      </li>
    {%- endif -%}
  {%- endfor -%}
</ul>
```

- **Empty state**: List is hidden when empty (CSS `:has()` selector)
- **Discount filtering**: Only shows discount codes (not automatic discounts)
- **Data attribute**: Each pill has `data-discount-code` for JavaScript targeting

### Discount Pill

```liquid
<li class="cart-discount__pill" data-discount-code="{{ discount_application.title | escape }}">
  <p class="cart-discount__pill-code">
    {{ discount_application.title | escape }}
  </p>
  <button
    type="button"
    class="cart-discount__pill-remove"
    aria-label="{{ 'cart.remove_discount' | t }} {{ discount_application.title | escape }}"
  >
    {{- 'icon-close.svg' | inline_asset_content -}}
  </button>
</li>
```

- **Code display**: Shows discount code in uppercase (via CSS)
- **Remove button**: Click removes the discount
- **Loading state**: Pill gets `cart-discount__pill--removing` class during removal
- **Accessibility**: Proper ARIA labels

### Error Container

```liquid
<div class="cart-discount__error" style="display: none;" role="alert">
  <span class="svg-wrapper">
    {{- 'icon-error.svg' | inline_asset_content -}}
  </span>
  <p class="cart-discount__error-text"></p>
</div>
```

- **Hidden by default**: Uses inline `display: none`
- **ARIA role**: `role="alert"` for screen reader announcements
- **Dynamic content**: Error text is set by JavaScript
- **Icon**: Error icon for visual indication

---

## Behavior

### Discount Application

1. User enters discount code and submits form
2. JavaScript validates input (non-empty, not duplicate)
3. Button shows "Applying..." and is disabled
4. Input is disabled during API call
5. Discount is applied via `/cart/update.js`
6. Cart state is fetched from `/cart.js`
7. Pills are updated dynamically
8. Liquid Ajax Cart updates cart sections
9. Input is cleared and loading state is reset

### Discount Removal

1. User clicks remove button on a pill
2. Pill gets loading class (opacity animation)
3. Remove button is disabled
4. Discount is removed via API
5. Cart state is fetched
6. Pills are updated (removed pill disappears)
7. Liquid Ajax Cart updates cart sections

### Error Handling

- Invalid discount codes show error message
- Network errors are caught and displayed
- Error messages are automatically hidden on new attempts
- Error state is restored on removal failures

### Loading States

**Button Loading:**
- Text: "Applying..."
- Disabled state
- Reduced opacity (60%)

**Pill Removal:**
- Class: `cart-discount__pill--removing`
- Opacity: 50%
- Pointer events disabled

---

## Usage Example

```liquid
{% render 'component-cart-discount' %}
```

Typically used in:
- Cart page (`sections/cart.liquid`)
- Cart drawer (`snippets/component-cart-drawer.liquid`)

---

## Implementation Notes

### Discount Code Extraction

Discount codes are extracted from the cart object:

```liquid
{%- for discount_application in cart.cart_level_discount_applications -%}
  {%- if discount_application.type == 'discount_code' -%}
    {{ discount_application.title }}
  {%- endif -%}
{%- endfor -%}
```

This filters for discount code type and extracts the title (code).

### Multiple Discount Codes

The component supports multiple discount codes:
- Codes are combined with commas: `"CODE1,CODE2"`
- All codes are sent together in a single API call
- Each code is displayed as a separate pill

### Duplicate Prevention

JavaScript prevents duplicate codes:
- Checks existing codes before submission
- Clears input if duplicate is detected
- No API call is made for duplicates

### Liquid Ajax Cart Integration

The component triggers Liquid Ajax Cart updates:
- Updates all `data-ajax-cart-section` elements
- Keeps cart totals and other cart UI in sync
- No page reload required

### Dynamic Pill Updates

Pills are updated dynamically:
- New pills are created when codes are applied
- Pills are removed when codes are removed
- Existing pills are preserved if still valid
- Updates happen immediately after API calls

### Translation Keys

All user-facing text uses translation filters:
- `cart.discount_code` - Input placeholder
- `cart.apply` - Submit button text
- `cart.remove_discount` - Remove button aria-label

### Icon Dependencies

Requires these icons in `assets/`:
- `icon-error.svg` - Error message icon
- `icon-close.svg` - Remove button icon

### CSS Class Dependencies

Relies on CSS classes defined in `cart.css`:
- `.cart-discount` - Container
- `.cart-discount__form` - Form wrapper
- `.cart-discount__input` - Input field
- `.cart-discount__button` - Submit button
- `.cart-discount__button:disabled` - Loading state
- `.cart-discount__codes` - Codes list
- `.cart-discount__pill` - Individual pill
- `.cart-discount__pill--removing` - Removal loading state
- `.cart-discount__pill-code` - Code text
- `.cart-discount__pill-remove` - Remove button
- `.cart-discount__error` - Error container
- `.cart-discount__error-text` - Error message
- `.svg-wrapper` - Icon wrapper

### Data Attributes

JavaScript uses these data attributes:
- `data-discount-code` - Discount code value on pills

### Form IDs

JavaScript requires these specific IDs:
- `cart-discount-form` - Form element
- `discount-code-input` - Input field

### No Page Reloads

Unlike older implementations, this component:
- Does not reload the page
- Updates UI dynamically
- Uses Liquid Ajax Cart for cart synchronization
- Provides smooth user experience

### Accessibility

- Proper ARIA labels on interactive elements
- Error messages use `role="alert"`
- Button states properly disabled
- Keyboard navigation support
- Screen reader friendly

---

## Script Loading

The JavaScript must be loaded as a module:

```liquid
<script src="{{ 'component-cart-discount.js' | asset_url }}" type="module"></script>
```

Ensure this is included on pages where the discount form appears.

---

## Cart Object Dependency

The snippet requires the `cart` object to be available in Liquid context. This is automatically available on:
- Cart page (`/cart`)
- Cart drawer (via Liquid Ajax Cart)
- Any page with cart context

---

## Error Scenarios

1. **Invalid Discount Code**
   - Error message: "That discount code is not valid."
   - Input remains enabled
   - User can try again

2. **Network Error**
   - Error message: "Something went wrong while applying the code."
   - Loading state is reset
   - User can retry

3. **Removal Failure**
   - Error message: "Something went wrong while removing the discount."
   - Pill state is restored
   - Cart state is refreshed
