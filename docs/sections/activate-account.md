# Activate Account Section (`sections/activate-account.liquid`)

`sections/activate-account.liquid` renders the customer account activation form for customers who have been invited to create an account. It includes fields for password and password confirmation, with comprehensive error handling and proper ARIA attributes for accessibility. The section uses Shopify's `activate_customer_password` form and provides both activate and cancel options.

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | `customer.css` |
| Icons | `icon-error.svg` (inline via `inline_asset_content`) |
| Forms | Shopify `activate_customer_password` form |

- Uses shared `customer.css` for consistent customer account styling.
- Error icon is embedded inline via the `inline_asset_content` filter.
- Form uses native HTML5 validation attributes and ARIA for accessibility.

---

## Dynamic Styles

Dynamic styles are generated via an inline `{% style %}` block:

```liquid
{%- style -%}
  .section-{{ section.id }}-padding {
    padding-top: {{ section.settings.padding_top | times: 0.75 | round: 0 }}px;
    padding-bottom: {{ section.settings.padding_bottom | times: 0.75 | round: 0 }}px;
  }

  @media screen and (min-width: 750px) {
    .section-{{ section.id }}-padding {
      padding-top: {{ section.settings.padding_top }}px;
      padding-bottom: {{ section.settings.padding_bottom }}px;
    }
  }
{%- endstyle -%}
```

- **Responsive padding**: Mobile padding is 75% of desktop padding for better mobile spacing.
- **Breakpoint**: Uses 750px breakpoint for responsive padding adjustment.

---

## Markup Structure

```liquid
<div class="customer activate section-{{ section.id }}-padding">
  <h1>{{ 'customer.activate_account.title' | t }}</h1>
  <p>{{ 'customer.activate_account.subtext' | t }}</p>
  {%- form 'activate_customer_password' -%}
    <!-- Error messages -->
    <!-- Password field -->
    <!-- Password confirmation field -->
    <!-- Activate and Cancel buttons -->
  {%- endform -%}
</div>
```

- **Form type**: Uses Shopify's `activate_customer_password` form type.
- **CSS classes**: Uses `customer` and `activate` classes for styling consistency.
- **Subtext**: Includes explanatory text about the account activation process.
- **Dual action**: Provides both activate and cancel/decline options.

### Error Handling

```liquid
{%- if form.errors -%}
  <h2 class="form__message" tabindex="-1" autofocus>
    <span class="svg-wrapper">
      {{- 'icon-error.svg' | inline_asset_content -}}
    </span>
    {{ 'templates.contact.form.error_heading' | t }}
  </h2>
  <ul>
    {%- for field in form.errors -%}
      <li>
        {%- if field == 'form' -%}
          {{ form.errors.messages[field] }}
        {%- else -%}
          <a href="#{{ field }}">
            {{ form.errors.translated_fields[field] | capitalize }}
            {{ form.errors.messages[field] }}
          </a>
        {%- endif -%}
      </li>
    {%- endfor -%}
  </ul>
{%- endif -%}
```

- **Error display**: Shows all form errors in a list format.
- **Field links**: Errors link to the corresponding form field for easy navigation.
- **Form-level errors**: Handles both field-specific and form-level errors.
- **Focus management**: Error heading has `tabindex="-1"` and `autofocus` for screen reader support.

### Form Fields

#### Password Field
```liquid
<div class="field">
  <input
    type="password"
    name="customer[password]"
    id="password"
    autocomplete="new-password"
    placeholder="{{ 'customer.activate_account.password' | t }}"
    {% if form.errors contains 'password' %}
      aria-invalid="true"
      aria-describedby="password-error"
    {% endif %}
  >
  <label for="password">
    {{ 'customer.activate_account.password' | t }}
  </label>
  {%- if form.errors contains 'password' -%}
    <small id="password-error" class="form__message">
      <span class="svg-wrapper">
        {{- 'icon-error.svg' | inline_asset_content -}}
      </span>
      {{ form.errors.translated_fields.password | capitalize }}
      {{ form.errors.messages.password }}
    </small>
  {%- endif -%}
</div>
```

- **Password field**: Uses `type="password"` to hide input.
- **Autocomplete**: Uses `autocomplete="new-password"` to indicate new password entry.
- **ARIA support**: Includes conditional `aria-invalid` and `aria-describedby` for error association.
- **Error display**: Shows inline error message within the field container.

#### Password Confirmation Field
```liquid
<div class="field">
  <input
    type="password"
    name="customer[password_confirmation]"
    id="password_confirmation"
    autocomplete="new-password"
    placeholder="{{ 'customer.activate_account.password_confirm' | t }}"
    {% if form.errors contains 'password' %}
      aria-invalid="true"
      aria-describedby="password_confirmation-error"
    {% endif %}
  >
  <label for="password_confirmation">
    {{ 'customer.activate_account.password_confirm' | t }}
  </label>
  {%- if form.errors contains 'password_confirmation' -%}
    <small id="password_confirmation-error" class="form__message">
      <span class="svg-wrapper">
        {{- 'icon-error.svg' | inline_asset_content -}}
      </span>
      {{ form.errors.translated_fields.password_confirmation | capitalize }}
      {{ form.errors.messages.password_confirmation }}
    </small>
  {%- endif -%}
</div>
```

