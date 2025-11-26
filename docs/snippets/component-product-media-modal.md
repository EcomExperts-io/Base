# component-product-media-modal Snippet

`snippets/component-product-media-modal.liquid` renders a product media modal (lightbox) for displaying product images and videos in full-screen view. It uses the `<product-media-modal>` custom element for JavaScript functionality and integrates with the product media gallery component. The modal displays all product media with the selected variant's featured media prioritized first.

---

## What It Does

- Renders a full-screen modal for product media viewing.
- Displays all product media items in a scrollable container.
- Prioritizes selected variant's featured media as the first item.
- Integrates with gallery component via click triggers.
- Provides close button for modal dismissal.
- Uses native `<dialog>`-like behavior via custom element.
- Supports keyboard and click-outside dismissal.
- Shows active media with scroll-to behavior.

---

## Parameters

| Parameter          | Type    | Default | Description                                                      |
|--------------------|---------|---------|------------------------------------------------------------------|
| `section_id`       | string  | **required** | Parent section id used for unique DOM IDs.                      |
| `color_scheme`     | string  | optional | Color scheme handle for modal background styling.                |
| `enable_video_looping` | boolean | optional | Whether to loop product videos.                                  |

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | External stylesheet (likely `section-product.css` or similar) |
| JavaScript | `component-product-media-modal.js` (defines `<product-media-modal>` custom element) |
| Custom Elements | `<product-media-modal>` |
| Snippets | `component-product-media` (renders individual media items) |
| Icons | `icon-close.svg` (inline via `inline_asset_content`) |
| Data | Requires `product` object with `media` array and `selected_or_first_available_variant` |

- Custom element handles modal open/close behavior and active media management.
- External CSS handles all modal styling.
- Modal integrates with gallery component via click triggers.

---

## Dynamic Styles

The snippet does not include inline styles. All styling is handled by external CSS files. However, the component uses dynamic class names based on color scheme:

```liquid
class="product-media-modal__dialog color-{{ color_scheme }} gradient"
```

- **Color scheme integration**: Modal uses theme color scheme for consistent styling.

---

## Markup Structure

```liquid
<product-media-modal id="ProductModal-{{ section_id }}" class="product-media-modal media-modal">
  <div class="product-media-modal__dialog color-{{ color_scheme }} gradient" role="dialog" aria-label="{{ 'products.modal.label' | t }}" aria-modal="true" tabindex="-1">
    <button id="ModalClose-{{ section_id }}" type="button" class="product-media-modal__toggle" aria-label="{{ 'accessibility.close' | t }}">
      {{ 'icon-close.svg' | inline_asset_content }}
    </button>
    <div class="product-media-modal__content color-{{ color_scheme }} gradient" role="document" aria-label="{{ 'products.modal.label' | t }}" tabindex="0">
      <!-- Product media items -->
    </div>
  </div>
</product-media-modal>
```

- **Custom element**: Wrapped in `<product-media-modal>` custom element.
- **Unique ID**: Modal ID format: `ProductModal-\{\{ section_id \}\}` for unique targeting.
- **Semantic structure**: Uses proper ARIA roles and attributes.

### Close Button

```liquid
<button
  id="ModalClose-{{ section_id }}"
  type="button"
  class="product-media-modal__toggle"
  aria-label="{{ 'accessibility.close' | t }}"
>
  {{ 'icon-close.svg' | inline_asset_content }}
</button>
```

- **Unique ID**: Close button ID format: `ModalClose-\{\{ section_id \}\}`.
- **Accessibility**: Includes `aria-label` for screen readers.
- **Icon display**: Shows close icon for visual indication.

### Media Content

```liquid
<div class="product-media-modal__content color-{{ color_scheme }} gradient" role="document" aria-label="{{ 'products.modal.label' | t }}" tabindex="0">
  {%- liquid
    if product.selected_or_first_available_variant.featured_media != null
      assign media = product.selected_or_first_available_variant.featured_media
      render 'component-product-media', media: media, loop: enable_video_looping
    endif
  -%}
  {%- for media in product.media -%}
    {%- liquid
      unless media.id == product.selected_or_first_available_variant.featured_media.id
        render 'component-product-media', media: media, loop: enable_video_looping
      endunless
    -%}
  {%- endfor -%}
</div>
```

- **Variant prioritization**: Selected variant's featured media rendered first.
- **Media exclusion**: Featured media excluded from loop to avoid duplication.
- **Media rendering**: All media items rendered via `component-product-media` snippet.
- **Video looping**: Video looping controlled by `enable_video_looping` parameter.

---

## Behavior

- **Modal opening**: Opens when gallery media items are clicked (handled by JavaScript).
- **Active media display**: Shows the clicked media item and scrolls it into view.
- **Close functionality**: Close button dismisses modal.
- **Click outside**: Clicking outside modal (on backdrop) dismisses it.
- **Body scroll lock**: Prevents body scrolling when modal is open.
- **Keyboard support**: Supports keyboard navigation and dismissal.
- **Focus management**: Manages focus when modal opens/closes.

---

## Usage Example

```liquid
{%- if section.settings.image_zoom != 'none' -%}
  {% render 'component-product-media-modal',
    section_id: section.id,
    color_scheme: section.settings.color_scheme,
    enable_video_looping: section.settings.enable_video_looping
  %}
{%- endif -%}
```

Typically used in:
- Product pages (`sections/product.liquid`) when zoom is enabled (`image_zoom != 'none'`)

---

## Implementation Notes

1. **Custom element requirement**: Snippet requires `component-product-media-modal.js` to be loaded, which defines the `<product-media-modal>` custom element.

