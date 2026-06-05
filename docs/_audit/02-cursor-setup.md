# Cursor Setup Audit (Section B)

> Read-only audit of `.cursor/` on branch `feature/ai-dev-standards-upgrade`.  
> No files were modified.

---

## 1. Rules Overview (`/.cursor/rules/`)

16 `.mdc` files total.

### Classification Table

| File | Lines | alwaysApply | globs | Description field | Classification |
|------|------:|------------|-------|-------------------|----------------|
| `rules-of-engagement.mdc` | 33 | **true** | _(none)_ | _(none)_ | Always-on / global |
| `naming-conventions.mdc` | 253 | **true** | _(none)_ | _(none)_ | Always-on / global |
| `prompts-and-references.mdc` | 50 | **true** | `(empty)` | `(empty)` | Always-on / global |
| `assets.mdc` | 12 | false | `assets/*` | present | Glob-scoped |
| `blocks.mdc` | 341 | false | `blocks/*.liquid` | present | Glob-scoped |
| `html-standards.mdc` | 299 | false | `*.liquid` | **empty** | Glob-scoped (description-blind) |
| `liquid.mdc` | 166 | false | `*.liquid` | present | Glob-scoped |
| `locales.mdc` | 68 | false | `locales/*.json` | present | Glob-scoped |
| `localization.mdc` | 67 | false | `*.liquid,schemas/*` | present | Glob-scoped |
| `sections.mdc` | 83 | false | `sections/*.liquid` | present | Glob-scoped |
| `snippets.mdc` | 132 | false | `snippets/*.liquid` | **empty** | Glob-scoped (description-blind) |
| `templates.mdc` | 154 | false | `templates/*.json` | _(none)_ | Glob-scoped |
| `theme-settings.mdc` | 51 | false | `config/settings_schema.json` | present | Glob-scoped |
| `schemas.mdc` | 137 | false | `blocks/*.liquid,sections/*.liquid,schemas/*` | **empty** | Glob-scoped (partial phantom glob) |
| `css-standards.mdc` | 918 | false | `(empty)` | present | **Description-only / over-length** |
| `javascript-standards.mdc` | 474 | false | _(none)_ | present | **Description-only (no globs key at all)** |

### Always-On Rules (3 files, ~336 lines total in context)

These are injected into every agent conversation regardless of which file is open.

**`rules-of-engagement.mdc`** (33 lines)
- No `main-` prefix, use custom elements, no jQuery, no `DOMContentLoaded`, consistent indentation, no commented-out code.
- Concise and actionable. Low noise.

**`naming-conventions.mdc`** (253 lines)
- Section naming, JS/CSS file naming, snippet `component-` prefix, custom element structure examples.
- **Full content is duplicated** — `# Architecture Standards` heading and all content appears at line 5 and again at line 130. The second copy is byte-for-byte identical. Adds ~120 lines of redundant context on every request.

**`prompts-and-references.mdc`** (50 lines)
- Explains the living-documents philosophy; instructs agents to update `.cursor/prompts/` and `.cursor/references/` proactively.
- `description:` and `globs:` are both empty despite `alwaysApply: true` — fields are present but blank (harmless since `alwaysApply` overrides).

### Glob-Scoped Rules

Activated when the agent opens a file matching the glob pattern.

**`assets.mdc`** (12 lines)  
Very lightweight; explains flat `assets/` directory and `asset_url`/`inline_asset_content` filter usage. Appropriate size for a context hint.

**`blocks.mdc`** (341 lines)  
Comprehensive coverage of theme block fundamentals, static vs. dynamic blocks, schema configuration, `{% stylesheet %}` usage, and CSS scoping. Long but structured; references inline examples via `mdc:` links. Appropriate for a complex topic.

**`html-standards.mdc`** (299 lines)  
Covers modern HTML features: `<details>`/`<summary>`, native lazy loading, `<dialog>`, `loading="eager"`, `fetchpriority`, etc.  
**Issue:** `description:` is empty. If a user asks about HTML patterns without opening a `.liquid` file, this rule won't surface via description search. Glob `*.liquid` will catch it in most real workflows.

**`liquid.mdc`** (166 lines)  
Liquid syntax standards — tag reference, filter conventions, `{% liquid %}` multi-line tag, performance patterns.  
Glob `*.liquid` is broad (same as `html-standards.mdc`); both rules fire together on any `.liquid` file open.

**`locales.mdc`** (68 lines)  
Translation key organization, naming conventions, plural forms, schema translations.  
**Issue:** References `schemas/schema.d.ts` at line 68: *"Use the rules outlined in our typescript schema (schemas/schema.d.ts)…"* — that file does not exist in the repo.

**`localization.mdc`** (67 lines)  
Translation filter usage (`| t`), hardcoded string checks, RTL considerations.  
**Issue:** Glob includes `schemas/*` which doesn't exist; Cursor will silently ignore the non-matching path but it signals stale content.

**`schemas.mdc`** (137 lines)  
JSON schema structure, required fields, block schemas, presets, localization keys.  
**Issue:** Instructs agents to *"write our schemas in the schemas folder and then run `npm run build:schemas`"* — neither the folder nor the npm script exist. This will cause incorrect AI behavior if followed literally.  
**Issue:** `description:` is empty.

