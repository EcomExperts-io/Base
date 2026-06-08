# Base Theme — AI-Dev Standards Modernization Plan

**Planned on:** 2026-06-05  
**Based on audit:** `docs/_audit/00–03` (branch `feature/ai-dev-standards-upgrade`)  
**Status:** Planning only. No code, rules, skills, or docs have been created yet.

Every proposal below is traced to an audit finding with an `[A-nn]` reference to `00-overview.md` observation numbers, or `[B-*]` / `[C-*]` for `02-cursor-setup.md` and `03-forward-looking.md` sections respectively.

---

## 1. Thesis & Scope

### Thesis

The Base theme's **code standards are sound**. The custom-element JS pattern, snippet naming, BEM CSS methodology, Alpine.js integration, and the Liquid AJAX Cart bridge are all coherent and well-executed. Developers writing new code have been following the rules — the theme works correctly in its primary use cases.

What has **decayed** is the **tooling that communicates and enforces those standards to AI agents**. Rules contain phantom references to infrastructure that never shipped, duplicate content that wastes context budget, syntax errors in instructional examples, and broken activation metadata. The accessibility workflow prompt references a tool that doesn't exist in Cursor. No Skills, no cross-tool backbone, and no onboarding layer mean the standards live only in rule files that only Cursor can see.

The project's stated goal — AI-dev standards upgrade — is therefore a **tooling modernization**, not a code rewrite.

### Scope: Two Buckets

#### Bucket 1 — Code Drift (OUT OF SCOPE for this project)

These are gaps between the existing written standards and the current codebase. They represent real technical debt but require careful per-file changes with QA/testing. They are captured here as a backlog to be handed off as a separate project.

| # | Finding | Audit Ref |
|---|---------|-----------|
| 1 | Swiper conditional load whitelist in `theme.liquid` missing `blog`, `article`, `list-collections`, and any custom template | [A-01] |
| 2 | `cart.css` — 18+ ID selectors (`#cart-drawer`, `#cart-main`) violating max `0 1 0` specificity rule | [A-03] |
| 3 | 41 undocumented `!important` declarations across CSS files | [A-04] |
| 4 | ~50 hardcoded hex color values bypassing the CSS custom-property color system | [A-05] |
| 5 | Schema label i18n drift — `dynamic-grid`, `collection`, `product-details`, `featured-collections*`, `shop-by-category*`, `featured-products`, `promo-banner`, `brand-story-v2` using raw English strings | [A-06] |
| 6 | `sections/Faq.liquid` — capital F filename, breaks case-sensitive file systems | [A-13] |
| 7 | `customer.js` — plain class, never registered with `customElements.define`, no observable initialization hook | [A-12] |
| 8 | `section-shop-by-category.liquid` loads its JS with `defer` instead of `type="module"` | [A-20] |
| 9 | 13 component snippets missing `{% doc %}` LiquidDoc blocks, including `component-product-card` | [A-18] |
| 10 | Hardcoded `"Quantity"` string in `sections/product.liquid:236` not passed through `\| t` | [A] |
| 11 | `locales.mdc` references multi-language file structure (`es.json`, `fr.json`, `de.json`) that does not exist | [B-locales.mdc] |

These items feed directly into the **pr-review skill checklist** (see §4) so that AI agents catch them on any future PR even before they are fixed.

#### Bucket 2 — Tooling Rot (IN SCOPE — this project)

These are defects in the AI instruction layer itself. Fixing them requires only changes to `.cursor/`, `AGENTS.md`, `CLAUDE.md`, skill files, and `docs/` — no theme code changes.

| # | Finding | Audit Ref |
|---|---------|-----------|
| T-01 | `naming-conventions.mdc` full content duplicated (line 5 and line 130) | [A-07] |
| T-02 | `schemas.mdc` instructs agents to use non-existent `schemas/` folder | [A-02] |
| T-03 | `schemas.mdc` instructs agents to run non-existent `npm run build:schemas` | [A-02] |
| T-04 | `locales.mdc` references `schemas/schema.d.ts` which does not exist | [B-locales.mdc] |
| T-05 | `localization.mdc` glob includes `schemas/*` which does not exist | [B-localization.mdc] |
| T-06 | `sections.mdc` code example has Liquid syntax error: `{% content_for 'blocks %}` | [A-08] |
| T-07 | `.cursor/rules/examples/section-example.liquid` has same syntax error (the source) | [B-examples] |
| T-08 | `snippets.mdc` has empty `description:` field | [A-09] |
| T-09 | `html-standards.mdc` has empty `description:` field | [A-09] |
| T-10 | `schemas.mdc` has empty `description:` field | [B-schemas.mdc] |
| T-11 | `javascript-standards.mdc` has no `globs:` key at all in frontmatter | [A-10] |
| T-12 | `css-standards.mdc` at 918 lines with no `globs:` — too large, no file-type trigger | [A-11] |
| T-13 | `javascript-standards.mdc` at 474 lines, description-activation only | [A-11] |
| T-14 | `fix-accesibility-issue.md` — filename typo (`accesibility`) | [A-17] |
| T-15 | `fix-accesibility-issue.md` references non-existent `fetch_rules` tool | [A-17] |
| T-16 | No AGENTS.md — zero cross-agent project context | [A-14] |
| T-17 | No CLAUDE.md — Claude Code / Anthropic ecosystem has no entry point | [A-14] |
| T-18 | No `.cursor/skills/` — no invokable Skill workflows | [A-14] |
| T-19 | No MCP config committed to repo | [A-15] |
| T-20 | Onboarding docs gaps (8 categories) | [C-§8] |

