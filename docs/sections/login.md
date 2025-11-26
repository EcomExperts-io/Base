# Login Section (`sections/login.liquid`)

`sections/login.liquid` renders the customer login page with two forms: password recovery and customer login. It supports Shop login integration, guest checkout (when enabled), and responsive padding controls. The section includes proper form validation, error handling, and accessibility features.

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | `customer.css`, inline `{% style %}` block for responsive padding |
| Icons | `icon-error.svg`, `icon-success.svg` (inline via `inline_asset_content`) |
| Data | Relies on `section.settings`, `form` object, and `shop` object |

- No JavaScript dependencies; the section is purely presentational.
- All text uses translation keys for localization.
- Icons are embedded inline via the `inline_asset_content` filter.

---

## Dynamic Styles

Inline styles generate responsive padding that scales down on mobile:

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

- Mobile uses 75% of the configured padding value (rounded to whole pixels).
- Desktop (≥750px) uses the full padding value from settings.
- Padding values range from 0–100px in 4px increments.

---

## Markup Structure

```liquid
<div class="customer login section-{{ section.id }}-padding">
  <!-- Password recovery form -->
  <h1 id="recover" tabindex="-1">
    {{ 'customer.recover_password.title' | t }}
  </h1>
  <div>
    {%- form 'recover_customer_password' -%}
      <!-- Email input and error handling -->
    {%- endform -%}
  </div>

  <!-- Customer login form -->
  <h1 id="login" tabindex="-1">
    {{ 'customer.login_page.title' | t }}
  </h1>
  <div>
    {%- form 'customer_login', novalidate: 'novalidate' -%}
      <!-- Shop login button (conditional) -->
      <!-- Email and password inputs -->
      <!-- Forgot password link -->
    {%- endform -%}
  </div>

  <!-- Guest checkout (conditional) -->
</div>
```

- Two separate forms: password recovery and customer login.
- Anchor links (`#recover`, `#login`) for form switching.
- Guest checkout section conditionally renders when enabled.

### Password Recovery Form

```liquid
<h1 id="recover" tabindex="-1">
  {{ 'customer.recover_password.title' | t }}
</h1>
<div>
  <p>
    {{ 'customer.recover_password.subtext' | t }}
  </p>

  {%- form 'recover_customer_password' -%}
    {% assign recover_success = form.posted_successfully? %}
    <div class="field">
      <input
        type="email"
        name="email"
        id="RecoverEmail"
        autocomplete="email"
        {% if form.errors %}
          aria-invalid="true"
          aria-describedby="RecoverEmail-email-error"
          autofocus
        {% endif %}
        placeholder="{{ 'customer.login_page.email' | t }}"
      >
      <label for="RecoverEmail">
        {{ 'customer.login_page.email' | t }}
      </label>
    </div>
    {%- if form.errors -%}
      <small id="RecoverEmail-email-error" class="form__message">
        <span class="svg-wrapper">
          {{- 'icon-error.svg' | inline_asset_content -}}
        </span>
        {{ form.errors.messages.form }}
      </small>
    {%- endif -%}

    <button>
      {{ 'customer.login_page.submit' | t }}
    </button>

    <a href="#login">
      {{ 'customer.login_page.cancel' | t }}
    </a>
  {%- endform -%}
</div>
```

- **Form type**: Uses `recover_customer_password` form type.
- **Success tracking**: Stores `form.posted_successfully?` in `recover_success` variable for use in login form.
- **Error handling**: Displays error message with icon when form submission fails.
- **Accessibility**: Proper ARIA attributes (`aria-invalid`, `aria-describedby`) and autofocus on errors.
- **Cancel link**: Links back to login form via `#login` anchor.

### Customer Login Form

```liquid
<h1 id="login" tabindex="-1">
  {{ 'customer.login_page.title' | t }}
</h1>
<div>
  {%- if recover_success == true -%}
    <h3 class="form__message" tabindex="-1" autofocus>
      <span class="svg-wrapper">
        {{- 'icon-success.svg' | inline_asset_content -}}
      </span>
      {{ 'customer.recover_password.success' | t }}
    </h3>
  {%- endif -%}
  {%- form 'customer_login', novalidate: 'novalidate' -%}
    {%- if form.errors -%}
      <h2 class="form__message" tabindex="-1" autofocus>
        <span class="visually-hidden">{{ 'accessibility.error' | t }} </span>
        <span class="svg-wrapper">
          {{- 'icon-error.svg' | inline_asset_content -}}
        </span>
        {{ 'templates.contact.form.error_heading' | t }}
      </h2>
      {{ form.errors | default_errors }}
    {%- endif -%}

    <!-- Shop login button (conditional) -->
    <!-- Email input -->
    <!-- Password input (conditional) -->
    <!-- Forgot password link -->
    <!-- Sign in button -->
    <!-- Create account link -->
  {%- endform -%}
</div>
```

