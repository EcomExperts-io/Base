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
"fix" Base to match while working on an unrelated task: document it, bank it,
move on.

## Stack

Liquid + vanilla CSS/JS. Online Store 2.0, Shopify CLI 3.0. No bundler, no
framework, no build step for assets. The only third-party runtime libraries are
**Alpine.js** (light UI state) and **Swiper** (carousels), both loaded from
`layout/theme.liquid`.

Most UI is a same-named triad:

```
sections/[name].liquid  +  assets/section-[name].css  +  assets/section-[name].js
snippets/component-[name].liquid  +  assets/component-[name].{css,js}
```

`assets/` is flat — a Shopify constraint — so every filename must be unique
theme-wide. Hence the prefixes.

## Non-negotiables

These come up in almost every task. The detail is in `.claude/rules/`.

- **Every new section exposes `padding_top`, `padding_bottom`, and
  `color_scheme`, plus a `presets` entry.** Padding has no exceptions. Colour
  scheme may be hardcoded only with a Liquid comment saying why. This is the
  single most-missed rule in this codebase's history — see `rules/sections.md`
  for what happened and why a Figma-driven build tends to skip it.
- **Every string is a translation key** — visible text, schema labels,
  `aria-label`, `alt`. Including in brand-new files with no existing `| t`
  calls nearby. See `rules/localization.md`.
- **Interactive JS is a custom element**, registered once behind
  `if (!customElements.get(...))`, initialising in `connectedCallback` and
  cleaning up in `disconnectedCallback`. No `DOMContentLoaded`. No jQuery, ever.
- **Native HTML first** — `<details>`, `<dialog>`, `popover` — over hand-rolled
  JS equivalents.
- **Alpine for ephemeral UI state** (drawer open, accordion expand). **Custom
  elements for data fetching, URL sync, and cross-region DOM updates.** Don't
  mix both in one section.
- **Load section CSS with `stylesheet_tag`** and section JS as
  `type="module"` — matching the theme, not older scaffolding examples.
- **No commented-out code.** Delete it or re-enable it.
- `layout/theme.liquid` stays thin — it delegates to snippets and sections.

## Rules

Full conventions are one-topic-per-file in `.claude/rules/`. Each is scoped by a
`paths` glob except the always-apply ones. **Read the relevant file before
writing non-trivial code in that area** — this summary is not a substitute.

Always applies: `rules-of-engagement.md`, `naming-conventions.md`.

Path-scoped: `sections.md`, `snippets.md`, `blocks.md`, `schemas.md`,
`liquid.md`, `html-standards.md`, `css-in-markup.md`, `css-standards.md`,
`javascript-standards.md`, `localization.md`, `locales.md`, `templates.md`,
`theme-settings.md`, `assets.md`, `living-documents.md`.

Two notes on scope, because both were wrong until recently:

- **`css-in-markup.md` vs `css-standards.md`.** Class naming, custom-property
  namespacing and passing settings in via a `style` attribute are decisions you
  make in the markup, so `css-in-markup.md` is scoped to `**/*.liquid` and
  `**/*.css` both. Everything else about CSS is scoped to `**/*.css` alone.
  Before the split, editing one snippet injected 2,444 lines of rules, 919 of
  them CSS authoring guidance that a Liquid file cannot act on.
- **`living-documents.md`** was `prompts-and-references`: always-apply, and
  entirely about two `.cursor/` directories that hold one file each here and do
  not exist in a client fork.

`.cursor/rules/*.mdc` is the Cursor-readable copy of the same content, generated
from `.claude/rules/`. **Edit `.claude/rules/` only**, then run:

```bash
sh .claude/scripts/sync-ai-config.sh
```

The two copies existing by hand is what caused this project's worst failure —
the conventions sat in `.cursor/rules/` where Claude Code could not read them
for the first 18 days of a client build. The script makes drift impossible.

## Skills, agents and workflows

- `.claude/skills/` — invoked procedures: building a page from a Figma frame,
  scaffolding a section, closing the QA loop, accessibility review.
- `.claude/agents/` — review passes with their own context:
  `shopify-standards-coach` (advisory, teaches) and `shopify-pr-reviewer`
  (gates, decides whether something is safe to merge).
- `.claude/workflows/` — multi-agent procedures a human starts deliberately.
  `parallel-section-build.md` builds a whole page by giving each section to its
  own agent, and carries the assembly and verification steps that make that
  safe. Point an agent at the file; it is not auto-loaded.

Skills only run when invoked. Conventions that must hold unprompted live in
`.claude/rules/`, not in a skill.

## Flowing changes back to Base

Base is the upstream every client theme is forked from, and until recently
**nothing had ever flowed back up**. That is not because the forks learned
nothing — it is because there was no written answer to "where does this go?",
so everything stayed where it was found.

The inheritance is working where it has been used: 14 of the 16 rules are
byte-identical between Base and the BPN fork, and the two that differ —
`sections.md` and `snippets.md` — differ *correctly*. Base says "grep `assets/`
and match whatever that theme settled on"; BPN says "769px, 14 files against
4". Generic principle upstream, measured specifics downstream. Keep that shape.

**The test:** would this be true in a Shopify theme that is not this client's?

| | Where it goes |
|---|---|
| A Liquid, Shopify or platform trap | **Base**, then forks pull it down |
| A convention we want every client to follow | **Base** |
| A measurement of *this* theme — breakpoints, container class, file counts | the client's rule copy only |
| A client's design decision | the client's rule copy only |

**How:** branch off `development` here, make the change generic — strip the
client's numbers, keep the incident — open the PR, and pull it down to the
client once merged. The four traps added in this change came from the BPN
Quick-Shop build and are the worked example: the bug was found there, the rule
lives here.

**What not to do:** copy a whole rule file up. The divergences above are load
bearing. Move the paragraph, not the file.

## Two success criteria, kept separate

A page built from a design is judged on two independent axes. Passing one says
nothing about the other:

1. **Code style and architecture** — does it look like Base? Governed by the
   rules here.
2. **Visual fidelity** — does it match the Figma frame?

A page can match a design pixel-for-pixel and still fail every convention in
this file. That is exactly what happened on Bites Vitamins. Check them
separately and report them separately.

## Commands

```bash
shopify theme dev --store <store-handle>
```

```bash
shopify theme check --config=.theme-check.yml
```

```bash
npx eslint --config .eslintrc.js path/to/file.js
```

```bash
npx prettier --config .prettierrc.json --write path/to/file.liquid
```

There is no test suite — `npm test` is a stub. Verification is manual, via the
dev server and the theme editor.