---

## 2. Rule Repairs

Repairs are in-place edits to existing `.mdc` files — no new rules are created in this step. All repairs must happen **before** the rule-vs-skill split so that the slim rules produced in §3 start from a clean baseline.

| ID | File | Repair | Source Finding |
|----|------|--------|---------------|
| R-01 | `naming-conventions.mdc` | Remove the duplicate block starting at line 130 (the second `# Architecture Standards` section is byte-for-byte identical to lines 1–129) | T-01 |
| R-02 | `schemas.mdc` | Remove all instructions referencing the `schemas/` folder. Replace with: *"Schemas are written inline in their section or block `.liquid` file inside a `{% schema %}` tag."* | T-02 |
| R-03 | `schemas.mdc` | Remove the `npm run build:schemas` instruction entirely | T-03 |
| R-04 | `schemas.mdc` | Add `description: "JSON schema standards for sections, blocks, and settings"` to frontmatter | T-10 |
| R-05 | `schemas.mdc` | Remove `schemas/*` from the `globs:` value; keep only `blocks/*.liquid,sections/*.liquid` | T-05 (shared path) |
| R-06 | `locales.mdc` | Remove the reference to `schemas/schema.d.ts`. Replace the sentence with: *"Refer to `locales/en.default.schema.json` for the current schema translation structure."* | T-04 |
| R-07 | `localization.mdc` | Remove `schemas/*` from the `globs:` value; keep only `*.liquid` | T-05 |
| R-08 | `sections.mdc` | Fix the code example: `{% content_for 'blocks %}` → `{% content_for 'blocks' %}` | T-06 |
| R-09 | `.cursor/rules/examples/section-example.liquid` | Same fix as R-08 (this is the source of the typo propagated to `sections.mdc`) | T-07 |
| R-10 | `snippets.mdc` | Add `description: "Snippet development standards including LiquidDoc, parameter defaults, and component patterns"` | T-08 |
| R-11 | `html-standards.mdc` | Add `description: "Modern semantic HTML standards for Shopify Liquid templates"` | T-09 |
| R-12 | `javascript-standards.mdc` | Add `globs: assets/*.js,sections/*.liquid,snippets/*.liquid` to frontmatter | T-11 |
| R-13 | `.cursor/prompts/fix-accesibility-issue.md` | Rename to `fix-accessibility-issue.md` (double 's') | T-14 |
| R-14 | `.cursor/prompts/fix-accessibility-issue.md` (post-rename) | Remove all `fetch_rules` references; replace with: *"Use the Read tool to load the relevant `.cursor/rules/*.mdc` or `.cursor/skills/accessibility-review/SKILL.md`"* | T-15 |

**What is not repaired here:** `css-standards.mdc` and `javascript-standards.mdc` are restructured in §3 rather than patched in place.

---

## 3. Rule-vs-Skill Split

### Principle

A **rule** is a constraint or standard that applies passively — the agent should always keep it in mind when editing the relevant file type. Rules work best when they are **concise, declarative, and glob-activated**.

A **skill** is a **procedural workflow** — a step-by-step recipe invoked intentionally for a specific task. Skills are where length is justified because the user is actively asking the agent to follow a process.

### Decision Table

| Rule file | Lines | Current state | Decision | Rationale |
|-----------|------:|--------------|----------|-----------|
| `rules-of-engagement.mdc` | 33 | Always-on | **Keep as-is** | Ideal size; pure constraints |
| `naming-conventions.mdc` | 253 → ~127 | Always-on | **Keep, remove duplicate** (R-01) | After dedup, ~127 lines is acceptable for always-on |
| `prompts-and-references.mdc` | 50 | Always-on | **Keep as-is** | Concise meta-instruction |
| `assets.mdc` | 12 | Glob-scoped | **Keep as-is** | Exemplary: short and targeted |
| `sections.mdc` | 83 | Glob-scoped | **Keep, fix typo** (R-08) | Appropriately sized |
| `snippets.mdc` | 132 | Glob-scoped | **Keep, add description** (R-10) | Good size; add description |
| `blocks.mdc` | 341 | Glob-scoped | **Keep as-is** | Long but justifiably complex topic |
| `html-standards.mdc` | 299 | Glob-scoped | **Keep, add description** (R-11) | Modern HTML reference; description fixes activation |
| `liquid.mdc` | 166 | Glob-scoped | **Keep as-is** | Appropriate size and scope |
| `locales.mdc` | 68 | Glob-scoped | **Keep, fix ref** (R-06) | Good size; one phantom ref to remove |
| `localization.mdc` | 67 | Glob-scoped | **Keep, fix glob** (R-07) | Good size; one phantom glob to remove |
| `schemas.mdc` | 137 | Glob-scoped | **Keep, remove phantom content** (R-02–R-05) | After repairs, becomes accurate and well-scoped |
| `templates.mdc` | 154 | Glob-scoped | **Keep as-is** | Contains useful JSON schema; well-scoped |
| `theme-settings.mdc` | 51 | Glob-scoped | **Keep as-is** | Ideal size |
| `css-standards.mdc` | 918 | Description-only | **Split**: slim rule + references file | 918 lines cannot reliably fit in context; the procedural/reference content belongs in a `references/` file |
| `javascript-standards.mdc` | 474 | Description-only | **Split**: slim rule + references file | Same rationale; globs fix makes it file-triggered but still too large |

