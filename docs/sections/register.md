# Register Section (`sections/register.liquid`)

`sections/register.liquid` renders the customer registration form with fields for first name, last name, email, and password. It includes form validation error handling, proper ARIA attributes for accessibility, and responsive padding controls. The section uses Shopify's `create_customer` form to handle account creation.

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | `customer.css` |
| Icons | `icon-error.svg` (inline via `inline_asset_content`) |
| Forms | Shopify `create_customer` form |

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
<div class="customer register section-{{ section.id }}-padding">
  <h1>{{ 'customer.register.title' | t }}</h1>
  {%- form 'create_customer', novalidate: 'novalidate' -%}
    <!-- Error messages -->
    <!-- Form fields: first_name, last_name, email, password -->
    <!-- Submit button -->
  {%- endform -%}
</div>
```

- **Form type**: Uses Shopify's `create_customer` form type.
- **Novalidate**: Form uses `novalidate: 'novalidate'` to allow server-side validation.
- **CSS classes**: Uses `customer` and `register` classes for styling consistency.

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
          <a href="#RegisterForm-{{ field }}">
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
- **Accessibility**: Error heading has `tabindex="-1"` and `autofocus` for screen reader support.

### Form Fields

#### First Name Field
```liquid
<div class="field">
  <input
    type="text"
    name="customer[first_name]"
    id="RegisterForm-FirstName"
    {% if form.first_name %}
      value="{{ form.first_name }}"
    {% endif %}
    autocomplete="given-name"
    placeholder="{{ 'customer.register.first_name' | t }}"
  >
  <label for="RegisterForm-FirstName">
    {{ 'customer.register.first_name' | t }}
  </label>
</div>
```

#### Last Name Field
```liquid
<div class="field">
  <input
    type="text"
    name="customer[last_name]"
    id="RegisterForm-LastName"
    {% if form.last_name %}
      value="{{ form.last_name }}"
    {% endif %}
    autocomplete="family-name"
    placeholder="{{ 'customer.register.last_name' | t }}"
  >
  <label for="RegisterForm-LastName">
    {{ 'customer.register.last_name' | t }}
  </label>
</div>
```

#### Email Field
```liquid
<div class="field">
  <input
    type="email"
    name="customer[email]"
    id="RegisterForm-email"
    {% if form.email %}
      value="{{ form.email }}"
    {% endif %}
    spellcheck="false"
    autocapitalize="off"
    autocomplete="email"
    aria-required="true"
    {% if form.errors contains 'email' %}
      aria-invalid="true"
      aria-describedby="RegisterForm-email-error"
    {% endif %}
    placeholder="{{ 'customer.register.email' | t }}"
  >
  <label for="RegisterForm-email">
    {{ 'customer.register.email' | t }}
  </label>
</div>
{%- if form.errors contains 'email' -%}
  <span id="RegisterForm-email-error" class="form__message">
    <span class="svg-wrapper">
      {{- 'icon-error.svg' | inline_asset_content -}}
    </span>
    {{ form.errors.translated_fields.email | capitalize }}
    {{ form.errors.messages.email }}.
  </span>
{%- endif -%}
```

- **Email validation**: Uses `type="email"` for native browser validation.
- **ARIA attributes**: Includes `aria-required="true"` and conditional `aria-invalid` for accessibility.
- **Error association**: Error message uses `id="RegisterForm-email-error"` linked via `aria-describedby`.

#### Password Field
```liquid
<div class="field">
  <input
    type="password"
    name="customer[password]"
    id="RegisterForm-password"
    aria-required="true"
    {% if form.errors contains 'password' %}
      aria-invalid="true"
      aria-describedby="RegisterForm-password-error"
    {% endif %}
    placeholder="{{ 'customer.register.password' | t }}"
  >
  <label for="RegisterForm-password">
    {{ 'customer.register.password' | t }}
  </label>
</div>
{%- if form.errors contains 'password' -%}
  <span id="RegisterForm-password-error" class="form__message">
    <span class="svg-wrapper">
      {{- 'icon-error.svg' | inline_asset_content -}}
    </span>
    {{ form.errors.translated_fields.password | capitalize }}
    {{ form.errors.messages.password }}.
  </span>
{%- endif -%}
```

- **Password field**: Uses `type="password"` to hide input.
- **ARIA support**: Includes `aria-required="true"` and conditional error attributes.
- **Error display**: Shows inline error message when password validation fails.

### Submit Button

```liquid
<button>
  {{ 'customer.register.submit' | t }}
</button>
```

- **Translation**: Button text uses translation filter for localization.

---

## Behavior

- **Form submission**: Submits to Shopify's customer creation endpoint.
- **Error persistence**: Form values are preserved on validation errors (via `form.first_name`, `form.last_name`, `form.email`).
- **Accessibility**: Full ARIA support with proper labels, error associations, and focus management.
- **Autocomplete**: Uses HTML5 autocomplete attributes (`given-name`, `family-name`, `email`) for browser autofill support.
- **Client-side validation**: Native HTML5 validation (email type) works alongside server-side validation.

---

## Schema

```json
{
  "name": "t:sections.main-register.name",
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

1. **Translation keys**: All user-facing text uses translation filters (`customer.register.*`, `templates.contact.form.error_heading`).

2. **Form field naming**: Form fields use Shopify's customer object structure: `customer[first_name]`, `customer[last_name]`, `customer[email]`, `customer[password]`.

3. **ID naming convention**: Form field IDs use `RegisterForm-` prefix (e.g., `RegisterForm-FirstName`, `RegisterForm-email`) for uniqueness and error linking.

4. **Error icon dependency**: Requires `icon-error.svg` in the `assets/` folder for error message display.

5. **CSS class dependencies**: Section relies on CSS classes from `customer.css`:
   - `.customer`
   - `.register`
   - `.field`
   - `.form__message`
   - `.svg-wrapper`

6. **Autocomplete attributes**: Uses HTML5 autocomplete values:
   - `given-name` for first name
   - `family-name` for last name
   - `email` for email address

7. **Email input attributes**: Email field includes:
   - `spellcheck="false"` to disable spell checking
   - `autocapitalize="off"` to prevent auto-capitalization
   - `autocomplete="email"` for browser autofill

8. **Error message structure**: Error messages include:
   - Icon via inline SVG
   - Translated field name (capitalized)
   - Error message text
   - Period at end for proper sentence structure

9. **Form value persistence**: Form fields preserve values on validation errors using `form.first_name`, `form.last_name`, and `form.email` objects.

10. **Accessibility features**:
    - Proper label associations via `for` attributes
    - ARIA required attributes on required fields
    - ARIA invalid attributes when errors exist
    - ARIA describedby linking errors to fields
    - Error heading with autofocus for screen readers

11. **Responsive design**: Padding adjusts from 75% on mobile to 100% on desktop (750px breakpoint).

12. **No JavaScript required**: Form works entirely with server-side rendering and native HTML5 validation.

13. **Novalidate attribute**: Form uses `novalidate: 'novalidate'` to allow server-side validation to take precedence, though native email validation still works.

14. **Error link anchors**: Error links use `#RegisterForm-\{\{ field \}\}` format to link to form fields (though fields don't have matching anchors - this may need adjustment).

15. **Translation key structure**: Translation keys follow hierarchical structure:
    - `customer.register.title`
    - `customer.register.first_name`
    - `customer.register.last_name`
    - `customer.register.email`
    - `customer.register.password`
    - `customer.register.submit`

