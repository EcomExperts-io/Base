---
name: store-recon
description: Find out what the store actually has before building against it — products, collections, pages, metafield definitions, policies — using the Shopify CLI and the store's Storefront MCP endpoint, and record the gap between what the design assumes and what exists. Use at the start of a rebuild, before wiring a section to a metafield or collection, or when a page 404s and nobody knows whether the code or the store is missing.
---

# store-recon

Ask the store before wiring anything to it.

**Why this exists.** The rule is "no invented data"; the review agents enforce
it after the fact by reading the diff. The failure it guards against is
upstream of the code: a design shows an ingredients panel, the section is wired
to `product.metafields.custom.ingredients`, and no product has it — or four
page templates are built and 404 because no page in admin uses them (MiLB).
The store is a source the workflow named in its vision and never read. These
are the reads, all of them without admin write access.

**Invocation:** `/store-recon` — needs the store handle
(`SHOPIFY_FLAG_STORE` in `settings.local.json` under `.claude/`; ask if unset).

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

The Shopify Dev MCP (declared in `.mcp.json`) answers the *platform* questions
— what a Liquid object exposes, what a filter does — via its docs search; use it
before asserting a fact about Liquid in a comment.

The CLI needs Node 22+ (see `/run-theme`) and a logged-in developer for the
store; the first command opens a browser login — hand it to them.

## Steps

1. **Inventory.** `shopify theme list`; `shopify theme metafields pull`; the
   Storefront `list`. Note which tools the store exposes — a password-protected
   store often exposes policies only, and the catalog questions then go
   through the console.
2. **Walk the design's assumptions.** From the Figma frame map (or the frames
   themselves), list every value the design shows that must come from the
   store: metafields, collections a band links to, menus, pages, policies,
   review data from an app. For each, ask the store and record
   **exists / exists but empty / missing**.
3. **Walk the templates.** For every `templates/page.*.json` and
   `templates/collection.*.json`, confirm a page or collection in admin uses
   it (dev server URL resolves). A template with no page is "inert until
   someone creates the page" — say so, with the handle it needs.
4. **Write the gap table** into `state-of-the-theme.md` under `docs/ai-workflow/`
   under "Pages and templates" (the `/recon-theme` document), in this shape:

   | design assumes | source | state | who creates it |
   |---|---|---|---|
   | `product.metafields.custom.ingredients` (PDP ingredients band) | metafield definition + values | definition missing | client admin |
   | `/collections/copa` (homepage band) | collection | exists, 0 products | client |
   | `/pages/shop-by-team` | page using `page.shop-by-team` | missing | client admin |

5. **Wire to the real source anyway, rendering nothing when absent**, and
   name the exact definition someone must create — name, type, owner type,
   consumer. That is the existing rule; the recon is what makes it checkable.

## Writes

None to the store. Creating pages, metafield definitions or menus needs the
Admin API and a human decision; if the developer wants that automated, it is a
separate, confirm-every-write step — not this skill.
