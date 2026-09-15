---
title: A t: key copied into a template value rendered its own path to the customer
date: 2026-08-28
repo: BarePerformanceNutritionRebuild
scope: generic
surfaced_by: theme-500
should_have_caught: .claude/rules/templates.md
status: harvested
---

# A t: key copied into a template value rendered its own path to the customer

## What happened

Assembling a page template from section presets carried the presets' `t:`
label keys into `templates/*.json` values. Shopify resolves `t:` in a schema
`default`, not in a value stored in a template, so the storefront rendered the
literal key path where the heading should have been. A related trap on the
same build: a brand-new block type referenced by a template before Shopify had
registered it (about 25 seconds) returned 500 on every route.

## How it surfaced

On the storefront, by eye, after the template was pushed. Theme Check reports
neither.

## What fixed it

Stripping the values to plain strings; waiting between pushing a section and
pushing the template that references its new block. `check-conventions.py`
now flags any `"t:` value in a template file, and `templates.md` carries both
traps.

## Which rule or check should have caught it, and why it did not

`templates.md` described the JSON shape and nothing about how values resolve.
Its own examples used Dawn's `main-*` section names, contradicting the naming
rule in the one file an agent reads while assembling a template. Both are
fixed; the mechanical half is a grep.
