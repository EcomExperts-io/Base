# component-social-icons Snippet

`snippets/component-social-icons.liquid` renders a list of social media icons linking to URLs configured in theme settings. It conditionally displays social icons based on which social links are configured, providing icon-only links with accessible labels for screen readers. The component supports multiple social platforms including Facebook, Instagram, YouTube, TikTok, Twitter, Pinterest, Snapchat, Tumblr, and Vimeo.

---

## What It Does

- Renders social media icons as a list of links.
- Conditionally displays icons based on theme settings.
- Provides accessible labels for screen readers.
- Supports multiple social platforms.
- Allows custom CSS class for styling.
- Uses inline SVG icons for crisp display.

---

## Parameters

| Parameter | Type   | Default | Description                                                      |
|-----------|--------|---------|------------------------------------------------------------------|
| `class`   | string | optional | Optional CSS class to append to the root `<ul>` element.         |

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | External stylesheet (handled by parent components) |
| JavaScript | None required |
| Icons | `icon-facebook.svg`, `icon-instagram.svg`, `icon-youtube.svg`, `icon-tiktok.svg`, `icon-twitter.svg`, `icon-pinterest.svg`, `icon-snapchat.svg`, `icon-tumblr.svg`, `icon-vimeo.svg` (inline via `inline_asset_content`) |
| Data | Requires theme settings: `social_facebook_link`, `social_instagram_link`, `social_youtube_link`, `social_tiktok_link`, `social_twitter_link`, `social_pinterest_link`, `social_snapchat_link`, `social_tumblr_link`, `social_vimeo_link` |

- No external JavaScript required.
- Icons loaded inline via `inline_asset_content` filter.
- External CSS handles styling.

---

## Dynamic Styles

The snippet does not include inline styles. All styling is handled by external CSS files. However, the component uses dynamic class names:

```liquid
class="list-unstyled list-social{% if class %} {{ class}}{% endif %}"
```

- **Dynamic class**: Optional class appended when provided.

---

## Markup Structure

```liquid
<ul class="list-unstyled list-social{% if class %} {{ class}}{% endif %}" role="list">
  {%- if settings.social_facebook_link != blank -%}
    <li class="list-social__item">
      <a href="{{ settings.social_facebook_link }}" class="link list-social__link">
        <span class="svg-wrapper">
          {{- 'icon-facebook.svg' | inline_asset_content -}}
        </span>
        <span class="visually-hidden">{{ 'general.social.links.facebook' | t }}</span>
      </a>
    </li>
  {%- endif -%}
  <!-- Additional social icons -->
</ul>
```

- **Conditional rendering**: Each icon only renders if corresponding setting is not blank.
- **Icon wrapper**: Icons wrapped in `.svg-wrapper` for styling.
- **Accessible labels**: Each link includes visually hidden text for screen readers.

### Supported Platforms

The component supports the following social platforms (each conditionally rendered):

1. **Facebook** (`settings.social_facebook_link`)
2. **Instagram** (`settings.social_instagram_link`)
3. **YouTube** (`settings.social_youtube_link`)
4. **TikTok** (`settings.social_tiktok_link`)
5. **Twitter** (`settings.social_twitter_link`)
6. **Pinterest** (`settings.social_pinterest_link`)
7. **Snapchat** (`settings.social_snapchat_link`)
8. **Tumblr** (`settings.social_tumblr_link`)
9. **Vimeo** (`settings.social_vimeo_link`)

---

## Behavior

- **Conditional display**: Icons only display when corresponding theme setting is configured.
- **Icon-only links**: Links contain only icons (no visible text).
- **Accessible**: Includes visually hidden labels for screen readers.
- **External links**: All links point to external social media URLs.
- **List structure**: Uses semantic `<ul>` and `<li>` elements.

---

## Usage Example

Basic usage:

```liquid
{% render 'component-social-icons' %}
```

With custom class:

```liquid
{% render 'component-social-icons', class: 'footer-social' %}
```

Typically used in:
- Footer (`sections/footer.liquid`)
- Header (less common)
- Any component needing social media links

---

## Implementation Notes

1. **Theme settings**: Component reads social links from theme settings (configured in theme customizer).

2. **Conditional rendering**: Each social icon only renders when its corresponding setting is not blank.

3. **Icon dependencies**: Requires the following icons in `assets/`:
    - `icon-facebook.svg`
    - `icon-instagram.svg`
    - `icon-youtube.svg`
    - `icon-tiktok.svg`
    - `icon-twitter.svg`
    - `icon-pinterest.svg`
    - `icon-snapchat.svg`
    - `icon-tumblr.svg`
    - `icon-vimeo.svg`

