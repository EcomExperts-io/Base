# CLAUDE.md

Guidance for Claude Code (and any AI coding tool) working in the Base Theme
repository, and in the client themes forked from it.

## What Base Theme is

Base is Moemen Hegazy's simplified take on Shopify's Dawn theme — Dawn debugged,
understood, and refactored down to a set of proven **code-organisation
conventions**. It is not a design system. Its value is that any page in any
client store built on it is structured predictably.

Base's current implementation is **not gospel**. The priority is building
consistently within its principles, not treating every line of existing code as
correct. Where Base contradicts the rules in `.claude/rules/`, the rules win —
they describe the standard, and some of Base's older code predates it. Do not
"fix" Base to match while working on an unrelated task: `/record-incident` it,
move on. (The standing count is `python3 .claude/scripts/report-compliance.py`;
the retrofit itself is an open ruling in the decisions log.)

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

`assets/` is flat — a Shopify constraint — so every filename must be unique
theme-wide. Hence the prefixes.

## Non-negotiables

These come up in almost every task. The detail is in `.claude/rules/`, and the
first three are checked by a hook the moment a file is written.

- **Every new section exposes `padding_top`, `padding_bottom`,
  `padding_top_mobile`, `padding_bottom_mobile` and `color_scheme`, plus a
  `presets` entry.** Padding has no exceptions, and mobile padding is its own
  setting, not `padding_top | times: 0.75`. Colour scheme may be hardcoded only
  with a Liquid comment saying why. This is the single most-missed rule in this
  codebase's history — see `rules/sections.md`.
- **Every string is a translation key** — visible text, schema labels,
  `aria-label`, `alt`. Including in brand-new files with no existing `| t`
  calls nearby. See `rules/localization.md`.
- **Mobile-first `min-width` queries, tokens not raw hex, no `DOMContentLoaded`,
  no jQuery, no `{% stylesheet %}` in a section, a `range` with at least three
  steps, no `t:` in a template value.** `check-conventions.py` reports these;
  in a new file they block.
- **Interactive JS is a custom element**, registered once behind
  `if (!customElements.get(...))`, initialising in `connectedCallback` and
  cleaning up in `disconnectedCallback`. A class on a custom-element tag needs
  an explicit `display`.
- **Native HTML first** — `<details>`, `<dialog>`, `popover` — over hand-rolled
  JS equivalents. Overlays get focus in and back, Escape, and a live region
  placed outside any region that is re-rendered.
- **Alpine for ephemeral UI state**; **custom elements for data fetching, URL
  sync, and cross-region DOM updates.** Don't mix both in one section.
- **Figma is design-only.** Values come from Shopify; absent values render
  nothing. Mark live values with `data-verify-mask` so the verifier ignores them.
- **No commented-out code.** `layout/theme.liquid` stays thin.

## Rules

Full conventions are one-topic-per-file in `.claude/rules/`, scoped by a
`paths` glob except the always-apply ones. **Read the relevant file before
writing non-trivial code in that area** — this summary is not a substitute.

Always applies: `rules-of-engagement.md`, `naming-conventions.md`.

Path-scoped: `sections.md`, `snippets.md`, `blocks.md`, `schemas.md`,
`liquid.md`, `html-standards.md`, `css-in-markup.md`, `css-standards.md`,
`javascript-standards.md`, `localization.md`, `locales.md`, `templates.md`,
`theme-settings.md`, `assets.md`, `living-documents.md`, `accessibility.md`.

`css-in-markup.md` (class naming, custom-property namespacing, settings passed
through a `style` attribute) is scoped to Liquid and CSS both; everything else
about CSS is `css-standards.md`, CSS only. `living-documents.md` says how the
documentation that guides the work — including this file — is kept true.

`.cursor/rules/*.mdc` is the Cursor-readable copy of the same content,
generated from `.claude/rules/` — as are `.cursor/skills`, `agents`,
`workflows`, `references` and `hooks`. **Edit `.claude/` only.** The pre-commit
hook regenerates the mirror and stages it; there is no command to remember.
The two copies existing by hand is what hid the conventions from Claude Code
for the first 18 days of a client build.

