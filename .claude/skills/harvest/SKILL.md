---
name: harvest
description: Send a generic learning from this client repo up to Base as a pull request — a rule paragraph, a reference, a check — from inside the client session, using the Base worktree. Use when asked to harvest, upstream, or flow an incident or rule edit back to Base.
disable-model-invocation: true
argument-hint: <incident-file | rule-file | "what was learned">
---

# harvest

Move the paragraph, not the file. A client repo shares no history with Base,
so this skill edits the Base worktree `base-link.sh` created, commits there,
pushes to Base's URL, opens the PR and marks the incident harvested.
Human-invoked: it pushes to a shared repository.

## Step 1 — Decide what goes up

Read the incident (or the rule edit `check-tooling-drift.py` listed) and apply
the CLAUDE.md test: **would this be true in a theme that is not this client's?**

| | Goes to Base as |
|---|---|
| A Liquid, Shopify or platform trap | a paragraph in the matching `.claude/rules/*.md`, incident-first |
| A CSS or browser behaviour that had to be measured | `.claude/references/<topic>-pitfalls.md`, new or extended |
| A gap a script could close | the check itself, in `.claude/scripts/`, plus its line in the pre-commit and the reusable workflow |
| A convention every client should follow | the matching rule |
| A client measurement — breakpoints, container, file counts — or a client design decision | **nothing**. Mark the incident `client-only` and stop. |

Strip the client's numbers: Base says "grep `assets/` and match what the
theme settled on"; only the fork says "769px".

## Step 2 — Start the branch

```bash
sh .claude/scripts/harvest.sh start <slug>
```

Prints `WORKTREE=…` and `BRANCH=harvest/<slug>`, from the current
`base/development`; refuses if the worktree has uncommitted work.

## Step 3 — Edit in the worktree, not here

Make the change under `WORKTREE`, in the target rule's voice: what to do,
then the consequence. A check goes in `check-conventions.py` (or the relevant
script), wired, tested against Base's tree, with a fixture in
`.claude/scripts/test-checks.py`. Regenerate the mirror there:

```bash
sh <WORKTREE>/.claude/scripts/sync-ai-config.sh
```

Commit in the worktree in the repo's message style (`[FIX]:` or
`[FEATURE]:`). The body describes the mechanism generically and **never
names the client** — not in a rule, a docstring, a commit or a branch. Base's
pre-commit runs on that commit.

## Step 4 — Push and open the pull request

Write the PR body to a file (what went wrong, generically; what changes in
Base; how verified; the generated-by line), then:

```bash
sh .claude/scripts/harvest.sh open <slug> "<title>" <body-file>
```

It runs `check-ai-config.py` in the worktree, pushes to Base's URL explicitly
(the `base` remote has pushing disabled), opens the PR with `gh`, prints `PR_URL=…`.

## Step 5 — Close the incident here

```bash
python3 .claude/scripts/new-incident.py --set-status docs/ai-workflow/incidents/<file>.md harvested --pr <PR_URL>
```

Commit that in this repo; the drift check stops listing the item once Base
merges and the tooling is pulled down. Never copy a whole rule file up — the
fork's copy carries measured specifics — and never edit `.cursor/`.
