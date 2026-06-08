# Code Patterns Audit (Section A)

> Read-only audit of the `feature/ai-dev-standards-upgrade` branch.  
> All findings are observational; no code was changed.

---

## 1. Layout

### `layout/theme.liquid` — 93 lines

Well within the 200–300-line target. Responsibilities:

- `<head>`: meta, font preconnects, critical CSS, Swiper conditional load, Alpine.js, Liquid AJAX Cart bootstrap, predictive search CSS toggle.
- `<body>`: GTM body, data layer, skip link, splash screen, `{% sections 'header-group' %}`, `<main>{{ content_for_layout }}</main>`, `{% sections 'footer-group' %}`, and lazy-load JS for predictive search and splash screen.

**Structural delegation is clean.** Markup fragments are in snippets (`css-variables`, `meta-tags`, `component-gtm-head`, `component-gtm-body`, `component-splash-screen`).

**One pattern to note:** Swiper is conditionally loaded via a `template.name` check:

```liquid
{% if template.name == 'collection' or template.name == 'product' or template.name == 'index' or template.name == 'page' or template.name == 'search' %}
  {{ 'swiper7.4.1.min.css' | asset_url | stylesheet_tag }}
  <script src="{{ 'swiper7.4.1.min.js' | asset_url }}" defer="defer"></script>
{% endif %}
```

The whitelist covers the main templates but does not account for Swiper usage in sections that can be placed on other templates via Online Store 2.0 flexibility (see §4 below).

### `layout/password.liquid`

Separate minimal layout for password-protected store state. No issues observed.

---

## 2. Sections

### File Count and Naming

50 section files total. Naming is consistently lowercase-hyphenated with two exceptions:

- `sections/Faq.liquid` — capital F; violates the lowercase convention and will cause case-sensitivity issues on Linux/CI.
- `sections/404.liquid` — numeric prefix; no convention violation in the rules but atypical.

**No `main-` prefix** on any section file — compliant with the naming rule.

### Schema Coverage

All sections include a `{% schema %}` tag except two utility/render-only sections:

- `sections/pickup-availability.liquid` — no schema (rendered via `{% render %}` in product section).
- `sections/predictive-results.liquid` — no schema (rendered on demand by predictive search JS).

Both are valid exceptions; they are not independently placed in templates.

### CSS Loading Pattern

The dominant pattern is **dual loading**: both an external `section-*.css` file (via `stylesheet_tag`) and a `{% style %}` block (for per-instance CSS custom properties, typically padding) coexist on the same section render. Example from `sections/Faq.liquid`:

```liquid
{{ 'section-faq.css' | asset_url | stylesheet_tag }}
{%- style -%}
  .section-{{ section.id }}-padding {
    padding-top: {{ section.settings.padding_top | times: 0.75 | round: 0 }}px;
    ...
  }
{%- endstyle -%}
```

This is intentional (per-instance padding is dynamic) but adds one `<style>` tag per section render per page.

