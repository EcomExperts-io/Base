# component-product-media-gallery Snippet

`snippets/component-product-media-gallery.liquid` renders a product media gallery with Swiper.js integration, supporting multiple layout modes (thumbnail, carousel, 2-columns) and zoom functionality. The component prioritizes the selected variant's featured media and integrates with a modal for lightbox viewing. It uses custom elements (`<media-gallery>`, `<product-media-magnify>`) for enhanced functionality.

---

## What It Does

- Renders product media in multiple layout modes (thumbnail, carousel, 2-columns).
- Prioritizes selected variant's featured media as the first item.
- Integrates with Swiper.js for carousel and thumbnail navigation.
- Supports zoom modes: none, hover (with magnify component).
- Provides lightbox triggers that open media in modal.
- Displays zoom icons and loading spinners for hover zoom.
- Uses custom elements for enhanced interactivity.

---

## Parameters

| Parameter          | Type    | Default | Description                                                      |
|--------------------|---------|---------|------------------------------------------------------------------|
| `product_media`    | array   | **required** | Array of product media objects to display.                       |
| `selected_variant` | object  | **required** | Variant object used to prioritize featured media.                |
| `is_zoom`         | string  | `'none'` | Zoom mode: `'none'` or `'hover'`.                                |
| `section_id`      | string  | **required** | Section DOM id used for modal targeting.                         |
| `video_looping`   | boolean | optional | Whether videos should loop.                                     |
| `media_layout`    | string  | `'carousel'` | Desktop layout: `'carousel'`, `'thumbnail'`, or `'2_columns'`. |
| `mobile_media_layout` | string | `'default'` | Mobile layout: `'default'` or `'thumbnail'`.                  |

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | External stylesheet (likely `section-product.css` or similar) |
| JavaScript | `swiper7.4.1.min.js` (Swiper library), `section-product.js` (Swiper initialization), `component-product-media-magnify.js` (conditional - for hover zoom) |
| Custom Elements | `<media-gallery>`, `<product-media-magnify>` (for hover zoom) |
| Snippets | `component-product-media` (renders individual media items) |
| Icons | `icon-zoom.svg`, `icon-spinner.svg` (inline via `inline_asset_content`) |
| Data | Requires `product_media` array, `selected_variant` object with `featured_media`/`featured_image` |

- Swiper.js powers carousel and thumbnail gallery functionality.
- Custom elements provide zoom and gallery management.
- External CSS handles all gallery styling.

---

## Dynamic Styles

The snippet does not include inline styles. All styling is handled by external CSS files. However, the component uses dynamic class names based on layout parameters:

```liquid
{% liquid
  assign gallery_classes = 'media-gallery'
  if media_layout == 'thumbnail'
    assign gallery_classes = gallery_classes | append: ' media-gallery--desktop-thumbnail'
  elsif media_layout == '2_columns'
    assign gallery_classes = gallery_classes | append: ' media-gallery--desktop-2columns'
  endif
  if mobile_media_layout == 'thumbnail'
    assign gallery_classes = gallery_classes | append: ' media-gallery--mobile-thumbnail'
  endif
%}
```

- **Dynamic classes**: Gallery classes change based on layout parameters.
- **Layout-specific styling**: Different classes for desktop and mobile layouts.

---

## Markup Structure

```liquid
<media-gallery class="{{ gallery_classes }}" data-desktop-layout="{{ media_layout }}" data-mobile-layout="{{ mobile_media_layout }}">
  {%- if render_thumbnail -%}
    <!-- Thumbnail layout -->
  {%- endif -%}
  {%- if render_carousel -%}
    <!-- Carousel layout -->
  {%- endif -%}
  {%- if render_2columns -%}
    <!-- 2-column layout -->
  {%- endif -%}
</media-gallery>
```

- **Custom element**: Wrapped in `<media-gallery>` custom element.
- **Layout data attributes**: Stores layout information for JavaScript access.
- **Conditional layouts**: Renders different layouts based on parameters.

### Thumbnail Layout

```liquid
{%- if render_thumbnail -%}
  <div class="swiper product-media-gallery__main">
    <!-- Main gallery slides -->
  </div>
  <div class="swiper product-media-gallery__thumbnails">
    <!-- Thumbnail navigation -->
  </div>
{%- endif -%}
```

- **Main gallery**: Swiper carousel for main media display.
- **Thumbnail gallery**: Swiper carousel for thumbnail navigation.
- **Swiper integration**: Both use Swiper.js for synchronized navigation.

### Carousel Layout

```liquid
{%- if render_carousel -%}
  <div class="swiper product-media-gallery__carousel">
    <!-- Carousel slides -->
    <div class="swiper-pagination product-media-gallery__pagination"></div>
    <div class="swiper-button-prev product-media-gallery__nav product-media-gallery__nav--prev"></div>
    <div class="swiper-button-next product-media-gallery__nav product-media-gallery__nav--next"></div>
  </div>
{%- endif -%}
```

- **Single carousel**: One Swiper carousel with pagination and navigation.
- **Pagination dots**: Shows current slide position.
- **Navigation arrows**: Previous/next buttons.

