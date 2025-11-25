# Article Section (`sections/article.liquid`)

`sections/article.liquid` renders individual blog article pages with a flexible block-based layout. It supports featured images, customizable typography, social sharing, and an optional comments system with moderation. The section uses dynamic CSS generation based on block settings and includes structured data for SEO.

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | `section-article.css`, `component-pagination.css`, `component-product-share-button.css`, inline `<style>` and `{% style %}` blocks |
| JS   | `component-product-share-button.js` (module) |
| Snippets | `component-product-share-button`, `component-pagination` |
| Icons | `icon-arrow.svg`, `icon-error.svg`, `icon-success.svg` (inline via `inline_asset_content`) |
| Data | Relies on the `article` object (content, image, author, comments) and `blog` object |

- Social sharing functionality is handled by the `component-product-share-button` snippet and its JavaScript module.
- Comments pagination uses the `component-pagination` snippet.
- Structured data (JSON-LD) is automatically generated from the article object.

---

## Dynamic Styles

The section uses two style blocks: a `<style>` tag for block-specific typography and an `{% style %}` block for responsive padding.

### Block-Based Typography

```liquid
<style>
  {% for block in section.blocks %}
    {% case block.type %}
      {% when 'title' %}
        .article-template__title {
          color: {{ block.settings.title_color }};
          text-align: {{ block.settings.title_alignment }};
          font-weight: {{ block.settings.title_font_weight }};
          @media screen and (min-width: 769px) {
            font-size: {{ block.settings.title_font_size }}px;
          }
        }
      {% when 'content' %}
        .article-template__content * {
          color: {{ block.settings.content_color }};
          text-align: {{ block.settings.content_alignment }};
          font-weight: {{ block.settings.content_font_weight }};
        }
    {% endcase %}
  {% endfor %}

  .article-template__link {
    justify-content: {{ section.settings.back_button_alignment }};
  }
</style>
```

- Title block settings control color, alignment, font weight, and desktop font size (16–72px).
- Content block settings apply to all child elements via the universal selector.
- Back button alignment is controlled by section settings.

### Responsive Padding

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

- Mobile uses 75% of configured padding (rounded to whole pixels).
- Desktop (≥769px) uses full padding values (0–100px, default 36px).

---

## Markup Structure

```liquid
<article class="article-template section-{{ section.id }}-padding">
  {%- for block in section.blocks -%}
    {%- case block.type -%}
      <!-- Block rendering -->
    {%- endcase -%}
  {%- endfor -%}

  <!-- Back to blog link -->
  <!-- Comments section (if enabled) -->
</article>
```

The section iterates through blocks in order, allowing merchants to customize the article layout via the theme editor.

### Block Types

#### `@app` Block

```liquid
{%- when '@app' -%}
  <div class="page-width article-content__page-width">
    {% render block %}
  </div>
```

- Allows app blocks to be inserted into the article layout.
- Wrapped in page-width container for consistent spacing.

#### `featured_image` Block

```liquid
{%- when 'featured_image' -%}
  {%- if article.image -%}
    <div
      class="article-template__hero-container"
      {{ block.shopify_attributes }}
    >
      <div
        class="article-template__hero-{{ block.settings.image_height }} media"
        {% if block.settings.image_height == 'adapt' and article.image %}
          style="padding-bottom: {{ 1 | divided_by: article.image.aspect_ratio | times: 100 }}%;"
        {% endif %}
      >
        <img
          srcset="
            {% if article.image.width >= 350 %}{{ article.image | image_url: width: 350 }} 350w,{% endif %}
            {% if article.image.width >= 750 %}{{ article.image | image_url: width: 750 }} 750w,{% endif %}
            {% if article.image.width >= 1100 %}{{ article.image | image_url: width: 1100 }} 1100w,{% endif %}
            {% if article.image.width >= 1500 %}{{ article.image | image_url: width: 1500 }} 1500w,{% endif %}
            {% if article.image.width >= 2200 %}{{ article.image | image_url: width: 2200 }} 2200w,{% endif %}
            {% if article.image.width >= 3000 %}{{ article.image | image_url: width: 3000 }} 3000w,{% endif %}
            {{ article.image | image_url }} {{ article.image.width }}w
          "
          sizes="(min-width: 1200px) 1100px, (min-width: 769px) calc(100vw - 10rem), 100vw"
          src="{{ article.image | image_url: width: 1100 }}"
          loading="eager"
          fetchpriority="high"
          width="{{ article.image.width }}"
          height="{{ article.image.height }}"
          alt="{{ article.image.alt | escape }}"
          class="article-template__hero-image"
        >
      </div>
    </div>
  {%- endif -%}
```

