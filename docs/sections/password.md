# Password Section (`sections/password.liquid`)

`sections/password.liquid` renders the password-protected storefront page, displaying a branded login form for customers to enter the store password. It supports logo display, custom messaging, and optional contact information. The section includes form validation, error handling, and a modern, centered design with gradient background.

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | Inline `{% stylesheet %}` block |
| Icons | `icon-error.svg`, `icon-arrow.svg` (inline via `inline_asset_content`) |
| Data | Relies on `section.settings`, global `settings` object (logo), and `shop` object (password_message) |

- No JavaScript dependencies; the section is purely presentational.
- Form submission handled server-side via Shopify's password protection system.
- All styling lives inside the `{% stylesheet %}` block.

---

## Markup Structure

```liquid
<section id="{{ section_id }}" class="password-page">
  <div class="password-container">
    <div class="password-content">
      <!-- Logo/Brand Area -->
      {% if section.settings.show_logo and settings.logo %}
        <div class="password-logo">
          <img src="{{ settings.logo | image_url: width: 200 }}" alt="{{ shop.name | escape }}" width="200" height="auto" loading="eager">
        </div>
      {% else %}
        <div class="password-brand">
          <h1>{{ shop.name | escape }}</h1>
        </div>
      {% endif %}

      <!-- Main Content -->
      <div class="password-main">
        <h2 class="password-title">{{ 'password.title' | t }}</h2>

        {% if shop.password_message %}
          <div class="password-message">
            <p>{{ shop.password_message }}</p>
          </div>
        {% endif %}

        {% if section.settings.subtitle %}
          <p class="password-subtitle">{{ section.settings.subtitle }}</p>
        {% endif %}

        <!-- Password Form -->
        {% form 'storefront_password', class: 'password-form' %}
          <!-- Form fields and error handling -->
        {% endform %}

        <!-- Contact Information (conditional) -->
      </div>
    </div>
  </div>
</section>
```

- Section ID generated as `Password-\{\{ section.id \}\}` for unique targeting.
- Centered layout with max-width container for optimal display.
- Conditional logo/brand display based on settings.

### Logo/Brand Display

```liquid
{% if section.settings.show_logo and settings.logo %}
  <div class="password-logo">
    <img src="{{ settings.logo | image_url: width: 200 }}" alt="{{ shop.name | escape }}" width="200" height="auto" loading="eager">
  </div>
{% else %}
  <div class="password-brand">
    <h1>{{ shop.name | escape }}</h1>
  </div>
{% endif %}
```

- **Logo priority**: Shows logo image when `show_logo` is enabled and logo exists in theme settings.
- **Brand fallback**: Displays shop name as H1 when logo is not available or disabled.
- **Image optimization**: Logo rendered at 200px width with `loading="eager"` for immediate display.

### Password Form

```liquid
{% form 'storefront_password', class: 'password-form' %}
  {% if form.errors %}
    <div class="password-errors" role="alert">
      <div class="error-icon">
        {{ 'icon-error.svg' | inline_asset_content }}
      </div>
      <div class="error-message">
        {{ form.errors | default_errors }}
      </div>
    </div>
  {% endif %}

  <div class="password-input-group">
    <label for="PasswordInput-{{ section.id }}" class="password-label visually-hidden">
      {{ 'password.password' | t }}
    </label>

    <div class="password-field">
      <input
        type="password"
        name="password"
        id="PasswordInput-{{ section.id }}"
        class="password-input"
        placeholder="{{ 'password.password_placeholder' | t }}"
        autocomplete="current-password"
        required
      >
      <button type="submit" class="password-submit">
        <span class="submit-text">{{ 'password.enter' | t }}</span>
        <span class="submit-icon">
          {{ 'icon-arrow.svg' | inline_asset_content }}
        </span>
      </button>
    </div>
  </div>
{% endform %}
```

- **Form type**: Uses `storefront_password` form type for password protection.
- **Error handling**: Displays form errors with icon and formatted error messages.
- **Accessibility**: Label is visually hidden but available for screen readers.
- **Input styling**: Password input and submit button combined in a single field container.
- **Submit button**: Includes text and arrow icon for visual indication.

### Contact Information