## What runs on its own

Configured in `.claude/settings.json`, so it travels with the tooling into
every fork:

- **SessionStart** injects doctor status, tooling drift from Base, the
  compliance number, open incidents and the three most-missed rules.
- **PostToolUse** on every theme-file write runs the settings contract, the
  conventions and JSON validity on that file and hands the findings back.
- **Stop** refuses to end a turn while a *new* theme file fails the contract, a
  convention, JSON validity or Theme Check, and flags section work with no
  verify report newer than the change. Modified legacy is reported, not gated.
- **PostToolUseFailure** on a Shopify command points at `/record-incident`.

The pre-commit (`.githooks/pre-commit`, called from husky in forks) and the
reusable CI workflow run the same checks. `python3 .claude/scripts/doctor.py`
says whether any of it is wired on this machine; `npm run setup` wires it.

## Skills, agents and workflows

- `.claude/skills/` — `build-page-from-figma`, `scaffold-section`,
  `figma-readiness`, `run-theme`, `verify-against-figma`, `record-incident`,
  `harvest`, `recon-theme`, `store-recon`, `close-qa-loop`,
  `accessibility-review`. Skills auto-invoke from their descriptions; `harvest`
  is human-only because it pushes to Base.
- `.claude/agents/` — `shopify-standards-coach` (advisory) and
  `shopify-pr-reviewer` (gates). Both keep project memory of what recurs.
- `.claude/workflows/` — `rebuild-playbook.md` (the dependency order for a
  whole store, and the three commands on arrival), `parallel-section-build.md`
  (one page, one agent per section), `multi-session-rebuild.md` (a storefront
  across sessions). Point an agent at the file; none is auto-loaded.
- `.claude/references/` — debugging accounts of traps that already cost hours.
  Rules stay short because these exist.
- `docs/base-theme-standards/` — the architecture references (Collection &
  PDP; Header, Cart Engine & Search), the compliance checklist, the decisions
  log, the vision. `docs/ai-workflow/` — the workflow, the first build, the
  designer checklist, and `incidents/`.

## Flowing changes between Base and the forks

No client fork shares git history with Base, and it does not need to.

- **Down:** `sh .claude/scripts/base-link.sh` attaches Base as a remote, a
  sibling worktree and a reference directory. `python3
  .claude/scripts/pull-base-tooling.py` overlays the tooling **three-way**
  against the `.base-version` stamp: Base's changes land where the fork never
  touched the file; the fork's edits — its measured breakpoints, its container,
  its decisions — are kept and listed. `check-tooling-drift.py` shows both
  directions at any time; SessionStart prints the one-line version.
- **Up:** `/record-incident` the moment a fix lands that a rule should have
  prevented. `/harvest` applies the CLAUDE.md test — *would this be true in a
  Shopify theme that is not this client's?* — edits the rule in the Base
  worktree, pushes to Base and opens the PR, then marks the incident.

| | Where it goes |
|---|---|
| A Liquid, Shopify or platform trap | **Base**, then forks pull it down |
| A convention we want every client to follow | **Base** |
| A measurement of *this* theme — breakpoints, container class, file counts | the client's rule copy only (`/recon-theme` writes them) |
| A client's design decision | the client's rule copy only |

**Move the paragraph, not the file.** Base says "grep `assets/` and match what
the theme settled on"; a fork says "769px, 14 files against 4". Generic
principle upstream, measured specifics downstream. New client repos start from
`new-client-theme.sh`, which keeps shared history and stamps the tooling.

## Two success criteria, kept separate

1. **Code style and architecture** — does it look like Base? Judged by the
   gate and the rules.
2. **Visual fidelity** — does it match the Figma frame? Judged by
   `/verify-against-figma`'s report on disk, never by an assertion.

A page can match a design pixel-for-pixel and still fail every convention in
this file. That is what happened on Bites Vitamins. Check them separately and
report them separately, with the evidence for each.

## Commands

```bash
npm run setup
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

There is no test suite — `npm test` is a stub. Verification is the gate, the
verifier's report, and the theme editor.
