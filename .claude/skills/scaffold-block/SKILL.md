---
name: scaffold-block
description: Generate a complete, standards-compliant Shopify theme block. Use when the user asks to scaffold, create, or add a new theme block in blocks/.
---

# scaffold-block

**Purpose:** Generate a complete, standards-compliant theme block.

**Invocation:** `/scaffold-block <name> [description]`
Example: `/scaffold-block rich-text "Renders a rich text content block"`

## Steps

1. Create `blocks/<name>.liquid` using `.cursor/rules/examples/block-example-group.liquid` as the
   structural template, with:
   - a `{% doc %}` block,
   - `{{ block.shopify_attributes }}` on the root element,
   - a `{% stylesheet %}` block (not an external CSS file — blocks use deduplicated inline CSS),
   - a `{% schema %}` with `t:` keys and `presets`.
2. Verify `{% content_for 'blocks' %}` is syntactically correct (closing quote present) — this is
   the known error point.
3. The schema must include at least one preset with a `name` key.
4. No `section-*` or `component-*` prefixing for block files — they live in `blocks/` flat.
5. Create `docs/assets/<name>.md` or an equivalent docs entry.
6. Confirm the schema uses `t:` keys, not raw English strings.

## Notes

- This repo has **no `schemas/` folder**. Schemas are written inline in the block `.liquid` file.
- Blocks scope per-instance values (padding, alignment, etc.) via inline `style` attribute custom
  properties rather than per-id selectors.