- **Form type**: Uses `customer_login` form with `novalidate: 'novalidate'` attribute.
- **Success message**: Displays recovery success message when `recover_success` is true.
- **Error handling**: Shows error heading and uses `default_errors` filter to display all form errors.
- **Password field**: Conditionally renders when `form.password_needed` is true.
- **Forgot password**: Links to recovery form via `#recover` anchor.

### Shop Login Integration

```liquid
{%- if shop.features.login_with_shop_classic_customer_accounts? -%}
  <section name="sign-in-with-shop-provider">
    {{ shop | login_button: hide_button: hide_shop_login_button }}

    {%- unless hide_shop_login_button -%}
      <p>
        {{ 'customer.login_page.alternate_provider_separator' | t }}
      </p>
    {%- endunless -%}
  </section>
{%- endif -%}
```

- Conditionally renders when Shop login feature is enabled.
- Uses `login_button` filter with `hide_button` parameter controlled by section setting.
- Displays separator text when Shop login button is visible.

### Guest Checkout

```liquid
{%- if shop.checkout.guest_login -%}
  <div>
    <hr>
    <h2>{{ 'customer.login_page.guest_title' | t }}</h2>

    {%- form 'guest_login' -%}
      <button>
        {{ 'customer.login_page.guest_continue' | t }}
      </button>
    {%- endform -%}
  </div>
{%- endif -%}
```

- Conditionally renders when guest checkout is enabled in shop settings.
- Uses `guest_login` form type for checkout without account creation.

---

## Behavior

- **Form switching**: Uses anchor links (`#recover`, `#login`) to toggle between password recovery and login forms.
- **Server-side validation**: All form validation handled server-side via Shopify's form processing.
- **Error handling**: Displays form errors with icons and proper ARIA attributes for accessibility.
- **Success messaging**: Shows success message after password recovery email is sent.
- **Conditional rendering**: Password field, Shop login, and guest checkout render based on shop settings and form state.
- **No JavaScript**: All functionality is server-side; no client-side interactions required.

---

## Schema

```json
{
  "name": "t:sections.main-login.name",
  "settings": [
    {
      "type": "checkbox",
      "id": "enable_shop_login_button",
      "label": "t:sections.main-login.shop_login_button.enable",
      "default": true
    },
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

### Section Settings

| Setting ID | Type | Default | Purpose |
|------------|------|---------|---------|
| `enable_shop_login_button` | checkbox | `true` | Show/hide Shop login button |
| `padding_top` | range (px) | 36 | Top padding (0–100px, step 4) |
| `padding_bottom` | range (px) | 36 | Bottom padding (0–100px, step 4) |

---

## Implementation Notes

1. **Translation keys**: All user-facing text uses translation filters (`customer.login_page.*`, `customer.recover_password.*`, `templates.contact.form.*`, etc.).

2. **Icon dependencies**: Ensure `icon-error.svg` and `icon-success.svg` exist in `assets/`; missing icons will break error/success message displays.

3. **Form types**: Section uses three different form types:
   - `recover_customer_password`: Password recovery form
   - `customer_login`: Customer login form
   - `guest_login`: Guest checkout form (conditional)

4. **Password field conditional**: Password input only renders when `form.password_needed` is true. This handles cases where password might not be required.

5. **Shop login integration**: Shop login button visibility controlled by:
   - `shop.features.login_with_shop_classic_customer_accounts?` (feature availability)
   - `section.settings.enable_shop_login_button` (section setting)

6. **Success message tracking**: Password recovery success is tracked via `recover_success` variable, which is set from `form.posted_successfully?` in the recovery form and used in the login form.

7. **Accessibility features**:
   - Proper ARIA attributes (`aria-invalid`, `aria-describedby`)
   - `tabindex="-1"` on headings for programmatic focus
   - `autofocus` on error states
   - Visually hidden error labels for screen readers
   - Proper form labels and input associations

8. **Form validation**: Login form uses `novalidate: 'novalidate'` to disable HTML5 validation, relying on server-side validation instead.

9. **Anchor navigation**: Form switching uses anchor links (`#recover`, `#login`). Ensure CSS handles smooth scrolling or that JavaScript handles this if needed.

10. **Guest checkout**: Guest checkout section only renders when `shop.checkout.guest_login` is enabled in shop settings. This is a shop-level setting, not a section setting.

11. **Error display**: Uses `form.errors | default_errors` filter to display all form errors in a formatted list.

12. **Responsive breakpoint**: Desktop padding applies at 750px; ensure this aligns with the theme's global breakpoint strategy.

13. **Customer CSS**: Section relies on `customer.css` for styling. Ensure this file exists and contains appropriate styles for login forms, fields, and error messages.

14. **Form state management**: The section handles multiple form states:
   - Initial login form
   - Password recovery form
   - Recovery success message
   - Form errors
   - Shop login integration

15. **Email autocomplete**: All email inputs use `autocomplete="email"` for better browser autofill support.

