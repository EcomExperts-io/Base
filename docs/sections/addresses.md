# Addresses Section (`sections/addresses.liquid`)

`sections/addresses.liquid` renders the customer addresses management page where customers can view, add, edit, and delete their saved addresses. It includes pagination for large address lists, dynamic province/state selection based on country, and comprehensive form validation. The section uses JavaScript for interactive address management and province/state dropdown population.

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | `customer.css` |
| JavaScript | `shopify.js`, `customer.js` (deferred) |
| Icons | `icon-caret.svg` (inline via `inline_asset_content`) |
| Forms | Shopify `customer_address` form (for add/edit) |
| Data | `customer.addresses` object, `all_country_option_tags` |

- Uses shared `customer.css` for consistent customer account styling.
- JavaScript files are loaded with `defer` attribute for non-blocking execution.
- Icons are embedded inline via the `inline_asset_content` filter.
- Section uses pagination to handle large address lists (5 addresses per page).

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
{%- paginate customer.addresses by 5 -%}
  <div class="customer addresses section-{{ section.id }}-padding" data-customer-addresses>
    <h1>{{ 'customer.addresses.title' | t }}</h1>
    <a href="{{ routes.account_url }}">{{ 'customer.account.return' | t }}</a>
    
    <!-- Add new address form -->
    <div data-address>
      <!-- Add address button and form -->
    </div>
    
    <!-- Existing addresses list -->
    <ul role="list">
      {%- for address in customer.addresses -%}
        <li data-address>
          <!-- Address display, edit form, delete button -->
        </li>
      {%- endfor -%}
    </ul>
    
    <!-- Pagination -->
  </div>
{%- endpaginate -%}
```

- **Pagination**: Addresses are paginated with 5 addresses per page.
- **Data attribute**: Uses `data-customer-addresses` for JavaScript targeting.
- **Return link**: Provides link back to account page.
- **Address containers**: Each address (new and existing) uses `data-address` attribute for JavaScript targeting.

### Add New Address Form

```liquid
<div data-address>
  <button type="button" aria-expanded="false" aria-controls="AddAddress">
    {{ 'customer.addresses.add_new' | t }}
  </button>
  <div id="AddAddress">
    <h2 id="AddressNewHeading">{{ 'customer.addresses.add_new' | t }}</h2>
    {%- form 'customer_address', customer.new_address, aria-labelledBy: 'AddressNewHeading' -%}
      <!-- Address form fields -->
    {%- endform -%}
  </div>
</div>
```

- **Collapsible form**: Form is hidden by default and toggled via button.
- **ARIA attributes**: Button uses `aria-expanded` and `aria-controls` for accessibility.
- **Form type**: Uses `customer_address` form with `customer.new_address` object.

### Address Form Fields

The form includes the following fields (same structure for both add and edit):

#### Text Fields
- **First Name**: `address[first_name]`, `autocomplete="given-name"`
- **Last Name**: `address[last_name]`, `autocomplete="family-name"`
- **Company**: `address[company]`, `autocomplete="organization"` (optional)
- **Address Line 1**: `address[address1]`, `autocomplete="address-line1"`
- **Address Line 2**: `address[address2]`, `autocomplete="address-line2"` (optional)
- **City**: `address[city]`, `autocomplete="address-level2"`
- **ZIP/Postal Code**: `address[zip]`, `autocomplete="postal-code"`, `autocapitalize="characters"`
- **Phone**: `address[phone]`, `type="tel"`, `autocomplete="tel"`

#### Country and Province Selects

```liquid
<div>
  <label for="AddressCountryNew">{{ 'customer.addresses.country' | t }}</label>
  <div class="select">
    <select
      id="AddressCountryNew"
      name="address[country]"
      data-default="{{ form.country }}"
      autocomplete="country"
    >
      {{ all_country_option_tags }}
    </select>
    <span class="svg-wrapper">
      {{- 'icon-caret.svg' | inline_asset_content -}}
    </span>
  </div>
</div>
<div id="AddressProvinceContainerNew" style="display: none">
  <label for="AddressProvinceNew">{{ 'customer.addresses.province' | t }}</label>
  <div class="select">
    <select
      id="AddressProvinceNew"
      name="address[province]"
      data-default="{{ form.province }}"
      autocomplete="address-level1"
    ></select>
    <span class="svg-wrapper">
      {{- 'icon-caret.svg' | inline_asset_content -}}
    </span>
  </div>
