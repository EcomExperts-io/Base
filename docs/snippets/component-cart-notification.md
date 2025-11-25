# component-cart-notification Snippet

`snippets/component-cart-notification.liquid` renders the add-to-cart confirmation drawer. It wraps the `<cart-notification>` web component, injects its markup/styles, and wires color scheme + layout options so the notification can be reused across headers.

---

## What It Does

- Outputs LiquidDoc documentation plus defaults for `color_scheme` and `desktop_menu_type`.
- Inlines scoped CSS (via `{% stylesheet %}`) to style the floating notification, headings, buttons, and responsive breakpoints.
- Renders the `<cart-notification>` custom element with the correct classes/ARIA attributes.
- Provides action links: view cart, checkout, and continue shopping.
- Includes `component-cart-notification.js` so the custom element can listen for Liquid Ajax Cart events.

---

## Parameters

| Parameter            | Type     | Default  | Description                                                                 |
|----------------------|----------|----------|-----------------------------------------------------------------------------|
| `color_scheme`       | string   | `nil`    | When provided, adds `color-{{ color_scheme }} gradient` to the drawer.      |
| `desktop_menu_type`  | string   | `blank`  | Determines layout wrapper; non-`drawer` adds the `page-width` utility class.|

> The snippet uses LiquidDoc style comments to describe these params inline.

---

## Markup Structure

```liquid
<cart-notification
  data-ajax-cart-section
  class="cart-notification-wrapper{% if desktop_menu_type != 'drawer' %} page-width{% endif %}"
>
  <div
    id="cart-notification"
    class="cart-notification {% if color_scheme %} color-{{ color_scheme }} gradient{% endif %}"
    aria-modal="true"
    aria-label="{{ 'general.cart.item_added' | t }}"
    role="dialog"
    tabindex="-1"
  >
    <!-- Header -->
    <!-- Product summary -->
    <!-- Actions -->
  </div>
</cart-notification>
<script src="{{ 'component-cart-notification.js' | asset_url }}" type="module"></script>
```

- Wrapper adds `data-ajax-cart-section` so Liquid Ajax Cart updates target the correct DOM node.
- Inner `div#cart-notification` acts as the dialog container with `role="dialog"` and localized `aria-label`.

---

## Sections

### 1. Inline Styles
- Declared inside `{% stylesheet %}` to scope the notification layout.
- Handles base positioning, transitions, typography, button styling, and responsive behavior for widths above/below 768px.

### 2. Header
- Contains `cart-notification__heading` with the checkmark icon (`icon-checkmark.svg`) and localized “item added” text.
- Close button uses `icon-close.svg`, `aria-label="\{\{ 'accessibility.close' | t \}\}"`, and a `cart-notification__close` class that the JS controller listens for.

### 3. Product Summary
- Placeholder `#cart-notification-product` updated by `component-cart-notification.js` with product image, vendor, title, and options.
- CSS ensures semantic `<dl>` styling for option pairs.

### 4. Actions
- “View cart” anchor shows current `item_count` via `data-ajax-cart-bind="item_count"`.
- Checkout form posts to `routes.cart_url` and submits `checkout`.
- “Continue shopping” button shares the `cart-notification-continue_shopping` class used by the JS controller to hide the drawer.

---

## JavaScript Dependency

The snippet always includes:

```liquid
<script src="{{ 'component-cart-notification.js' | asset_url }}" type="module"></script>
```

This ensures the `<cart-notification>` web component is registered. The module:
- Binds click handlers to the close/continue buttons.
- Listens for `liquid-ajax-cart:request-end`.
- Injects product markup and toggles the `cart-notification-open` class.

---

## Usage Example

```liquid
{% render 'component-cart-notification',
  color_scheme: 'scheme-2',
  desktop_menu_type: section.settings.desktop_menu_type
%}
```

Place the snippet near the header or global layout so it can overlay any page. Pass the header’s selected `color_scheme` for consistent theming and the desktop menu type to control the wrapper width.

---

## Implementation Notes

1. Keep translation keys like `general.cart.item_added`, `general.cart.view_empty_cart`, and `sections.cart.checkout` updated in `locales/en.default.json`.
2. The snippet relies on `icon-checkmark.svg` and `icon-close.svg` assets; avoid renaming without updating references.
3. If you customize button styles, do so inside the `{% stylesheet %}` block so overrides remain scoped.
4. Ensure only one instance of the snippet exists per page to avoid duplicate IDs (`cart-notification`, `cart-notification-product`).

