# meta-tags Snippet

`snippets/meta-tags.liquid` outputs SEO and social meta tags (Open Graph, Twitter) and the `<title>` tag. It automatically adapts tags for product, article, and password pages. The component generates comprehensive meta tags for search engines and social media sharing, including structured data for products.

---

## What It Does

- Outputs essential HTML meta tags (charset, viewport, X-UA-Compatible).
- Generates Open Graph meta tags for social sharing.
- Generates Twitter Card meta tags.
- Creates page title with shop name and pagination.
- Outputs canonical URL link.
- Generates meta description.
- Creates structured data (JSON-LD) for products.
- Adapts tags based on page type (product, article, password).

---

## Parameters

None. This snippet takes no parameters. It reads from global Liquid objects.

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | None required |
| JavaScript | None required |
| Shopify Objects | `page_title`, `canonical_url`, `page_description`, `page_image`, `shop`, `product`, `cart`, `request`, `current_tags`, `current_page` |
| Shopify Filters | `escape`, `image_url`, `money_without_currency`, `strip_html`, `join`, `structured_data` |

- No external dependencies required.
- All data comes from Shopify Liquid objects.
- Shopify filters handle formatting and escaping.

---

## Dynamic Styles

The snippet does not include any styles. It only outputs HTML meta tags and structured data.

---

## Markup Structure

The snippet outputs HTML meta tags in the `<head>` section:

### Essential Meta Tags

```liquid
<meta charset="utf-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="viewport" content="width=device-width,initial-scale=1">
```

### Open Graph Tags

```liquid
<meta property="og:site_name" content="{{ shop.name }}">
<meta property="og:url" content="{{ og_url }}">
<meta property="og:title" content="{{ og_title | escape }}">
<meta property="og:type" content="{{ og_type }}">
<meta property="og:description" content="{{ og_description | escape }}">
```

### Open Graph Image Tags (Conditional)

```liquid
{%- if page_image -%}
  <meta property="og:image" content="http:{{ page_image | image_url }}">
  <meta property="og:image:secure_url" content="https:{{ page_image | image_url }}">
  <meta property="og:image:width" content="{{ page_image.width }}">
  <meta property="og:image:height" content="{{ page_image.height }}">
{%- endif -%}
```

### Product-Specific Tags

```liquid
{%- if request.page_type == 'product' -%}
  <script type="application/ld+json">
    {{ product | structured_data }}
  </script>
  <meta property="og:price:amount" content="{{ product.price | money_without_currency | strip_html }}">
  <meta property="og:price:currency" content="{{ cart.currency.iso_code }}">
{%- endif -%}
```

### Twitter Card Tags

```liquid
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{{ og_title | escape }}">
<meta name="twitter:description" content="{{ og_description | escape }}">
```

### Title Tag

```liquid
<title>
  {{ page_title }}
  {%- if current_tags %} &ndash; tagged "{{ current_tags | join: ', ' }}"{% endif -%}
  {%- if current_page != 1 %} &ndash; Page {{ current_page }}{% endif -%}
  {%- unless page_title contains shop.name %} &ndash; {{ shop.name }}{% endunless -%}
</title>
```

### Canonical Link

```liquid
<link rel="canonical" href="{{ canonical_url }}">
```

### Meta Description (Conditional)

```liquid
{% if page_description %}
  <meta name="description" content="{{ page_description | escape }}">
{% endif %}
```

---

## Behavior

- **Page type detection**: Detects page type and adapts meta tags accordingly.
- **Open Graph type**: Sets `og:type` to 'product', 'article', or 'website' based on page.
- **URL handling**: Uses canonical URL or request origin based on page type.
- **Image handling**: Includes Open Graph image tags when `page_image` is available.
- **Structured data**: Outputs JSON-LD structured data for product pages.
- **Price information**: Includes product price in Open Graph tags for product pages.
- **Title construction**: Builds title with page title, tags, pagination, and shop name.
- **Content escaping**: All user-generated content is escaped for security.

---

## Usage Example

```liquid
{% render 'meta-tags' %}
```

Typically used in:
- Theme layout (`layout/theme.liquid`) in `<head>` section

---

## Implementation Notes

1. **No parameters**: Snippet takes no parameters - reads all data from global Liquid objects.

2. **Essential meta tags**: Outputs three essential meta tags:
    - `charset="utf-8"`: Character encoding
    - `X-UA-Compatible`: IE compatibility
    - `viewport`: Responsive viewport settings

