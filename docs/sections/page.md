# Page Section (`sections/page.liquid`)

`sections/page.liquid` renders individual page content with a customizable narrow page width. It displays the page title and content in a centered, constrained layout with responsive padding controls. The section is designed for content-focused pages like About, Terms, or Policy pages.

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | `section-page.css`, inline `{% style %}` block for responsive padding and page width |
| Data | Relies on the `page` object (title, content) |

- No JavaScript dependencies; the section is purely presentational.
- All styling controlled via CSS with dynamic page width setting.
- Content is rendered from the `page` object provided by Shopify.

---

## Dynamic Styles

Inline styles generate responsive padding and dynamic page width:

```liquid
{%- style -%}
  .section-{{ section.id }}-padding {
    padding-top: {{ section.settings.padding_top | times: 0.75 | round: 0 }}px;
    padding-bottom: {{ section.settings.padding_bottom | times: 0.75 | round: 0 }}px;
  }

  .page-width--narrow {
    max-width: {{ section.settings.max_page_width_narrow }}px;
    margin: 0 auto;
  }

  @media screen and (min-width: 769px) {
    .section-{{ section.id }}-padding {
      padding-top: {{ section.settings.padding_top }}px;
      padding-bottom: {{ section.settings.padding_bottom }}px;
    }
  }
{%- endstyle -%}
```

- **Responsive padding**: Mobile uses 75% of configured padding (rounded to whole pixels), desktop (≥769px) uses full value.
- **Page width**: `max_page_width_narrow` controls maximum content width (600–1200px, default 1000px, step 25px).
- **Centering**: Page width uses `margin: 0 auto` for horizontal centering.

---

## Markup Structure

```liquid
<div class="page-width page-width--narrow section-{{ section.id }}-padding">
  <h1 class="main-page-title page-title">
    {{ page.title | escape }}
  </h1>
  <div class="rte">
    {{ page.content }}
  </div>
</div>
```

- **Container**: Uses `page-width` and `page-width--narrow` classes for constrained, centered layout.
- **Title**: Page title displayed as H1 with `main-page-title` and `page-title` classes.
- **Content**: Page content rendered in a `rte` (rich text editor) container for proper HTML formatting.

---

## Behavior

- Purely presentational; there's no JavaScript.
- Content width is constrained for better readability on large screens.
- Responsive padding adapts to viewport size.
- Rich text content supports HTML formatting via the `rte` class.

---

## Schema

```json
{
  "name": "t:sections.main-page.name",
  "tag": "section",
  "class": "section",
  "settings": [
    {
      "type": "range",
      "id": "max_page_width_narrow",
      "min": 600,
      "max": 1200,
      "step": 25,
      "default": 1000,
      "unit": "px",
      "label": "t:labels.page_width_narrow"
    },
    {
      "type": "header",
      "content": "t:sections.all.padding.section_padding_heading"
    },
    {
      "type": "range",
      "id": "padding_top",
      "min": 0,
      "max": 100,
      "step": 4,
      "unit": "px",
      "label": "t:sections.all.padding.padding_top",
      "default": 36
    },
    {
      "type": "range",
      "id": "padding_bottom",
      "min": 0,
      "max": 100,
      "step": 4,
      "unit": "px",
      "label": "t:sections.all.padding.padding_bottom",
      "default": 36
    }
  ]
}
```

### Section Settings

| Setting ID | Type | Default | Purpose |
|------------|------|---------|---------|
| `max_page_width_narrow` | range (px) | 1000 | Maximum content width (600–1200px, step 25) |
| `padding_top` | range (px) | 36 | Top padding (0–100px, step 4) |
| `padding_bottom` | range (px) | 36 | Bottom padding (0–100px, step 4) |

---

## Implementation Notes

1. **Translation keys**: Section name and all setting labels use translation filters (`t:sections.main-page.name`, `t:labels.page_width_narrow`, `t:sections.all.padding.*`).

2. **Page object**: This section requires a `page` object context. It's typically used on page template pages where Shopify automatically provides the page object.

3. **Rich text content**: Content is rendered in a `rte` (rich text editor) container, which applies styling for HTML content created in the Shopify admin.

4. **Page width control**: The `max_page_width_narrow` setting allows merchants to control content width for optimal readability. The narrow width is ideal for long-form content.

5. **Responsive breakpoint**: Desktop padding applies at 769px; ensure this aligns with the theme's global breakpoint strategy.

6. **Text escaping**: Page title is escaped using the `escape` filter for security. Page content is not escaped as it may contain HTML from the rich text editor.

7. **CSS class dependencies**: Section relies on `page-width` class being defined in theme CSS. The `page-width--narrow` class is dynamically styled via inline styles.

8. **Content formatting**: The `rte` class should be styled in `section-page.css` to properly format rich text content (paragraphs, headings, lists, etc.).

9. **SEO considerations**: Page title uses `<h1>` tag, which is appropriate for page templates. Ensure proper heading hierarchy if other headings exist in page content.

10. **Accessibility**: Semantic HTML structure with proper heading hierarchy. Ensure `section-page.css` includes appropriate typography and spacing for readability.

