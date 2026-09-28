---
title: "CLAUDE.md claimed 14 of 16 rules identical to a fork; the number was 6"
date: 2026-09-14
repo: Base
scope: generic
surfaced_by: review
should_have_caught: .claude/scripts/check-ai-config.py
status: harvested
---

# CLAUDE.md claimed 14 of 16 rules identical to a fork; the number was 6

## What happened

CLAUDE.md stated, as evidence that inheritance was working, that 14 of the 16
rules were byte-identical between Base and the BPN fork. Base changed on 1 Sep;
the fork could not pull the change because it had no `base` remote and no
shared history. By 14 Sep the true count was 6 of 16, and the sentence was
loaded into every session as fact.

## How it surfaced

An audit compared the two trees with `cmp`. Nothing in the repo could have
noticed on its own: the claim was prose, and the fork was in another
repository.

## What fixed it

`check-tooling-drift.py` computes the number on demand from a `.base-version`
stamp and lists the files either side changed. CLAUDE.md now describes the
mechanism instead of quoting a measurement.

## Which rule or check should have caught it, and why it did not

`check-ai-config.py` verifies CLAUDE.md's inventory of rule files against disk
but has no notion of a measurable claim in prose. A number that a script could
verify should not be written where only a human can read it; the drift script
is where it lives now.
