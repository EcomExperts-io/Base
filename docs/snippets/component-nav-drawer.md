# component-nav-drawer Snippet

`snippets/component-nav-drawer.liquid` renders a slide-in navigation drawer for mobile and desktop navigation. It provides a toggle button, slide-in panel with nested navigation, and optional localization and account links in the footer. The drawer uses Alpine.js for open/close state management and integrates with `component-nav-dropdown` for nested menu rendering.

---

## What It Does

- Renders a slide-in navigation drawer that slides in from the left.
- Provides a toggle button that switches between menu and close icons.
- Displays nested navigation via `component-nav-dropdown` snippet.
- Includes optional localization selectors (country/language) in footer.
- Includes optional customer account link in footer.
- Uses Alpine.js for drawer state management and click-outside detection.
- Supports full-height drawer with scrollable content.

---

## Parameters

| Parameter              | Type    | Default | Description                                                      |
|------------------------|---------|---------|------------------------------------------------------------------|
| `menu`                 | linklist| **required** | Menu object to render in navigation.                             |
| `menu_color_scheme`    | string  | optional | Color scheme handle for drawer background styling.              |
| `enable_country_selector` | boolean | optional | If true, show country selector in drawer footer.                |
| `enable_language_selector` | boolean | optional | If true, show language selector in drawer footer.               |
| `enable_customer_avatar` | boolean | optional | If true, show customer account icon link in drawer footer.        |

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | Inline `{% stylesheet %}` block with comprehensive drawer styling |
| JavaScript | Alpine.js (required for drawer state) |
| Snippets | `component-nav-dropdown` (for nested navigation), `component-localization-form` (conditional) |
| Icons | `icon-menu.svg`, `icon-close.svg`, `icon-account.svg` (inline via `inline_asset_content`) |
| Data | Requires `menu` linklist object, `shop.customer_accounts_enabled`, `customer` object (conditional), `localization` object (conditional) |

- Alpine.js powers drawer state (`x-data`, `:class`, `@click.outside`).
- Inline styles provide all drawer-specific CSS (no external CSS file required).
- Navigation rendering delegated to `component-nav-dropdown` snippet.

---

## Dynamic Styles

The snippet includes inline styles for drawer positioning, animations, and layout:

```liquid
{% stylesheet %}
  #menu-drawer {
    position: absolute;
    top: calc(100% + 1px);
    left: 0;
    width: min(500px, 100%);
    height: calc(100vh - var(--header-height));
    transform: translateX(-100%);
    z-index: -1;
    transition: 300ms ease;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }
  #header-drawer #menu-drawer.drawer-open {
    transform: translateX(0);
  }
  /* ... additional styling ... */
{% endstylesheet %}
```

- **Slide animation**: Drawer slides in from left using `transform: translateX(-100%)` to `translateX(0)`.
- **Full height**: Drawer height accounts for header: `calc(100vh - var(--header-height))`.
- **Max width**: Drawer width limited to `min(500px, 100%)` for responsive sizing.
- **Z-index**: Uses `z-index: -1` when closed to prevent interaction.

---

## Markup Structure

```liquid
<div id="header-drawer" x-data="{ drawerOpen: false }" @click.outside="drawerOpen = false">
  <button class="header-drawer_icons" @click="drawerOpen = !drawerOpen" :class="{ 'drawer-open': drawerOpen }">
    <!-- Menu and close icons -->
  </button>
  <div id="menu-drawer" class="color-{{ menu_color_scheme }} gradient" :class="{ 'drawer-open': drawerOpen }">
    <!-- Navigation dropdown -->
    <!-- Footer actions (localization, account) -->
  </div>
</div>
```

- **Alpine.js state**: Uses `x-data="{ drawerOpen: false }"` for drawer open/close state.
- **Click outside**: Closes drawer when clicking outside via `@click.outside`.
- **Dynamic class**: Applies `drawer-open` class when drawer is open.

### Toggle Button

