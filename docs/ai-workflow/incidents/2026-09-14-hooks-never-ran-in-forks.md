---
title: Base's pre-commit hook had never run on a client machine
date: 2026-09-14
repo: Base
scope: generic
surfaced_by: review
should_have_caught: .claude/scripts/doctor.py
status: harvested
---

# Base's pre-commit hook had never run on a client machine

## What happened

Base wires its gate through `core.hooksPath = .githooks`. All four client forks
run husky, with `core.hooksPath = .husky`, so the file Base ships was present
in every fork and executed in none. The section contract, the mirror check and
Theme Check ran only in Base itself, and in one fork's CI.

## How it surfaced

An audit ran `git config core.hooksPath` in each fork. Every developer had
committed for months under a gate that did not exist for them, and every
commit looked normal.

## What fixed it

`setup.sh` detects `.husky/` and appends a call to `.githooks/pre-commit` to
the husky hook instead of changing the hooks path; `doctor.py` reports which
of the two is wired and FAILs when neither is. The runtime hooks in
`.claude/settings.json` do not depend on either — they travel with the tooling
and fire inside the session.

## Which rule or check should have caught it, and why it did not

Nothing checked the checkout itself. The hook could not report its own
absence, and the audit was the first time anyone measured the forks rather
than reading Base.