### 2-Column Layout

```liquid
{%- if render_2columns -%}
  <div class="media-gallery__2columns">
    <!-- Grid of media items -->
  </div>
{%- endif -%}
```

- **Grid layout**: Simple 2-column grid without Swiper.
- **Static display**: No carousel functionality.

### Media Slide Structure

```liquid
{% if is_zoom == 'hover' %}
  <product-media-magnify class="swiper-slide image-magnify-hover" data-media-id="{{ media.id }}" data-media-index="{{ media_index }}">
{% else %}
  <div class="swiper-slide" data-media-id="{{ media.id }}" data-media-index="{{ media_index }}">
{% endif %}
  {%- if is_zoom == 'hover' -%}
    <div class="loading__spinner hidden">
      {{ 'icon-spinner.svg' | inline_asset_content }}
    </div>
  {%- endif -%}
  <div class="product-media">
    {%- if is_zoom != 'none' -%}
      <div class="light-box-zoom-trigger {% if is_zoom == 'hover' %}hover-zoom-enabled{% endif %}" data-media-id="{{ media.id }}" data-modal="#ProductModal-{{ section_id }}">
        &nbsp;
      </div>
    {%- endif -%}
    {% render 'component-product-media', media: media, loop: video_looping %}
  </div>
  {%- if is_zoom != 'none' -%}
    <div class="product__media-icon {% if is_zoom == 'hover' %}hover-zoom-enabled{% endif %}">
      <span class="lightbox-icon">
        <div class="svg-wrapper">
          {{ 'icon-zoom.svg' | inline_asset_content }}
        </div>
      </span>
    </div>
  {%- endif -%}
{% if is_zoom == 'hover' %}
  </product-media-magnify>
{% else %}
  </div>
{% endif %}
```

- **Conditional wrapper**: Uses `<product-media-magnify>` for hover zoom, `<div>` otherwise.
- **Loading spinner**: Shows during zoom image loading (hover mode only).
- **Lightbox trigger**: Clickable overlay that opens modal.
- **Zoom icon**: Visual indicator for zoom functionality.
- **Media rendering**: Delegates to `component-product-media` snippet.

---

## Behavior

- **Variant prioritization**: Selected variant's featured media appears first.
- **Swiper navigation**: Carousel and thumbnail galleries use Swiper for smooth navigation.
- **Zoom functionality**: Hover zoom provides magnified view on mouse hover.
- **Modal integration**: Clicking media opens lightbox modal.
- **Layout switching**: Different layouts render based on desktop/mobile parameters.
- **Media indexing**: Each media item has unique index for tracking.

---

## Usage Example

```liquid
{% render 'component-product-media-gallery',
  product_media: product.media,
  selected_variant: product.selected_or_first_available_variant,
  is_zoom: section.settings.image_zoom,
  section_id: section.id,
  video_looping: section.settings.enable_video_looping,
  media_layout: section.settings.media_layout,
  mobile_media_layout: section.settings.mobile_media_layout
%}
```

Typically used in:
- Product pages (`sections/product.liquid`) for main product media display

---

## Implementation Notes

1. **Swiper.js requirement**: Component requires Swiper.js library (`swiper7.4.1.min.js`) to be loaded for carousel and thumbnail functionality.

2. **Swiper initialization**: Swiper instances are initialized by `section-product.js` in the `<product-info>` custom element's `connectedCallback`.

3. **Layout logic**: Component determines which layouts to render based on `media_layout` and `mobile_media_layout` parameters:
    - `render_thumbnail`: True if desktop or mobile layout is 'thumbnail'
    - `render_carousel`: True if desktop layout is 'carousel' or empty, or mobile is 'default' or empty
    - `render_2columns`: True if desktop layout is '2_columns'

4. **Variant featured media**: Selected variant's featured media is prioritized and appears first, then excluded from the main loop to avoid duplication.

5. **Media indexing**: Each media item has a `data-media-index` attribute for tracking and JavaScript access.

6. **Media ID tracking**: Each media item has a `data-media-id` attribute matching the media object's ID for modal targeting.

7. **Zoom modes**:
    - `'none'`: No zoom functionality, simple click-to-modal
    - `'hover'`: Hover zoom with magnify component, plus click-to-modal

8. **Custom elements**:
    - `<media-gallery>`: Wrapper element for gallery functionality
    - `<product-media-magnify>`: Provides hover zoom functionality (when `is_zoom == 'hover'`)

9. **Lightbox trigger**: Each media item has a `.light-box-zoom-trigger` div that opens the modal when clicked. The trigger uses `data-modal` attribute to target the modal element.

10. **Modal targeting**: Modal ID format: `#ProductModal-\{\{ section_id \}\}`, which must match the modal component's ID.

11. **Icon dependencies**: Requires the following icons in `assets/`:
    - `icon-zoom.svg` (zoom indicator)
    - `icon-spinner.svg` (loading indicator for hover zoom)

