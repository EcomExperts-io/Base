---
name: store-recon
description: Find out what the store actually has before building against it — products, collections, pages, metafield definitions, policies — using the Shopify CLI and the store's Storefront MCP endpoint, and record the gap between what the design assumes and what exists. Use at the start of a rebuild, before wiring a section to a metafield or collection, or when a page 404s and nobody knows whether the code or the store is missing.
---

# store-recon

Ask the store before wiring anything to it — a metafield no product carries,
a page template no admin page uses. All read-only.

Needs the store handle (`SHOPIFY_FLAG_STORE` in `settings.local.json` under `.claude/`; ask if unset).

## Sources, in order of what they can answer

| Question | Source | Command |
|---|---|---|
| Which themes exist, which is live, which is the dev theme | Shopify CLI | `shopify theme list` |
| What metafield definitions exist (product, collection, page, shop) | Shopify CLI | `shopify theme metafields pull` — writes `.shopify/metafields.json`; read it, do not commit it |
| Does any product/collection carry a value for a metafield | Shopify CLI Liquid REPL | `shopify theme console` then e.g. `{{ collections.all.products.first.metafields.custom.ingredients }}` |
| What products/collections exist, by search | Storefront MCP | `sh .claude/scripts/storefront-mcp.sh <store> call search_shop_catalog '{"query":"…","context":"recon"}'` |
| Policies and FAQ content the footer/PDP show | Storefront MCP | `sh .claude/scripts/storefront-mcp.sh <store> call search_shop_policies_and_faqs '{"query":"shipping"}'` |
| Which Storefront tools this store exposes at all | Storefront MCP | `sh .claude/scripts/storefront-mcp.sh <store> list` |
| Whether a page/collection URL resolves | dev server | `curl -sI http://127.0.0.1:9292/pages/<handle> \| head -1` after `/run-theme` |

The Shopify Dev MCP (`.mcp.json`) answers *platform* questions — what a
Liquid object exposes, what a filter does. The CLI needs Node 22+
(`/run-theme`) and a logged-in developer; hand the browser login to them.

## Steps

1. **Inventory.** `shopify theme list`; `shopify theme metafields pull`; the
   Storefront `list`. A password-protected store often exposes policies only;
   catalog questions then go through the console.
2. **Walk the design's assumptions.** List every value that must come from
   the store — metafields, collections, menus, pages, policies, app review
   data — and record **exists / exists but empty / missing** for each.
3. **Walk the templates.** For every `templates/page.*.json` and
   `templates/collection.*.json`, confirm a page or collection in admin uses
   it; one with none is "inert until someone creates the page", handle named.
4. **Write the gap table** into `state-of-the-theme.md` under
   `docs/ai-workflow/`, under "Pages and templates":

   | design assumes | source | state | who creates it |
   |---|---|---|---|
   | `product.metafields.custom.ingredients` (PDP ingredients band) | metafield definition + values | definition missing | client admin |
   | `/collections/<handle>` (homepage band) | collection | exists, 0 products | client |
   | `/pages/<handle>` | page using `page.<handle>` | missing | client admin |

5. **Wire to the real source anyway, rendering nothing when absent**, and
   name the exact definition someone must create: name, type, owner type, consumer.

## Writes

None. Creating pages, definitions or menus needs the Admin API and a human
decision — a separate, confirm-every-write step.