```liquid
<button
  class="header-drawer_icons"
  @click="drawerOpen = !drawerOpen"
  :class="{ 'drawer-open': drawerOpen }"
>
  {{- 'icon-menu.svg' | inline_asset_content -}}
  {{- 'icon-close.svg' | inline_asset_content -}}
</button>
```

- **Icon toggle**: Shows menu icon when closed, close icon when open.
- **CSS control**: Icon visibility controlled via CSS based on `drawer-open` class.
- **Toggle behavior**: Clicking button toggles drawer open/closed.

### Drawer Content

```liquid
<div
  id="menu-drawer"
  class="color-{{ menu_color_scheme }} gradient"
  :class="{ 'drawer-open': drawerOpen }"
>
  {% render 'component-nav-dropdown', nav_style: 'drawer', menu: menu, menu_color_scheme: menu_color_scheme %}

  <div class="menu-drawer_action">
    <!-- Localization and account links -->
  </div>
</div>
```

- **Navigation**: Renders `component-nav-dropdown` with `nav_style: 'drawer'`.
- **Color scheme**: Applies theme color scheme for consistent styling.
- **Footer actions**: Contains localization and account links at bottom.

### Footer Actions

```liquid
<div class="menu-drawer_action">
  {% if enable_country_selector or enable_language_selector %}
    <div class="menu-drawer_localization">
      {%- render 'component-localization-form',
        enable_country_selector: enable_country_selector,
        enable_language_selector: enable_language_selector,
        menu_color_scheme: menu_color_scheme
      -%}
    </div>
  {% endif %}

  {% if shop.customer_accounts_enabled and enable_customer_avatar %}
    <a
      href="{% if customer %}{{ routes.account_url }}{% else %}{{ routes.account_login_url }}{% endif %}"
      rel="nofollow"
      class="menu-drawer_account"
    >
      {{ 'icon-account.svg' | inline_asset_content }}
    </a>
  {% endif %}
</div>
```

- **Conditional rendering**: Localization and account links only render when enabled.
- **Account link logic**: Links to account page if customer logged in, login page otherwise.
- **Localization styling**: Localization dropdown positioned above button (bottom: 100%) for drawer context.

---

## Behavior

- **Drawer toggle**: Button opens/closes drawer via Alpine.js state.
- **Click outside**: Clicking outside drawer closes it automatically.
- **Slide animation**: Drawer slides in from left with 300ms ease transition.
- **Icon switching**: Menu icon switches to close icon when drawer opens.
- **Full height**: Drawer spans from header to viewport bottom.
- **Scrollable content**: Navigation content scrolls if it exceeds drawer height.
- **Footer positioning**: Footer actions stay at bottom via flexbox `justify-content: space-between`.

---

## Usage Example

```liquid
{% render 'component-nav-drawer',
  menu: section.settings.menu,
  menu_color_scheme: section.settings.menu_color_scheme,
  enable_country_selector: section.settings.enable_country_selector,
  enable_language_selector: section.settings.enable_language_selector,
  enable_customer_avatar: section.settings.enable_customer_avatar
%}
```

Typically used in:
- Header (`sections/header.liquid`) for mobile navigation
- Can be used on desktop when `menu_type_desktop == 'drawer'`

---

## Implementation Notes

1. **Alpine.js requirement**: Snippet requires Alpine.js to be loaded in the theme for drawer state management.

2. **Navigation snippet**: Drawer delegates navigation rendering to `component-nav-dropdown` with `nav_style: 'drawer'` parameter.

3. **Drawer positioning**: Drawer positioned absolutely below header with `top: calc(100% + 1px)`.

4. **Slide animation**: Drawer uses CSS `transform: translateX(-100%)` when closed, `translateX(0)` when open.

5. **Z-index management**: Drawer uses `z-index: -1` when closed to prevent interaction, should be updated to positive value when open (handled by CSS or JavaScript).

6. **Icon visibility**: Icon visibility controlled via CSS:
    - When drawer open: hide menu icon, show close icon
    - When drawer closed: show menu icon, hide close icon