4. **CSS class dependencies**: Snippet relies on CSS classes:
    - `.list-unstyled`
    - `.list-social`
    - `.list-social__item`
    - `.list-social__link`
    - `.link`
    - `.svg-wrapper`
    - `.visually-hidden`

5. **Translation keys**: Uses translation keys from `locales/en.default.json`:
    - `general.social.links.facebook`
    - `general.social.links.instagram`
    - `general.social.links.youtube`
    - `general.social.links.tiktok`
    - `general.social.links.twitter`
    - `general.social.links.pinterest`
    - `general.social.links.snapchat`
    - `general.social.links.tumblr`
    - `general.social.links.vimeo`

6. **Accessibility features**:
    - `role="list"` on `<ul>` for semantic structure
    - `visually-hidden` class for screen reader labels
    - Icon-only links with accessible text

7. **Icon loading**: Icons loaded inline via `inline_asset_content` filter for immediate display.

8. **Icon wrapper**: Icons wrapped in `.svg-wrapper` span for styling purposes.

9. **Link structure**: Each link uses `.link` and `.list-social__link` classes for consistent styling.

10. **List structure**: Uses semantic `<ul>` and `<li>` elements for proper list structure.

11. **Custom class**: Optional `class` parameter appended to root `<ul>` for custom styling.

12. **Blank check**: Each social link checked for blank value before rendering.

13. **External links**: All social links point to external URLs (no `rel` attributes specified).

14. **No target attribute**: Links don't specify `target="_blank"` (may be handled by CSS or JavaScript).

15. **Icon format**: Icons must be SVG format for inline loading.

16. **Platform order**: Icons rendered in fixed order (Facebook, Instagram, YouTube, etc.).

17. **Empty list**: If no social links configured, empty `<ul>` is rendered.

18. **Translation support**: All platform names use translation keys for internationalization.

19. **Visually hidden text**: Platform names hidden visually but available to screen readers.

20. **Semantic HTML**: Uses proper semantic structure for accessibility.

21. **No JavaScript**: Component doesn't require any JavaScript functionality.

22. **No inline styles**: All styling handled by external CSS files.

23. **Icon sizing**: Icon sizing controlled by CSS (via `.svg-wrapper` or icon classes).

24. **Link hover states**: Link hover effects handled by CSS.

25. **List styling**: List uses `.list-unstyled` class to remove default list styling.

26. **Item spacing**: Item spacing controlled by CSS (via `.list-social__item`).

27. **Link styling**: Link styling controlled by CSS (via `.link` and `.list-social__link`).

28. **Icon color**: Icon colors controlled by CSS (likely inherits from link color).

29. **Responsive behavior**: Responsive behavior handled by CSS.

30. **Theme setting format**: Social links should be full URLs (e.g., `https://facebook.com/username`).

31. **Setting names**: Theme setting names follow pattern: `social_[platform]_link`.

32. **Platform support**: Supports 9 social platforms total.

33. **Extensibility**: Easy to add new platforms by adding conditional block with new setting.

34. **Icon consistency**: All icons use same structure and classes for consistency.

35. **Accessibility compliance**: Meets WCAG guidelines with proper labels and semantic HTML.

36. **Translation structure**: Translation keys follow pattern: `general.social.links.[platform]`.

37. **No conditional logic**: Simple conditional rendering - no complex logic.

38. **Icon loading method**: Icons loaded inline (not as separate HTTP requests).

39. **SVG advantages**: SVG icons provide crisp display at any size.

40. **List role**: `role="list"` ensures proper screen reader announcement.

41. **Visually hidden class**: `.visually-hidden` class hides text visually but keeps it accessible.

42. **Link accessibility**: Icon-only links are accessible via screen reader labels.

43. **External link handling**: External links may need `rel="noopener"` for security (not in snippet).

44. **Target attribute**: Links may need `target="_blank"` for new tab (not in snippet, may be handled by CSS/JS).

45. **Custom class usage**: Custom class allows component to be styled differently in different contexts.

46. **Empty state**: Component gracefully handles empty state (no social links configured).

47. **Setting validation**: Component assumes settings contain valid URLs (no validation in snippet).

48. **Icon availability**: Component assumes all required icons exist in assets folder.

49. **Translation availability**: Component assumes translation keys exist in locale files.

50. **Performance**: Inline SVG icons prevent additional HTTP requests but increase HTML size.

