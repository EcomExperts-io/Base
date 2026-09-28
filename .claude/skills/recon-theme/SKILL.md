---
name: recon-theme
description: Measure a theme before building in it — lineage against Base, the conventions actually in use, compliance, which pages exist and which are left, tooling state — and write the state-of-the-theme document plus the fork's measured rule values. Use when arriving on a client repo for the first time, resuming a rebuild another team started, or when asked what was done previously, what conventions to follow, or what is left.
---

# recon-theme

Read the repo before writing to it. Arriving on a rebuild — new or someone
else's — the store depends on what was built first and what can be carried, so
the first act is measurement, not code.

**Why this exists.** The downstream rule copies are supposed to carry the
numbers a client theme settled on ("769px, 14 files against 4") so that agents
build to the theme in front of them rather than to Base's generic text. That was
done by hand, once, for one fork. Meanwhile a developer landing on Furbish found
no rules at all, and one landing on BPN found rules that had drifted from Base
with no record of which edits were deliberate. The recon makes the measurement
a script and the judgment a checklist.

**Invocation:** `/recon-theme` — in the client repo, after
`sh .claude/scripts/base-link.sh` (so lineage can be measured) and
`python3 .claude/scripts/pull-base-tooling.py` (so the scripts exist).

## Step 1 — Measure

```bash
python3 .claude/scripts/recon-theme.py
```

Writes `state-of-the-theme.md` under `docs/ai-workflow/`: lineage against Base per
directory (unchanged / modified / deleted / new), the majority breakpoint and
every other one in use, container classes by frequency, px vs rem, the
LiquidDoc form, custom elements defined and used-but-undefined, how sections
load CSS, the compliance tally with the non-compliant sections split into
"this build's" and "Base's legacy", templates and page templates, sections no
template references, and the tooling state including drift.

Read the whole file. Every later step refers to it.

## Step 2 — Look at what the numbers cannot see

Open the ten most-modified or newest sections and three snippets and answer,
in the "What the numbers cannot see" section of the document:

- **Design system in use.** Are values tokens (`var(--…)`) or raw? Which token
  file — Base's `css-variables.liquid`, or something the build added? Any
  second token layer (a `tokens.css`, a Tailwind-ish utility set)?
- **What was generalised.** Which Base components were widened (a
  `component-*` with new data attributes or custom properties), and were they
  renamed when their scope widened? A `section-*` file loaded by several
  sections is the smell the naming rule names.
- **What the previous team wrote down.** Their rule edits (the drift report
  lists them), their references, their decisions log, their frame map. Treat
  a doc an AI wrote during a build as a claim, not a ruling, until it is
  checked against the code — the Bites `shared-page-sections.md` was a post-hoc
  rationalisation.
- **Half-built pages.** Templates with no admin page, sections in no template,
  frames in the map with nothing built. This is the "what is left" list.
- **Three decisions** to make before the next section: the breakpoint to build
  new work at, the container class to use, and whether to keep or retire any
  convention that contradicts the rules (say which way, and why).

## Step 3 — Record the measured conventions where agents read them

The fork's rule copies are where the numbers live — Base stays generic. Edit
**this repo's** `.claude/rules/sections.md` (the breakpoint note under the
padding boilerplate) and `snippets.md`, following the pattern Base's own
`sections.md` uses to say "measure, don't copy": state the measured value, the
count behind it, and the date. If a rule was already edited by the previous
team and the numbers still hold, leave it; if they no longer hold, update and
say so in the state document.

Do not edit anything under `.cursor/`; run `sh .claude/scripts/sync-ai-config.sh`.

## Step 4 — Say what can be carried

End the state document with a short verdict, in this order:

1. **Carry as-is** — stages of the dependency order that are done and sound
   (tokens, chrome, shared components — see `rebuild-playbook.md`).
2. **Carry with fixes** — built but failing the contract or the conventions;
   list the sections and the fix class.
3. **Rebuild** — what is not worth keeping, and why, in one line each.
4. **Missing** — the frames or pages with nothing behind them, in the order the
   playbook would build them.

Commit the state document and the rule edits together. The next session's
SessionStart hook will print the drift and compliance lines from the same
measurements, so the document does not need to be re-read to know whether the
numbers moved.

## Notes

- Read-only apart from the state document and the rule copies. Do not fix
  what the recon finds in this pass; record it and, where a rule should have
  prevented it, `/record-incident`.
- Without a Base checkout the lineage section is skipped and the document
  says so. Run `base-link.sh` first; it needs no shared history.
- `/store-recon` answers the other half — what the store has — and its output
  belongs in the same document under "Pages and templates".
