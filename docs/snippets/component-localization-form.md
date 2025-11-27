# component-localization-form Snippet

`snippets/component-localization-form.liquid` renders country and/or language selectors for Shopify store localization. It provides dropdown menus with Alpine.js for toggle behavior and uses the `<localization-form>` custom element to handle form submission. The component conditionally renders based on available countries/languages and integrates with Shopify's localization system.

---

## What It Does

- Renders country selector dropdown with currency information.
- Renders language selector dropdown with native language names.
- Uses Alpine.js for dropdown open/close state and click-outside detection.
- Integrates with Shopify's `localization` form for country/language switching.
- Uses `<localization-form>` custom element for form submission handling.
- Conditionally renders only when multiple options are available.
- Displays currency codes and symbols for country selection.

---

## Parameters

| Parameter              | Type    | Default | Description                                                      |
|------------------------|---------|---------|------------------------------------------------------------------|
| `enable_country_selector` | boolean | optional | If true, show country selector (only renders if multiple countries available). |
| `enable_language_selector` | boolean | optional | If true, show language selector (only renders if multiple languages available). |
| `menu_color_scheme`    | string  | optional | Color scheme for the dropdown list styling.                     |

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | Inline `{% stylesheet %}` block with localization styling |
| JavaScript | Alpine.js (required for dropdown state), `component-localization-form.js` (defines `<localization-form>` custom element) |
| Icons | `icon-caret.svg` (inline via `inline_asset_content`) |
| Forms | Shopify `localization` form (for country/language switching) |
| Data | Requires `localization` object with `available_countries`, `available_languages`, `country`, `language` |

- Alpine.js powers dropdown state (`x-data`, `x-show`, `@click.outside`).
- Custom element handles form submission and value updates.
- Inline styles provide all localization-specific CSS (no external CSS file required).

---

## Dynamic Styles

The snippet includes inline styles for localization button, dropdown, and list styling:

```liquid
{% stylesheet %}
  localization-form {
    display: grid;
    place-items: center;
  }
  .localization-button {
    display: flex;
    align-items: center;
    gap: 10px;
    color: inherit;
    background: transparent;
    min-width: max-content;
    max-width: 100%;
    border: 0;
    padding: 0;
    cursor: pointer;
  }
  .localization-button.localization-open svg {
    transform: scaleY(-1);
  }
  .localization-list {
    position: absolute;
    box-shadow: #0000001a 0 1px 3px,#0000000f 0 1px 2px;
    list-style: none;
    padding: 0;
    margin-top: 10px;
    max-height: 60vh;
    overflow: auto;
  }
{% endstylesheet %}
```

- **Grid layout**: Custom element uses grid for centering.
- **Button styling**: Transparent button with flex layout.
- **Caret rotation**: Caret icon flips vertically when dropdown is open.
- **Dropdown positioning**: Absolute positioning with shadow for card-like appearance.
- **Scrollable list**: Max height with overflow for long country/language lists.

---

## Markup Structure

### Country Selector

```liquid
{% if enable_country_selector and localization.available_countries.size > 1 %}
  <localization-form>
    {% form 'localization' %}
      <div class="localization-wrapper" x-data="{ localizationOpen: false }" @click.outside="localizationOpen = false">
        <button type="button" class="localization-button" aria-controls="CountryList" @click="localizationOpen = !localizationOpen" :class="{ 'localization-open': localizationOpen }">
          <span>
            {{ localization.country.name }} ({{ localization.country.currency.iso_code }} {{ localization.country.currency.symbol }})
          </span>
          {{- 'icon-caret.svg' | inline_asset_content -}}
        </button>
        <ul x-show="localizationOpen" x-cloak id="CountryList" role="list" class="localization-list color-{{ menu_color_scheme }} gradient">
          {% for country in localization.available_countries %}
            <li class="localization-item" tabindex="-1">
              <a href="#" {% if country.iso_code == localization.country.iso_code %}aria-current="true"{% endif %} data-value="{{ country.iso_code }}">
                {{ country.name }} ({{ country.currency.iso_code }} {{ country.currency.symbol }})
              </a>
            </li>
          {% endfor %}
        </ul>
        <input type="hidden" name="country_code" value="{{ localization.country.iso_code }}">
      </div>
    {% endform %}
  </localization-form>
{% endif %}
```