2. **Modal integration**: Modal is opened by clicking `.light-box-zoom-trigger` elements in the gallery component. The trigger's `data-modal` attribute targets this modal.

3. **Modal ID format**: Modal ID must match gallery trigger's `data-modal` attribute: `#ProductModal-\{\{ section_id \}\}`.

4. **Close button ID**: Close button uses ID format: `ModalClose-\{\{ section_id \}\}` for JavaScript targeting.

5. **Custom element methods**: The custom element provides:
    - `showModal(opener)`: Opens modal and shows active media
    - `hideModal()`: Closes modal and restores body scroll
    - `showActiveMedia()`: Highlights and scrolls active media into view

6. **Active media tracking**: Custom element tracks which media opened the modal via `openedBy` property.

7. **Active media display**: When modal opens, the clicked media item is marked with `active` class and scrolled into view.

8. **Body scroll lock**: When modal opens, `overflow-hidden` class is added to body to prevent background scrolling.

9. **Open attribute**: Modal uses `open` attribute (set by custom element) to control visibility.

10. **Click outside handling**: Custom element listens for `pointerup` events on modal backdrop to close modal (mouse only, not touch).

11. **Close button handling**: Close button click triggers `hideModal()` method.

12. **Icon dependency**: Requires `icon-close.svg` in the `assets/` folder for close button.

13. **CSS class dependencies**: Snippet relies on CSS classes:
    - `.product-media-modal`
    - `.media-modal`
    - `.product-media-modal__dialog`
    - `.product-media-modal__toggle`
    - `.product-media-modal__content`
    - `.color-\{\{ color_scheme \}\}`
    - `.gradient`
    - `.active` (added by JavaScript to active media)

14. **Translation keys**: Uses translation keys from `locales/en.default.json`:
    - `products.modal.label`
    - `accessibility.close`

15. **Accessibility features**:
    - `role="dialog"` on dialog container
    - `aria-modal="true"` indicating modal behavior
    - `aria-label` on dialog and content
    - `aria-label` on close button
    - `tabindex="-1"` on dialog for focus management
    - `tabindex="0"` on content for keyboard navigation

16. **Media prioritization**: Selected variant's featured media is rendered first, then excluded from main loop to avoid duplication.

17. **Media rendering**: All media items rendered via `component-product-media` snippet for consistency.

18. **Video looping**: Video looping controlled by `enable_video_looping` parameter, passed to media component.

19. **Color scheme integration**: Modal uses theme color scheme via `color-\{\{ color_scheme \}\}` class.

20. **Gradient class**: Modal includes `gradient` class for additional styling options.

21. **Data media ID**: Each media item should have `data-media-id` attribute matching the media object's ID for active media targeting.

22. **Scroll into view**: Active media is scrolled into view using `scrollIntoView()` method.

23. **Active class management**: Custom element adds `active` class to clicked media, removes from others.

24. **Conditional rendering**: Modal typically only renders when zoom is enabled (`image_zoom != 'none'`).

25. **No inline styles**: All styling handled by external CSS files.

26. **Semantic HTML**: Uses proper semantic structure with roles and ARIA attributes.

27. **Focus trap**: Modal should trap focus within modal when open (handled by CSS or JavaScript).

28. **Escape key**: Escape key should close modal (handled by custom element or browser default).

29. **Backdrop click**: Clicking modal backdrop (outside content) closes modal (handled by custom element).

30. **Pointer event handling**: Custom element uses `pointerup` event with `pointerType === 'mouse'` check to distinguish mouse from touch.

31. **Modal content structure**: Content area uses `role="document"` for semantic structure.

32. **Tabindex management**: Dialog uses `tabindex="-1"` to prevent tabbing, content uses `tabindex="0"` to allow tabbing.

33. **Media ID matching**: Custom element matches media IDs between gallery triggers and modal content to find active media.

34. **Query selector**: Custom element uses `querySelector` to find media items by `data-media-id` attribute.

35. **Class list manipulation**: Custom element adds/removes `active` class to highlight active media.

36. **Body class management**: Custom element adds/removes `overflow-hidden` class to body for scroll lock.

37. **Attribute management**: Custom element sets/removes `open` attribute to control modal visibility.

38. **Event listener setup**: Custom element sets up event listeners in constructor:
    - Click listeners on gallery triggers (set up once)
    - Click listener on close button
    - Pointerup listener on modal for backdrop clicks

39. **Media exclusion logic**: Featured media excluded from loop using `unless media.id == product.selected_or_first_available_variant.featured_media.id`.

40. **Featured media check**: Component checks if `product.selected_or_first_available_variant.featured_media != null` before rendering.

41. **Liquid syntax**: Uses `{% liquid %}` block for cleaner conditional logic.

42. **Media array iteration**: Loops through `product.media` array to render all media items.

43. **Media component parameter**: Passes `loop: enable_video_looping` parameter to media component.

44. **Unique ID generation**: Section ID used for unique DOM IDs to support multiple modals on page.

45. **Modal targeting**: Gallery triggers use `data-modal="#ProductModal-\{\{ section_id \}\}"` to target this modal.

46. **Close button targeting**: Custom element finds close button using `querySelector('[id^="ModalClose-"]')` selector.

47. **No JavaScript file reference**: JavaScript file must be loaded separately (typically in product section).

48. **Conditional script loading**: Modal JavaScript typically loaded conditionally when zoom is enabled.

49. **Accessibility labels**: All interactive elements have descriptive `aria-label` attributes.

50. **Translation support**: Modal labels use translation filters for internationalization.

