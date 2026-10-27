# CLAUDE.md

Guidance for Claude Code (and any AI coding tool) working in the Base Theme
repository, and in the client themes forked from it.

## What Base Theme is

Base is Moemen Hegazy's simplified take on Shopify's Dawn theme: Dawn
refactored down to a set of **code-organisation conventions**, not a design
system, so that any page in any client store built on it is structured predictably.

Where Base's own code contradicts `.claude/rules/`, the rules win; some older
code predates them. Do not "fix" Base while working on an unrelated task:
`/record-incident` it and move on. (`python3 .claude/scripts/report-compliance.py`
is the standing count; the retrofit is an open item in `docs/base-theme-standards.md`.)

## Stack

Liquid + vanilla CSS/JS. Online Store 2.0, Shopify CLI 3.0. No bundler, no
framework, no build step for assets. The only third-party runtime libraries are
**Alpine.js** (light UI state) and **Swiper** (carousels), both loaded from
`layout/theme.liquid`. The cart is a native engine, `assets/cart.js`.

Most UI is a same-named triad:

```
sections/[name].liquid  +  assets/section-[name].css  +  assets/section-[name].js
snippets/component-[name].liquid  +  assets/component-[name].{css,js}
```

`assets/` is flat, so every filename must be unique theme-wide.

## Non-negotiables

The detail is in `.claude/rules/`; the first three are checked by a hook the
moment a file is written.

- **Every new section exposes `padding_top`, `padding_bottom`,
  `padding_top_mobile`, `padding_bottom_mobile` and `color_scheme`, plus a
  `presets` entry** (`sections.md`). Padding has no exceptions; colour scheme
  may be hardcoded only with a Liquid comment saying why.
- **Every string is a translation key** — visible text, schema labels,
  `aria-label`, `alt`, in brand-new files too (`localization.md`).
- **Mobile-first `min-width` queries, tokens not raw hex, no `DOMContentLoaded`,
  no jQuery, no `{% stylesheet %}` in a section, a `range` with at least three
  steps, no `t:` in a template value.** `check-conventions.py` reports these;
  in a new file they block.
- **Interactive JS is a custom element**, registered once behind
  `if (!customElements.get(...))`. A class on a custom-element tag needs an
  explicit `display`.
- **Native HTML first** — `<details>`, `<dialog>`, `popover` — over hand-rolled
  JS equivalents. Overlays get focus in and back, Escape, and a live region
  placed outside any region that is re-rendered.
- **Alpine for ephemeral UI state**; **custom elements for data fetching, URL
  sync, and cross-region DOM updates.** Don't mix both in one section.
- **Figma is design-only.** Values come from Shopify; absent values render
  nothing. Mark live values with `data-verify-mask` so the verifier ignores them.
- **Live is a reference for behaviour, copy and data, never for code.** A
  section that matches live and carries live's markup has failed the
  migration. The brief names the reference — Figma, live or both — per band.
- **No commented-out code.** `layout/theme.liquid` stays thin.

## Rules

One topic per file in `.claude/rules/`, scoped by a `paths` glob except the
always-apply ones. **Read the relevant file before writing non-trivial code in
that area.**

Always applies: `rules-of-engagement.md`, `naming-conventions.md`,
`code-review-policy.md`, `storefront-infrastructure.md`.

Path-scoped: `sections.md`, `snippets.md`, `blocks.md`, `schemas.md`,
`liquid.md`, `html-standards.md`, `css-in-markup.md`, `css-standards.md`,
`javascript-standards.md`, `localization.md`, `locales.md`, `templates.md`,
`theme-settings.md`, `assets.md`, `living-documents.md`, `accessibility.md`.

`css-in-markup.md` is the CSS decided in markup (class names, custom
properties on a `style` attribute), scoped to Liquid and CSS; the rest of CSS
is `css-standards.md`, CSS only.

`.cursor/` and the Codex copies (`.agents/skills`, `.codex/`, `AGENTS.md`)
are generated from `.claude/`. **Edit `.claude/` only**; the pre-commit hook
regenerates and stages the mirrors.

## What runs on its own

Configured in `.claude/settings.json`, so it travels into every fork:

- **SessionStart** injects doctor status, tooling drift from Base, the
  compliance number, open incidents, the three most-missed rules, and which
  situation the repo looks like — fresh rebuild, joining midway, correcting
  after QA (`where-are-we.py`).