### css-standards Split

**`css-standards.mdc`** (retained rule, target ~120 lines):
- Keep: Specificity rules, `!important` policy, ID selector ban, BEM naming summary (the "never do X" list), CSS custom property mandate, media query breakpoints table.
- Add: `globs: assets/*.css,sections/*.liquid,snippets/*.liquid,blocks/*.liquid`
- Add: `description: "CSS specificity, BEM naming, custom property, and selector standards"`

**`.cursor/references/css-reference.md`** (new reference file, the bulk):
- Move to here: Full BEM naming guide with examples, modern CSS features (container queries, cascade layers, view transitions, logical properties), performance patterns, property ordering, accessibility patterns, documentation/commenting standards, example component structure.
- This file is loaded on demand via the Read tool or linked from the slim rule.

### javascript-standards Split

**`javascript-standards.mdc`** (retained rule, target ~100 lines):
- Keep: Core principles (zero deps, `const` over `let`, `for...of`), the custom element structure requirement (connectedCallback/disconnectedCallback), the `customElements.get` guard requirement, async/await mandate, no `DOMContentLoaded`, no jQuery.
- Add: `globs: assets/*.js,sections/*.liquid,snippets/*.liquid` (already planned in R-12)
- Trim: Remove the detailed code examples for Intersection Observer, Shopify API integration, performance patterns — these move to the reference.

**`.cursor/references/javascript-reference.md`** (new reference file):
- Move to here: Full async/await patterns with code examples, request cancellation with AbortController, Intersection Observer patterns, error handling strategies, Shopify API integration examples, performance patterns, testing patterns.

### What Feeds Skills

The procedural workflows in the current rule set that are better expressed as invokable Skills (see §4):

| Current location | Content that becomes a Skill |
|-----------------|------------------------------|
| `sections.mdc` example + scaffold structure | `scaffold-section` skill |
| `snippets.mdc` example + parameter pattern | `scaffold-snippet` skill |
| `blocks.mdc` block creation workflow | `scaffold-block` skill |
| `.cursor/prompts/fix-accesibility-issue.md` | `accessibility-review` skill |
| _(new)_ Bucket 1 checklist | `pr-review` skill |

---

## 4. Skill Set v1

Skills live in `.cursor/skills/<skill-name>/SKILL.md`. Each skill is invoked by typing `/skill-name` in the Cursor chat. Skills should also be mirrored for Claude Code in `.claude/skills/<skill-name>/SKILL.md` or referenced from `AGENTS.md` (see §5).

---

### Skill 1: `scaffold-section`

**Purpose:** Generate a complete, standards-compliant new section from a description.

**Invocation:** `/scaffold-section <name> [description]`  
Example: `/scaffold-section testimonials "Displays customer testimonials in a grid"`

**Steps the skill instructs the agent to perform:**
1. Confirm section name is lowercase-hyphenated and does not use `main-` prefix.
2. Create `sections/<name>.liquid` using `section-example.liquid` as the structural template, with: `<section>` wrapper, `page-width` div, `{% style %}` block for padding vars, `{% schema %}` tag, schema keys using `t:` prefixes, and `{% stylesheet %}` or `stylesheet_tag` reference.
3. Create `assets/section-<name>.css` with BEM class structure scoped to the section.
4. If JS is needed (>100 lines of logic): create `assets/section-<name>.js` with the `customElements.define` guard pattern; load it in the Liquid file with `type="module"`.
5. Add the section to at least one demo template (e.g., `templates/page.<name>.json`).
6. Create `docs/sections/<name>.md` with the standard VitePress documentation structure (what it does, dependencies table, schema settings table, example usage).
7. Confirm no hardcoded English strings in schema labels — all use `t:` keys.
8. Confirm no hardcoded hex colors — all colors use `var(--color-*)` tokens.

**Traceability:** Addresses the onboarding gap [C-§8 item 8] and enforces Bucket 1 standards proactively on new work.

---

### Skill 2: `scaffold-block`

**Purpose:** Generate a complete, standards-compliant theme block.