- **Conditional rendering**: Only renders if `enable_country_selector` is true and multiple countries available.
- **Custom element**: Uses `<localization-form>` wrapper for JavaScript functionality.
- **Shopify form**: Uses `form 'localization'` for country switching.
- **Currency display**: Shows country name, currency ISO code, and symbol.

### Language Selector

```liquid
{% if enable_language_selector and localization.available_languages.size > 1 %}
  <localization-form>
    {% form 'localization' %}
      <div class="localization-wrapper" x-data="{ localizationOpen: false }" @click.outside="localizationOpen = false">
        <button type="button" class="localization-button" aria-controls="LanguageList" @click="localizationOpen = !localizationOpen" :class="{ 'localization-open': localizationOpen }">
          {{ localization.language.endonym_name | capitalize }}
          {{- 'icon-caret.svg' | inline_asset_content -}}
        </button>
        <ul x-show="localizationOpen" x-cloak id="LanguageList" role="list" class="localization-list color-{{ menu_color_scheme }} gradient">
          {% for language in localization.available_languages %}
            <li class="localization-item" tabindex="-1">
              <a href="#" {% if language.iso_code == localization.language.iso_code %}aria-current="true"{% endif %} hreflang="{{ language.iso_code }}" lang="{{ language.iso_code }}" data-value="{{ language.iso_code }}">
                {{ language.endonym_name | capitalize }}
              </a>
            </li>
          {% endfor %}
        </ul>
        <input type="hidden" name="language_code" value="{{ localization.language.iso_code }}">
      </div>
    {% endform %}
  </localization-form>
{% endif %}
```

- **Conditional rendering**: Only renders if `enable_language_selector` is true and multiple languages available.
- **Native names**: Uses `endonym_name` (language name in its own language).
- **Language attributes**: Includes `hreflang` and `lang` attributes for proper language indication.

---

## Behavior

- **Dropdown toggle**: Clicking button opens/closes dropdown.
- **Click outside**: Clicking outside dropdown closes it automatically.
- **Form submission**: Selecting country/language triggers form submission via custom element.
- **Value update**: Custom element updates hidden input and submits form.
- **Page reload**: Form submission causes page reload with new country/language.
- **Current indicator**: Current selection marked with `aria-current="true"`.
- **Smooth transitions**: Alpine.js provides smooth show/hide animations.

---

## Usage Example

```liquid
{% render 'component-localization-form',
  enable_country_selector: section.settings.enable_country_selector,
  enable_language_selector: section.settings.enable_language_selector,
  menu_color_scheme: section.settings.menu_color_scheme
%}
```

Or with individual settings:

```liquid
{% render 'component-localization-form',
  enable_country_selector: true,
  enable_language_selector: false,
  menu_color_scheme: 'scheme-1'
%}
```

Typically used in:
- Header (`sections/header.liquid`)
- Footer (`sections/footer.liquid`)
- Navigation components

---

## Implementation Notes

1. **Alpine.js requirement**: Snippet requires Alpine.js to be loaded in the theme for dropdown state management.

2. **Custom element requirement**: Requires `component-localization-form.js` to be loaded which defines the `<localization-form>` custom element.

3. **Conditional rendering**: Both selectors only render when:
    - Parameter is enabled (`enable_country_selector` or `enable_language_selector`)
    - Multiple options are available (`localization.available_countries.size > 1` or `localization.available_languages.size > 1`)

4. **Shopify localization form**: Uses `form 'localization'` which is Shopify's built-in form for country/language switching.

5. **Hidden inputs**: Each form includes hidden input with current value:
    - Country: `name="country_code"` with `value="\{\{ localization.country.iso_code \}\}"`
    - Language: `name="language_code"` with `value="\{\{ localization.language.iso_code \}\}"`

6. **Custom element behavior**: The `<localization-form>` custom element:
    - Listens for clicks on dropdown links
    - Updates hidden input value from `data-value` attribute
    - Submits the form automatically
    - Causes page reload with new country/language

7. **Currency display**: Country selector shows:
    - Country name
    - Currency ISO code (e.g., "USD")
    - Currency symbol (e.g., "$")
    Format: `Country Name (USD $)`

