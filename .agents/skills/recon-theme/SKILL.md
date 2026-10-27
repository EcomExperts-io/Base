---
name: recon-theme
description: Measure a theme before building in it — lineage against Base, the conventions actually in use, compliance, which pages exist and which are left, tooling state — and write the state-of-the-theme document plus the fork's measured rule values. Use when arriving on a client repo for the first time, resuming a rebuild another team started, or when asked what was done previously, what conventions to follow, or what is left.
argument-hint: [--live-url <storefront-url>]
---

# recon-theme

Read the repo before writing to it: the measurement is a script, the
judgment a checklist, and the numbers land in the fork's rule copies.

**Invocation:** `/recon-theme` — in the client repo, after
`sh .claude/scripts/base-link.sh` (so lineage can be measured) and
`python3 .claude/scripts/pull-base-tooling.py` (so the scripts exist).

## Step 1 — Measure

```bash
python3 .claude/scripts/recon-theme.py
```

With the published storefront's URL, so the live feature inventory is in the
document from day one:

```bash
python3 .claude/scripts/recon-theme.py --live-url https://www.<store>
```

Writes `state-of-the-theme.md` under `docs/ai-workflow/`: lineage against Base
per directory, breakpoints in use, container classes by frequency, px vs rem,
the LiquidDoc form, custom elements defined and used-but-undefined, how
sections load CSS, the compliance tally split into "this build's" and "Base's
legacy", templates, sections no template references, tooling and drift. Read it whole.

## Step 2 — Look at what the numbers cannot see

Open the ten most-modified or newest sections and three snippets and answer,
in the "What the numbers cannot see" section of the document:

- **Design system in use.** Tokens (`var(--…)`) or raw values? Base's
  `css-variables.liquid` or a second layer the build added?
- **What was generalised.** Which Base components were widened, and were they
  renamed when their scope widened? A `section-*` file loaded by several
  sections is the smell the naming rule names.
- **What the previous team wrote down.** Their rule edits (the drift report
  lists them), references, decisions log, frame map. A doc an AI wrote during
  a build is a claim until checked against the code.
- **Half-built pages.** Templates with no admin page, sections in no template,
  frames in the map with nothing built — the "what is left" list.
- **Three decisions** before the next section: the breakpoint to build at,
  the container class, and whether to keep or retire any convention that
  contradicts the rules (which way, and why).

## Step 2½ — Read the live inventory as things the theme must not fight

For each line of the "Live site inventory" section, decide and write down:

- **An app that acts on the theme** (subscriptions, reviews, upsells): which
  sections it injects into or owns, and whether the rebuilt section drives it,
  switches it off or leaves it.
- **A popup or chat** paints over every capture; `live-parity.py` hides the
  known ones. An unknown one is added to its overlay list, not masked by hand.
- **Markets**: the list to verify in, logged in and out.
- **A page builder** owns template names until admin is changed; its pages
  are migrations of HTML, not sections to restyle (`build-section-from-live` §3).
- **Tracking** stays the platform's (`storefront-infrastructure.md`).

Then write the reference map — `docs/ai-workflow/reference-map.md`, one row
per band: which reference (Figma, live or both), the Figma node ids with
exact sizes, the live URL and section key, and whether it is in scope.

## Step 3 — Record the measured conventions where agents read them

Edit **this repo's** `.claude/rules/sections.md` (the breakpoint note under
the padding boilerplate) and `snippets.md`, following the pattern Base's own
`sections.md` uses: the measured value, the count behind it, the date. A
previous team's edit whose numbers still hold stays; one that no longer holds
is updated and noted in the state document. Base stays generic.

Do not edit `.cursor/`; run `sh .claude/scripts/sync-ai-config.sh`.

## Step 4 — Say what can be carried

End the state document with a verdict, in this order:

1. **Carry as-is** — stages of the dependency order that are done and sound
   (tokens, chrome, shared components — `rebuild-playbook.md`).
2. **Carry with fixes** — built but failing the contract or the conventions;
   the sections and the fix class.
3. **Rebuild** — what is not worth keeping, one line each.
4. **Missing** — frames or pages with nothing behind them, in playbook order.

Commit the state document and the rule edits together. SessionStart prints
the drift and compliance lines from the same measurements.

## Notes

- Read-only apart from the state document and the rule copies. Record what
  the recon finds; `/record-incident` where a rule should have prevented it.
- Without a Base checkout the lineage section is skipped and the document
  says so; `base-link.sh` needs no shared history.
- `/store-recon` fills "Pages and templates" in the same document.