</div>
```

- **Country select**: Populated with `all_country_option_tags` Liquid tag.
- **Province container**: Hidden by default, shown when selected country has provinces.
- **Dynamic province loading**: Province options are populated via JavaScript based on selected country.
- **Data attributes**: Country select uses `data-default` to set initial value.
- **Edit forms**: Edit forms use `data-address-country-select` and `data-form-id` attributes for JavaScript targeting.

#### Default Address Checkbox

```liquid
<div>
  {{ form.set_as_default_checkbox }}
  <label for="address_default_address_new">{{ 'customer.addresses.set_default' | t }}</label>
</div>
```

- **Shopify helper**: Uses `form.set_as_default_checkbox` to generate checkbox markup.
- **Default address**: Allows setting the address as the default shipping/billing address.

### Existing Addresses Display

```liquid
<ul role="list">
  {%- for address in customer.addresses -%}
    <li data-address>
      {%- if address == customer.default_address -%}
        <h2>{{ 'customer.addresses.default' | t }}</h2>
      {%- endif -%}
      {{ address | format_address }}
      <button type="button" id="EditFormButton_{{ address.id }}" aria-label="..." aria-controls="EditAddress_{{ address.id }}" aria-expanded="false" data-address-id="{{ address.id }}">
        {{ 'customer.addresses.edit' | t }}
      </button>
      <button type="button" aria-label="..." data-target="{{ address.url }}" data-confirm-message="{{ 'customer.addresses.delete_confirm' | t }}">
        {{ 'customer.addresses.delete' | t }}
      </button>
      <div id="EditAddress_{{ address.id }}">
        <!-- Edit form (same structure as add form) -->
      </div>
    </li>
  {%- endfor -%}
</ul>
```

- **Default address indicator**: Shows "Default" heading for the default address.
- **Address formatting**: Uses `format_address` filter for proper address display.
- **Edit button**: Toggles edit form visibility with proper ARIA attributes.
- **Delete button**: Includes `data-target` (address URL) and `data-confirm-message` for JavaScript confirmation.
- **Edit form**: Same structure as add form but with address-specific IDs and form values.

### Pagination

```liquid
{%- if paginate.pages > 1 -%}
  {%- if paginate.parts.size > 0 -%}
    <nav class="pagination" role="navigation" aria-label="{{ 'general.pagination.label' | t }}">
      <ul role="list">
        <!-- Previous, page numbers, next -->
      </ul>
    </nav>
  {%- endif -%}
{%- endif -%}
```

- **Conditional display**: Only shows when multiple pages exist.
- **Accessibility**: Proper ARIA roles and labels for navigation.
- **Page numbers**: Shows page numbers with current page indicated via `aria-current="page"`.

### JavaScript Initialization

```liquid
<script>
  window.addEventListener('load', () => {
    typeof CustomerAddresses !== 'undefined' && new CustomerAddresses();
  });