**Invocation:** `/scaffold-block <name> [description]`  
Example: `/scaffold-block rich-text "Renders a rich text content block"`

**Steps:**
1. Create `blocks/<name>.liquid` using `block-example-group.liquid` as the structural template, with: `{% doc %}`, `{{ block.shopify_attributes }}`, `{% stylesheet %}` (not external file — blocks use deduplicated inline CSS), and `{% schema %}` with `t:` keys and `presets`.
2. Verify `{% content_for 'blocks' %}` is syntactically correct (closing quote present) — this is the known error point [T-06].
3. Schema must include at least one preset with a `name` key.
4. No `section-*` or `component-*` prefixing for block files — they live in `blocks/` flat.
5. Create `docs/assets/<name>.md` or equivalent docs entry.
6. Confirm schema uses `t:` keys, not raw English strings.

**Traceability:** Directly prevents the schema i18n drift found in [A-06]; enforces the `{% content_for %}` quote fix from [T-06].

---

### Skill 3: `scaffold-snippet`

**Purpose:** Generate a complete, standards-compliant component snippet.

**Invocation:** `/scaffold-snippet <name> [description]`  
Example: `/scaffold-snippet video-player "Renders a responsive video player with poster"`

**Steps:**
1. Create `snippets/component-<name>.liquid` with mandatory `{% doc %}` block including `@param` entries for every parameter, `@example` usage.
2. Add parameter validation block using `{% liquid %}` tag with `assign param = param | default: value` for every parameter; add early `break` guard for required parameters that are blank.
3. Create `assets/component-<name>.css` with BEM class structure.
4. If JS needed: create `assets/component-<name>.js` with `customElements.define` guard, `connectedCallback`, `disconnectedCallback`.
5. Load JS in the Liquid file with `type="module"` (not `defer`).
6. Create `docs/snippets/component-<name>.md` with standard VitePress structure.
7. Confirm no hardcoded hex colors; use `var(--color-*)` tokens.

**Traceability:** Addresses the 13 snippets missing LiquidDoc [A-18], enforces the `type="module"` requirement vs. the `defer` anomaly in `shop-by-category` [A-20], and applies the parameter validation standard from `snippets.mdc`.

---

### Skill 4: `pr-review`

**Purpose:** Run a standards checklist against any set of changed files in a PR before merge.

**Invocation:** `/pr-review` (run against current git diff, or against a named PR)

**Steps:**
1. Identify all changed files (Liquid, CSS, JS).
2. Run each check in the checklist below and emit a structured pass/fail report.
3. For any failure, cite the file, line number, and the specific standard violated.
4. Do not auto-fix — report only. The developer decides whether to fix before merge.

**Checklist — derived from Bucket 1 findings and existing standards:**

| # | Check | Standard | Bucket 1 Finding |
|---|-------|----------|-----------------|
| P-01 | No new `sections/` files with capital letters in name | `naming-conventions.mdc` | Faq.liquid anomaly |
| P-02 | No new `sections/` files with `main-` prefix | `naming-conventions.mdc` | Pre-existing rule |
| P-03 | All new/modified snippets have a `{% doc %}` block | `snippets.mdc` | 13 missing LiquidDoc |
| P-04 | All `<script src>` tags for section/component JS use `type="module"` not `defer` | `javascript-standards.mdc` | `shop-by-category` `defer` anomaly |
| P-05 | No new `customElements.define` without a `customElements.get` guard | `javascript-standards.mdc` | Pre-existing rule |
| P-06 | No ID selectors in new/modified CSS | `css-standards.mdc` | `cart.css` ID selectors |
| P-07 | No new `!important` declarations without an explanatory comment on the same line | `css-standards.mdc` | 41 undocumented `!important` |
| P-08 | No hardcoded hex color values in new/modified CSS or Liquid | `css-standards.mdc` | ~50 hardcoded hex values |
| P-09 | All schema labels in new/modified sections use `t:` key format | `schemas.mdc` / `localization.mdc` | i18n drift in multiple sections |
| P-10 | All user-facing strings in Liquid output pass through `\| t` | `localization.mdc` | `"Quantity"` hardcoded string |
| P-11 | If section uses Swiper, verify `theme.liquid` template whitelist covers the template where the section appears | `theme.liquid` pattern | Swiper conditional load gap |
| P-12 | No `DOMContentLoaded` event listeners in new JS | `rules-of-engagement.mdc` | Pre-existing rule |
| P-13 | No jQuery usage | `rules-of-engagement.mdc` | Pre-existing rule |
| P-14 | `theme.liquid` remains ≤ 300 lines | `rules-of-engagement.mdc` | Pre-existing rule |
| P-15 | New snippet parameters have default values assigned via `\| default:` | `snippets.mdc` | Parameter validation gap |

---

### Skill 5: `accessibility-review`

**Purpose:** Audit a component or section for WCAG 2.1 AA accessibility issues and produce a structured fix plan.

**Invocation:** `/accessibility-review <component-or-section-name>`  
Example: `/accessibility-review component-filters-sidebar`