3. **Open Graph variables**: Calculates Open Graph values:
    - `og_title`: `page_title` or `shop.name`
    - `og_url`: `canonical_url` or `request.origin`
    - `og_type`: 'website', 'product', or 'article'
    - `og_description`: `page_description` or `shop.description` or `shop.name`

4. **Page type detection**: Detects page type via `request.page_type`:
    - `'product'`: Sets `og_type` to 'product'
    - `'article'`: Sets `og_type` to 'article'
    - `'password'`: Uses `request.origin` for URL
    - Otherwise: Uses 'website' type

5. **Open Graph tags**: Generates standard Open Graph meta tags:
    - `og:site_name`: Shop name
    - `og:url`: Page URL
    - `og:title`: Page title
    - `og:type`: Content type
    - `og:description`: Page description

6. **Open Graph image**: Conditionally includes image tags when `page_image` is available:
    - `og:image`: HTTP image URL
    - `og:image:secure_url`: HTTPS image URL
    - `og:image:width`: Image width
    - `og:image:height`: Image height

7. **Product structured data**: Outputs JSON-LD structured data for product pages using `product | structured_data`.

8. **Product price tags**: Includes Open Graph price tags for product pages:
    - `og:price:amount`: Product price (without currency symbol)
    - `og:price:currency`: Currency ISO code

9. **Twitter Card tags**: Generates Twitter Card meta tags:
    - `twitter:card`: Set to 'summary_large_image'
    - `twitter:title`: Page title
    - `twitter:description`: Page description

10. **Title construction**: Builds title with:
    - Base: `page_title`
    - Tags: `&ndash; tagged "tag1, tag2"` (if tags exist)
    - Pagination: `&ndash; Page 2` (if not page 1)
    - Shop name: `&ndash; Shop Name` (if not already in title)

11. **Canonical URL**: Outputs canonical link tag for SEO.

12. **Meta description**: Conditionally outputs meta description when `page_description` exists.

13. **Content escaping**: All user-generated content escaped using `escape` filter:
    - Titles
    - Descriptions
    - Tags

14. **Image URL generation**: Uses `image_url` filter to generate image URLs.

15. **Price formatting**: Uses `money_without_currency` and `strip_html` filters for price.

16. **Tag joining**: Uses `join` filter to combine tags with comma separator.

17. **Structured data format**: Product structured data output as JSON-LD script tag.

18. **Currency code**: Uses `cart.currency.iso_code` for currency information.

19. **Secure image URL**: Generates both HTTP and HTTPS image URLs for compatibility.

20. **Image dimensions**: Includes image width and height for proper display.

21. **Password page handling**: Password pages use `request.origin` instead of canonical URL.

22. **Title shop name check**: Only adds shop name if not already in title.

23. **Tag display**: Tags displayed in quotes with comma separation.

24. **Pagination display**: Page number only shown if not page 1.

25. **Description fallback**: Description falls back to shop description or shop name.

26. **URL fallback**: URL falls back to request origin if canonical URL not available.

27. **Title fallback**: Title falls back to shop name if page title not available.

28. **Type fallback**: Open Graph type defaults to 'website'.

29. **Image conditional**: Image tags only output when `page_image` is available.

30. **Description conditional**: Meta description only output when `page_description` exists.

31. **Product conditional**: Product-specific tags only output on product pages.

32. **Structured data script**: Structured data wrapped in `<script type="application/ld+json">` tag.

33. **Price strip HTML**: Price stripped of HTML tags for clean numeric value.

34. **Currency ISO code**: Uses ISO currency code (e.g., 'USD', 'EUR').

35. **Image protocol**: Generates both HTTP and HTTPS image URLs.

36. **Tag separator**: Tags joined with comma and space: `', '`.

37. **Title separator**: Title parts separated with `&ndash;` (en dash).

38. **Shop name check**: Checks if shop name already in title to avoid duplication.

39. **Page number format**: Page number formatted as "Page 2" (not "Page 1").

40. **Tag format**: Tags formatted as `tagged "tag1, tag2"`.

41. **Canonical link**: Uses `rel="canonical"` for SEO.

42. **Meta description name**: Uses `name="description"` (not `property`).

43. **Open Graph property**: Uses `property` attribute (not `name`).

44. **Twitter name**: Uses `name` attribute for Twitter tags.

45. **Structured data type**: Uses `application/ld+json` MIME type.

46. **Image URL filter**: Uses `image_url` filter without size parameter (uses original size).

47. **Price without currency**: Strips currency symbol for numeric price value.

48. **HTML stripping**: Strips HTML from price for clean numeric value.

49. **Content security**: All user content escaped to prevent XSS.

50. **SEO best practices**: Follows SEO best practices for meta tags and structured data.