- **Responsive images**: Full srcset with breakpoints from 350w to 3000w.
- **Height options**: `adapt` (maintains aspect ratio), `small`, `medium`, `large` (fixed heights).
- **Performance**: Uses `loading="eager"` and `fetchpriority="high"` since it's above the fold.
- **Aspect ratio**: When `adapt` is selected, calculates padding-bottom from image aspect ratio.

#### `title` Block

```liquid
{%- when 'title' -%}
  <header
    class="page-width article-content__page-width"
    {{ block.shopify_attributes }}
  >
    <h1 class="article-template__title">
      {{ article.title | escape }}
    </h1>
    {%- if block.settings.blog_show_date -%}
      <span class="article-template__date">
        {{- article.published_at | time_tag: format: 'date' -}}
      </span>
    {%- endif -%}
    {%- if block.settings.blog_show_author -%}
      <span class="article-template__author">
        <span>{{ article.author }}</span>
      </span>
    {%- endif -%}
  </header>
```

- Displays article title with customizable typography (color, alignment, size, weight).
- Optional date and author display controlled by block settings.
- Date uses `time_tag` filter for semantic HTML and localization.

#### `content` Block

```liquid
{%- when 'content' -%}
  <div
    class="article-template__content page-width article-content__page-width rte"
    {{ block.shopify_attributes }}
  >
    {{ article.content }}
  </div>
```

- Renders the full article content with `rte` class for rich text styling.
- Typography settings (color, alignment, weight) apply to all child elements.

#### `share` Block

```liquid
{%- when 'share' -%}
  <div
    class="article-template__social-sharing page-width article-content__page-width"
    {{ block.shopify_attributes }}
  >
    {% assign share_url = request.origin | append: article.url %}
    {% render 'component-product-share-button', block: block, share_link: share_url, section_id: section.id %}
  </div>
```

- Uses the `component-product-share-button` snippet for social sharing functionality.
- Constructs full URL using `request.origin` and `article.url`.
- Up to 2 share blocks allowed per section.

### Back to Blog Link

```liquid
<div class="article-template__back element-margin-top page-width article-content__page-width center">
  <a href="{{ blog.url }}" class="article-template__link link animate-arrow">
    <span class="icon-wrap">
      <span class="svg-wrapper">
        {{- 'icon-arrow.svg' | inline_asset_content -}}
      </span>
    </span>
    {{ 'blogs.article.back_to_blog' | t: title: blog.title | escape }}
  </a>
</div>
```

- Alignment controlled by `section.settings.back_button_alignment` (flex-start, center, flex-end).
- Uses `animate-arrow` class for arrow animation on hover.
- Link text includes the blog title via translation interpolation.

### Comments Section

```liquid
{%- if blog.comments_enabled? -%}
  <div class="article-template__comment-wrapper background-secondary">
    <div id="comments" class="page-width">
      {%- if article.comments_count > 0 -%}
        {%- assign anchor_id = '#Comments-' | append: article.id -%}

        <h2 id="Comments-{{ article.id }}" tabindex="-1">
          {{ 'blogs.article.comments' | t: count: article.comments_count }}
        </h2>
        {% paginate article.comments by 5 %}
          <div class="article-template__comments">
            {%- if comment.status == 'pending' and comment.content -%}
              <article id="{{ comment.id }}" class="article-template__comments-comment">
                {{ comment.content }}
                <footer class="right">
                  <span class="circle-divider caption-with-letter-spacing">{{ comment.author }}</span>
                </footer>
              </article>
            {%- endif -%}

            {%- for comment in article.comments -%}
              <article id="{{ comment.id }}" class="article-template__comments-comment">
                {{ comment.content }}
                <footer class="right">
                  <span class="circle-divider caption-with-letter-spacing">{{ comment.author }}</span>
                  <span class="caption-with-letter-spacing">
                    {{- comment.created_at | time_tag: format: 'date' -}}
                  </span>
                </footer>
              </article>
            {%- endfor -%}
            {% render 'component-pagination', paginate: paginate, anchor: anchor_id %}
          </div>
        {% endpaginate %}
      {%- endif -%}
      <!-- Comment form -->
    </div>
  </div>
{%- endif -%}
```

- **Conditional rendering**: Only displays if `blog.comments_enabled?` is true.
- **Pagination**: Shows 5 comments per page using the `component-pagination` snippet.
- **Pending comments**: Displays pending comments (awaiting moderation) separately.
- **Accessibility**: Uses semantic `<article>` elements and proper heading structure.

### Comment Form