12. **CSS class dependencies**: Component relies on CSS classes:
    - `.media-gallery`
    - `.media-gallery--desktop-thumbnail`
    - `.media-gallery--desktop-2columns`
    - `.media-gallery--mobile-thumbnail`
    - `.product-media-gallery__main`
    - `.product-media-gallery__thumbnails`
    - `.product-media-gallery__carousel`
    - `.product-media-gallery__pagination`
    - `.product-media-gallery__nav`
    - `.swiper`, `.swiper-wrapper`, `.swiper-slide`
    - `.light-box-zoom-trigger`
    - `.hover-zoom-enabled`
    - `.product__media-icon`
    - `.lightbox-icon`
    - `.loading__spinner`
    - `.hidden`

13. **Swiper configuration**: Swiper instances are configured in `section-product.js`:
    - **Thumbnail layout**: Main gallery with thumbnail gallery as thumbs
    - **Carousel layout**: Single carousel with pagination and navigation
    - **2-column layout**: No Swiper (static grid)

14. **Thumbnail navigation**: Thumbnail gallery has prev/next buttons for navigation when there are many thumbnails.

15. **Carousel pagination**: Carousel layout uses Swiper pagination dots to show current slide.

16. **Carousel navigation**: Carousel layout has prev/next buttons for navigation.

17. **Hover zoom component**: When `is_zoom == 'hover'`, media items are wrapped in `<product-media-magnify>` custom element which provides hover zoom functionality.

18. **Loading spinner**: Hover zoom shows loading spinner while zoom image loads (initially hidden, shown by JavaScript).

19. **Media rendering**: All media items are rendered via `component-product-media` snippet, which handles images, videos, and 3D models.

20. **Video looping**: Video looping controlled by `video_looping` parameter, passed to `component-product-media` snippet.

21. **Empty space trigger**: Lightbox trigger uses `&nbsp;` for clickable area (styled via CSS to cover media).

22. **Zoom icon positioning**: Zoom icon positioned absolutely over media (handled by CSS).

23. **Data attributes**: Component uses data attributes for JavaScript access:
    - `data-desktop-layout`: Desktop layout mode
    - `data-mobile-layout`: Mobile layout mode
    - `data-media-id`: Media object ID
    - `data-media-index`: Media position index
    - `data-modal`: Modal target selector

24. **Conditional rendering**: Different layouts render conditionally - only the selected layout(s) are rendered in HTML.

25. **Swiper synchronization**: In thumbnail layout, main gallery and thumbnail gallery are synchronized via Swiper's thumbs option.

26. **Media exclusion**: Selected variant's featured media is excluded from main loop using `{% unless selected_variant.featured_media.id == media.id %}` to avoid duplication.

27. **Index tracking**: Media index is tracked via `media_index` variable, incremented after each media item.

28. **Featured media check**: Component checks if `selected_variant.featured_image != null` before rendering featured media.

29. **Modal integration**: Modal is opened by clicking `.light-box-zoom-trigger` elements, which are handled by `component-product-media-modal.js`.

30. **No inline styles**: All styling handled by external CSS files.

31. **Responsive layouts**: Different layouts can be specified for desktop and mobile via separate parameters.

32. **Default values**: Layout parameters default to `'carousel'` for desktop and `'default'` for mobile if not provided.

33. **2-column grid**: 2-column layout uses simple grid CSS, no Swiper functionality.

34. **Swiper pagination**: Carousel layout includes pagination dots container (content added by Swiper.js).

35. **Swiper navigation**: Carousel and thumbnail layouts include navigation button containers (content added by Swiper.js).

36. **Hover zoom loading**: Loading spinner for hover zoom is initially hidden and shown by JavaScript when zoom image loads.

37. **Icon wrapper**: Zoom icon wrapped in `.svg-wrapper` div for styling purposes.

38. **Lightbox icon class**: Zoom icon uses `.lightbox-icon` class for styling.

39. **Media icon class**: Zoom icon container uses `.product__media-icon` class.

40. **Hover zoom class**: When hover zoom enabled, elements get `.hover-zoom-enabled` class for styling.

41. **Image magnify class**: Hover zoom slides use `.image-magnify-hover` class.

42. **Swiper button classes**: Navigation buttons use Swiper's standard classes: `.swiper-button-prev`, `.swiper-button-next`.

43. **Swiper pagination class**: Pagination uses Swiper's standard class: `.swiper-pagination`.

44. **Gallery wrapper**: All layouts wrapped in `<media-gallery>` custom element for consistent structure.

45. **Layout data attributes**: Layout information stored in data attributes for JavaScript access and CSS targeting.

46. **Media component**: All media rendering delegated to `component-product-media` snippet for consistency.

47. **Video loop parameter**: Video looping controlled via `loop` parameter passed to media component.

48. **Section ID usage**: Section ID used for unique modal targeting: `#ProductModal-\{\{ section_id \}\}`.

49. **Conditional zoom elements**: Zoom-related elements (trigger, icon, magnify wrapper) only render when `is_zoom != 'none'`.

50. **Swiper initialization timing**: Swiper instances initialized after DOM ready, in custom element's `connectedCallback`.

