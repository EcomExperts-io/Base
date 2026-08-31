---
description: Schema standards for section and block {% schema %} tags
paths:
  - "blocks/**/*.liquid"
  - "sections/**/*.liquid"
  - "schemas/**"
---

# Schema Standards

Every section and block must include a `{% schema %}` tag with valid JSON structure.

**Schemas are written inline**, inside the `{% schema %}` tag in the section or
block's own `.liquid` file. This theme has no `schemas/` directory and no
`npm run build:schemas` step — earlier versions of this rule described one, but
neither exists here. Do not look for them and do not create them.

## Required settings on every section

A section schema is not complete without these. The full pattern, including the
matching `{%- style -%}` block and the one permitted exception, is in
`sections.md` — this is the schema-side summary:

| Setting | Type | Label |
|---|---|---|
| `color_scheme` | `color_scheme` | `t:sections.all.colors.label` |
| `padding_top` | `range` 0–100, step 4, default 40 | `t:sections.all.padding.padding_top` |
| `padding_bottom` | `range` 0–100, step 4, default 40 | `t:sections.all.padding.padding_bottom` |

Plus a `presets` array — without one, a merchant cannot add the section in the
theme editor at all.

`padding_top` and `padding_bottom` are unconditional. `color_scheme` may be
omitted only with a Liquid comment explaining why, per `sections.md`.

## Labels must be translation keys

Every `label`, `content`, `info`, and preset `name` uses a `t:` key resolving in
`locales/en.default.schema.json`. Never a bare English string.

```json
{ "type": "range", "id": "padding_top", "label": "t:sections.all.padding.padding_top" }
```

not

```json
{ "type": "range", "id": "padding_top", "label": "Padding Top" }
```

Some existing Base sections use bare English labels for padding. Those predate
this rule; match the `t:` form above, not them.

## `name` is capped at 25 characters

Theme Check's `ValidSchemaName` fails a schema whose `name` exceeds 25
characters. It is a hard limit, it is not obvious from the error, and it is
easy to hit with a descriptive name:

```json
"name": "Complete Your Stack Drawer"   // 26 — fails
"name": "Complete Your Stack"          // 19 — fine
```

The limit is on `name` only. Preset names, labels and headings are unaffected —
put the longer wording in the preset name, which is what a merchant actually
reads in the theme editor:

```json
{
  "name": "Quick Shop",
  "presets": [{ "name": "t:sections.quick_shop.preset_name" }]
}
```

Count it before you commit; the pre-commit Theme Check will otherwise tell you
at the worst moment.

## Schema Structure
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["name", "settings"],
  "properties": {
    "name": {
      "type": "string",
      "maxLength": 50
    },
    "tag": {
      "type": "string",
      "enum": ["div", "section", "aside", "header", "footer", "main"]
    },
    "class": {
      "type": "string"
    },
    "settings": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["type", "id", "label"],
        "properties": {
          "type": {
            "enum": ["text", "textarea", "number", "range", "color", "checkbox", "select", "radio", "collection", "product", "blog", "page", "header", "paragraph", "image_picker", "font_picker", "video", "richtext"]
          },
          "id": {
            "type": "string",
            "pattern": "^[a-z][a-z0-9_]*$"
          },
          "label": {
            "type": "string",
            "maxLength": 30
          },
          "visible_if": {
            "type": "string",
            "pattern": "\\{\\{\\s+[a-zA-Z_][a-zA-Z0-9_]*\\s+\\}\\}"
          }
        }
      }
    },
    "blocks": {
      "type": "array",
      "maxItems": 20,
      "items": {
        "type": "object",
        "required": ["type", "name", "settings"],
        "properties": {
          "type": {
            "type": "string",
            "pattern": "^(@theme|@app|[a-z][a-z0-9_]*)$"
          },
          "name": {
            "type": "string",
            "maxLength": 30
          },
          "settings": {
            "type": "array"
          }
        }
      }
    },
    "presets": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name"],
        "properties": {
          "name": {
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
```

## Setting Types and Usage

### Input settings

These are the bulk of the settings with which the merchant will interact.

See [input settings documentation](https://shopify.dev/docs/storefronts/themes/architecture/settings/input-settings)

### Sidebar settings

These are informative settings to guide the merchant.

See [sidebar settings documentation](https://shopify.dev/docs/storefronts/themes/architecture/settings/sidebar-settings)


## Best practices

### Label Guidelines

- Keep labels concise (under 30 characters)
- Setting type provides context - "Columns" not "Number of columns"
- No verb-based labels for checkboxes
- Use title case: "Show Vendor" not "show vendor"


### Setting Organization Rules

**1. Resource Pickers First**
- Collection, product, blog, page pickers come first
- These are required for section functionality

**2. Visual Impact Order**
- Layout settings (columns, spacing)
- Typography settings (fonts, sizes)
- Color settings (background, text)
- Padding/margin last

**3. Group settings using Headers**
```json
{
  "type": "header",
  "content": "Layout"
}
```