8. **Language display**: Language selector shows:
    - Native language name (`endonym_name`)
    - Capitalized for consistency
    - Examples: "English", "Español", "Français"

9. **Alpine.js directives**:
    - `x-data="{ localizationOpen: false }"`: Initializes dropdown state
    - `@click="localizationOpen = !localizationOpen"`: Toggles dropdown on button click
    - `x-show="localizationOpen"`: Shows/hides dropdown
    - `@click.outside="localizationOpen = false"`: Closes on outside click
    - `:class="{ 'localization-open': localizationOpen }"`: Adds class when open
    - `x-cloak`: Prevents flash of unstyled content

10. **Icon dependency**: Requires `icon-caret.svg` in the `assets/` folder for dropdown indicator.

11. **CSS class dependencies**: Snippet relies on CSS classes:
    - `.localization-wrapper`
    - `.localization-button`
    - `.localization-open`
    - `.localization-list`
    - `.localization-item`
    - `.color-\{\{ menu_color_scheme \}\}`
    - `.gradient`

12. **Accessibility features**:
    - Proper ARIA attributes (`aria-controls`, `aria-current`)
    - Semantic HTML (`role="list"`, proper list structure)
    - Keyboard navigation support
    - Screen reader support via ARIA

13. **Current selection**: Current country/language is marked with `aria-current="true"` for screen readers.

14. **Language attributes**: Language links include `hreflang` and `lang` attributes for proper language indication and SEO.

15. **Tabindex**: List items use `tabindex="-1"` to allow programmatic focus management.

16. **Color scheme**: Dropdown list uses `color-\{\{ menu_color_scheme \}\}` class for theme integration.

17. **Gradient class**: Dropdown includes `gradient` class for additional styling options.

18. **Form submission**: Form submission causes full page reload to apply new country/language settings.

19. **Data attributes**: Links use `data-value` attribute to store country/language ISO codes for JavaScript targeting.

20. **No translation keys**: Country and language names come directly from Shopify `localization` object, not translation files.

21. **Currency symbol**: Currency symbol is retrieved from `localization.country.currency.symbol`.

22. **Currency ISO code**: Currency ISO code is retrieved from `localization.country.currency.iso_code`.

23. **Language endonym**: Uses `endonym_name` which is the language name in its own language (e.g., "Español" for Spanish, not "Spanish").

24. **Capitalization**: Language names are capitalized using `capitalize` filter for consistency.

25. **Multiple forms**: Country and language selectors use separate forms, allowing independent selection.

26. **Dropdown positioning**: Dropdown uses absolute positioning with shadow for card-like appearance above other content.

27. **Max height**: Dropdown has `max-height: 60vh` with `overflow: auto` for scrollable long lists.

28. **Caret animation**: Caret icon flips vertically (`scaleY(-1)`) when dropdown is open for visual feedback.

29. **Click outside handling**: Uses Alpine.js `@click.outside` directive to close dropdown when clicking outside.

30. **Hidden input names**: 
    - Country form uses `name="country_code"`
    - Language form uses `name="language_code"`
    These are Shopify's required form field names for localization.

31. **ISO code format**: Both country and language use ISO codes (e.g., "US", "EN") stored in `data-value` attributes.

32. **Link prevention**: Links use `href="#"` and prevent default via JavaScript to handle selection without navigation.

33. **Custom element structure**: The `<localization-form>` custom element wraps each form and handles:
    - Finding the hidden input
    - Listening for link clicks
    - Updating input value
    - Submitting form

34. **Grid centering**: Custom element uses `display: grid` and `place-items: center` for centering content.

35. **Button text**: Button displays current selection (country with currency or language name).

36. **List styling**: Dropdown list has:
    - Box shadow for depth
    - No list markers
    - Border between items
    - Padding for touch targets

37. **Responsive design**: Dropdown adapts to content width with `min-width: max-content` and `max-width: 100%` constraints.

38. **Transition timing**: Caret icon transition uses 300ms ease for smooth animation.

39. **No conditional logic for single option**: If only one country/language is available, the selector doesn't render (no need for selection).

40. **Shopify localization integration**: Fully integrates with Shopify's localization system, which handles:
    - Currency conversion
    - Language-specific content
    - Regional pricing
    - Tax calculations

