# Blogs Section (`sections/blogs.liquid`)

`sections/blogs.liquid` renders a grid of curated articles selected via blocks. Each card displays an image (with optional override), title, description, and a “READ MORE” link. The section also supports a heading and an optional navigation link.

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | `section-blogs.css`, inline `{%- style -%}` block for responsive padding |
| Blocks | `blog_article` block type (limit: 3) |
| Data | Relies on `section.blocks` for article selection and `section.settings` for section options |

- No JavaScript dependencies; the section is purely presentational.
- Articles are curated via blocks (max 3).

---

## Dynamic Styles

The section uses responsive padding set via a `{%- style -%}` block:

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

- **Responsive padding**: Mobile padding is 75% of desktop value; full padding applies at 750px+.

---

## Markup Structure

```liquid
{%- if blocks_to_show > 0 -%}
  <div
    class="blogs-section section-{{ section.id }}-padding color-{{ section.settings.color_scheme }}"
  >
    <div class="page-width">
      <div class="blogs-section__navigation">
        <!-- Heading and navigation link -->
      </div>

      <div class="blogs-section__grid">
        {%- for block in section.blocks -%}
          <!-- Article card -->
        {%- endfor -%}
      </div>
    </div>
  </div>
{%- endif -%}
```

- Section only renders if `section.blocks.size > 0`.
- Header area is optional (shows if heading text or nav link is provided).

### Navigation Header

```liquid
{%- if heading_text != blank or navigation_link_text != blank -%}
  <div class="blogs-section__navigation">
    {%- if heading_text != blank -%}
      <h2 class="blogs-section__heading">{{ heading_text | escape }}</h2>
    {%- endif -%}
    {%- if navigation_link_text != blank and navigation_link_url != blank -%}
      <a href="{{ navigation_link_url }}" class="blogs-section__nav-link">
        {{ navigation_link_text | escape }}
      </a>
    {%- endif -%}
  </div>
{%- endif -%}
```

- **Heading**: Rendered if `heading_text` is present.
- **Nav link**: Rendered only if **both** text and URL are present.

### Article Card

```liquid
{%- for block in section.blocks -%}
  {%- assign article = block.settings.blog -%}
  {%- assign override_image = block.settings.image -%}

  {%- liquid
    assign display_image = blank
    assign article_title = 'Blog title'
    assign article_description = 'Short blog description will appear here.'
    assign article_url = routes.blogs_url

    if article != blank
      assign display_image = override_image
      if display_image == blank
        assign display_image = article.image
      endif

      assign article_title = article.title
      assign article_description = article.summary
      if article_description == blank
        assign article_description = article.content | strip_html | truncatewords: 60
      endif

      assign article_url = article.url
    endif
  -%}

  <article class="blogs-section__article" {{ block.shopify_attributes }}>
    {%- if display_image != blank -%}
      <div class="blogs-section__image-wrapper">
        <img
          srcset="
            {%- if display_image.width >= 165 -%}{{ display_image | image_url: width: 165 }} 165w,{%- endif -%}
            {%- if display_image.width >= 360 -%}{{ display_image | image_url: width: 360 }} 360w,{%- endif -%}
            {%- if display_image.width >= 533 -%}{{ display_image | image_url: width: 533 }} 533w,{%- endif -%}
            {%- if display_image.width >= 720 -%}{{ display_image | image_url: width: 720 }} 720w,{%- endif -%}
            {%- if display_image.width >= 1000 -%}{{ display_image | image_url: width: 1000 }} 1000w,{%- endif -%}
            {{ display_image | image_url }} {{ display_image.width }}w
          "
          src="{{ display_image | image_url: width: 533 }}"
          sizes="(min-width: 769px) 33vw, 100vw"
          alt="{{ display_image.alt | default: article_title | escape }}"
          loading="lazy"
          width="{{ display_image.width }}"
          height="{{ display_image.height }}"
          class="blogs-section__image"
        >
      </div>
    {%- else -%}
      <div class="blogs-section__image-placeholder">
        {{ 'image' | placeholder_svg_tag: 'placeholder-svg' }}
      </div>
    {%- endif -%}

    <div class="blogs-section__content">
      <p class="blogs-section__article-title">
        {{ article_title | escape }}
      </p>
      <p class="blogs-section__description">
        {{ article_description | escape }}
      </p>
      <a href="{{ article_url }}" class="blogs-section__read-more"> READ MORE </a>
    </div>
  </article>
{%- endfor -%}
```

- **Image priority**: `block.settings.image` → `article.image` → placeholder.
- **Description priority**: `article.summary` → stripped/truncated `article.content`.
- **Fallbacks when no article selected**: Defaults to “Blog title”, “Short blog description…”, and `routes.blogs_url`.

---

## Behavior

- **Purely presentational**: No JavaScript required.
- **Conditional rendering**: Section renders only when at least one block exists.
- **Responsive images**: Uses srcset + sizes and `loading="lazy"`.

---

## Schema

```json
{
  "name": "Blogs",
  "tag": "section",
  "class": "blogs",
  "settings": [
    { "type": "header", "content": "Color Settings" },
    { "type": "color_scheme", "id": "color_scheme", "label": "t:sections.all.colors.label", "default": "scheme-1" },
    { "type": "header", "content": "Navigation" },
    { "type": "text", "id": "heading_text", "label": "Heading Text", "default": "VIEW LOOKBOOKS" },
    { "type": "text", "id": "navigation_link_text", "label": "Navigation Link Text", "default": "VIEW LOOKBOOK" },
    { "type": "url", "id": "navigation_link_url", "label": "Navigation Link URL" },
    { "type": "header", "content": "Spacing Settings" },
    { "type": "range", "id": "padding_top", "label": "Padding Top", "min": 0, "max": 100, "step": 4, "unit": "px", "default": 40 },
    { "type": "range", "id": "padding_bottom", "label": "Padding Bottom", "min": 0, "max": 100, "step": 4, "unit": "px", "default": 40 }
  ],
  "blocks": [
    {
      "type": "blog_article",
      "name": "Blog Article",
      "limit": 3,
      "settings": [
        { "type": "article", "id": "blog", "label": "Article" },
        { "type": "image_picker", "id": "image", "label": "Image", "info": "Optional: Override the article's featured image" }
      ]
    }
  ],
  "presets": [
    { "name": "Blogs", "blocks": [{ "type": "blog_article" }, { "type": "blog_article" }, { "type": "blog_article" }] }
  ]
}
```

### Section Settings

| Setting ID | Type | Default | Purpose |
|------------|------|---------|---------|
| `color_scheme` | color_scheme | `scheme-1` | Section color scheme |
| `heading_text` | text | `VIEW LOOKBOOKS` | Heading text |
| `navigation_link_text` | text | `VIEW LOOKBOOK` | Navigation link text |
| `navigation_link_url` | url | — | Navigation link URL |
| `padding_top` | range (px) | 40 | Top padding |
| `padding_bottom` | range (px) | 40 | Bottom padding |

### Blocks

- **`blog_article`** (limit: 3)
  - `blog`: Article picker
  - `image`: Optional image override

### Presets

- Includes a preset with 3 `blog_article` blocks.

---

## Implementation Notes

1. **Block limit**: Max 3 articles per section.
2. **Image override**: Block-level image overrides the article’s image if set.
3. **Description fallback**: Summary first; otherwise `strip_html` + `truncatewords: 60`.
4. **Placeholder behavior**: If no image is available, uses Shopify’s `image` placeholder SVG.
5. **Accessibility**: Image `alt` falls back to the article title.