```liquid
{% if section.settings.show_contact_info %}
  <div class="password-contact">
    <p>{{ 'password.contact_info' | t }}</p>
    {% if section.settings.contact_email %}
      <a href="mailto:{{ section.settings.contact_email }}" class="contact-link">
        {{ section.settings.contact_email }}
      </a>
    {% endif %}
  </div>
{% endif %}
```

- Conditionally renders when `show_contact_info` is enabled.
- Displays contact email as a mailto link when provided.
- Separated from main content with a border-top divider.

---

## Behavior

- **Server-side form processing**: Password form submission handled by Shopify's password protection system.
- **Error display**: Form errors shown with icon and formatted messages when password is incorrect.
- **Conditional content**: Logo, shop message, subtitle, and contact info all conditionally render based on settings and data availability.
- **Responsive design**: Layout adapts to mobile screens with reduced padding and font sizes.
- **No JavaScript**: All functionality is server-side; no client-side interactions required.

---

## Schema

```json
{
  "name": "Password Page",
  "settings": [
    {
      "type": "checkbox",
      "id": "show_logo",
      "label": "Show logo",
      "default": true,
      "info": "Uses the logo from theme settings"
    },
    {
      "type": "text",
      "id": "subtitle",
      "label": "Subtitle",
      "placeholder": "We're preparing something special for you..."
    },
    {
      "type": "checkbox",
      "id": "show_contact_info",
      "label": "Show contact information",
      "default": false
    },
    {
      "type": "text",
      "id": "contact_email",
      "label": "Contact email",
      "placeholder": "hello@example.com",
      "info": "Only shown if contact information is enabled"
    }
  ]
}
```

### Section Settings

| Setting ID | Type | Default | Purpose |
|------------|------|---------|---------|
| `show_logo` | checkbox | `true` | Display logo from theme settings |
| `subtitle` | text | — | Custom subtitle text below password message |
| `show_contact_info` | checkbox | `false` | Display contact information section |
| `contact_email` | text | — | Contact email address (mailto link) |

---

## Implementation Notes

1. **Translation keys**: Most user-facing text uses translation filters (`password.title`, `password.password`, `password.enter`, etc.), but some setting labels are hardcoded in English.

2. **Icon dependencies**: Ensure `icon-error.svg` and `icon-arrow.svg` exist in `assets/`; missing icons will break error display and submit button.

3. **Logo source**: Logo comes from theme settings (`settings.logo`), not section settings. Ensure logo is configured in theme settings.

4. **Shop password message**: The password message comes from `shop.password_message`, which is set in Shopify admin under Online Store > Preferences > Password protection.

5. **Form validation**: Password input uses HTML5 `required` attribute. Server-side validation handles incorrect passwords and displays errors.

6. **Section ID generation**: Section ID is constructed as `Password-\{\{ section.id \}\}` to ensure uniqueness.

7. **CSS styling**: All styles are defined in the `{% stylesheet %}` block, including:
   - Gradient background with decorative radial gradients
   - Centered card layout with shadow and border
   - Form field styling with focus states
   - Responsive breakpoints for mobile
   - Animation (fadeInUp) for content appearance
   - Accessibility styles (visually-hidden, focus outlines)

8. **Responsive breakpoint**: Mobile styles apply at 768px, adjusting padding, border radius, and font sizes.

9. **Accessibility features**:
   - Visually hidden label for password input (available to screen readers)
   - Proper form structure with labels and inputs
   - Focus styles for keyboard navigation
   - ARIA role="alert" for error messages

10. **Password form type**: Uses `storefront_password` form type, which is Shopify's built-in password protection form handler.

11. **Email validation**: Contact email is displayed as a mailto link. No validation is performed on the email format; ensure merchants enter valid email addresses.

12. **Animation**: Content card includes a fadeInUp animation for visual appeal. Animation is defined in the stylesheet block.

13. **Background styling**: Page uses gradient background with decorative radial gradients via CSS `::before` pseudo-element for visual depth.

14. **CSS custom properties**: Styles use CSS custom properties (`--color-background`, `--color-foreground`) for theme color integration. Ensure these variables are defined in the theme.

15. **No padding settings**: Unlike other sections, this section does not include padding controls in the schema. Padding is hardcoded in the stylesheet (2rem 1rem on page, 3rem on content).