- **PostToolUse** on every theme-file write runs the settings contract, the
  conventions and JSON validity on that file and hands the findings back.
- **Stop** refuses to end a turn while a *new* theme file fails the contract, a
  convention, JSON validity or Theme Check, and flags section work with no
  verify report newer than the change. Modified legacy is reported, not gated.
- **PostToolUseFailure** on a Shopify command points at `/record-incident`.
- **PostToolUse** on a `git push` in a client repo points at
  `/gitbot-preflight`; the Stop hook says, once per turn, when a client
  branch's GitBot findings have not been read since its last commit.

The pre-commit (`.githooks/pre-commit`, via husky in forks) and the reusable
CI workflow run the same checks plus `test-checks.py`, one fixture per promise
a gate script makes. `python3 .claude/scripts/doctor.py` says whether it is
wired on this machine; `npm run setup` wires it (`sh .claude/scripts/setup.sh`
for a fork whose `package.json` has no `setup` script).

## Skills, agents and workflows

- `.claude/skills/` — `build-page-from-figma`, `build-section-from-live`,
  `scaffold-section`, `figma-readiness`, `run-theme`, `verify-against-reference`,
  `record-incident`, `harvest`, `recon-theme`, `store-recon`, `close-qa-loop`,
  `accessibility-review`, `gitbot-preflight`. Skills auto-invoke from their
  descriptions; `harvest` is human-only because it pushes to Base.
- `.claude/agents/` — `shopify-pr-reviewer`, the local review before a PR; it
  reads the verify report and the running theme, which GitBot cannot.
- `.claude/workflows/` — `rebuild-playbook.md` (the dependency order for a
  whole store, and the three commands on arrival), `parallel-section-build.md`
  (one page, one agent per section), `multi-session-rebuild.md` (a storefront
  across sessions), `landing-batch.md` (a card of landing pages matched to
  live, with its three agent briefs). Point an agent at the file; none is auto-loaded.
- `.claude/references/` — symptom, cause and fix for traps too situational for
  a rule.
- `docs/base-theme-standards.md` — the collection and PDP pattern, the shell,
  cart engine and search, the rulings, and the open items.
  `docs/ai-workflow/` — the workflow, the Figma handoff, and `incidents/`.

## Flowing changes between Base and the forks

No client fork shares git history with Base, and it does not need to.

- **Down:** `sh .claude/scripts/base-link.sh` attaches Base as a remote, a
  sibling worktree and a reference directory. `python3
  .claude/scripts/pull-base-tooling.py` overlays the tooling three-way
  against the `.base-version` stamp: Base's changes land where the fork never
  touched the file; the fork's edits are kept and listed.
  `check-tooling-drift.py` shows both directions.
- **Up:** `/record-incident` the moment a fix lands that a rule should have
  prevented. `/harvest` asks *would this be true in a Shopify theme that is
  not this client's?*, edits the rule in the Base worktree, pushes to Base and
  opens the PR, then marks the incident.

| | Where it goes |
|---|---|
| A Liquid, Shopify or platform trap | **Base**, then forks pull it down |
| A convention we want every client to follow | **Base** |
| A measurement of *this* theme — breakpoints, container class, file counts | the client's rule copy only (`/recon-theme` writes them) |
| A client's design decision | the client's rule copy only |

**Move the paragraph, not the file.** Generic principle upstream, measured
specifics downstream. New client repos start from `new-client-theme.sh`.

## Two success criteria, kept separate

1. **Code style and architecture** — does it look like Base? Judged by the
   gate and the rules.
2. **Visual fidelity** — does it match the Figma frame? Judged by
   `/verify-against-reference`'s report on disk, never by an assertion.

A page can match a design pixel-for-pixel and still fail every convention.
Check and report them separately, with the evidence for each.

## Commands

```bash
npm run setup   # or: sh .claude/scripts/setup.sh — identical, for a fork without the script
```

```bash
python3 .claude/scripts/doctor.py
```

```bash
shopify theme dev --store <store-handle>
```

```bash
shopify theme check --config=.theme-check.yml
```

```bash
python3 .claude/scripts/report-compliance.py
```

```bash
python3 .claude/scripts/check-conventions.py --all
```

```bash
npx prettier --config .prettierrc.json --write path/to/file.liquid
```

Name the files. Never pass a glob to `--write`: the theme is not uniformly
formatted, so a glob reformats untouched files into the commit.

There is no test suite — `npm test` is a stub. Verification is the gate, the
verifier's report, and the theme editor.