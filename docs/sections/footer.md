# Footer Section (`sections/footer.liquid`)

`sections/footer.liquid` renders the site footer with flexible block-based content areas, localization selectors, payment icons, copyright information, and policy links. It supports multiple block types including link lists, text content, brand information, and social icons. The footer conditionally renders content based on block configuration and theme settings.

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | `section-footer.css` |
| Snippets | `component-social-icons`, `component-localization-form` |
| Blocks | `@app`, `link_list`, `brand_information`, `text` |
| Data | Relies on `section.blocks`, `section.settings`, and global `settings` object |

- No JavaScript dependencies; the section is purely presentational.
- Social icons are rendered via `component-social-icons` snippet.
- Localization (country/language selectors) handled by `component-localization-form` snippet.

---

## Dynamic Styles

The section uses inline styles for dynamic values:

```liquid
<div
  class="footer-block__image-wrapper"
  style="max-width: min(100%, {{ settings.brand_image_width }}px);"
>
```

- `brand_image_width`: Controls maximum width of brand image from theme settings (applied via inline style).

**Note**: The section also includes a hardcoded background color in a `<style>` block (`background-color: rgb(243, 243, 243)`), which is not configurable via settings.

---

## Markup Structure

```liquid
<footer class="footer color-{{ section.settings.color_scheme }} section-{{ section.id }}-padding">
  {%- if section.blocks.size > 0 or section.settings.show_social and has_social_icons == true -%}
    {%- unless only_empty_brand -%}
      <div class="footer__content-top page-width">
        <div class="footer__blocks-wrapper">
          {%- for block in section.blocks -%}
            <!-- Block rendering -->
          {%- endfor -%}
        </div>
      </div>
    {%- endunless -%}
  {%- endif -%}

  <div class="footer__content-bottom">
    <!-- Localization, payment icons, copyright, policies -->
  </div>
</footer>
```

- Footer uses color scheme class: `color-\{\{ section.settings.color_scheme \}\}`.
- Content-top section only renders if blocks exist or social icons are enabled.
- Conditional logic prevents rendering when only empty brand block exists.

### Block Types

#### `link_list` Block

```liquid
{%- when 'link_list' -%}
  {%- if block.settings.menu != blank -%}
    <h2 class="footer-block__heading">{{ block.settings.heading }}</h2>
    <ul class="footer-block__details-content">
      {%- for link in block.settings.menu.links -%}
        <li>
          <a
            href="{{ link.url }}"
            class="list-menu__item--link{% if link.active %} list-menu__item--active{% endif %}"
          >
            {{- link.title | escape -}}
          </a>
        </li>
      {%- endfor -%}
    </ul>
  {%- endif -%}
```

- Renders a menu link list with heading.
- Only displays when a menu is selected.
- Active links receive `list-menu__item--active` class.

#### `text` Block

```liquid
{%- when 'text' -%}
  <h2 class="footer-block__heading">{{ block.settings.heading }}</h2>
  <div class="footer-block__details-content">{{ block.settings.subtext }}</div>
```

- Displays heading and rich text content.
- `subtext` supports HTML/rich text formatting.

#### `brand_information` Block

```liquid
{%- when 'brand_information' -%}
  <div class="footer-block__brand-info">
    {%- if settings.brand_image != blank -%}
      <div class="footer-block__image-wrapper" style="max-width: min(100%, {{ settings.brand_image_width }}px);">
        {{ settings.brand_image | image_url: width: 1100 | image_tag: loading: 'lazy', widths: '50, 100, 150, 200, 300, 400, 550, 800, 1100', height: brand_image_height, width: settings.brand_image_width }}
      </div>
    {%- endif -%}
    {%- if settings.brand_headline != blank -%}
      <h2 class="footer-block__heading">{{ settings.brand_headline }}</h2>
    {%- endif -%}
    {%- if settings.brand_description != blank -%}
      <div>{{ settings.brand_description }}</div>
    {%- endif -%}
    {%- if block.settings.show_social and has_social_icons -%}
      {%- render 'component-social-icons', class: 'footer__list-social' -%}
    {%- endif -%}
  </div>
```

- Displays brand image, headline, and description from theme settings.
- Image width controlled by `settings.brand_image_width` (max-width via inline style).
- Optional social icons when `block.settings.show_social` is enabled.
- Image height calculated from aspect ratio: `brand_image_width / brand_image.aspect_ratio`.

#### `social_icons` Block

