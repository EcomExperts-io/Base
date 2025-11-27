# component-product-media Snippet

`snippets/component-product-media.liquid` renders a single product media item (image, video, external video, or 3D model) using Shopify's media filters. It handles different media types with appropriate rendering methods and supports video looping for product videos.

---

## What It Does

- Renders product images with proper dimensions and alt text.
- Renders product videos with autoplay, looping, and controls.
- Renders external videos (YouTube, Vimeo) via Shopify's external video tag.
- Renders 3D models using Shopify's model viewer tag.
- Handles unknown media types with generic media tag.
- Supports video looping via parameter.
- Includes media ID data attribute for JavaScript targeting.

---

## Parameters

| Parameter | Type    | Default | Description                                                      |
|-----------|---------|---------|------------------------------------------------------------------|
| `media`   | object  | **required** | Product media object to render.                                  |
| `loop`    | boolean | optional | Whether videos should loop (default: false).                     |

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | External stylesheet (handled by parent components) |
| JavaScript | None required (media tags are self-contained) |
| Shopify Filters | `image_url`, `image_tag`, `external_video_tag`, `media_tag`, `model_viewer_tag` |
| Data | Requires `media` object with `media_type`, `width`, `height`, `alt`, `id` properties |

- No external JavaScript required - all functionality provided by Shopify's media filters.
- Media types handled via Liquid `case` statement.
- External CSS handles styling (provided by parent components).

---

## Dynamic Styles

The snippet does not include inline styles. All styling is handled by external CSS files in parent components.

---

## Markup Structure

The snippet uses a `case` statement to render different media types:

```liquid
{% case media.media_type %}
  {% when 'image' %}
    <!-- Image rendering -->
  {% when 'external_video' %}
    <!-- External video rendering -->
  {% when 'video' %}
    <!-- Video rendering -->
  {% when 'model' %}
    <!-- 3D model rendering -->
  {% else %}
    <!-- Fallback rendering -->
{% endcase %}
```

### Image Rendering

```liquid
{% when 'image' %}
  {{
    media
    | image_url: width: media.width
    | image_tag:
      width: media.width,
      height: media.height,
      loading: 'eager',
      alt: media.alt,
      data-media-id: media.id
  }}
```

- **Image URL**: Uses `image_url` filter with original width.
- **Image tag**: Uses `image_tag` filter with dimensions and attributes.
- **Eager loading**: Images load immediately (`loading: 'eager'`).
- **Alt text**: Uses media object's alt text for accessibility.
- **Media ID**: Includes `data-media-id` attribute for JavaScript targeting.

### External Video Rendering

```liquid
{% when 'external_video' %}
  {{ media | external_video_tag }}
```

- **External video tag**: Uses Shopify's `external_video_tag` filter.
- **Platform support**: Handles YouTube and Vimeo videos.
- **Automatic embedding**: Shopify handles iframe embedding automatically.

### Video Rendering

```liquid
{% when 'video' %}
  {{
    media
    | media_tag:
      image_size: '2048x',
      autoplay: true,
      loop: loop,
      controls: true,
      preload: 'none',
      data-media-id: media.id
  }}
```

- **Media tag**: Uses Shopify's `media_tag` filter for video rendering.
- **Poster image**: Uses `image_size: '2048x'` for video poster.
- **Autoplay**: Videos autoplay when loaded.
- **Looping**: Video looping controlled by `loop` parameter.
- **Controls**: Video controls enabled for user interaction.
- **Preload**: Set to `'none'` to reduce initial load.
- **Media ID**: Includes `data-media-id` attribute for JavaScript targeting.

### 3D Model Rendering

```liquid
{% when 'model' %}
  {{ media | model_viewer_tag }}
```

- **Model viewer**: Uses Shopify's `model_viewer_tag` filter.
- **3D interaction**: Provides interactive 3D model viewing.
- **WebGL support**: Uses model-viewer web component.

### Fallback Rendering

```liquid
{% else %}
  {{ media | media_tag }}
```

- **Generic media tag**: Uses `media_tag` filter for unknown media types.
- **Future-proof**: Handles any new media types Shopify may add.

---

## Behavior

- **Media type detection**: Automatically detects media type and renders appropriately.
- **Image optimization**: Images use original dimensions for quality.
- **Video autoplay**: Product videos autoplay when loaded.
- **Video looping**: Videos loop when `loop` parameter is true.
- **3D model interaction**: 3D models provide interactive viewing experience.
- **Media ID tracking**: All media includes `data-media-id` for JavaScript access.

---

## Usage Example

```liquid
{% render 'component-product-media',
  media: product.featured_media,
  loop: true
%}
```

Or in a loop:

```liquid
{% for media in product.media %}
  {% render 'component-product-media',
    media: media,
    loop: section.settings.enable_video_looping
  %}
{% endfor %}
```