7. **Header height variable**: Drawer height calculation uses `var(--header-height)` CSS variable, which should be set by header JavaScript.

8. **Localization integration**: Localization form rendered with drawer-specific styling (dropdown appears above button).

9. **Account link conditional**: Account link only shows when:
    - `shop.customer_accounts_enabled` is true
    - `enable_customer_avatar` is true

10. **Account URL logic**: Account link uses conditional logic:
    - If customer logged in: links to `routes.account_url`
    - If customer not logged in: links to `routes.account_login_url`

11. **Icon dependencies**: Requires the following icons in `assets/`:
    - `icon-menu.svg` (hamburger menu icon)
    - `icon-close.svg` (close/X icon)
    - `icon-account.svg` (account/user icon)

12. **CSS class dependencies**: Snippet relies on CSS classes:
    - `#header-drawer`
    - `#menu-drawer`
    - `.drawer-open`
    - `.header-drawer_icons`
    - `.menu-drawer_action`
    - `.menu-drawer_localization`
    - `.menu-drawer_account`
    - `.color-\{\{ menu_color_scheme \}\}`
    - `.gradient`

13. **Alpine.js directives**:
    - `x-data="{ drawerOpen: false }"`: Initializes drawer state
    - `@click="drawerOpen = !drawerOpen"`: Toggles drawer on button click
    - `:class="{ 'drawer-open': drawerOpen }"`: Adds class when drawer is open
    - `@click.outside="drawerOpen = false"`: Closes drawer on outside click

14. **Flexbox layout**: Drawer uses flexbox with `justify-content: space-between` to position navigation at top and footer actions at bottom.

15. **Drawer width**: Drawer width uses `min(500px, 100%)` to limit maximum width while being responsive.

16. **Transition timing**: Drawer slide animation uses 300ms ease transition for smooth movement.

17. **Color scheme integration**: Drawer uses theme color scheme via `color-\{\{ menu_color_scheme \}\}` class.

18. **Gradient class**: Drawer includes `gradient` class for additional styling options.

19. **Localization styling override**: Localization dropdown in drawer has custom positioning (appears above button instead of below).

20. **Account icon sizing**: Account icon has fixed size (40px × 40px) for consistent appearance.

21. **No translation keys**: Navigation labels come directly from menu object, not translation files.

22. **Accessibility considerations**:
    - Proper button semantics
    - Icon-only button should have aria-label (may need to be added)
    - Click-outside handling for keyboard users
    - Focus management when drawer opens/closes

23. **Performance**: Inline styles prevent additional HTTP request but increase HTML size.

24. **Header height dependency**: Drawer height calculation depends on `--header-height` CSS variable being set. Ensure header JavaScript sets this variable.

25. **Drawer state persistence**: Drawer state is not persisted - it always starts closed on page load.

26. **Navigation nesting**: Nested navigation handled by `component-nav-dropdown` snippet, which supports 3 levels of nesting.

27. **Footer border**: Footer actions section has top border for visual separation from navigation.

28. **Account link rel**: Account link uses `rel="nofollow"` attribute.

29. **Responsive width**: Drawer width adapts to viewport with `min(500px, 100%)` ensuring it never exceeds screen width.

30. **Z-index consideration**: When drawer is open, z-index should be updated to appear above other content. This may be handled by CSS or needs JavaScript update.

31. **Icon class names**: Icons use class names `.icon-menu` and `.icon-close` for CSS targeting (may need to be added to SVG markup).

32. **Drawer overlay**: No overlay is rendered - drawer slides in without blocking background content. Consider adding overlay for better UX if needed.

33. **Body scroll lock**: Drawer doesn't prevent body scrolling when open. Consider adding body scroll lock for better mobile UX.

34. **Navigation scroll**: Navigation content within drawer should scroll if it exceeds available height (handled by `component-nav-dropdown`).

35. **Footer flex layout**: Footer uses flexbox with `justify-content: space-between` to position localization on left and account on right.

