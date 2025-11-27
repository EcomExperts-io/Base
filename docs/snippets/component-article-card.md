# component-article-card Snippet

`snippets/component-article-card.liquid` renders a reusable article card component for displaying blog articles in grids, lists, and search results. It supports optional image display, date/author information, excerpts, and responsive images with lazy loading.

---

## What It Does

- Renders a card component for blog articles with consistent styling.
- Conditionally displays article featured image with responsive srcset.
- Shows article title, publication date, author, and optional excerpt.
- Supports lazy loading for images to improve page performance.
- Displays optional blog badge overlay on images.
- Handles articles with or without images (text-only cards).
- Truncates title and excerpt for consistent card sizing.

---

## Parameters

| Parameter     | Type    | Default | Description                                                      |
|---------------|---------|---------|------------------------------------------------------------------|
| `article`     | object  | **required** | Article object to render (must be passed).                       |
| `blog`        | object  | optional | Blog object (documented but not used in current implementation).|
| `show_image`  | boolean | `true`  | Display the article featured image.                              |
| `show_date`   | boolean | `false` | Display the article publication date.                            |
| `show_author` | boolean | `false` | Display the article author name.                                  |
| `show_badge`  | boolean | `false` | Display blog badge overlay on image.                             |
| `show_excerpt`| boolean | `false` | Display article excerpt or content preview.                       |
| `lazy_load`   | boolean | `true`  | Enable lazy loading for images.                                  |

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | Card component styles (likely in `section-blog.css` or shared card styles) |
| Data | Requires `article` object with properties: `image`, `url`, `title`, `published_at`, `author`, `excerpt`, `content` |

- No external JavaScript required - pure Liquid/HTML rendering.
- CSS classes follow card component pattern (`.card`, `.card__inner`, `.card__content`, etc.).
- Images use responsive srcset for optimal loading across devices.

---

## Markup Structure

```liquid
{%- if article and article != empty -%}
  <div class="article-card-wrapper card-wrapper underline-links-hover">
    <div class="card article-card {% if article.image and show_image %} card--media{% else %} card--text{% endif %}">
      <div class="card__inner">
        <!-- Image section (conditional) -->
        <!-- Content section -->
      </div>
    </div>
  </div>
{%- endif -%}
```

- **Conditional rendering**: Only renders if `article` exists and is not empty.
- **Card classes**: Uses `card--media` when image is shown, `card--text` when no image.
- **Wrapper classes**: Includes `underline-links-hover` for link styling.

### Image Section

```liquid
{%- if show_image == true and article.image -%}
  <a href="{{ article.url }}" class="article-card__image-wrapper card__media">
    <div class="article-card__image--medium">
      <img
        srcset="
          {%- if article.image.src.width >= 165 -%}{{ article.image.src | image_url: width: 165 }} 165w,{%- endif -%}
          {%- if article.image.src.width >= 360 -%}{{ article.image.src | image_url: width: 360 }} 360w,{%- endif -%}
          {%- if article.image.src.width >= 533 -%}{{ article.image.src | image_url: width: 533 }} 533w,{%- endif -%}
          {%- if article.image.src.width >= 720 -%}{{ article.image.src | image_url: width: 720 }} 720w,{%- endif -%}
          {%- if article.image.src.width >= 1000 -%}{{ article.image.src | image_url: width: 1000 }} 1000w,{%- endif -%}
          {%- if article.image.src.width >= 1500 -%}{{ article.image.src | image_url: width: 1500 }} 1500w,{%- endif -%}
          {{ article.image.src | image_url }} {{ article.image.src.width }}w
        "
        src="{{ article.image.src | image_url: width: 533 }}"
        alt="{{ article.image.src.alt | escape }}"
        {% unless lazy_load == false %}
          loading="lazy"
        {% endunless %}
        width="{{ article.image.width }}"
        height="{{ article.image.height }}"
        class="article-card__image"
      >
      {%- if show_badge -%}
        <div class="card__badge-wrapper">
          <div class="card__badge article-card__badge">
            <span class="badge">{{ 'blogs.article.blog' | t }}</span>
          </div>
        </div>
      {%- endif -%}
    </div>
  </a>
{%- endif -%}
```

- **Responsive images**: Uses srcset with multiple breakpoints (165w, 360w, 533w, 720w, 1000w, 1500w, full width).
- **Conditional widths**: Only includes srcset entries if image is wide enough for that size.
- **Lazy loading**: Enabled by default unless `lazy_load == false`.
- **Image dimensions**: Includes explicit width and height attributes for layout stability.
- **Badge overlay**: Optional blog badge displayed on image when `show_badge` is true.
- **Linked image**: Image links to article URL.

### Content Section

```liquid
<div class="card__content">
  <div class="card__information">
    <h3 class="card__heading{% if show_excerpt %} h2{% endif %}">
      <a href="{{ article.url }}" class="article-card__title">
        {{ article.title | truncate: 50 | escape }}
      </a>
    </h3>
    <div class="article-card__info">
      {%- if show_date -%}
        <p class="article-card__date">{{ article.published_at | time_tag: '%B %Y' }}</p>
      {%- endif -%}
      {%- if show_author -%}
        <p class="article-card__author">{{ article.author }}</p>
      {%- endif -%}
    </div>
    {%- if show_excerpt -%}
      {%- if article.excerpt.size > 0 or article.content.size > 0 -%}
        <p class="article-card__excerpt">
          {%- if article.excerpt.size > 0 -%}
            {{ article.excerpt | strip_html | truncatewords: 30 }}
          {%- else -%}
            {{ article.content | strip_html | truncatewords: 30 }}
          {%- endif -%}
        </p>
      {%- endif -%}
    {%- endif -%}
  </div>
</div>
```

