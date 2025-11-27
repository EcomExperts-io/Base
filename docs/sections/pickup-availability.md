# Pickup Availability Section (`sections/pickup-availability.liquid`)

`sections/pickup-availability.liquid` displays local pickup availability information for product variants. It shows the closest pickup location with availability status and pickup time, and provides a drawer interface to view all available pickup locations. The section uses custom elements for interactive behavior and conditionally renders based on pickup availability.

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | Likely requires CSS for custom elements (not explicitly loaded in this file) |
| Custom Elements | `<pickup-availability-preview>`, `<pickup-availability-drawer>` (require JavaScript definitions) |
| Icons | `icon-tick.svg`, `icon-close.svg` (inline via `inline_asset_content`) |
| Data | Relies on `product_variant` object (store_availabilities, product) |

- Requires JavaScript to define custom elements and handle drawer interactions.
- Section only renders when pickup-enabled locations exist (`pick_up_availabilities.size > 0`).
- Icons are embedded inline via the `inline_asset_content` filter.

---

## Markup Structure

```liquid
{%- assign pick_up_availabilities = product_variant.store_availabilities | where: 'pick_up_enabled', true -%}

{%- if pick_up_availabilities.size > 0 -%}
  <pickup-availability-preview class="pickup-availability-preview">
    <!-- Preview content with closest location -->
  </pickup-availability-preview>

  <pickup-availability-drawer class="gradient" tabindex="-1" role="dialog" aria-modal="true" aria-labelledby="PickupAvailabilityHeading">
    <!-- Drawer content with all locations -->
  </pickup-availability-drawer>
{%- endif -%}
```

- Section only renders when at least one pickup-enabled location exists.
- Two custom elements: preview (inline) and drawer (modal).
- Drawer uses proper ARIA attributes for accessibility.

### Preview Component

```liquid
<pickup-availability-preview class="pickup-availability-preview">
  {% assign closest_location = pick_up_availabilities.first %}

  {% if closest_location.available %}
    <span class="svg-wrapper">{{- 'icon-tick.svg' | inline_asset_content -}}</span>
  {% endif %}

  <div class="pickup-availability-info">
    {%- if closest_location.available -%}
      <p class="caption-large">
        {{ 'sections.main-product.blocks.pickup_availability.pick_up_available_at_html' | t: location_name: closest_location.location.name }}
      </p>
      <p class="caption">{{ closest_location.pick_up_time }}</p>
      <button
        id="ShowPickupAvailabilityDrawer"
        class="pickup-availability-button link link--text underlined-link"
        aria-haspopup="dialog"
      >
        {%- if pick_up_availabilities.size == 1 -%}
          {{ 'sections.main-product.blocks.pickup_availability.view_store_info' | t }}
        {%- else -%}
          {{ 'sections.main-product.blocks.pickup_availability.check_other_stores' | t }}
        {%- endif -%}
      </button>
    {%- else -%}
      <p class="caption-large">
        {{ 'sections.main-product.blocks.pickup_availability.pick_up_unavailable_at_html' | t: location_name: closest_location.location.name }}
      </p>
      {%- if pick_up_availabilities.size > 1 -%}
        <button id="ShowPickupAvailabilityDrawer" class="pickup-availability-button link link--text underlined-link" aria-haspopup="dialog">
          {{ 'sections.main-product.blocks.pickup_availability.check_other_stores' | t }}
        </button>
      {%- endif -%}
    {%- endif -%}
  </div>
</pickup-availability-preview>
```

- **Closest location**: Uses `pick_up_availabilities.first` to get the nearest location.
- **Availability status**: Shows tick icon and availability message when location has stock.
- **Pickup time**: Displays estimated pickup time when available.
- **Button text**: Changes based on number of locations (single vs. multiple).
- **Unavailable state**: Shows unavailable message and button only if multiple locations exist.

### Drawer Component

```liquid
<pickup-availability-drawer
  class="gradient"
  tabindex="-1"
  role="dialog"
  aria-modal="true"
  aria-labelledby="PickupAvailabilityHeading"
>
  <div class="pickup-availability-header">
    <h2 class="h3 pickup-availability-drawer-title" id="PickupAvailabilityHeading">
      {{ product_variant.product.title | escape }}
    </h2>
    <button class="pickup-availability-drawer-button" type="button" aria-label="{{ 'accessibility.close' | t }}">
      {{- 'icon-close.svg' | inline_asset_content -}}
    </button>
  </div>

  {%- unless product_variant.product.has_only_default_variant -%}
    <p class="pickup-availability-variant">
      <!-- Variant options display -->
    </p>
  {%- endunless -%}

  <div class="pickup-availability-list list-unstyled" role="list" data-store-availability-drawer-content>
    {%- for availability in pick_up_availabilities -%}
      <div class="pickup-availability-list__item">
        <h3 class="h4">{{ availability.location.name | escape }}</h3>
        <p class="pickup-availability-preview caption-large">
          {%- if availability.available -%}
            <span class="svg-wrapper">
              {{- 'icon-tick.svg' | inline_asset_content -}}
            </span>
            {{ 'sections.main-product.blocks.pickup_availability.pick_up_available' | t }},
            {{ availability.pick_up_time | downcase }}
          {%- endif -%}
        </p>

        {%- assign address = availability.location.address -%}
        <address class="pickup-availability-address">
          {{ address | format_address }}

          {%- if address.phone.size > 0 -%}
            <p>{{ address.phone }}</p>
          {%- endif -%}
        </address>
      </div>
    {%- endfor -%}
  </div>
</pickup-availability-drawer>
```

