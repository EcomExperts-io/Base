---
description: Localization standards — applies to every string in every file, including brand-new sections with no existing translation calls nearby
paths:
  - "**/*.liquid"
  - "schemas/**"
---

# Localization Standards

## Scope

This rule applies to **every string you write**, whatever the surrounding code
looks like. A brand-new section with no `| t` calls in it is not evidence that
translation does not apply; English copy in a Figma frame is a design artifact,
not an instruction to hardcode it.

## What counts as a string

| Where | Example |
|---|---|
| Visible text | `<h2>{{ 'sections.faq.title' \| t }}</h2>` |
| Schema labels and preset names | `"label": "t:sections.all.colors.label"` |
| **Accessibility attributes** | `aria-label`, `alt`, `title` |
| **Screen-reader-only text** | `.visually-hidden` spans |

Schema strings use the `t:` prefix and live in `locales/en.default.schema.json`;
storefront strings use `| t` and live in `locales/en.default.json`.

### What does *not* need `| t`

Merchant-entered text: `{{ section.settings.heading | escape }}`,
`{{ product.title }}`, a merchant-uploaded image's alt. `| t` is for
**theme-provided** strings the merchant never sees a field for — "Add to
cart", empty-state and error copy, `aria-label` and `alt` you authored, schema
labels. A content section can legitimately contain few `| t` calls; the miss is
the theme-authored accessibility attribute or schema label hardcoded because
nobody noticed it was a string.

## Translation Filter Usage

```liquid
<!-- Good -->
<h2>{{ 'sections.featured_collection.title' | t }}</h2>
<button>{{ 'products.add_to_cart' | t }}</button>

<!-- Bad -->
<h2>Featured Collection</h2>
<button>Add to cart</button>
```

- Add every new key to `locales/en.default.json`, in English only; a `| t`
  pointing at a missing key renders the key path as visible text
- Descriptive, hierarchical keys
- Sentence case for UI text

## Never chain `| escape` onto `| t`

`t` already escapes the values it interpolates; `| escape` after it encodes
them twice, so **Salt & Pepper** renders as `Salt &amp; Pepper`. Liquid
parses filter arguments up to the next `|`, so `escape` receives the finished
output of `t`, not the argument.

```liquid
<!-- Bad — double-encoded -->
{{ 'blogs.article.back_to_blog' | t: title: blog.title | escape }}

<!-- Good -->
{{ 'blogs.article.back_to_blog' | t: title: blog.title }}
```

A key ending in `_html` is left unescaped on purpose so it can carry markup;
do not add `| escape` to it either. `| escape` is still correct on a bare
object in its own output tag: `{{ product.title | escape }}`.

## Translation with Variables

Interpolate; never append strings together.

```liquid
<p>{{ 'products.price_range' | t: min: product.price_min | money, max: product.price_max | money }}</p>
<p>{{ 'general.pagination.page' | t: page: paginate.current_page, pages: paginate.pages }}</p>
```

```json
{
  "products": { "price_range": "From {{ min }} to {{ max }}" },
  "general": { "pagination": { "page": "Page {{ page }} of {{ pages }}" } }
}
```

## Before you finish a file

Grep your own output for bare English in `aria-label`, `alt` and `"label"`,
and confirm every new key exists in the locale file.
