# Forward-Looking Inventory (Section C)

> Read-only audit of the `feature/ai-dev-standards-upgrade` branch.  
> This section documents what is present and what is absent.

---

## 1. Agent / AI Config Files

### Skills

| Location | Status |
|----------|--------|
| `.cursor/skills/` | **Does not exist** |
| `.claude/skills/` | **Does not exist** |

No Cursor Skills are defined in this repository. The Cursor Skills system allows packaging reusable agent workflows (SKILL.md files) that can be invoked by slash commands (e.g., `/fix-accessibility`). The current `fix-accesibility-issue.md` in `.cursor/prompts/` is a prompt file, not a Skill — it cannot be invoked as a slash command.

### AGENTS.md

| Location | Status |
|----------|--------|
| `AGENTS.md` (root) | **Does not exist** |

`AGENTS.md` is the cross-agent instruction standard supported by Codex, Claude Code, Gemini CLI, and other non-IDE agents. Its absence means AI agents outside of Cursor IDE have no project-level instructions, conventions, or context to work from.

### CLAUDE.md

| Location | Status |
|----------|--------|
| `CLAUDE.md` (root) | **Does not exist** |
| `.claude/` (folder) | **Does not exist** |

Claude-specific agent configuration is absent. The Anthropic agent ecosystem (Claude Code, etc.) would operate without project awareness.

---

## 2. MCP (Model Context Protocol) Configuration

| Location | Status |
|----------|--------|
| `.cursor/mcp.json` | **Does not exist** |
| `mcp.json` (root) | **Does not exist** |
| `.mcp.json` (root) | **Does not exist** |

No MCP server configuration is committed to the repository. Any MCP connections (e.g., Shopify Dev MCP, Figma MCP) exist only in individual developer's local Cursor settings and are not shared across the team via the repo.

---

## 3. Figma / Code Connect

| Asset | Status |
|-------|--------|
| `.figma/` folder | **Does not exist** |
| `*.figma.ts` files | **Does not exist** |
| `*.figma.js` files | **Does not exist** |

No Figma Code Connect mapping exists. Design-to-code traceability (mapping Figma components to their Liquid/JS counterparts) is absent.

---

## 4. `.github/workflows/`

One workflow file exists:

### `deploy-docs.yml`

```yaml
on:
  push:
    branches: [development]
    paths:
      - 'docs/**'
```

| Property | Value |
|----------|-------|
| Trigger | Push to `development` branch, only when `docs/**` changes |
| Build | `cd docs && npm ci && npm run build` (VitePress) |
| Deploy | GitHub Pages via `actions/deploy-pages@v4` |
| Artifact | `docs/.vitepress/dist` |

**Observations:**
- Deploys only from `development` branch. Changes on `main`, feature branches (including `feature/ai-dev-standards-upgrade`), or PRs do not trigger the docs build.
- No preview deployment on PRs.
- No Liquid linting (no Shopify Theme Check CI job).
- No JavaScript linting (ESLint is installed as a dev dependency in root `package.json` but no lint script or CI job exists).
- No Shopify CLI theme push/deploy workflow.
- No test runner.

---

## 5. `docs/` — VitePress Documentation Site

### Structure

```
docs/
├── index.md                  # Home page with hero + feature cards
├── package.json              # VitePress dev dependency
├── package-lock.json
├── OLD_README.md             # Archived readme
├── public/                   # Static assets for VitePress
├── assets/                   # Component asset documentation
│   ├── component-*.md        # 17 component asset files
│   └── section-*.md + theme.md, customer.md etc.
├── sections/                 # Per-section documentation
│   └── *.md                  # ~50 section markdown files
└── snippets/                 # Per-snippet documentation
    └── component-*.md + others
```

### Coverage

The docs site has near-1:1 coverage of sections and snippets — each section and component snippet has a corresponding `.md` file with:
- What the section/component does
- Dependencies (CSS, JS)
- Schema settings table or parameter table
- Code examples

**Quality is high** on well-used components (product card, cart drawer, product section). Some docs files appear auto-generated or thin (minimal prose beyond parameter table).

### What's Missing from Docs

| Missing Content | Impact |
|----------------|--------|
| Contributor setup guide (local dev prerequisites, Shopify CLI version, `shopify theme dev` instructions) | New developers have no onboarding path |
| Environment setup (`.env` needs, store URL, dev store credentials structure) | Requires tribal knowledge |
| Architecture overview (how sections, blocks, snippets, and templates relate) | No system-level map for new contributors |
| Third-party library usage guide (when/how to use Alpine vs. custom element vs. Liquid AJAX Cart) | Decision framework absent |
| CSS variable reference / design token catalogue | Developers must read `css-variables.liquid` directly |
| Git branching strategy / PR process | No contribution workflow documented |
| Deployment guide | No steps for pushing to Shopify store |
| `.cursor/` AI tooling guide | AI setup not documented for new team members |

---

## 6. Root-Level Files

| File | Status | Notes |
|------|--------|-------|
| `README.md` | Present | Good developer overview; references live demo and docs URL; mentions third-party libraries. Contains "StarterTheme" branding in intro paragraph (likely a copy-paste artifact from a template). |
| `CONTRIBUTING.md` | Present | Generic GitHub contribution guide (issue reporting, PR labels, code review). Does not cover Shopify theme development specifics. |
| `CODE_OF_CONDUCT.md` | Present | Standard Contributor Covenant. |
| `LICENSE.md` | Present | MIT license. |
| `.prettierrc.json` | Present | Prettier config (likely includes `@shopify/prettier-plugin-liquid`). |
| `.shopifyignore` | Present | Standard ignore file. |
| `package.json` | Present | Dev dependencies: `@shopify/eslint-plugin`, `@shopify/prettier-plugin-liquid`, `eslint`, `prettier`. No `build:schemas` script, no `lint` script. |
| `.shopify/metafields.json` | Present | Metafield definitions. |
| `AGENTS.md` | **Absent** | |
| `CLAUDE.md` | **Absent** | |
| `.cursor/mcp.json` | **Absent** | |

---

## 7. Branch Context

This audit is on `feature/ai-dev-standards-upgrade`. The primary branch appears to be `development` (docs deploy target) with `main` implied. The current branch contains no commits visible beyond the baseline — it appears to be at the starting point for planned AI tooling improvements.

---

## 8. Onboarding Content Gap Summary

A new developer joining this project today would need to discover the following through tribal knowledge or direct code reading:

1. Which Shopify CLI version to use.
2. How to connect to a development store (`shopify theme dev --store=…`).
3. Which npm scripts to run and when (`npm run dev` does not exist; docs have their own `npm run dev`).
4. When to use Alpine.js vs. a custom element vs. `data-ajax-cart-*` attributes.
5. The color scheme / CSS variable system and how to use `--color-foreground` etc.
6. How the `{% sections 'header-group' %}` / `{% sections 'footer-group' %}` section group mechanism works.
7. What `blocks/group.liquid` and `blocks/text.liquid` are and how to compose them.
8. How to add a new section end-to-end (Liquid + schema + CSS + JS + docs entry).
9. That `schemas/` does not exist despite being referenced in the rules.
10. How to set up `.cursor/` rules in their local IDE (not documented).
