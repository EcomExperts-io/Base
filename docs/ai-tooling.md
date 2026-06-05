# AI Tooling

How the AI-assist layer in this repo is set up, what each piece does, and how to extend it. This
covers Cursor rules, the invokable skills, the cross-agent backbone (`AGENTS.md`/`CLAUDE.md`), and
the committed MCP config.

---

## How `.cursor/rules/` works

Rules are Markdown files (`.mdc`) with YAML frontmatter that controls **when** they load:

- **Always-on** (`alwaysApply: true`): injected into every request. Keep these short.
- **Glob-scoped** (`globs: <patterns>`): auto-attached when a matching file is in context (e.g.
  `assets/*.css`).
- **Description-activated** (`description: …`, no/empty globs): the agent pulls it in when the
  description matches the task.

A rule can combine a `description` and `globs`. The two reference files in `.cursor/references/`
(`css-reference.md`, `javascript-reference.md`) are **not** rules — they're long-form docs the slim
CSS/JS rules link to, loaded on demand with the Read tool.

---

## The 16 rules

| Rule | Activation | What it covers |
|------|-----------|----------------|
| `rules-of-enagagment.mdc` | Always-on | Theme-wide engagement rules: custom elements over `DOMContentLoaded`, no jQuery, `theme.liquid` ≤ ~300 lines, formatting/hygiene |
| `naming-conventions.mdc` | Always-on | Section/snippet/asset naming (`section-`/`component-` prefixes, no `main-` prefix) |
| `prompts-and-references.mdc` | Always-on | Meta-rule: keep `.cursor/prompts` & `.cursor/references` as living docs |
| `assets.mdc` | `assets/*` | Assets dir is flat; how to reference assets / inline icons |
| `blocks.mdc` | `blocks/*.liquid` | Theme block standards: schema, presets, `shopify_attributes`, inline CSS |
| `css-standards.mdc` | `assets/*.css`, `sections/*.liquid`, `snippets/*.liquid`, `blocks/*.liquid` | CSS specificity, BEM, custom-property mandate, selector rules (long-form in `css-reference.md`) |
| `html-standards.mdc` | `*.liquid` | Modern semantic HTML, native elements, accessibility, ID naming |
| `javascript-standards.mdc` | `assets/*.js`, `sections/*.liquid`, `snippets/*.liquid` | Custom-element pattern, async/await, no jQuery/`DOMContentLoaded` (examples in `javascript-reference.md`) |
| `liquid.mdc` | `*.liquid` | Liquid syntax standards |
| `locales.mdc` | `locales/*.json` | Locale file structure (English-only reality), key organization |
| `localization.mdc` | `*.liquid` | Translation filter usage; all user-facing text through `\| t` |
| `schemas.mdc` | `blocks/*.liquid`, `sections/*.liquid` | Inline `{% schema %}` JSON standards (no `schemas/` folder) |
| `sections.mdc` | `sections/*.liquid` | Section structure, schema, `{% content_for 'blocks' %}` |
| `snippets.mdc` | `snippets/*.liquid` | LiquidDoc `{% doc %}`, parameter defaults, component patterns |
| `templates.mdc` | `templates/*.json` | Online Store 2.0 JSON template structure |
| `theme-settings.mdc` | `config/settings_schema.json` | Organizing the theme settings schema |

---

## Skills (invokable workflows)

Skills are procedural recipes in `.cursor/skills/<name>/SKILL.md`, invoked in Cursor with a slash
command. They are mirrored byte-for-byte in `.claude/skills/<name>/SKILL.md` for Claude Code.

| Skill | Invoke | Purpose |
|-------|--------|---------|
| `/scaffold-section` | `/scaffold-section <name> [desc]` | Generate a standards-compliant section + CSS/JS + docs |
| `/scaffold-block` | `/scaffold-block <name> [desc]` | Generate a standards-compliant theme block |
| `/scaffold-snippet` | `/scaffold-snippet <name> [desc]` | Generate a `component-` snippet with `{% doc %}` |
| `/pr-review` | `/pr-review` | Run the 15-item standards checklist against a diff (report only) |
| `/accessibility-review` | `/accessibility-review <component>` | WCAG 2.1 AA audit + structured fix plan (report only) |

`/pr-review` and `/accessibility-review` are **report-only** — they never auto-fix.

There is also a legacy prompt at `.cursor/prompts/fix-accessibility-issue.md`; prefer
`/accessibility-review`, which supersedes it.

---

## Cross-agent backbone: `AGENTS.md` & `CLAUDE.md`

- **`AGENTS.md`** (repo root) is the single source of truth any AI agent reads — Cursor, Claude
  Code, Codex, Gemini CLI, etc. It states the non-negotiable standards and points to the deeper
  layers; it deliberately does **not** duplicate full rule bodies.
- **`CLAUDE.md`** (repo root) is a thin pointer to `AGENTS.md` plus Claude-specific notes (skills
  live in `.claude/skills/`, and the "no `schemas/` folder" guard).

The `.cursor/rules/*.mdc` files are a Cursor-specific bonus layer on top of `AGENTS.md`.

---

## MCP servers

The committed MCP config is `.cursor/mcp.json`. It contains no auth tokens or secrets.

| Server | Command | Purpose |
|--------|---------|---------|
| `shopify-dev-mcp` | `npx -y @shopify/dev-mcp@latest` | Shopify dev docs/API reference (Liquid, Storefront/Admin) |

The server is launched on demand via `npx`, so no manual install is required. If your team uses
additional MCP servers (e.g. Figma) with credentials, those connection details are **not** committed
— **confirm with the team** where to find them.

---

## Extending the tooling: rule vs. skill vs. `AGENTS.md`

- **Add a rule** when you have a *passive constraint* that should apply automatically while editing
  a file type. Create `.cursor/rules/<name>.mdc` with a `description` and `globs`. Keep it concise;
  put long-form examples in a `.cursor/references/*.md` file and link to it.
- **Add a skill** when you have a *procedural workflow* a developer invokes intentionally. Create
  `.cursor/skills/<name>/SKILL.md` **and** mirror it to `.claude/skills/<name>/SKILL.md` (keep them
  identical).
- **Update `AGENTS.md`** only when a *non-negotiable* changes that every agent must know. Add the
  detail to the relevant rule/skill; add only a one-line pointer/standard to `AGENTS.md` so it stays
  short.
