---
description: Locales coding standards and best practices guide
paths:
  - "locales/**/*.json"
---

# Translation Development Standards

## File Structure

`en.default.json` is required; other languages are `es.json`, `fr.json`, and
so on, and `*.schema.json` holds the theme editor strings.

## Key Organization

```json
{
  "general": {
    "meta": { "title": "{{ shop_name }}" },
    "accessibility": { "skip_to_content": "Skip to content", "close": "Close" }
  },
  "products": {
    "add_to_cart": "Add to cart",
    "price": { "regular": "Regular price", "sale": "Sale price" }
  }
}
```

```liquid
{{ 'general.meta.title' | t: shop_name: shop.name }}
```

## Translation Guidelines

- Descriptive, hierarchical `snake_case` keys, at most 3 levels deep
- Concise UI text; variables for dynamic content; consistent terminology
- Schema strings go in `en.default.schema.json`, not here

## A locale file holds at most 3,400 keys

Shopify's documented limit: 3,400 translations per locale file, no value over
1,000 characters (<https://shopify.dev/docs/storefronts/themes/architecture/locales>).
The upload rejects a file over it ("Too many translation keys") and takes every
page of the theme down; Theme Check passes the file. `check-json.py` errors
above 3,400 and warns above 3,300. Near the cap: reuse a generic label
(`labels.*`, `sections.all.*`), fold `info` lines into one `paragraph`
setting, and remove an unused key in the same change.