- **Confirmation field**: Requires users to confirm their new password.
- **Same autocomplete**: Uses `autocomplete="new-password"` for both fields.
- **Error handling**: Separate error message for password confirmation validation.
- **Note**: The password confirmation field checks `form.errors contains 'password'` for ARIA attributes (this may be a bug - should check `'password_confirmation'`).

### Submit Buttons

```liquid
<button>
  {{ 'customer.activate_account.submit' | t }}
</button>
<button name="decline">
  {{ 'customer.activate_account.cancel' | t }}
</button>
```

- **Activate button**: Submits the form to activate the account.
- **Cancel button**: Includes `name="decline"` attribute to decline account activation.
- **Translation**: Both button texts use translation filters for localization.

---

## Behavior

- **Form submission**: Submits to Shopify's account activation endpoint.
- **Password validation**: Server validates password strength and confirmation match.
- **Account activation**: Activates the customer account when form is submitted.
- **Account decline**: Allows customers to decline account activation via the cancel button.
- **Accessibility**: Full ARIA support with proper labels, error associations, and focus management.
- **Autocomplete**: Uses HTML5 autocomplete attributes (`new-password`) for browser password manager support.
- **Error display**: Shows field-specific errors inline and form-level errors at the top.

---

## Schema

```json
{
  "name": "t:sections.main-activate-account.name",
  "settings": [
    {
      "type": "header",
      "content": "t:sections.all.padding.section_padding_heading"
    },
    {
      "type": "range",
      "id": "padding_top",
      "min": 0,
      "max": 100,
      "step": 4,
      "unit": "px",
      "label": "t:sections.all.padding.padding_top",
      "default": 36
    },
    {
      "type": "range",
      "id": "padding_bottom",
      "min": 0,
      "max": 100,
      "step": 4,
      "unit": "px",
      "label": "t:sections.all.padding.padding_bottom",
      "default": 36
    }
  ]
}
```

- **Minimal schema**: Only includes padding settings.
- **Translation keys**: All labels use translation filters.
- **Padding defaults**: Default padding is 36px top and bottom.

---

## Implementation Notes

1. **Translation keys**: All user-facing text uses translation filters (`customer.activate_account.*`, `templates.contact.form.error_heading`).

2. **Form field naming**: Form fields use Shopify's customer object structure: `customer[password]` and `customer[password_confirmation]`.

3. **ID naming convention**: Form field IDs are simple (`password`, `password_confirmation`) rather than prefixed, which is acceptable for this single-purpose form.

4. **Error icon dependency**: Requires `icon-error.svg` in the `assets/` folder for error message display.

5. **CSS class dependencies**: Section relies on CSS classes from `customer.css`:
   - `.customer`
   - `.activate`
   - `.field`
   - `.form__message`
   - `.svg-wrapper`

6. **Autocomplete attributes**: Both password fields use `autocomplete="new-password"` to indicate new password entry, which helps password managers understand the context.

7. **Error message structure**: Error messages include:
   - Icon via inline SVG
   - Translated field name (capitalized)
   - Error message text
   - No period at end

8. **Error element type**: Password field errors use `<small>` element instead of `<span>`, providing semantic meaning for inline error text.

9. **Accessibility features**:
    - Proper label associations via `for` attributes
    - ARIA invalid attributes when errors exist
    - ARIA describedby linking errors to fields
    - Error heading with autofocus for screen readers

10. **Responsive design**: Padding adjusts from 75% on mobile to 100% on desktop (750px breakpoint).

11. **No JavaScript required**: Form works entirely with server-side rendering and validation.

12. **Account activation link**: This form is accessed via account activation links sent to customers via email. The activation token is handled by Shopify automatically.

13. **Subtext display**: Includes explanatory text (`customer.activate_account.subtext`) to guide users through the account activation process.

14. **Error link anchors**: Error links use `#\{\{ field \}\}` format (e.g., `#password`, `#password_confirmation`) to link to form fields.

15. **Translation key structure**: Translation keys follow hierarchical structure:
    - `customer.activate_account.title`
    - `customer.activate_account.subtext`
    - `customer.activate_account.password`
    - `customer.activate_account.password_confirm`
    - `customer.activate_account.submit`
    - `customer.activate_account.cancel`

16. **Password confirmation**: Requires users to enter the password twice to prevent typos and ensure password accuracy.

17. **No form value persistence**: Unlike the register form, this form doesn't preserve values on error (passwords shouldn't be preserved for security reasons).

18. **Dual button functionality**: The cancel button with `name="decline"` allows customers to decline account activation, which is useful for customers who didn't request the account.

19. **Account invitation flow**: This section is part of Shopify's account invitation system where store owners can invite customers to create accounts.

20. **Potential bug**: The password confirmation field checks `form.errors contains 'password'` for ARIA attributes instead of `'password_confirmation'`. This may need to be corrected to properly show ARIA invalid state for confirmation field errors.