**Converted from:** `.cursor/prompts/fix-accesibility-issue.md` (the orphaned prompt that referenced the non-existent `fetch_rules` tool) [T-14, T-15].

**Steps:**
1. Read the target `.liquid` file and its corresponding `.js` file (if any).
2. Check against these categories (replacing the `fetch_rules` calls from the original prompt with direct reads of the relevant rules):
   - **ARIA roles:** role must be on the element that directly contains the items; no role on wrapper divs above the semantic container.
   - **Keyboard navigation:** all interactive elements reachable by Tab; custom elements handle `keydown` for Enter/Space/Escape where appropriate.
   - **Focus management:** focus does not get lost on open/close of drawers, modals, dropdowns; use `focus()` or `inert` attribute.
   - **Screen reader text:** icon-only buttons must have `aria-label`; use `aria-labelledby` to reference existing visible text rather than duplicating with `aria-label`.
   - **Contrast:** flag any hardcoded colors that may fail 4.5:1 ratio; recommend `var(--color-*)` tokens instead.
   - **Motion:** verify CSS animations respect `prefers-reduced-motion`.
   - **Alpine.js components:** `x-data` components should have correct `aria-expanded`, `aria-controls`, `aria-selected` attributes reflecting Alpine state.
3. Output a structured issue list: issue description, current code snippet, recommended fix, WCAG criterion.
4. Do **not** auto-apply fixes — the developer reviews and approves.

**Key differences from original prompt:**
- Removes all `fetch_rules` tool calls.
- Removes references to `accordion-accessibility`, `carousel-accessibility`, etc. as separate fetch targets — the relevant patterns are read directly from the component file and the relevant `.mdc` rule.
- Adds Alpine.js-specific ARIA guidance (relevant given the 17 `x-data` declarations in this codebase).

---

## 5. Cross-Tool Layer

### The Problem

All current AI instruction lives in `.cursor/rules/` — readable only when a developer has Cursor IDE open and configured. Claude Code, Codex, Gemini CLI, or any other agent that opens this repo sees no project standards whatsoever. [A-14, C-§1]

### The Solution: One Source of Truth

```
AGENTS.md (root)              ← shared backbone, all agents read this
CLAUDE.md (root)              ← thin pointer for Claude-specific config
.cursor/rules/*.mdc           ← Cursor-specific glob-scoped bonus layer
.cursor/skills/<name>/SKILL.md  ← invokable by Cursor slash command
.claude/skills/<name>/SKILL.md  ← same content, Claude Code path
```

### AGENTS.md — Shared Backbone

`AGENTS.md` becomes the **single authoritative project context** for any AI agent. It must be concise enough to fit in the context of any model's system prompt.

**Proposed content outline:**

```
# Base Theme — Agent Context

## What This Is
Shopify theme (Online Store 2.0). Liquid + custom web components + Alpine.js 3.14 +
Liquid AJAX Cart 2.1.1 + Swiper 7.4.1. VitePress docs site in docs/.

## File Structure
sections/ — sections/*.liquid (no main- prefix)
snippets/ — snippets/component-*.liquid
assets/   — section-*.{css,js}, component-*.{css,js}
blocks/   — blocks/*.liquid (theme-level blocks)
.cursor/  — AI tooling (Cursor-specific)
docs/     — VitePress documentation site

## Core Standards (Mandatory for all agents)
1. Custom elements: all JS uses HTMLElement + connectedCallback/disconnectedCallback + customElements.get guard
2. Naming: sections use section- prefix for CSS/JS, snippets use component- prefix
3. CSS: BEM classes, var(--color-*) tokens, no ID selectors, no undocumented !important
4. Schemas: inline {% schema %} in each .liquid file; all labels use t: keys
5. Snippets: {% doc %} with @param entries required on all component- snippets
6. No DOMContentLoaded, no jQuery, no hardcoded hex colors

## Skills Available
/scaffold-section, /scaffold-block, /scaffold-snippet, /pr-review, /accessibility-review

## Key Libraries
- Alpine.js: declarative state (x-data, @event, $persist). Loaded globally.
- Liquid AJAX Cart: cart mutations via data-ajax-cart-* attributes and <ajax-cart-*> elements
- Swiper: loaded conditionally in theme.liquid; sections using Swiper must confirm template coverage

## Docs
VitePress site: docs/. Per-section and per-snippet markdown in docs/sections/ and docs/snippets/.
```

**Anti-drift principle:** `AGENTS.md` must not duplicate the full content of rules — it only states the non-negotiables. Rule files in `.cursor/` add depth. This keeps `AGENTS.md` short enough to be actually read.

### CLAUDE.md — Thin Claude Pointer

`CLAUDE.md` at the root should be 10–20 lines maximum:

```markdown
# Base Theme — Claude Configuration

See AGENTS.md for full project context and standards.

## Claude-Specific Notes
- Skills are in .claude/skills/ (same content as .cursor/skills/)
- When asked to scaffold a section, block, or snippet, follow AGENTS.md §Core Standards exactly
- Run /pr-review equivalent steps before suggesting any merge-ready code
- Do not introduce `schemas/` folder references — this folder does not exist in this project
```

