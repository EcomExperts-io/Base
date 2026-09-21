---
title: "A section was reported as matching its frame because 614px matched 615px"
date: 2026-09-14
repo: Base
scope: generic
surfaced_by: eyeball
should_have_caught: .claude/skills/verify-against-figma/SKILL.md
status: harvested
---

# A section was reported as matching its frame because 614px matched 615px

## What happened

On the parallel section build for a client PDP, an agent reported a section as
built because its rendered height measured 614px against the frame's 615px,
and a scope document independently agreed. The section shared nothing else
with the design. A FAQ was reported at 728 vs 727 while its media column
rendered completely empty. Two of three "X is broken" reports on the same
build were also false — agents measuring inside their own static harness.

## How it surfaced

The orchestrator opened the page and looked. Nothing before that step could
have caught it: the only verification artefact was a number in a chat message.

## What fixed it

`verify-against-figma`: the frame exported at native size, the page rendered
at the exact width and height, live regions masked, a pixel diff with a
heatmap and a worst-band profile, a box table computed by script from
`get_metadata` and the DOM, one deliberate look at the side-by-side, and a
report on disk that the Stop hook and `/goal` can read. A height is one row of
that table, not the verdict.

## Which rule or check should have caught it, and why it did not

The build skill said "measure, don't eyeball" and the agents did exactly that
— they measured. The rule needed the other half: a measurement is a check on a
screenshot, never a substitute for one, and a table typed from memory is not a
measurement. Both halves are now in the skill and in the tooling.