Typically used in:
- Product media gallery (`component-product-media-gallery`)
- Product media modal (`component-product-media-modal`)
- Any component that needs to render product media

---

## Implementation Notes

1. **Media type detection**: Component uses `media.media_type` to determine rendering method.

2. **Shopify media filters**: All rendering uses Shopify's built-in media filters:
    - `image_url`: Generates optimized image URL
    - `image_tag`: Generates complete `<img>` tag
    - `external_video_tag`: Generates iframe for external videos
    - `media_tag`: Generates appropriate media tag (video, etc.)
    - `model_viewer_tag`: Generates 3D model viewer

3. **Image dimensions**: Images use original dimensions (`width: media.width`, `height: media.height`) for quality.

4. **Image loading**: Images use `loading: 'eager'` for immediate loading (no lazy loading).

5. **Video autoplay**: Product videos autoplay by default (`autoplay: true`).

6. **Video looping**: Video looping controlled by `loop` parameter (passed to `media_tag` filter).

7. **Video controls**: Videos include controls (`controls: true`) for user interaction.

8. **Video preload**: Videos use `preload: 'none'` to reduce initial page load.

9. **Video poster**: Videos use poster image with size `'2048x'` for thumbnail.

10. **Media ID attribute**: All media includes `data-media-id` attribute with media object's ID for JavaScript targeting.

11. **Alt text**: Images use `media.alt` for accessibility (may be empty if not set).

12. **External video support**: External videos (YouTube, Vimeo) handled automatically by Shopify.

13. **3D model support**: 3D models use model-viewer web component for interactive viewing.

14. **Fallback handling**: Unknown media types use generic `media_tag` filter.

15. **No JavaScript required**: Component doesn't require any JavaScript - all functionality provided by Shopify filters.

16. **No inline styles**: Component doesn't include any inline styles - styling handled by parent components.

17. **Case statement**: Uses Liquid `case` statement for clean media type handling.

18. **Parameter defaults**: `loop` parameter is optional and defaults to false if not provided.

19. **Media object structure**: Requires `media` object with:
    - `media_type`: Type of media ('image', 'video', 'external_video', 'model')
    - `width`: Image width (for images)
    - `height`: Image height (for images)
    - `alt`: Alt text (for images)
    - `id`: Media ID (for data attribute)

20. **Image URL generation**: Image URL uses `image_url` filter with original width for quality.

21. **Image tag generation**: Image tag includes all necessary attributes for proper rendering.

22. **Video tag options**: Video tag includes comprehensive options for autoplay, looping, controls, and preload.

23. **Model viewer**: 3D models use Shopify's model-viewer integration for WebGL rendering.

24. **External video embedding**: External videos automatically embedded via iframe by Shopify.

25. **Media ID usage**: `data-media-id` attribute used by JavaScript for:
    - Modal targeting
    - Active media tracking
    - Gallery synchronization

26. **Eager loading**: Images load immediately (no lazy loading) for product media galleries.

27. **Video poster image**: Videos display poster image before playback starts.

28. **Video autoplay behavior**: Videos autoplay when loaded (may be muted by browser policies).

29. **Video loop parameter**: Loop parameter passed directly to `media_tag` filter.

30. **Accessibility**: Images include alt text for screen readers (from `media.alt`).

31. **Responsive images**: Images use original dimensions - responsive behavior handled by CSS.

32. **No conditional logic**: Component is straightforward - no complex conditional rendering.

33. **Reusable component**: Designed to be used in multiple contexts (gallery, modal, etc.).

34. **Media type support**: Supports all Shopify media types:
    - Images
    - Videos
    - External videos (YouTube, Vimeo)
    - 3D models
    - Future media types (via fallback)

35. **Filter chaining**: Image rendering uses filter chaining (`image_url` then `image_tag`).

36. **Data attribute**: `data-media-id` attribute uses media object's ID for unique identification.

37. **Video controls**: Video controls enabled for user interaction (play, pause, volume, etc.).

38. **Video preload strategy**: Videos use `preload: 'none'` to reduce initial bandwidth usage.

39. **Poster image size**: Video poster uses `'2048x'` size for high-quality thumbnail.

40. **External video platforms**: External videos support YouTube and Vimeo automatically.

41. **3D model interaction**: 3D models provide interactive viewing with rotation, zoom, etc.

42. **Fallback media tag**: Unknown media types use generic `media_tag` for basic rendering.

43. **No error handling**: Component assumes valid media object - errors handled by Shopify filters.

44. **Media object validation**: Parent components should validate media object before rendering.

45. **Loop parameter type**: `loop` parameter should be boolean (true/false).

46. **Image dimensions**: Image dimensions come from media object properties.

47. **Alt text source**: Alt text comes from media object's `alt` property.

48. **Media ID source**: Media ID comes from media object's `id` property.

49. **Filter documentation**: All filters documented in Shopify Liquid reference.

50. **Performance**: Component is lightweight with no JavaScript overhead.