</script>
```

- **Class initialization**: Initializes `CustomerAddresses` class from `customer.js`.
- **Safety check**: Checks if class exists before instantiating.
- **Window load**: Waits for full page load before initialization.

---

## Behavior

- **Add address**: Button toggles add address form visibility.
- **Edit address**: Edit button toggles edit form visibility for each address.
- **Delete address**: Delete button triggers confirmation dialog and removes address.
- **Province/state selection**: Province dropdown dynamically populates based on selected country via JavaScript.
- **Form validation**: Server-side validation with error display.
- **Default address**: Checkbox allows setting address as default.
- **Pagination**: Navigate through multiple pages of addresses (5 per page).
- **Accessibility**: Full ARIA support for collapsible forms and buttons.

---

## Schema

```json
{
  "name": "t:sections.main-addresses.name",
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

1. **Translation keys**: All user-facing text uses translation filters (`customer.addresses.*`, `customer.account.return`, `general.pagination.*`).

2. **Form field naming**: Form fields use Shopify's address object structure: `address[first_name]`, `address[last_name]`, etc.

3. **ID naming convention**: Form field IDs use descriptive prefixes:
   - Add form: `AddressFirstNameNew`, `AddressLastNameNew`, etc.
   - Edit form: `AddressFirstName_\{\{ form.id \}\}`, `AddressLastName_\{\{ form.id \}\}`, etc.

4. **Icon dependency**: Requires `icon-caret.svg` in the `assets/` folder for select dropdown indicators.

5. **CSS class dependencies**: Section relies on CSS classes from `customer.css`:
   - `.customer`
   - `.addresses`
   - `.field`
   - `.select`
   - `.svg-wrapper`
   - `.pagination`

6. **Autocomplete attributes**: All form fields use appropriate HTML5 autocomplete values:
   - `given-name`, `family-name` for names
   - `address-line1`, `address-line2` for addresses
   - `address-level2` for city
   - `address-level1` for province
   - `postal-code` for ZIP
   - `country`, `tel`, `organization` for respective fields

7. **JavaScript dependencies**: Requires `shopify.js` and `customer.js` for:
   - Province/state dropdown population
   - Form toggle functionality
   - Delete confirmation dialogs
   - Address management

8. **Pagination**: Uses `{% paginate customer.addresses by 5 %}` to limit addresses per page.

9. **Address formatting**: Uses `format_address` filter to display addresses in localized format.

10. **Default address**: Checks `address == customer.default_address` to identify and display default address indicator.

11. **Edit form IDs**: Edit forms use `form.id` in field IDs to ensure uniqueness across multiple addresses.

12. **Province container visibility**: Province container is hidden by default (`style="display: none"` or `style="display:none;"`) and shown via JavaScript when country with provinces is selected.

13. **Country option tags**: Uses `all_country_option_tags` Liquid tag to generate country dropdown options.

14. **Data attributes for JavaScript**:
    - `data-customer-addresses`: Main container
    - `data-address`: Individual address containers
    - `data-address-id`: Address ID for edit forms
    - `data-address-country-select`: Country select for edit forms
    - `data-form-id`: Form ID for province container targeting
    - `data-target`: Address URL for delete functionality
    - `data-confirm-message`: Confirmation message for delete

15. **ARIA attributes**: Comprehensive ARIA support:
    - `aria-expanded` for collapsible forms
    - `aria-controls` linking buttons to forms
    - `aria-label` for button descriptions
    - `aria-labelledBy` for form headings
    - `role="list"` and `role="navigation"` for semantic structure

16. **Form value persistence**: Form fields preserve values on validation errors using `form.first_name`, `form.last_name`, etc.

17. **ZIP code autocapitalize**: ZIP code field uses `autocapitalize="characters"` to suggest uppercase input.

18. **Phone field type**: Phone field uses `type="tel"` for mobile keyboard optimization.

19. **Delete confirmation**: Delete buttons include `data-confirm-message` for JavaScript confirmation dialogs.

20. **Pagination accessibility**: Pagination includes proper ARIA labels for previous, next, and page number links.

21. **CustomerAddresses class**: JavaScript class handles:
    - Province/state dropdown population
    - Form show/hide toggles
    - Delete confirmation and submission
    - Address form management

22. **Responsive design**: Padding adjusts from 75% on mobile to 100% on desktop (750px breakpoint).

23. **Return link**: Provides navigation back to account page via `routes.account_url`.

24. **Address URL**: Each address has a `url` property used for delete operations (`address.url`).

25. **Form ID usage**: Edit forms use `form.id` to generate unique IDs and data attributes for JavaScript targeting.

26. **Default checkbox**: Uses Shopify's `form.set_as_default_checkbox` helper which generates proper checkbox markup with correct name and ID attributes.

27. **Province data attributes**: Edit forms use `data-default` on both country and province selects to set initial values from existing address data.

28. **Empty state**: No explicit empty state - if customer has no addresses, only the add form is shown.

29. **Address limit**: Pagination shows 5 addresses per page, but there's no hard limit on total addresses a customer can have.

30. **Translation key structure**: Translation keys follow hierarchical structure:
    - `customer.addresses.title`
    - `customer.addresses.add_new`
    - `customer.addresses.first_name`
    - `customer.addresses.*` (all field labels)
    - `customer.addresses.edit`, `delete`, `update`, `cancel`
    - `customer.addresses.set_default`
    - `customer.addresses.delete_confirm`

