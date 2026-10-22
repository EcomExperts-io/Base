---
description: Locales coding standards and best practices guide
paths:
  - "locales/**/*.json"
---

# Translation Development Standards

Auto-attached when working in `locales/` directory.

## File Structure

```
locales/
├── en.default.json     # English (required)
├── es.json             # Spanish
├── fr.json             # French
└── de.json             # German
```

## Key Organization

**Hierarchical Structure:**
```json
{
  "general": {
    "meta": {
      "title": "{{ shop_name }}",
      "description": "{{ shop_description }}"
    },
    "accessibility": {
      "skip_to_content": "Skip to content",
      "close": "Close"
    }
  },
  "products": {
    "add_to_cart": "Add to cart",
    "quick_view": "Quick view",
    "price": {
      "regular": "Regular price",
      "sale": "Sale price",
      "unit": "Unit price"
    }
  }
}
```
**Usage**
```liquid
{{ 'general.meta.title' | t: shop_name: shop.name }}
{{ 'general.meta.description' | t: shop_description: shop.description }}
```

## Translation Guidelines

**Key Naming:**
- Use descriptive, hierarchical keys
- Maximum 3 levels deep
- Use snake_case for key names
- Group related translations

**Content Rules:**
- Keep text concise for UI elements
- Use variables for dynamic content
- Consider character limits
- Maintain consistent terminology

**Schema Translations:**

Use the rules outlined in our typescript schema (`schemas/schema.d.ts`, if present in this repo) to determine the appropriate key structure for schema translations.

## A locale file holds at most 3,400 keys

Shopify's documented limit: at most 3,400 translations in a single locale file,
and no value over 1,000 characters
(<https://shopify.dev/docs/storefronts/themes/architecture/locales>, "Requirements
and limitations"). The upload rejects a file over it ("Too many translation
keys") and the failed upload takes every page of the theme down; Theme Check,
Prettier and a JSON parse all pass the file. `check-json.py` errors above 3,400
and warns above 3,300. Near the cap, before adding a schema key: reuse a generic
label (`labels.*`, `sections.all.*`) wherever its wording fits, fold `info`
lines into one `paragraph` setting, and remove an unused key in the same
change.
