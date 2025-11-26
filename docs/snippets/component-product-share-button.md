# component-product-share-button Snippet

`snippets/component-product-share-button.liquid` renders a share button that uses the Web Share API when available and falls back to a copy-to-clipboard interface. It provides a native share experience on supported devices and a manual copy interface as a fallback. The component uses a `<share-button>` custom element for JavaScript functionality and a `<details>` element for the fallback UI.

---

## What It Does

- Renders a share button with native Web Share API support.
- Provides fallback copy-to-clipboard interface for unsupported browsers.
- Uses `<details>` element for accessible collapsible fallback UI.
- Displays share URL input field for manual copying.
- Shows success message when URL is copied.
- Integrates with section blocks for editor attributes and labels.
- Supports keyboard navigation and screen readers.

---

## Parameters

| Parameter   | Type   | Default | Description                                                      |
|-------------|--------|---------|------------------------------------------------------------------|
| `block`     | object | **required** | Section block object providing labels and editor attributes.    |
| `share_link`| string | **required** | URL to share when using native share or fallback.                |
| `section_id`| string | **required** | Section DOM id used to namespace element IDs.                    |

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | External stylesheet (likely `component-product-share-button.css` or similar) |
| JavaScript | `component-product-share-button.js` (defines `<share-button>` custom element) |
| Custom Elements | `<share-button>` |
| Icons | `icon-share.svg`, `icon-close.svg`, `icon-copy.svg` (inline via `inline_asset_content`) |
| Data | Requires `block` object with `settings.share_label`, `id`, `shopify_attributes` |

- Custom element handles Web Share API detection and clipboard functionality.
- External CSS handles all button and fallback UI styling.
- Native `<details>` element provides accessible collapsible UI.

---

## Dynamic Styles

The snippet does not include inline styles. All styling is handled by external CSS files. However, the component uses dynamic IDs and classes:

```liquid
id="Details-{{ block.id }}-{{ section_id }}"
id="ShareMessage-{{ section_id }}"
id="ShareUrl-{{ section_id }}"
```

- **Dynamic IDs**: Element IDs use block and section IDs for uniqueness.

---

## Markup Structure

```liquid
<share-button class="share-button quick-add-hidden" {{ block.shopify_attributes }}>
  <button class="share-button__button hidden">
    <!-- Native share button (shown when Web Share API available) -->
  </button>
  <details id="Details-{{ block.id }}-{{ section_id }}">
    <summary class="share-button__button">
      <!-- Fallback share button (shown when Web Share API unavailable) -->
    </summary>
    <div class="share-button__fallback">
      <!-- Copy-to-clipboard interface -->
    </div>
  </details>
</share-button>
```

- **Custom element**: Wrapped in `<share-button>` custom element.
- **Two buttons**: Native share button (hidden by default) and fallback button (in details summary).
- **Collapsible fallback**: Fallback UI uses `<details>` for accessible collapsible interface.

### Native Share Button

```liquid
<button class="share-button__button hidden">
  <span class="svg-wrapper">{{ 'icon-share.svg' | inline_asset_content }}</span>
  {{ block.settings.share_label | escape }}
</button>
```

- **Hidden by default**: Button hidden until Web Share API is detected.
- **Icon and label**: Shows share icon and label from block settings.
- **JavaScript control**: Custom element shows/hides this button based on API support.

### Fallback Share Button

```liquid
<details id="Details-{{ block.id }}-{{ section_id }}">
  <summary class="share-button__button">
    <span class="svg-wrapper">{{ 'icon-share.svg' | inline_asset_content }}</span>
    {{ block.settings.share_label | escape }}
  </summary>
  <!-- Fallback UI -->
</details>
```

- **Details element**: Uses native `<details>` for collapsible UI.
- **Summary button**: Summary acts as share button trigger.
- **Accessible**: Native details element provides keyboard navigation and screen reader support.

### Fallback UI

```liquid
<div class="share-button__fallback">
  <div class="field">
    <span id="ShareMessage-{{ section_id }}" class="share-button__message hidden" role="status"></span>
    <input
      type="text"
      class="field__input"
      id="ShareUrl-{{ section_id }}"
      value="{{ share_link }}"
      placeholder="{{ 'general.share.share_url' | t }}"
      onclick="this.select();"
      readonly
    >
    <label class="field__label" for="ShareUrl-{{ section_id }}">{{ 'general.share.share_url' | t }}</label>
  </div>
  <button class="share-button__close hidden">
    <span class="svg-wrapper">{{- 'icon-close.svg' | inline_asset_content -}}</span>
    <span class="visually-hidden">{{ 'general.share.close' | t }}</span>
  </button>
  <button class="share-button__copy">
    <span class="svg-wrapper">{{- 'icon-copy.svg' | inline_asset_content -}}</span>
    <span class="visually-hidden">{{ 'general.share.copy_to_clipboard' | t }}</span>
  </button>
</div>
```

- **URL input**: Read-only input field with share URL.
- **Auto-select**: Input selects all text on click (`onclick="this.select();"`).
- **Success message**: Hidden span for copy success message.
- **Copy button**: Button to copy URL to clipboard.
- **Close button**: Hidden button to close fallback UI (shown by JavaScript).

---

## Behavior

- **Web Share API detection**: Custom element detects Web Share API support and shows appropriate button.
- **Native sharing**: When Web Share API available, clicking button opens native share dialog.
- **Fallback UI**: When Web Share API unavailable, clicking button opens copy-to-clipboard interface.
- **URL copying**: Copy button copies URL to clipboard and shows success message.
- **Auto-select**: Clicking URL input selects all text for easy copying.
- **Details toggle**: Fallback UI toggles open/closed via native details behavior.
- **Success feedback**: Shows "Link copied!" message after successful copy.

---

