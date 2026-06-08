# Base Theme — AI-Dev Standards Upgrade Audit

**Branch audited:** `feature/ai-dev-standards-upgrade`  
**Date:** 2026-06-05  
**Scope:** Read-only "before" snapshot. No code was modified.

---

## Files in This Audit

| File | Covers |
|------|--------|
| `01-code-patterns.md` | Section A — Liquid, CSS, JS, Alpine, AJAX Cart, Swiper, templates, locales, schema |
| `02-cursor-setup.md` | Section B — All `.cursor/rules/*.mdc` classification, prompts/, references/, examples/ |
| `03-forward-looking.md` | Section C — Skills, AGENTS.md, CLAUDE.md, MCP, docs/, workflows, onboarding gaps |

---

## Key Findings at a Glance

### Code Patterns (A)

- `layout/theme.liquid` is 93 lines — well within the 200–300-line target; delegates cleanly to snippets and section groups.
- Custom-element pattern is consistently applied across 30+ JS files (`customElements.get` guard + `connectedCallback`/`disconnectedCallback`). Two outliers: `customer.js` (plain class, no custom element) and `theme.js` (utility exports only — not an element, so expected).
- No `DOMContentLoaded` usage anywhere. No jQuery.
- Naming conventions are followed throughout: all snippets use `component-` prefix; all section JS/CSS use `section-` prefix. One casing anomaly: `sections/Faq.liquid` (capital F).
- CSS methodology is BEM-aligned with heavy custom-property usage (424 `var(--…)` instances across stylesheets). Non-trivial violations exist: `cart.css` uses `#cart-drawer` and `#cart-main` ID selectors extensively (18 instances); 41 `!important` declarations across the codebase.
- Schema i18n is inconsistent: ~42 sections use `t:` keys; several sections (`dynamic-grid`, `collection`, `shop-by-category`, etc.) use raw English strings in schema labels/options — bypassing the locales system.
- `schemas.mdc` and `locales.mdc` both reference a `schemas/` folder and a `build:schemas` npm script that do not exist in this repo. The `package.json` has no `build:schemas` script.
- Swiper 7.4.1 is conditionally loaded in `theme.liquid` only for `collection`, `product`, `index`, `page`, and `search` templates — but Swiper is also used in `featured-products`, `featured-collections-v2`, `shop-the-look`, `selling-points-v2`, `shop-categories`, and `related-products`. Any of those sections on a template not in that whitelist would silently fail.
- LiquidDoc (`{% doc %}`) is used in 16 of 29 component snippets — 13 snippets lack documentation.
- Sections use a mix of `{% style %}` (inline, per-render padding variables) alongside separate `section-*.css` external files — a dual-load pattern seen on ~38 sections simultaneously.

### Cursor Setup (B)

- 16 `.mdc` rule files. Three are `alwaysApply: true` (always loaded into context): `rules-of-engagement`, `naming-conventions`, `prompts-and-references`. Remaining 13 are glob-scoped or description-only (dynamic/on-demand).
- `css-standards.mdc` at 918 lines and `javascript-standards.mdc` at 474 lines are far too large for reliable in-context use as always-on rules; their `globs` field is empty or missing, making them description-activated only.
- `naming-conventions.mdc` (253 lines) has its full content duplicated — the same `# Architecture Standards` section appears at line 5 and again at line 130.
- `sections.mdc` code example contains a typo: `{% content_for 'blocks %}` (missing closing quote).
- `schemas.mdc` glob includes `schemas/*` but that directory does not exist. `locales.mdc` references `schemas/schema.d.ts` which also does not exist.
- `html-standards.mdc` and `snippets.mdc` have empty `description:` fields, making them invisible to description-based rule retrieval.
- `javascript-standards.mdc` has no `globs:` field at all in its frontmatter.
- One prompt file: `fix-accesibility-issue.md` (note the typo in the filename: `accesibility`). References `fetch_rules` tool not available in standard Cursor.
- One reference file: `vitepress-docs.md` (Vue/Liquid mustache gotcha notes).
- One `examples/` folder under rules with 4 example liquid files.

### Forward-Looking (C)

- **No Skills** (`.cursor/skills/` or `.claude/skills/`): absent.
- **No AGENTS.md**: absent.
- **No CLAUDE.md**: absent.
- **No MCP config** (`mcp.json`, `.mcp.json`, or `.cursor/*.json`): absent.
- **No `.figma` / Code Connect files**: absent.
- **GitHub Actions**: one workflow (`deploy-docs.yml`) deploys the VitePress docs site on pushes to `development` branch. No CI for Liquid linting, JS linting, or theme check.
- **docs/**: VitePress-powered documentation site with per-section and per-snippet markdown files (well-populated). Docs deploy is branch-gated to `development`, not `main`.
- Onboarding content missing: no contributor setup guide, no environment setup doc, no Shopify CLI setup instructions in `docs/`.

---

## Observations / Possible Improvement Areas (Flags Only)

1. **Swiper conditional loading gap** — template whitelist in `theme.liquid` does not cover all sections that use Swiper.
2. **`schemas/` phantom references** — two rules and `locales.mdc` reference a folder and npm script that don't exist.
3. **ID selectors in `cart.css`** — violates CSS specificity rule (max `0 1 0`) documented in `css-standards.mdc`.
4. **41 `!important` declarations** — most undocumented; rule mandates a comment explaining any use.
5. **~50 hardcoded hex color values** — scattered across `cart.css`, `critical.css`, `section-product.css`, and `404.liquid`; the theme has a full CSS custom-property color system.
6. **Schema label i18n drift** — several sections (`dynamic-grid`, `collection`, `product-details`, `featured-collections*`, `shop-by-category*`) use raw English strings in schema labels/options rather than `t:` keys.
7. **`naming-conventions.mdc` full duplication** — the entire content block repeats; one copy should be removed.
8. **`sections.mdc` code typo** — `{% content_for 'blocks %}` missing closing quote in the example template.
9. **Empty descriptions on rules** — `snippets.mdc`, `html-standards.mdc` have no `description:`; they won't surface in description-based retrieval.
10. **`javascript-standards.mdc` has no `globs:`** — completely relies on description-match; no file-type trigger.
11. **`css-standards.mdc` at 918 lines** — risks being truncated or ignored; may benefit from splitting.
12. **`customer.js` not using custom element** — class-based but not registered with `customElements.define`; initialization mechanism unclear from static analysis.
13. **`Faq.liquid` casing anomaly** — capital F breaks consistent lowercase section-file naming.
14. **No AGENTS.md / CLAUDE.md / Skills** — no cross-agent or cross-tool instruction files; AI agent onboarding relies entirely on `.cursor/` which is IDE-specific.
15. **No MCP config** — no `.cursor/mcp.json` or root `mcp.json` to document or persist MCP server connections for team members.
16. **Docs deploy gated to `development` branch** — changes on other branches (including this one) do not trigger documentation deployment.
17. **`fix-accesibility-issue.md`** — filename typo (`accesibility`); references a `fetch_rules` tool not available in standard Cursor.
18. **13 component snippets lack LiquidDoc** — inconsistent documentation standard.
19. **Dual CSS load on most sections** — both `{% style %}` (inline padding vars) and `stylesheet_tag` (external file) are active simultaneously on ~38 sections; worth reviewing whether the inline block is always necessary.
20. **`section-shop-by-category.js` loaded with `defer` not `type="module"`** — inconsistent with all other section JS which uses `type="module"`.