- **Title**: Truncated to 50 characters, escaped for security, links to article.
- **Heading size**: Uses `h2` class when excerpt is shown for better hierarchy.
- **Date format**: Uses `time_tag` filter with `'%B %Y'` format (e.g., "January 2024").
- **Excerpt logic**: Prefers `article.excerpt`, falls back to `article.content` if no excerpt.
- **Excerpt length**: Truncated to 30 words, HTML stripped.

---

## Behavior

- **Conditional rendering**: Only renders if article exists.
- **Image display**: Shows image only if `show_image == true` and `article.image` exists.
- **Responsive images**: Browser selects appropriate image size from srcset based on viewport.
- **Lazy loading**: Images load only when scrolled into view (unless disabled).
- **Excerpt fallback**: Uses article content if excerpt is empty.
- **Title truncation**: Limits title to 50 characters for consistent card heights.

---

## Usage Example

```liquid
{% render 'component-article-card',
  article: article,
  show_image: section.settings.show_image,
  show_date: section.settings.show_date,
  show_author: section.settings.show_author,
  show_badge: true,
  lazy_load: true
%}
```

Or in a loop:

```liquid
{%- for article in blog.articles -%}
  {% render 'component-article-card',
    article: article,
    show_image: true,
    show_date: true,
    show_author: false,
    show_badge: true
  %}
{%- endfor -%}
```

Typically used in:
- Blog index pages (`sections/blog.liquid`)
- Search results (`sections/search.liquid`)
- Article recommendations
- Related articles sections

---

## Implementation Notes

1. **Article validation**: Snippet checks `article and article != empty` before rendering to prevent errors.

2. **Image srcset generation**: Srcset includes multiple sizes with conditional checks:
   - Only includes sizes that the source image can provide
   - Falls back to full image width if larger sizes aren't available
   - Default src uses 533px width for initial load

3. **Lazy loading**: Uses native `loading="lazy"` attribute for browser-native lazy loading. Can be disabled by passing `lazy_load: false`.

4. **Card type classes**: Dynamically applies `card--media` or `card--text` based on whether image is displayed, allowing different styling for each type.

5. **Title truncation**: Uses `truncate: 50` filter to limit title length. Consider adjusting if card width changes significantly.

6. **Date formatting**: Uses `time_tag` filter with `'%B %Y'` format which displays month name and year (e.g., "January 2024"). This is a simplified format - consider using full date format if needed.

7. **Excerpt handling**: 
   - Checks for `article.excerpt.size > 0` first
   - Falls back to `article.content` if no excerpt
   - Uses `strip_html` to remove HTML tags
   - Truncates to 30 words with `truncatewords: 30`

8. **Badge display**: Badge shows translated text `'blogs.article.blog' | t` which typically displays "Blog" or similar.

9. **CSS class dependencies**: Snippet relies on CSS classes:
   - `.article-card-wrapper`
   - `.card-wrapper`
   - `.underline-links-hover`
   - `.card`
   - `.article-card`
   - `.card--media`
   - `.card--text`
   - `.card__inner`
   - `.card__media`
   - `.card__content`
   - `.card__information`
   - `.card__heading`
   - `.article-card__title`
   - `.article-card__info`
   - `.article-card__date`
   - `.article-card__author`
   - `.article-card__excerpt`
   - `.card__badge-wrapper`
   - `.card__badge`
   - `.article-card__badge`
   - `.badge`

10. **Translation keys**: Uses translation filter:
    - `blogs.article.blog` for badge text

11. **Image alt text**: Uses `article.image.src.alt | escape` for accessible alt text.

12. **Responsive image strategy**: Srcset provides images from 165px to full width, allowing browsers to select optimal size based on:
    - Viewport size
    - Device pixel ratio
    - Network conditions

13. **No JavaScript required**: Snippet is pure Liquid/HTML with no JavaScript dependencies.

14. **Blog parameter**: The `blog` parameter is documented in comments but not currently used in the implementation. It may be reserved for future use.

15. **Heading hierarchy**: When excerpt is shown, heading uses `h2` class for better semantic hierarchy. Without excerpt, uses default `h3` styling.

16. **Link styling**: Wrapper includes `underline-links-hover` class for consistent link hover effects across the theme.

17. **Image aspect ratio**: Image container uses `article-card__image--medium` class which likely controls aspect ratio via CSS.

18. **Accessibility**: 
    - Images include alt text
    - Links are properly structured
    - Semantic HTML (headings, paragraphs)
    - No accessibility issues identified

19. **Performance considerations**:
    - Lazy loading reduces initial page load
    - Responsive images prevent loading oversized images
    - Conditional rendering avoids unnecessary markup

20. **Excerpt word limit**: 30 words is a reasonable default, but may need adjustment based on card height requirements.

21. **Title character limit**: 50 characters may be too short for some titles. Consider making this configurable or adjusting based on card width.

22. **Date format**: Current format (`'%B %Y'`) shows only month and year. Consider supporting full date format if needed for better article identification.

23. **Author display**: Author name is displayed as plain text without any formatting or linking. Consider adding author profile links if needed.

24. **Empty state**: Snippet doesn't render anything if article is empty, which is appropriate but means no placeholder or error message is shown.

25. **Image fallback**: No placeholder image is shown if `show_image` is true but `article.image` is missing. The card will render as text-only in this case.

