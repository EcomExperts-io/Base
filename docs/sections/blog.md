# Blog Section (`sections/blog.liquid`)

`sections/blog.liquid` renders the main blog listing page, displaying articles in either a grid or collage layout. It supports pagination, customizable article card display options, and responsive spacing controls. The section uses the `component-article-card` snippet to render individual articles and includes pagination when multiple pages are needed.

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | `component-article-card.css`, `section-blog.css`, `component-pagination.css`, inline `{% style %}` block for responsive padding |
| Snippets | `component-article-card`, `component-pagination` |
| Data | Relies on the `blog` object (articles, title) |

- No JavaScript dependencies; the section is purely presentational.
- Article rendering is delegated to the `component-article-card` snippet.
- Pagination uses the `component-pagination` snippet when multiple pages exist.

---

## Dynamic Styles

Inline styles generate responsive padding that scales down on mobile:

```liquid
{%- style -%}
  .section-{{ section.id }}-padding {
    padding-top: {{ section.settings.padding_top | times: 0.75 | round: 0 }}px;
    padding-bottom: {{ section.settings.padding_bottom | times: 0.75 | round: 0 }}px;
  }

  @media screen and (min-width: 769px) {
    .section-{{ section.id }}-padding {
      padding-top: {{ section.settings.padding_top }}px;
      padding-bottom: {{ section.settings.padding_bottom }}px;
    }
  }
{%- endstyle -%}
```

- Mobile uses 75% of the configured padding value (rounded to whole pixels).
- Desktop (≥769px) uses the full padding value from settings.
- Padding values range from 0–100px in 4px increments.

---

## Markup Structure

```liquid
{%- paginate blog.articles by 6 -%}
  <div class="main-blog page-width section-{{ section.id }}-padding" style="--background-color: #F0F0F0;">
    <h1 class="blog-title">
      {{ blog.title | escape }}
    </h1>

    <div class="blog-articles {% if section.settings.layout == 'collage' %}blog-articles--collage{% endif %}">
      {%- for article in blog.articles -%}
        <div class="blog-articles__article article">
          {%- render 'component-article-card',
            article: article,
            show_image: section.settings.show_image,
            show_date: section.settings.show_date,
            show_author: section.settings.show_author,
            show_excerpt: true
          -%}
        </div>
      {%- endfor -%}
    </div>

    {%- if paginate.pages > 1 -%}
      {%- render 'component-pagination', paginate: paginate -%}
    {%- endif -%}
  </div>
{%- endpaginate -%}
```

### Structure Breakdown

- **Container**: Uses `page-width` class for consistent horizontal spacing and includes a hardcoded background color CSS variable (`--background-color: #F0F0F0`).
- **Blog title**: Displays the blog title as an H1 heading, escaped for security.
- **Articles container**: Applies `blog-articles--collage` class when layout setting is set to "collage", otherwise uses default grid layout.
- **Article cards**: Each article is wrapped in a `blog-articles__article` div and rendered via the `component-article-card` snippet with display options passed from section settings.
- **Pagination**: Conditionally renders pagination controls when more than one page exists (6 articles per page).

### Article Card Rendering

The `component-article-card` snippet receives the following parameters:

- `article`: The article object being rendered
- `show_image`: Boolean from `section.settings.show_image` (default: true)
- `show_date`: Boolean from `section.settings.show_date` (default: true)
- `show_author`: Boolean from `section.settings.show_author` (default: false)
- `show_excerpt`: Hardcoded to `true` (always shows excerpt)

---

## Behavior

- **Server-side pagination**: Uses Liquid's `paginate` tag with 6 articles per page (hardcoded).
- **Layout switching**: CSS class toggles between grid and collage layouts based on `section.settings.layout`.
- **Conditional pagination**: Pagination controls only appear when `paginate.pages > 1`.
- **Responsive design**: Padding scales automatically based on viewport size.
- **No JavaScript**: All rendering is server-side; no client-side interactions required.

---

## Schema

### Section Settings

| Setting ID | Type | Default | Purpose |
|------------|------|---------|---------|
| `layout` | select | `collage` | Article layout style (grid or collage) |
| `show_image` | checkbox | `true` | Display article featured images |
| `show_date` | checkbox | `true` | Display article publication date |
| `show_author` | checkbox | `false` | Display article author name |
| `padding_top` | range (px) | 36 | Top padding (0–100px, step 4) |
| `padding_bottom` | range (px) | 36 | Bottom padding (0–100px, step 4) |

### Settings Details

**Layout Options:**
- `grid`: Standard grid layout for articles
- `collage`: Alternative collage-style layout (applies `blog-articles--collage` class)

**Display Options:**
- All checkbox settings control what information appears on article cards via the `component-article-card` snippet.
- `show_excerpt` is hardcoded to `true` in the render call and cannot be toggled via settings.

---

## Implementation Notes

1. **Translation keys**: Section name and all setting labels use translation filters (`t:sections.main-blog.*`, `t:sections.all.padding.*`).

2. **Pagination limit**: Articles are paginated at 6 per page; this is hardcoded in the `paginate` tag and cannot be changed via settings.

3. **Background color**: The container includes a hardcoded CSS variable `--background-color: #F0F0F0`. Consider:
   - Making this configurable via schema settings
   - Using theme color scheme variables for consistency
   - Removing inline styles in favor of CSS classes

4. **Article card snippet**: The section delegates all article rendering to `component-article-card`. Ensure this snippet exists and handles all passed parameters correctly.

5. **Layout classes**: The `blog-articles--collage` class is conditionally applied. Ensure CSS handles both `.blog-articles` (grid) and `.blog-articles--collage` (collage) layouts.

6. **Excerpt display**: `show_excerpt` is hardcoded to `true` in the render call. If merchants need to toggle excerpts, add a schema setting and pass it as a parameter.

7. **Page-width class**: Relies on the global `page-width` class for horizontal spacing; ensure this class is defined in the theme's base CSS.

8. **Pagination snippet**: Uses `component-pagination` snippet for pagination controls. Ensure this snippet exists and handles the `paginate` object correctly.

9. **Responsive breakpoint**: Desktop padding applies at 769px; ensure this aligns with the theme's global breakpoint strategy.

10. **Blog object**: This section requires a `blog` object context. It's typically used on blog template pages where Shopify automatically provides the `blog` object.