The last bullet directly encodes the rule fix from T-02/T-03 so Claude Code doesn't regress even if it doesn't read `schemas.mdc`.

### Skills Across Tools

The five v1 Skills from §4 should exist in both locations:

```
.cursor/skills/
  scaffold-section/SKILL.md
  scaffold-block/SKILL.md
  scaffold-snippet/SKILL.md
  pr-review/SKILL.md
  accessibility-review/SKILL.md

.claude/skills/
  (same five SKILL.md files — identical content or symlinked)
```

Content is identical. The Skills system is Cursor's invocation mechanism; Claude Code's equivalent is instructed via `AGENTS.md` to treat these as named workflows.

### MCP Config

A `.cursor/mcp.json` (or root `mcp.json`) should be committed to document the MCP servers the team uses, even if individual credentials are not committed. [A-15]

Proposed structure:

```json
{
  "servers": {
    "shopify": {
      "description": "Shopify Dev MCP — Liquid, Storefront API, Admin API reference",
      "url": "see team docs for connection details"
    },
    "figma": {
      "description": "Figma MCP — design context and Code Connect",
      "url": "see team docs for connection details"
    }
  }
}
```

This ensures new developers know which MCP servers are expected and what they are for, without committing auth tokens.

---

## 6. Onboarding Docs to Add

Each file goes in `docs/` (alongside existing VitePress docs). All should be added to the VitePress sidebar config. [C-§8]

---

### `docs/architecture.md`

**Gap filled:** No system-level map of how sections, snippets, blocks, templates, and the layout relate to each other. New developers must discover this by reading code. [C-§8 items 6, 7]

**Scope:**
- Diagram/table of: `layout/theme.liquid` → `{% sections 'header-group' %}` → `sections/*.liquid` → `{% render 'component-*' %}` → `snippets/*.liquid`
- Explanation of Online Store 2.0 JSON templates and how `{% content_for 'blocks' %}` enables nested composition
- Explanation of theme blocks in `blocks/` vs. section blocks
- How `css-variables.liquid` generates the CSS custom property system
- How Liquid AJAX Cart integrates with sections and the cart drawer

---

### `docs/development-workflow.md`

**Gap filled:** No environment setup, Shopify CLI instructions, or local dev process. [C-§8 items 1, 2, 3, 9]

**Scope:**
- Prerequisites: Node version, Shopify CLI version, required accounts
- `shopify theme dev --store=<your-dev-store>` command and flags
- What `npm run dev` does in `docs/` vs. root (VitePress vs. theme — important distinction)
- How to install ESLint and Prettier (already in `package.json` but no documented workflow)
- Git branching strategy: `development` as the integration branch, `main` as release, feature branches
- How docs deployment works (pushes to `development` only) [C-§4]
- Note that `schemas/` does not exist — do not create it [T-02]

---

### `docs/design-system.md`

**Gap filled:** No CSS variable reference or design token catalogue. Developers must read `css-variables.liquid` directly. [C-§8 item 5]

**Scope:**
- Full table of all `--color-*` CSS custom properties and their semantic meaning
- How color schemes work (per-scheme variables emitted by `css-variables.liquid`)
- Typography variables (`--font-body-*`, `--font-heading-*`)
- Spacing and layout variables
- How to use `color-{{ section.settings.color_scheme }}` class on section wrappers
- BEM naming convention quick reference (summary; full reference in `references/css-reference.md`)

---

### `docs/javascript-patterns.md`

**Gap filled:** No decision framework for when to use Alpine.js vs. custom element vs. `data-ajax-cart-*`. [C-§8 item 4]

**Scope:**
- Decision tree: use Alpine when state is declarative and local to HTML; use a custom element when behavior is encapsulated and reusable; use `data-ajax-cart-*` attributes for cart mutations
- Custom element anatomy with annotated example (connectedCallback, disconnectedCallback, customElements.get guard)
- How Alpine.js communicates with custom elements via `window.dispatchEvent` (the cart-open pattern)
- How Liquid AJAX Cart events (`liquid-ajax-cart:request-end`) are consumed in JS
- Swiper initialization pattern and the template whitelist requirement
- `theme.js` utility functions available to import

---

### `docs/ai-tooling.md`

**Gap filled:** AI setup not documented for new team members. [C-§8 item 10, A-15]

**Scope:**
- How `.cursor/rules/` works: always-on vs. glob-scoped vs. description-activated
- List of all 16 rules with one-line descriptions of what each one does
- How to invoke Skills: `/scaffold-section`, `/scaffold-block`, `/scaffold-snippet`, `/pr-review`, `/accessibility-review`
- How `AGENTS.md` works and which other AI tools read it
- Which MCP servers the team uses and where to find connection details
- How to add a new rule vs. a new skill vs. updating `AGENTS.md`

---

### `docs/integrations.md`