```liquid
{% form 'new_comment', article %}
  <!-- Error handling -->
  {%- if form.errors -%}
    <div class="form__message" role="alert">
      <h3 class="form-status caption-large text-body" tabindex="-1" autofocus>
        <span class="svg-wrapper">
          {{- 'icon-error.svg' | inline_asset_content -}}
        </span>
        {{ 'templates.contact.form.error_heading' | t }}
      </h3>
    </div>
    <ul class="form-status-list caption-large">
      {%- for field in form.errors -%}
        <li>
          <a href="#CommentForm-{{ field }}" class="link">
            <!-- Field-specific error messages -->
          </a>
        </li>
      {%- endfor -%}
    </ul>
  {%- elsif form.posted_successfully? -%}
    <div class="form-status-list form__message" role="status">
      <h3 class="form-status" tabindex="-1" autofocus>
        <span class="svg-wrapper">
          {{- 'icon-success.svg' | inline_asset_content -}}
        </span>
        {{ post_message | t }}
      </h3>
    </div>
  {%- endif -%}

  <!-- Form fields: author, email, body -->
  <!-- Submit button -->
{% endform %}
```

- **Validation**: Full HTML5 validation with `required` and `aria-required` attributes.
- **Error handling**: Field-specific error messages with links to problematic fields.
- **Success messages**: Different messages for moderated vs. unmoderated blogs.
- **Accessibility**: Proper ARIA attributes (`aria-invalid`, `aria-describedby`, `role="alert"`).
- **Form fields**: Name (text), email (email), message (textarea) with labels and placeholders.

---

## Structured Data

```liquid
<script type="application/ld+json">
  {{ article | structured_data }}
</script>
```

- Automatically generates JSON-LD structured data from the article object.
- Improves SEO and enables rich snippets in search results.
- Uses Shopify's built-in `structured_data` filter.

---

## Behavior

- **Block-based layout**: Merchants can reorder and configure blocks via the theme editor.
- **Server-side rendering**: All content is rendered server-side; no client-side JavaScript for core functionality.
- **Comments pagination**: Uses Liquid's `paginate` tag with 5 comments per page.
- **Form submission**: Standard form POST to Shopify's comment endpoint.
- **Moderation**: Supports both moderated and unmoderated comment workflows.
- **Responsive images**: Full srcset implementation for optimal image delivery across devices.

---

## Schema

### Section Settings

| Setting ID | Type | Default | Purpose |
|------------|------|---------|---------|
| `back_button_alignment` | select | `center` | Controls back button alignment (flex-start, center, flex-end) |
| `padding_top` | range (px) | 36 | Top padding (0–100px, step 4) |
| `padding_bottom` | range (px) | 36 | Bottom padding (0–100px, step 4) |

### Blocks

#### `@app`
- Allows app blocks to be inserted into the article layout.
- No limit on quantity.

#### `featured_image`
- **Limit**: 1
- **Settings**:
  - `image_height`: Select (adapt, small, medium, large) — Controls hero image height

#### `title`
- **Limit**: 1
- **Settings**:
  - `title_color`: Color picker (default: #000000)
  - `title_alignment`: Select (left, center, right)
  - `title_font_size`: Range (16–72px, default: 32px) — Desktop only
  - `title_font_weight`: Select (300, 500, 700, default: 500)
  - `blog_show_date`: Checkbox (default: true)
  - `blog_show_author`: Checkbox (default: false)

#### `content`
- **Limit**: 1
- **Settings**:
  - `content_color`: Color picker (default: #000000)
  - `content_alignment`: Select (left, center, right)
  - `content_font_weight`: Select (300, 500, 700, default: 500)

#### `share`
- **Limit**: 2
- **Settings**:
  - `share_label`: Text input — Custom label for share button
  - Two paragraph settings with informational content

---

## Implementation Notes

1. **Translation keys**: All user-facing text uses translation filters (`blogs.article.*`, `templates.contact.form.*`, etc.).
2. **Icon dependencies**: Ensure `icon-arrow.svg`, `icon-error.svg`, and `icon-success.svg` exist in `assets/`.
3. **Block order matters**: Blocks render in the order they appear in `section.blocks`; merchants can reorder via theme editor.
4. **Comments pagination**: Hardcoded to 5 comments per page; cannot be changed via settings.
5. **Image performance**: Featured image uses `loading="eager"` and `fetchpriority="high"` since it's typically above the fold.
6. **Structured data**: The JSON-LD script is automatically generated and should not be modified manually.
7. **Form validation**: Uses both HTML5 validation attributes and server-side validation; ensure error handling CSS is in place.
8. **Moderation workflow**: When `blog.moderated?` is true, comments show a warning message and success message changes to indicate moderation.
9. **Responsive breakpoints**: Desktop styles apply at 769px; ensure mobile-first CSS approach.
10. **Share functionality**: Requires `component-product-share-button.js` to be loaded; the module handles social platform interactions.

