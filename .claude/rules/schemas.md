---
description: Schema standards for section and block {% schema %} tags
paths:
  - "blocks/**/*.liquid"
  - "sections/**/*.liquid"
  - "schemas/**"
---

# Schema Standards

Every section and block has a `{% schema %}` tag with valid JSON, written
inline in its own `.liquid` file. There is no `schemas/` directory and no
build step; do not create them.

## Required settings on every section

The full pattern, with the matching `{%- style -%}` block and the one
permitted exception, is in `sections.md`:

| Setting | Type | Label |
|---|---|---|
| `color_scheme` | `color_scheme` | `t:sections.all.colors.label` |
| `padding_top` | `range` 0–100, step 4, default 40 | `t:sections.all.padding.padding_top` |
| `padding_bottom` | `range` 0–100, step 4, default 40 | `t:sections.all.padding.padding_bottom` |
| `padding_top_mobile` | `range` 0–100, step 4, default 40 | `t:sections.all.padding.padding_top_mobile` |
| `padding_bottom_mobile` | `range` 0–100, step 4, default 40 | `t:sections.all.padding.padding_bottom_mobile` |

Plus a `presets` array, or a merchant cannot add the section. All four padding
settings are unconditional; `color_scheme` may be omitted only with a Liquid
comment saying why.

## Labels must be translation keys

Every `label`, `content`, `info` and preset `name` is a `t:` key resolving in
`locales/en.default.schema.json`; never a bare English string, even where an
older Base section has one.

```json
{ "type": "range", "id": "padding_top", "label": "t:sections.all.padding.padding_top" }
```

## `range` needs at least three steps

`(max - min) / step` below 3 fails the theme upload; `check-conventions.py`
reports it.

## `name` is capped at 25 characters

Theme Check's `ValidSchemaName` fails a schema `name` over 25 characters.
Preset names and labels are unaffected, so the longer wording goes in the
preset name, which is what the merchant reads:

```json
{
  "name": "Quick Shop",
  "presets": [{ "name": "t:sections.quick_shop.preset_name" }]
}
```

## Blocks are capped at 50; settings are not

A section defines at most **50 blocks**; `max_blocks` can lower that, not
raise it. There is **no documented maximum on `settings`** — a sixty-setting
section is a usability judgement, never a validation or deploy risk, and must
not be reported as one.

## Limits the upload enforces and Theme Check does not

Each passes Theme Check and every local gate, then fails on upload — and one
rejected file leaves `theme dev` serving a 500 on every route, with the error
only in the dev-server terminal.

| Rejected on upload | Do instead |
|---|---|
| A second `product` setting in the section's own `settings` ("can only be inserted once"); a block's settings are not limited | put the second picker in a block's settings |
| `visible_if` on an `article_list` or `blog` setting ("not a valid attribute"); other resource pickers untested | drop the condition, name the source in the label |
| A multi-line text metafield as the dynamic source of a `text` setting; a `textarea` takes no dynamic source at all | a `richtext` setting, connected as `"<p>{{ … \| metafield_tag }}</p>"` |
| More than 3,400 keys in a locale file | see `locales.md` |

`check-conventions.py` flags the first two. The third depends on the store's
metafield type: after writing a template with dynamic sources, curl the page
and grep for "Upload Errors" before measuring anything.

**Two things that upload fine and render nothing.** A `shopify://shop_images/…`
value on an `image_picker` resolves blank when the file is an older generic
upload the picker never lists, although `'<name>' | file_url` finds it — give
the setting a `text` fallback that takes the file name. And a template setting
uploaded before its section's schema defines it is dropped silently; see
`templates.md`.

## Setting types

[Input settings](https://shopify.dev/docs/storefronts/themes/architecture/settings/input-settings)
are what the merchant edits; [sidebar settings](https://shopify.dev/docs/storefronts/themes/architecture/settings/sidebar-settings)
(`header`, `paragraph`) guide them.

## Labels and order

- Labels under 30 characters, title case, no verb on a checkbox; the type
  gives context — "Columns", not "Number of columns"
- Resource pickers first, then layout, typography, colour, and padding last
- Group with `{ "type": "header", "content": "t:…" }`
