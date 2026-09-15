---
title: "A range setting with two steps passed Theme Check and failed the theme upload"
date: 2026-08-28
repo: BarePerformanceNutritionRebuild
scope: generic
surfaced_by: theme-500
should_have_caught: .claude/rules/schemas.md
status: harvested
---

# A range setting with two steps passed Theme Check and failed the theme upload

## What happened

A section schema declared a `range` whose `(max - min) / step` was 2. Theme
Check accepted it; the theme upload rejected the whole theme, and every route
returned 500 — not just the page with the section.

## How it surfaced

Every route 500ing after a push, traced back by removing settings one at a
time.

## What fixed it

Widening the range to at least three steps. `check-conventions.py` computes
`(max - min) / step` for every `range` in a section or block schema and blocks
a new file below 3; the parallel-build agent brief names the trap.

## Which rule or check should have caught it, and why it did not

`schemas.md` had no minimum for range steps because nobody had hit it. Theme
Check does not validate it either. The check is arithmetic on values the schema
already contains, which is exactly what a grep-level gate is for.