```liquid
{%- when 'social_icons' -%}
  <h2 class="footer-block__heading">Follow Us</h2>
  <div class="footer-block__details-content footer-block-social-icons">
    {%- render 'component-social-icons', class: 'footer__list-social' -%}
  </div>
```

- Displays social media icons via `component-social-icons` snippet.
- Heading is hardcoded as "Follow Us" (not translatable).

### Footer Bottom

```liquid
<div class="footer__content-bottom">
  <div class="footer__content-bottom-wrapper">
    <div class="footer__column footer__localization">
      {%- render 'component-localization-form',
        enable_country_selector: section.settings.enable_country_selector,
        enable_language_selector: section.settings.enable_language_selector,
        menu_color_scheme: section.settings.color_scheme
      -%}
    </div>
    <div class="footer__column footer__column--info">
      {%- if section.settings.payment_enable -%}
        <div class="footer__payment">
          <ul class="list-payment" role="list">
            {%- for type in shop.enabled_payment_types -%}
              <li class="list-payment__item">
                {{ type | payment_type_svg_tag: class: 'icon' }}
              </li>
            {%- endfor -%}
          </ul>
        </div>
      {%- endif -%}
    </div>
  </div>
  <div class="footer__content-bottom-wrapper">
    <div class="footer__copyright">
      <small class="copyright__content">
        &copy; {{ 'now' | date: '%Y' }}, {{ shop.name | link_to: routes.root_url }} - {{ powered_by_link }}
      </small>
      {%- if section.settings.show_policy -%}
        <ul class="policies">
          {%- for policy in shop.policies -%}
            {%- if policy != blank -%}
              <li>
                <small class="copyright__content">
                  <a href="{{ policy.url }}">{{ policy.title | escape }}</a>
                </small>
              </li>
            {%- endif -%}
          {%- endfor -%}
        </ul>
      {%- endif -%}
    </div>
  </div>
</div>
```

- **Localization**: Country and language selectors via `component-localization-form` snippet.
- **Payment icons**: Displays enabled payment types as SVG icons when `payment_enable` is true.
- **Copyright**: Shows current year, shop name (linked), and Shopify powered-by link.
- **Policies**: Conditionally displays shop policies (Privacy, Terms, etc.) when `show_policy` is true.

---

## Behavior

- **Conditional rendering**: Footer content-top only renders when blocks exist or social icons are enabled.
- **Empty state handling**: Prevents rendering when only an empty brand block exists.
- **Social icon detection**: Checks multiple social media settings to determine if social icons should display.
- **Animation support**: Footer bottom includes animation classes when `settings.animations_reveal_on_scroll` is enabled.
- **Responsive layout**: Footer adapts layout based on localization selector visibility (centers copyright when selectors are hidden).

---

## Schema

```json
{
  "name": "t:sections.footer.name",
  "blocks": [
    {
      "type": "@app"
    },
    {
      "type": "link_list",
      "name": "t:sections.footer.blocks.link_list.name",
      "settings": [
        {
          "type": "inline_richtext",
          "id": "heading",
          "default": "t:sections.footer.blocks.link_list.settings.heading.default",
          "label": "t:sections.footer.blocks.link_list.settings.heading.label"
        },
        {
          "type": "link_list",
          "id": "menu",
          "default": "footer",
          "label": "t:sections.footer.blocks.link_list.settings.menu.label",
          "info": "t:sections.footer.blocks.link_list.settings.menu.info"
        }
      ]
    },
    {
      "type": "brand_information",
      "name": "t:sections.footer.blocks.brand_information.name",
      "settings": [
        {
          "type": "checkbox",
          "id": "show_social",
          "default": true,
          "label": "t:sections.footer.blocks.brand_information.settings.show_social.label"
        }
      ]
    },
    {
      "type": "text",
      "name": "t:sections.footer.blocks.text.name",
      "settings": [
        {
          "type": "inline_richtext",
          "id": "heading",
          "default": "t:sections.footer.blocks.text.settings.heading.default",
          "label": "t:sections.footer.blocks.text.settings.heading.label"
        },
        {
          "type": "richtext",
          "id": "subtext",
          "default": "t:sections.footer.blocks.text.settings.subtext.default",
          "label": "t:sections.footer.blocks.text.settings.subtext.label"
        }
      ]
    }
  ],
  "settings": [
    {
      "type": "color_scheme",
      "id": "color_scheme",
      "label": "t:sections.all.colors.label",
      "default": "scheme-1"
    },
    {
      "type": "checkbox",
      "id": "enable_country_selector",
      "default": true,
      "label": "t:sections.footer.settings.enable_country_selector.label"
    },
    {
      "type": "checkbox",
      "id": "enable_language_selector",
      "default": true,
      "label": "t:sections.footer.settings.enable_language_selector.label"
    },
    {
      "type": "checkbox",
      "id": "payment_enable",
      "default": true,
      "label": "t:sections.footer.settings.payment_enable.label"
    },
    {
      "type": "checkbox",
      "id": "show_policy",
      "default": true,
      "label": "t:sections.footer.settings.show_policy.label"
    },
    {
      "type": "range",
      "id": "margin_top",
      "min": 0,
      "max": 100,
      "step": 4,
      "unit": "px",
      "label": "t:sections.footer.settings.margin_top.label",
      "default": 0
    }
  ],
  "presets": [
    {
      "name": "t:sections.footer.name",
      "blocks": [
        { "type": "link_list" },
        { "type": "text" }
      ]
    }
  ]
}
```

