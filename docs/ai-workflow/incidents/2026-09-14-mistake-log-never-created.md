---
title: The mistake log the workflow asked for existed in zero client repos
date: 2026-09-14
repo: Base
scope: generic
surfaced_by: review
should_have_caught: .claude/skills/build-page-from-figma/SKILL.md
status: harvested
---

# The mistake log the workflow asked for existed in zero client repos

## What happened

Step 7 of the build skill specified a mistake log: in the client repo,
excluded from version control, created only when the AI offered and a human
agreed. Four client builds later — Bites, BPN, MiLB, Furbish — no such file
existed anywhere, while every incident that mattered had become a Base rule by
a different route: one person reading the code weeks later.

## How it surfaced

`find` across the client repos for anything named like a mistake log. The
workflow README even listed "nothing aggregates the mistake logs" as a known
gap; there was nothing to aggregate.

## What fixed it

`/record-incident` and `new-incident.py`: a committed, structured file with a
`scope`, a `should_have_caught` path and a `status`, created by one command at
the moment of failure. `doctor.py` counts the open ones every session and
`/harvest` moves generic ones to Base.

## Which rule or check should have caught it, and why it did not

The skill itself. Three design choices each guaranteed zero entries: gitignored
(invisible in review), created only on offer-and-consent (never created), and
written at the end of the build (when the details were gone). A mechanism that
depends on someone remembering is a habit, not a mechanism.