Four sections use `{% stylesheet %}` (Liquid-scoped CSS, deduplicated by Shopify's engine):
`custom-section.liquid`, `collections.liquid`, `hello-world.liquid`, `password.liquid`.

Nineteen sections have no dedicated `section-*.css` in `assets/`, including `cart.liquid`, `header.liquid`, `announcement-bar.liquid`, `dynamic-grid.liquid`. Their CSS is either inlined in the section, loaded via the external `cart.css`/`customer.css`, or loaded from a snippet's CSS file.

### Schema i18n Consistency

Sections broadly split into two camps:

| Pattern | Sections |
|---------|----------|
| `t:` translation keys in schema labels | Most sections (hero, footer, product, collection, featured-collections, etc.) |
| Raw English strings in schema labels/options | `dynamic-grid`, `product-details`, `collection`, `shop-by-category*`, `featured-collections*`, `featured-products`, `promo-banner`, `brand-story-v2` |

The `dynamic-grid.liquid` section is the worst offender — all 30+ schema labels use raw English, bypassing `locales/en.default.schema.json` entirely.

A hardcoded-text example in Liquid output (not schema) was also found:

```liquid
<!-- sections/product.liquid:236 -->
<label class="option__label" for="Quantity-{{ section.id }}">Quantity</label>
```

This string is not passed through `| t`.

### Notable Large Sections

| Section | Lines |
|---------|-------|
| `product.liquid` | 1248 |
| `dynamic-grid.liquid` | 955 |
| `header.liquid` | 716 |
| `search.liquid` | 627 |
| `article.liquid` | 581 |
| `shop-the-look.liquid` | 540 |
| `collection.liquid` | 531 |

`product.liquid` at 1248 lines is notably large. It conditionally renders complementary products, media gallery, selling plans, pickup availability, and variant selectors inline. The JS loading at the top of the file is extensive. No external JS file is loaded for the product section — `section-product.js` is loaded inside the `<product-info>` custom element tag (via `product.liquid` directly).

### Block Sections (Online Store 2.0 Blocks)

The `blocks/` folder contains two theme-level blocks:

- `blocks/group.liquid` — layout wrapper with `{% content_for 'blocks' %}` for nesting.
- `blocks/text.liquid` — simple text output with style variants.

Both use `{% doc %}`, `{% stylesheet %}`, and fully translated schema labels via `t:` keys. These are the exemplary patterns in the codebase.

---

## 3. Snippets

### Naming Convention

All 29 snippet files follow the `component-` prefix convention. Two non-component snippets exist as expected exceptions: `css-variables.liquid` and `meta-tags.liquid`.

### LiquidDoc Coverage

| Status | Count | Files |
|--------|-------|-------|
| Has `{% doc %}` | 16 | `component-social-icons`, `component-cart-notification`, `component-localization-form`, `component-predictive-search`, `component-nav-drawer`, `component-nav-megamenu`, `component-nav-dropdown`, `component-cart-drawer`, `component-cart-discount`, `component-product-media`, `component-product-media-gallery`, `component-product-media-modal`, `component-product-price`, `component-product-share-button`, `component-splash-screen`, `css-variables` |
| Missing `{% doc %}` | 13 | `component-article-card`, `component-cart-discount` *(inconsistent)*, `component-data-layer`, `component-filters-horizontal`, `component-filters-price-range`, `component-filters-sidebar`, `component-gtm-body`, `component-gtm-head`, `component-hotspot`, `component-pagination`, `component-product-card`, `component-splash-screen-head` |

`component-product-card` is among the most widely rendered snippets in the theme and lacks documentation.

### Parameter Defaults Pattern

The `snippets.mdc` rule mandates parameter validation with defaults. Actual snippets are inconsistent — some validate and assign defaults (well-documented ones), others assume callers pass the correct values.

---

## 4. JavaScript

### Summary

| Category | Count |
|----------|-------|
| Section JS files (`section-*.js`) | 12 |
| Component JS files (`component-*.js`) | 17 |
| Utility/library JS | 5 (`theme.js`, `customer.js`, `liquid-ajax-cart-*.js`, `shopify.js`, `product-recommendations.js`) |
| Third-party minified | 2 (`alpinejs*.min.js`, `swiper*.min.js`) |

### Custom Element Pattern

All component and section JS files (except `customer.js`) use the `customElements.define` pattern with `customElements.get` guard:

```javascript
if (!customElements.get('cart-drawer')) {
  customElements.define('cart-drawer', CartDrawer);
}
```

`connectedCallback` and `disconnectedCallback` are used consistently for initialization and cleanup.

**`customer.js`** is the single outlier — it defines a `CustomerAddresses` class that is not registered as a custom element and has no observable initialization hook visible in the file (the class is defined but no instantiation is shown).

### Module Type Inconsistency

All section scripts use `type="module"` when loaded in section Liquid files except:

```liquid
<!-- sections/shop-by-category.liquid:4 -->
<script src="{{ 'section-shop-by-category.js' | asset_url }}" defer></script>
```

This uses `defer` instead of `type="module"`. In `section-shop-by-category.js`, the class extends `HTMLElement` with `export class ShopByCategory` — without `type="module"` the `export` keyword causes a runtime syntax error in non-module context. (Shopify's CDN serves assets as-is.)

### Alpine.js Usage

Alpine.js is used for lightweight stateful UI components:

| Usage | Locations |
|-------|-----------|
| `x-data` declarations | 17 across sections and snippets |
| `@event.window` listeners | `header.liquid` (cart open/close), `announcement-bar.liquid` |
| `$persist(...)` | `component-filters-sidebar.liquid` (filter "show more" state) |
| `x-cloak` | FAQ, product details, and announcement bar |

Alpine is loaded globally in `theme.liquid` via the Persist plugin and core, in this order:
1. `alpinejs-persist@3.14.8.min.js` (deferred)
2. `alpinejs@3.14.8.min.js` (deferred)

This is the correct load order (plugin before core? — actually Alpine requires the plugin loaded before `alpinejs` initializes; here it is reversed: persist is listed first, but both are deferred so execution order depends on parse order, which is correct here).

### Liquid AJAX Cart

AJAX Cart is bootstrapped in `theme.liquid` via ES module import:

```liquid
<script type="application/json" data-ajax-cart-initial-state>
  {{ cart | json }}
</script>
<script type="module">
  import '{{ "liquid-ajax-cart-v2.1.1.js" | asset_url }}';
</script>
```

Usage patterns across sections and snippets:

- `data-ajax-cart-section` (reactive section re-renders): `cart.liquid`
- `data-ajax-cart-bind`: header cart count badge
- `<ajax-cart-product-form>`, `<ajax-cart-quantity>`: `product.liquid`, `cart.liquid`
- `data-ajax-cart-request-button`: remove links in `cart.liquid`
- Cart drawer open is triggered via Alpine `window.dispatchEvent(new CustomEvent('cart-open'))` from `component-cart-drawer.js` on `liquid-ajax-cart:request-end` event.

The integration is cohesive. The `component-cart-drawer.js` bridges AJAX Cart events to Alpine state cleanly.

### Swiper Usage

Swiper 7.4.1 is used in:

| Section | Swiper Use |
|---------|-----------|
| `product.liquid` / `section-product.js` | Main gallery + thumbnail gallery |
| `featured-products.liquid` | Product slider |
| `featured-collections-v2.liquid` | Per-collection product carousel |
| `shop-the-look.liquid` | Product grid slider |
| `selling-points-v2.liquid` | Mobile-only slider |
| `shop-categories.liquid` | Category carousel |
| `related-products.liquid` | Related product slider |

`theme.liquid` only loads Swiper for `collection`, `product`, `index`, `page`, `search` templates. Sections like `featured-products` and `selling-points-v2` are frequently placed on non-covered templates (e.g., a dedicated landing page template). Any such placement would fail silently since `Swiper` would be undefined.

---

## 5. CSS Methodology

### Positive Signals

- 424 `var(--…)` references — strong custom property system.
- CSS variables are centrally defined per color scheme in `snippets/css-variables.liquid` and emitted into `<style>` in `<head>`.
- Per-section CSS scoping uses `.section-{{ section.id }}-padding` class.
- BEM-like class names are generally followed: `.faq__header`, `.announcement-bar__content`, `.product-media-gallery__thumbnails`.

### Violations

**ID selectors in `cart.css`** (18+ uses):
```css
#cart-drawer:not(.cart-open) .drawer-overlay { … }
#cart-main .cart-items { … }
```
The CSS specificity rule mandates max `0 1 0` (single class). ID selectors are `1 0 0`.

**`!important` usage** — 41 declarations total, none with explanatory comments (required by `css-standards.mdc`):
- `critical.css`: 5 (mostly utility classes like `.visually-hidden` — arguably justified)
- `section-product.css`: 7 (layout overrides)
- `customer.css`: 2
- Others scattered

**Hardcoded hex colors** (~50 instances) — examples:
- `sections/404.liquid`: `color: #121212`, `background: #121212`, `color: #121212BF`
- `assets/critical.css`: `background: #0003`, `color: #fff`
- `assets/cart.css`: `border: 1px solid #d1d5db`, `color: #dc2626`

The color system defines `--color-foreground`, `--color-background`, `--color-button` etc. These hardcoded values bypass it.

---

## 6. Templates

### Structure

37 template files (including `templates/customers/`). All use the JSON template format (OS 2.0). `gift_card.liquid` is the single Liquid template (required by Shopify).

Template files correctly reference section IDs and settings. The `index.json` contains pre-populated demo content including an `overlay_color: "#e8e1e1"` hardcoded hex value in `settings_data.json`.

### Page Variants

Many demo templates exist as `page.[section-name].json`, allowing the full section library to be previewed. These appear to be developer/demo scaffolding rather than merchant-facing templates.

---

## 7. Locales

Two locale files:
- `locales/en.default.json` — storefront translations
- `locales/en.default.schema.json` — theme editor label translations

Both are marked auto-generated (standard Shopify pattern). Only English is present — the codebase does not currently support multiple languages.

`locales.mdc` rule assumes multiple language files (`en.json`, `es.json`, `fr.json`, `de.json`), which do not exist.

---

## 8. Config

`config/settings_schema.json` — 12 setting groups:
`theme_info`, `logo`, `typography`, `layout`, `colors`, `cart`, `search_input`, `splash_screen`, `brand_information`, `social-media`, `currency_format`, `gtm`.

Schema group names use `t:` translation keys correctly. The GTM integration group is a non-standard addition for Google Tag Manager — surfaced via `component-gtm-head.liquid` and `component-gtm-body.liquid` snippets.

`settings_data.json` contains the current (likely demo) theme configuration — includes an `overlay_color: "#e8e1e1"` hardcoded hex in a section setting, which is merchant-set and not a code concern.