### Section Settings

| Setting ID | Type | Default | Purpose |
|------------|------|---------|---------|
| `color_scheme` | color_scheme | `scheme-1` | Footer color palette |
| `enable_country_selector` | checkbox | `true` | Show country/region selector |
| `enable_language_selector` | checkbox | `true` | Show language selector |
| `payment_enable` | checkbox | `true` | Display payment method icons |
| `show_policy` | checkbox | `true` | Display shop policy links |
| `margin_top` | range (px) | 0 | Top margin spacing (0–100px, step 4) |

### Blocks

- **`@app`**: App blocks (no limit)
- **`link_list`**: Menu link list block
  - `heading`: Block heading (inline richtext)
  - `menu`: Menu picker (default: "footer")
- **`brand_information`**: Brand info block (uses theme settings)
  - `show_social`: Toggle social icons display
- **`text`**: Text content block
  - `heading`: Block heading (inline richtext)
  - `subtext`: Rich text content

### Presets

- Includes a preset with `link_list` and `text` blocks for quick setup.

---

## Implementation Notes

1. **Translation keys**: All section names, labels, and default values use translation filters (`t:sections.footer.*`).

2. **Social icon detection**: The section checks multiple social media settings to determine if social icons should display:
   - `settings.social_facebook_link`
   - `settings.social_instagram_link`
   - `settings.social_youtube_link`
   - `settings.social_tiktok_link`
   - `settings.social_twitter_link`
   - `settings.social_pinterest_link`
   - `settings.social_snapchat_link`
   - `settings.social_tumblr_link`
   - `settings.social_vimeo_link`

3. **Brand information**: Brand image, headline, and description come from global theme settings, not section settings. Ensure these are configured in theme settings.

4. **Hardcoded background color**: Footer section has a hardcoded background color (`rgb(243, 243, 243)`) in a `<style>` block. Consider making this configurable via color scheme or section settings.

5. **Empty state logic**: Complex conditional logic prevents rendering when only an empty brand block exists. The `only_empty_brand` variable checks if:
   - Only one block exists
   - Block type is `brand_information`
   - Brand image, headline, and description are all blank
   - No social icons are configured

6. **Brand image sizing**: Image width is controlled by `settings.brand_image_width` (theme setting), with max-width applied via inline style. Image height is calculated from aspect ratio.

7. **Payment icons**: Uses `shop.enabled_payment_types` to display payment method icons. Icons are rendered as SVG via `payment_type_svg_tag` filter.

8. **Copyright year**: Uses `'now' | date: '%Y'` to display current year dynamically.

9. **Policy links**: Iterates through `shop.policies` to display all available policies (Privacy Policy, Terms of Service, etc.).

10. **Localization snippet**: Requires `component-localization-form` snippet to handle country and language selector functionality. Ensure this snippet exists and is properly configured.

11. **Animation support**: Footer bottom includes animation classes when `settings.animations_reveal_on_scroll` is enabled, using `scroll-trigger animate--slide-in` and `data-cascade` attributes.

12. **Layout centering**: Copyright section centers when both country and language selectors are disabled (`footer__content-bottom-wrapper--center` class).

13. **Social icons block**: The "Follow Us" heading is hardcoded in English. Consider making it translatable or configurable.

14. **Menu default**: Link list blocks default to "footer" menu. Ensure a footer menu exists in navigation settings.

