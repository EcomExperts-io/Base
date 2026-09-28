---
description: JSON template file structure rules
paths:
  - "templates/**/*.json"
---

# Templates

All JSON templates must follow this exact structure:

## Required Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["sections"],
  "properties": {
    "sections": {
      "type": "object",
      "patternProperties": {
        "^[a-zA-Z0-9_-]+$": {
          "type": "object",
          "required": ["type"],
          "properties": {
            "type": {
              "type": "string",
              "pattern": "^[a-zA-Z0-9_-]+$"
            },
            "settings": {
              "type": "object"
            },
            "blocks": {
              "type": "array",
              "items": {
                "type": "object",
                "required": ["type"],
                "properties": {
                  "type": {
                    "type": "string"
                  },
                  "settings": {
                    "type": "object"
                  }
                }
              }
            }
          }
        }
      }
    },
    "order": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  }
}
```

## Template Structure Rules

- Every template must have a `sections` object
- Section keys must be alphanumeric with dashes/underscores
- Each section must have a `type` property
- `settings` and `blocks` are optional
- `order` array defines section sequence
- Blocks must have a `type` property


## Template Types

**Standard Templates:**
- `index.json` - Homepage
- `product.json` - Product pages
- `collection.json` - Collection pages
- `page.json` - Static pages
- `blog.json` - Blog listing
- `article.json` - Blog posts
- `cart.json` - Shopping cart
- `search.json` - Search results

**Alternate Templates:**
Alternative templates may exist for any of the standard templates, following the structure `template-name.template-suffix.template-file-type`, for example: `product.alternate.json`

## Valid Template Examples

**Product Template:**
```json
{
  "sections": {
    "header": {
      "type": "header"
    },
    "main": {
      "type": "product",
      "settings": {
        "show_vendor": true,
        "show_sku": false,
        "media_size": "medium"
      },
      "blocks": {
        "title": {
          "type": "title",
          "settings": {}
        },
        "price": {
          "type": "price",
          "settings": {
            "show_compare_at": true
          }
        },
        "variant_picker": {
          "type": "variant_picker",
          "settings": {
            "picker_type": "dropdown"
          }
        }
      },
      "block_order": ["title", "price", "variant_picker"]
    },
    "footer": {
      "type": "footer"
    }
  },
  "order": ["header", "main", "footer"]
}
```

**Collection Template:**
```json
{
  "sections": {
    "header": {
      "type": "header"
    },
    "collection-banner": {
      "type": "collection-banner",
      "settings": {
        "show_collection_description": true,
        "show_collection_image": false
      }
    },
    "main": {
      "type": "collection",
      "settings": {
        "products_per_page": 24,
        "columns_desktop": 4,
        "columns_mobile": 2
      }
    }
  },
  "order": ["header", "collection-banner", "main"]
}
```

A section's `type` is its filename in `sections/`. Base names sections by
function — `product`, `collection` — and never with a `main-` prefix; see
`naming-conventions.md`. Earlier versions of these examples used Dawn's
`main-product` and `main-collection-product-grid`, which contradicted that rule
in the one file an agent reads while assembling a template.

## Traps that take the whole theme down

Neither of these is reported by Theme Check. Both were found on a client build
by every route returning 500, or by a key path rendering to a customer.

- **`t:` keys do not resolve in template values.** Shopify resolves `t:` in a
  schema `default`, not in a value stored in a template. A preset copied into
  `templates/*.json` with its `t:` values intact renders the literal key path
  on the storefront. Strip them to plain strings when assembling a template.
  `.claude/scripts/check-conventions.py` flags any `"t:` value in a template.
- **A brand-new block type needs roughly 25 seconds to register** with Shopify
  before a template may reference it. Reference it too early and every route on
  the theme returns 500 until the registration catches up — push the section,
  wait, then push the template.
