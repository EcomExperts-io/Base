---
name: harvest
description: Send a generic learning from this client repo up to Base as a pull request — a rule paragraph, a reference, a check — from inside the client session, using the Base worktree. Use when asked to harvest, upstream, or flow an incident or rule edit back to Base.
disable-model-invocation: true
---

# harvest

Move the paragraph, not the file. Open the Base PR from here.

**Why this exists.** For the whole of v1 nothing flowed back to Base during a
build. The rule for what belonged upstream existed; the mechanics did not — a
client repo shares no history with Base, so there was no branch to cherry-pick
onto, and "open a PR to Base" meant a separate afternoon. The worktree that
`base-link.sh` creates is a real Base checkout beside this repo; this skill
edits it, commits there, pushes to Base's URL and opens the PR, then marks the
incident harvested. Human-invoked on purpose: it pushes to a shared repository.

**Invocation:** `/harvest <incident-file | rule-file | "what was learned">`

## Step 1 — Decide what goes up

Read the incident (or the local rule edit `check-tooling-drift.py` listed) and
apply the CLAUDE.md test: **would this be true in a Shopify theme that is not
this client's?**

| | Goes to Base as |
|---|---|
| A Liquid, Shopify or platform trap | a paragraph in the matching `.claude/rules/*.md`, incident-first |
| A CSS or browser behaviour that had to be measured | `.claude/references/<topic>-pitfalls.md`, new or extended |
| A gap a script could close | the check itself, in `.claude/scripts/`, plus its line in the pre-commit and the reusable workflow |
| A convention every client should follow | the matching rule |
| A client measurement — breakpoints, container, file counts — or a client design decision | **nothing**. Mark the incident `client-only` and stop. |

Strip the client's numbers; keep the incident. Base says "grep `assets/` and
match what the theme settled on"; the fork says "769px, 14 files against 4".
Generic principle upstream, measured specifics downstream.

## Step 2 — Start the branch

```bash
sh .claude/scripts/harvest.sh start <slug>
```

Prints `WORKTREE=…` and `BRANCH=harvest/<client>-<slug>`, checked out from the
current `base/development`. It refuses if the worktree has uncommitted work.

## Step 3 — Edit in the worktree, not here

Make the change under `WORKTREE`. Read the target rule first and match its
voice: what to do, then the incident that earned it, in a few lines. If the
learning is a check, add it to `check-conventions.py` (or the relevant script),
wire it, and test it against Base's own tree. Regenerate the mirror there:

```bash
sh <WORKTREE>/.claude/scripts/sync-ai-config.sh
```

Commit in the worktree with the repo's message style (`[FIX]:` or
`[FEATURE]:`), naming the client incident in the body. Base's pre-commit runs
on that commit — a harvest that fails Base's own gate is not ready.

## Step 4 — Push and open the pull request

Write the PR body to a file (what happened on the client build, what changes in
Base, how it was verified; end with the generated-by line the repo uses), then:

```bash
sh .claude/scripts/harvest.sh open <slug> "<title>" <body-file>
```

It runs `check-ai-config.py` inside the worktree, pushes to Base's URL
explicitly (the `base` remote has pushing disabled), and opens the PR with
`gh`. It prints `PR_URL=…`.

## Step 5 — Close the incident here

```bash
python3 .claude/scripts/new-incident.py --set-status docs/ai-workflow/incidents/<file>.md harvested --pr <PR_URL>
```

Commit that in this repo. The drift check stops listing the item once Base
merges and this repo pulls the tooling down.

## What not to do

- Do not copy a whole rule file up. The fork's copies carry measured specifics
  that must not land in Base.
- Do not edit `.cursor/` anywhere — it is generated.
- Do not push to `base` as a remote. The script pushes to the URL for a reason.
- Do not harvest a client design decision because it felt like a rule.