**Gap filled:** No reference for the three third-party libraries' usage patterns within this specific codebase. README mentions them at a high level but gives no implementation guidance. [C-§5 (docs) + 01-code-patterns §4]

**Scope:**
- **Alpine.js 3.14**: which directives are used (`x-data`, `@event`, `x-show`, `x-transition`, `$persist`, `x-cloak`), the `x-cloak` + CSS pattern, the `$persist` filter state pattern
- **Liquid AJAX Cart 2.1.1**: which attributes are used and where (`data-ajax-cart-section`, `data-ajax-cart-bind`, `<ajax-cart-product-form>`, `<ajax-cart-quantity>`, `data-ajax-cart-errors`), the `liquid-ajax-cart:request-end` event, initial state bootstrap in `theme.liquid`
- **Swiper 7.4.1**: which modules are used, the template whitelist requirement and why it exists, how to add a new Swiper section (what to check in `theme.liquid`)

---

## 7. Deferred / Future Work

These items were identified in the audit but are deliberately not included in v1 of this project. Each entry explains why the idea is compelling, why it is deferred, and when to revisit.

---

### Cursor Hooks / Automation

**Why compelling:** Hooks can auto-run `/pr-review` on every agent session end, or trigger a docs update whenever a new section is created, removing the need to remember to invoke Skills manually.

**Why deferred:** Hooks are powerful but fragile — a misconfigured hook that fires too eagerly interrupts the development flow. The v1 Skills need to be stable and well-tested by humans before they are automated. Hooks also require team agreement on which events to hook.

**When to revisit:** After the five v1 Skills have been used in at least 10 real PRs and the team has validated that their output is consistently correct. At that point, a `post-session` hook that runs `/pr-review` automatically would add value without risk.

---

### Multi-Agent Subagents

**Why compelling:** A `best-of-n` pattern (running `scaffold-section` three times and picking the best output) would increase quality. A dedicated subagent that audits the docs site for stale content could maintain accuracy automatically.

**Why deferred:** Multi-agent orchestration has non-trivial cost (both token cost and cognitive cost to configure). The team should first establish what "good output" from a single agent looks like before optimizing with multiple agents. The Cursor subagent/Task tool is available but should be introduced deliberately.

**When to revisit:** After a stable v1 skill set is in production for 4–6 weeks. At that point, identify which skill produces the most inconsistent output — that is the first candidate for a best-of-n wrapper.

---

### Figma-to-Section Workflow

**Why compelling:** A Figma Code Connect workflow mapping Figma components to Liquid snippets would close the design-to-code gap [C-§3]. A `figma-to-section` skill could read a Figma frame and scaffold the Liquid, CSS, and JS from the design. This is already possible with the Figma MCP server.

**Why deferred:** Code Connect requires that Figma components and Liquid components have a stable, 1:1 mapping. The codebase currently has no Code Connect files at all. Before building the design-to-code skill, the team needs to: (a) establish which sections/snippets map to Figma components, (b) create at least a sample Code Connect config for 3–5 components, and (c) validate the mapping is accurate. Doing this without the foundational work produces hallucinated code that looks plausible but doesn't match the real design system.

**Teach before enforce:** The `design-system.md` onboarding doc (§6) must be written and accurate before Code Connect mapping can begin, because the doc itself is the source of truth that Code Connect consumes.

**When to revisit:** After `docs/design-system.md` is complete and the team has validated the CSS variable catalogue is accurate. At that point, start Code Connect with the 3–5 highest-usage snippets (`component-product-card`, `component-cart-drawer`, `component-nav-dropdown`, etc.).

---

### CI Linting & Theme Check

**Why compelling:** ESLint (`@shopify/eslint-plugin`) and Shopify Theme Check are already available as dev dependencies or CLI tools. Adding CI jobs would catch Bucket 1 code drift automatically before merge. [C-§4]

**Why deferred — teach before enforce:** Introducing CI checks that fail on existing violations (41 `!important`, 50 hardcoded hex values, etc.) would make every PR fail until the entire backlog is cleared. This creates a painful developer experience and risks the team disabling the checks entirely. The right sequence is:

1. Document the standards clearly (this project: rules + skills + AGENTS.md + onboarding docs).
2. Use the `pr-review` skill to surface violations as advisory warnings on new code.
3. Fix the Bucket 1 backlog incrementally over several sprints.
4. Once the backlog is below a manageable threshold, add CI checks as hard failures on new violations only (using `--diff` or changed-file scoping).

**When to revisit:** After Bucket 1 fixes are ≥ 80% complete, as a separate CI project. The GitHub Actions workflow (`deploy-docs.yml`) already demonstrates the team is comfortable with CI — expanding it is the natural next step.

---

## 8. Gap-Analysis: Before → After Metrics

This table skeleton documents the baseline state captured in the audit. After implementation, re-measure each metric and fill the "After" column to demonstrate improvement.