## Usage Example

```liquid
{% render 'component-product-share-button',
  block: block,
  share_link: product.url,
  section_id: section.id
%}
```

Typically used in:
- Product pages (`sections/product.liquid`) as a share block
- Article pages (`sections/article.liquid`) as a share block
- Any section that needs share functionality

---

## Implementation Notes

1. **Custom element requirement**: Snippet requires `component-product-share-button.js` to be loaded, which defines the `<share-button>` custom element.

2. **Web Share API detection**: Custom element detects Web Share API support (`navigator.share`) and shows/hides appropriate buttons.

3. **Two-button system**: Component uses two buttons:
    - Native share button (shown when Web Share API available)
    - Fallback button in details summary (shown when Web Share API unavailable)

4. **Details element**: Fallback UI uses native `<details>` element for accessible collapsible interface.

5. **Block integration**: Component expects to be rendered within a section block for:
    - Block settings (share label)
    - Block ID (for unique element IDs)
    - Shopify attributes (for theme editor)

6. **Icon dependencies**: Requires the following icons in `assets/`:
    - `icon-share.svg` (share icon)
    - `icon-close.svg` (close button icon)
    - `icon-copy.svg` (copy button icon)

7. **CSS class dependencies**: Snippet relies on CSS classes:
    - `.share-button`
    - `.quick-add-hidden`
    - `.share-button__button`
    - `.hidden`
    - `.share-button__fallback`
    - `.field`
    - `.field__input`
    - `.field__label`
    - `.share-button__message`
    - `.share-button__close`
    - `.share-button__copy`
    - `.svg-wrapper`
    - `.visually-hidden`

8. **Translation keys**: Uses translation keys from `locales/en.default.json`:
    - `general.share.share_url`
    - `general.share.close`
    - `general.share.copy_to_clipboard`

9. **Accessibility features**:
    - `role="status"` on success message for screen readers
    - `visually-hidden` class for icon-only button labels
    - Proper label associations for form fields
    - Native details element for keyboard navigation
    - Semantic HTML structure

10. **Dynamic IDs**: Element IDs use block and section IDs for uniqueness:
    - `Details-\{\{ block.id \}\}-\{\{ section_id \}\}`
    - `ShareMessage-\{\{ section_id \}\}`
    - `ShareUrl-\{\{ section_id \}\}`

11. **Shopify attributes**: Component includes `\{\{ block.shopify_attributes \}\}` for theme editor integration.

12. **Quick add hidden**: Component includes `quick-add-hidden` class (likely for quick add functionality).

13. **Hidden classes**: Several elements use `hidden` class, toggled by JavaScript:
    - Native share button (shown when API available)
    - Success message (shown after copy)
    - Close button (shown by JavaScript)

14. **URL input**: Input field is readonly and auto-selects text on click for easy copying.

15. **Copy functionality**: Custom element handles clipboard copying using:
    - Modern API: `navigator.clipboard.writeText()`
    - Fallback: `document.execCommand('copy')`

16. **Success message**: Shows "Link copied!" message after successful copy (hardcoded in JavaScript).

17. **Close button**: Close button hidden by default, shown by JavaScript when needed.

18. **Label escaping**: Share label escaped using `escape` filter for security.

19. **Placeholder text**: URL input uses translation key for placeholder text.

20. **Icon wrapper**: Icons wrapped in `.svg-wrapper` div for styling purposes.

21. **Visually hidden text**: Icon-only buttons include visually hidden text for screen readers.

22. **Field structure**: URL input uses proper field structure with label association.

23. **Readonly input**: URL input is readonly to prevent editing.

24. **Auto-select on click**: URL input selects all text on click for easy copying.

25. **Details ID**: Details element uses block and section IDs for unique identification.

26. **Block settings**: Component uses `block.settings.share_label` for button label.

27. **Block ID usage**: Block ID used in details element ID for uniqueness.

28. **Section ID usage**: Section ID used in multiple element IDs for namespacing.

29. **Custom element methods**: Custom element provides:
    - Web Share API detection
    - Native share functionality
    - Clipboard copy functionality
    - Success message display
    - Button visibility management

30. **Web Share API**: When available, uses `navigator.share()` for native sharing.

31. **Clipboard API**: Uses `navigator.clipboard.writeText()` for modern browsers.

32. **Legacy clipboard**: Falls back to `document.execCommand('copy')` for older browsers.

33. **Success feedback**: Shows success message for 2 seconds after copy (handled by JavaScript).

34. **Details toggle**: Fallback UI toggles via native details element behavior.

35. **Keyboard navigation**: Details element provides native keyboard navigation.

36. **Screen reader support**: Proper ARIA roles and visually hidden text for accessibility.

37. **Icon-only buttons**: Copy and close buttons are icon-only with visually hidden labels.

38. **URL value**: Share URL comes from `share_link` parameter.

39. **No inline styles**: All styling handled by external CSS files.

40. **Conditional rendering**: Component doesn't conditionally render - JavaScript handles button visibility.

41. **Block attributes**: Includes `block.shopify_attributes` for theme editor block targeting.

42. **Quick add class**: `quick-add-hidden` class likely hides component during quick add flow.

43. **Hidden button management**: JavaScript toggles `hidden` class on buttons based on API support.

44. **Success message role**: Success message uses `role="status"` for screen reader announcements.

45. **Input label association**: URL input properly associated with label via `for` attribute.

46. **Placeholder translation**: Input placeholder uses translation key for internationalization.

47. **Close button visibility**: Close button hidden by default, shown by JavaScript when fallback UI opens.

48. **Copy button visibility**: Copy button always visible in fallback UI.

49. **Details summary**: Summary element acts as fallback share button trigger.

50. **Native details behavior**: Details element provides native open/close behavior without JavaScript.