- **Dialog structure**: Proper ARIA attributes for modal dialog (`role="dialog"`, `aria-modal="true"`).
- **Header**: Product title and close button with accessible label.
- **Variant display**: Shows selected variant options when product has multiple variants.
- **Location list**: Iterates through all pickup-enabled locations with:
  - Location name
  - Availability status and pickup time
  - Formatted address
  - Phone number (if available)

---

## Behavior

- **Conditional rendering**: Section only renders when `pick_up_availabilities.size > 0`.
- **Custom elements**: Requires JavaScript to define `<pickup-availability-preview>` and `<pickup-availability-drawer>` custom elements.
- **Drawer interaction**: Button with `id="ShowPickupAvailabilityDrawer"` triggers drawer opening (handled by JavaScript).
- **Accessibility**: Full ARIA support for modal dialog, proper heading hierarchy, and keyboard navigation.
- **Server-side rendering**: All content rendered server-side; JavaScript handles drawer show/hide behavior.

---

## Schema

This section does not include a `{% schema %}` block, meaning:

- No customizable settings in the theme editor.
- All configuration comes from the `product_variant` object and store availability data.
- Section is likely used as a block within product sections or as a snippet.

**Note**: This section may be intended for use as a block or snippet rather than a standalone section. Consider adding a schema block if merchants need customization options.

---

## Implementation Notes

1. **Translation keys**: All user-facing text uses translation filters (`sections.main-product.blocks.pickup_availability.*`, `accessibility.close`).

2. **Icon dependencies**: Ensure `icon-tick.svg` and `icon-close.svg` exist in `assets/`; missing icons will break availability indicators and close button.

3. **Product variant context**: This section requires a `product_variant` object. It's typically used within product sections or as a block that receives the variant as a parameter.

4. **Custom elements**: The section uses custom elements (`<pickup-availability-preview>` and `<pickup-availability-drawer>`) which must be defined in JavaScript. Ensure corresponding JavaScript files exist and are loaded:
   - `component-pickup-availability.js` or similar
   - Custom elements should handle drawer open/close behavior

5. **Store availability filtering**: Uses Liquid filter to get only pickup-enabled locations: `product_variant.store_availabilities | where: 'pick_up_enabled', true`.

6. **Closest location logic**: Uses `pick_up_availabilities.first` to get the closest location. Shopify orders locations by proximity automatically.

7. **Availability status**: Each location has an `available` property that determines if stock is available for pickup.

8. **Pickup time display**: Pickup time is displayed in lowercase via `downcase` filter for consistent formatting.

9. **Variant options display**: Shows selected variant options when product has multiple variants. Options are displayed as "Option Name: Selected Value" format.

10. **Address formatting**: Uses Shopify's `format_address` filter for proper address localization and formatting.

11. **Phone number display**: Location phone numbers are conditionally displayed when available (`address.phone.size > 0`).

12. **Button ID**: Preview button uses `id="ShowPickupAvailabilityDrawer"` which should be targeted by JavaScript to open the drawer.

13. **Drawer content attribute**: Drawer list uses `data-store-availability-drawer-content` attribute, which may be used by JavaScript for dynamic updates.

14. **No schema block**: Section lacks a schema, suggesting it may be used as a block or snippet. If used as a section, consider adding settings for customization.

15. **Accessibility features**:
    - Proper ARIA roles and attributes for modal dialog
    - `aria-labelledby` linking to heading
    - `aria-haspopup="dialog"` on trigger button
    - `tabindex="-1"` on drawer for focus management
    - Semantic HTML (`<address>` tag for addresses)

16. **Conditional button display**: Button text and visibility change based on:
    - Number of locations (single vs. multiple)
    - Availability status (available vs. unavailable)

17. **CSS class dependencies**: Section relies on CSS classes like `gradient`, `caption-large`, `caption`, `link`, `underlined-link`, etc. Ensure these are defined in theme CSS.