| Metric | Before (audit date 2026-06-05) | After (to be measured) | Target |
|--------|-------------------------------|----------------------|--------|
| `.mdc` rules with phantom references | 3 (`schemas.mdc`, `localization.mdc`, `locales.mdc`) | — | 0 |
| `.mdc` rules with missing `globs:` | 2 (`javascript-standards.mdc`, `css-standards.mdc`) | — | 0 |
| `.mdc` rules with empty `description:` | 3 (`snippets.mdc`, `html-standards.mdc`, `schemas.mdc`) | — | 0 |
| Largest rule file (lines) | 918 (`css-standards.mdc`) | — | < 150 |
| `naming-conventions.mdc` duplicated lines | ~120 | — | 0 |
| Syntax errors in instructional examples | 1 (`{% content_for 'blocks %}`) | — | 0 |
| Broken tool references in prompts | 1 (`fetch_rules` in accessibility prompt) | — | 0 |
| Skills defined | 0 | — | 5 |
| Cross-agent instruction files (`AGENTS.md`) | 0 | — | 1 |
| `CLAUDE.md` | 0 | — | 1 |
| MCP config committed | 0 | — | 1 |
| Onboarding docs (architecture, workflow, etc.) | 0 | — | 6 |
| CSS reference file in `.cursor/references/` | 0 | — | 1 |
| JS reference file in `.cursor/references/` | 0 | — | 1 |
| Total always-on context lines (rules) | ~336 (`rules-of-engagement` + `naming-conventions` + `prompts-and-references`) | — | < 220 (after naming-conventions dedup) |
| **Bucket 1 — code drift items (tracked separately)** | | | |
| Sections missing `t:` schema labels | ~8 sections | — | 0 |
| CSS ID selectors | 18+ (`cart.css`) | — | 0 |
| Undocumented `!important` | 41 | — | 0 |
| Hardcoded hex color values | ~50 | — | 0 |
| Snippets missing `{% doc %}` | 13 | — | 0 |
| `type="module"` anomalies in section scripts | 1 (`shop-by-category`) | — | 0 |

---

## Post-Writing Notes

### Summary of Sections

| Section | Key Output |
|---------|-----------|
| §1 Thesis & Scope | Bucket 1 (code drift, 11 items, separate backlog) vs. Bucket 2 (tooling rot, 20 items, this project) |
| §2 Rule Repairs | 14 targeted in-place edits to existing `.mdc` files and one example file |
| §3 Rule-vs-Skill Split | 14 rules stay; `css-standards` and `javascript-standards` each split into a slim rule + a `references/` file |
| §4 Skill Set v1 | 5 skills: `scaffold-section`, `scaffold-block`, `scaffold-snippet`, `pr-review` (15-item checklist), `accessibility-review` |
| §5 Cross-Tool Layer | `AGENTS.md` backbone + `CLAUDE.md` pointer + skills in both `.cursor/` and `.claude/` + MCP config |
| §6 Onboarding Docs | 6 new docs: `architecture.md`, `development-workflow.md`, `design-system.md`, `javascript-patterns.md`, `ai-tooling.md`, `integrations.md` |
| §7 Deferred | Hooks, subagents, Figma Code Connect, CI linting — each with teach-before-enforce rationale |
| §8 Metrics | 22-row before→after table skeleton covering both tooling and code quality |

### Audit Items This Plan May Have Underweighted

1. **`customer.js` non-custom-element pattern [A-12]:** The plan puts this in Bucket 1 (code drift, out of scope). However, it's worth noting that `customer.js` initializes via a class instantiation that isn't visible in the file — the initialization may happen via Shopify's `customer.js` auto-loading or via a `<script>` tag in a template. Before fixing this in the code backlog, the actual initialization mechanism should be confirmed rather than assumed broken.

2. **Dual CSS load on sections [A-19]:** The plan does not include this in either the rule repairs or the skill checklists. The dual load (`{% style %}` + `stylesheet_tag`) is intentional for dynamic padding variables, but the `pr-review` skill could optionally flag sections that use `{% style %}` for non-dynamic content (i.e., static CSS that should be in the external file). Worth adding as a low-priority check.

3. **`locales.mdc` multi-language assumption [B-locales.mdc]:** This is fixed in Bucket 2 (remove the `schemas/schema.d.ts` reference) but the rule's overall assumption of multi-language files (`es.json`, `fr.json`, `de.json`) is not explicitly corrected. The `development-workflow.md` doc should note the single-language state, and `locales.mdc` should be updated to not imply multiple language files exist when they don't.

4. **`README.md` "StarterTheme" branding artifact [C-§6]:** Left unaddressed — minor but worth a one-line fix when `development-workflow.md` is written (it would be updated in the same pass).

5. **`docs/OLD_README.md` in the docs directory [C-§5]:** The plan does not address this archived file. It should either be removed or moved outside of the VitePress source if it's not meant to be published.

6. **`deploy-docs.yml` gated to `development` only [A-16]:** The plan notes this in §7 (CI) as deferred, but it arguably belongs in the onboarding docs plan — `development-workflow.md` should clearly document which branch triggers docs deploy and what to do on feature branches (run `npm run dev` locally).