**`sections.mdc`** (83 lines)  
Section requirements, basic structure pattern, performance hints, link to example file.  
**Issue:** Code example contains `{% content_for 'blocks %}` — missing the closing quote (`'`). This is a Liquid syntax error in the instructional example.

**`snippets.mdc`** (132 lines)  
LiquidDoc requirements, parameter defaults, common patterns (icon snippet, price snippet), testing comment patterns.  
**Issue:** `description:` is empty.

**`templates.mdc`** (154 lines)  
JSON template schema, section order, required fields. Contains a full JSON schema definition for validation. Appropriately scoped to `templates/*.json`.

**`theme-settings.mdc`** (51 lines)  
Settings schema structure and examples. Well-scoped to `config/settings_schema.json`.

### Description-Only / Over-Length Rules

**`css-standards.mdc`** (918 lines)  
Activated by description match ("Writing CSS…") only — no `globs:` value. At 918 lines, this is the largest rule in the set. Covers:
- Specificity rules, CSS variables (global, scoped, namespaced, semantic, design tokens)
- BEM naming (full reference with good/bad examples)
- Modern CSS (container queries, cascade layers, view transitions, nesting, logical properties)
- Media queries and breakpoints
- Performance, accessibility, documentation, property ordering

The breadth and depth are valuable but the file is too large to reliably fit in context alongside other rules and the actual code being edited. No mechanism splits or prioritizes sections.

**`javascript-standards.mdc`** (474 lines)  
`alwaysApply: false`, no `globs:` key in frontmatter at all (not even an empty one). Activated by description match only. Covers async/await, request management, Intersection Observer, event handling, Web Component patterns, error handling, Shopify API integration, performance, testing. At 474 lines, it is also large but more manageable than `css-standards.mdc`.

---

## 2. Prompts (`/.cursor/prompts/`)

One file: **`fix-accesibility-issue.md`**

- **Filename typo:** `accesibility` (missing a second 's'). Affects discoverability when prompted with correct spelling.
- Content: A full accessibility issue workflow — references component-specific rules by name (e.g., `accordion-accessibility`, `carousel-accessibility`), instructs use of a `fetch_rules` tool.
- **`fetch_rules` tool** is not a standard Cursor tool. This appears to be a reference to a toolset from a different agent framework (possibly a custom MCP or another AI coding tool). The file as written would not function as intended in standard Cursor.
- Otherwise the content covers: ARIA role placement, screen reader testing, focus management, performance considerations — high quality but non-operational in current setup.

The prompt named `vitepress-docs.md` referenced in `.cursor/prompts/` **does not exist** — it lives in `.cursor/references/` instead.

---

## 3. References (`/.cursor/references/`)

One file: **`vitepress-docs.md`**

Content: Vue/Liquid mustache collision avoidance in VitePress docs pages.
- Documents the "blank page" cause: Liquid `{{ }}` mustaches in raw markdown text are evaluated by Vue's template engine.
- Escape pattern: `\{\{ section.id \}\}` inside prose; use fenced code blocks for examples.
- Also documents a pitfall: inline `<script>` tags in sections that run unconditionally (querying DOM outside a section render guard).

Accurate and useful for documentation contributors. Appropriately scoped.

---

## 4. Examples (`/.cursor/rules/examples/`)

Four example Liquid files:

| File | Purpose |
|------|---------|
| `section-example.liquid` | Full section scaffold with `{% stylesheet %}`, inline CSS, `{% schema %}` |
| `snippet-example.liquid` | Full snippet scaffold with `{% doc %}`, parameter defaults, early return |
| `block-example-group.liquid` | Group block with `{% content_for 'blocks' %}` |
| `block-example-text.liquid` | Simple text block |

Examples are referenced by `sections.mdc` and `snippets.mdc` via `mdc:` links. They appear to be accurate references for the expected patterns.

**One discrepancy:** `section-example.liquid` uses `{% content_for 'blocks %}` (missing closing quote — same typo as in `sections.mdc`). This suggests the example file is the source of the rule's typo.

---

## 5. Rule Contradictions and Gaps

| Issue | Files Involved |
|-------|---------------|
| `schemas/` folder referenced but doesn't exist | `schemas.mdc`, `localization.mdc`, `locales.mdc` |
| `npm run build:schemas` referenced but script doesn't exist in `package.json` | `schemas.mdc` |
| `schemas/schema.d.ts` TypeScript file referenced but doesn't exist | `locales.mdc` |
| `{% content_for 'blocks %}` syntax error in example | `sections.mdc`, `examples/section-example.liquid` |
| Full content duplicated in `naming-conventions.mdc` | `naming-conventions.mdc` |
| `description:` empty on rules that need description-activation | `snippets.mdc`, `html-standards.mdc`, `schemas.mdc` |
| No `globs:` key in frontmatter | `javascript-standards.mdc` |
| `fetch_rules` tool reference for non-existent tool | `.cursor/prompts/fix-accesibility-issue.md` |
| Prompt filename typo | `fix-accesibility-issue.md` |
| `vitepress-docs.md` in `references/` not `prompts/` (not a bug, but mislabeled in prompt readme) | `prompts-and-references.mdc` says "prompts/ and references/ folders" |
