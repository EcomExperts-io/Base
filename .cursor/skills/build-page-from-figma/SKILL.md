---
name: build-page-from-figma
description: Build a store page from a Figma design against Base Theme standards, then update Notion and produce a QA checklist. Use when asked to build, rebuild, or implement a page or section from a Figma frame.
---

# build-page-from-figma

The end-to-end workflow: Figma frame in, Base-standard code out, Notion updated,
QA checklist written for a non-technical reviewer.

**This is v1.** It reflects how we actually work today, not a finished process.
Expect to hit cases it doesn't cover — when that happens, record it in the
project's mistake log (see step 6) rather than working around it silently.

## Two success criteria, judged separately

A page is judged on two independent axes, and passing one says nothing about the
other:

| | Criterion | Judged against |
|---|---|---|
| **1** | **Code style and architecture** | `.claude/rules/` — does it look like Base? |
| **2** | **Visual fidelity** | The Figma frame — does it match the design? |

Keep them separate in your work and in your reporting. On the Bites Vitamins
build, visual fidelity was good while the merchant-facing settings contract was
near-zero — a page can be pixel-perfect and fail every convention we have.
Never report "matches the design" as if it covered both.

## Step 1 — Confirm what you are building. Ask; do not guess.

Before any Figma call, establish and state back:

- **Which project / store** this is
- **Which Figma file** — the file key, confirmed for this project
- **Which frame** — a node ID, and whether it is the desktop or mobile variant
- **Which template** the result belongs to

If any of these is missing or ambiguous, **ask**. Do not infer a file key from
repo documentation without checking it — on Bites Vitamins a stale file key
appeared in 10 places across the docs against 3 for the correct one, and the
stale one is not readable by the connected account.

If a Figma call fails with an access error, do not assume the account needs a
share grant. Ask whether there is a newer file first; that has been the cause
before.

## Step 2 — Fetch the frame by node ID, one frame at a time

**Always pass an explicit `nodeId`.** Never rely on file-wide page listing.

`get_metadata` with no `nodeId` is unreliable on our files — on the Bites
Vitamins file it returns only a single "Cover" page, while frames on other pages
fetch perfectly well when addressed directly by ID. That is a tool limitation,
not a permissions problem, and it has already blocked one audit. Get node IDs
from a human, from a Figma share link (`?node-id=`), or from a registry the
project keeps.

Fetch desktop and mobile as **separate calls** — they are separate frames with
different specs, not one responsive artifact.

If `get_design_context` fails, fall back to `get_screenshot` plus attached
images, and say plainly in your report that you worked from screenshots. Never
guess a node ID to get unblocked: a wrong guess silently builds the wrong
design, which is worse than reporting a block.

## Step 3 — Build against the standards

Use `/scaffold-section` for each new section rather than hand-rolling the shape.

The rules apply in full. The three that a design-driven build most reliably
misses, because none of them appear in a Figma frame:

1. **The merchant settings contract** — `padding_top`, `padding_bottom`,
   `color_scheme`, plus a preset. A frame shows one spacing value because a
   frame can only show one.
2. **Translation keys** — the copy in the frame is English because the designer
   wrote it in English. That is not an instruction to hardcode it. This applies
   to brand-new files with no existing `| t` calls nearby.
3. **Naming by function** — the Figma file is organised by page, so page-named
   sections feel natural. Name by what the section *is*.

Extract real values from the frame — spacing, type scale, colours — rather than
approximating by eye. Where the design uses a value that already exists as a
theme token, use the token.

## Step 4 — Verify both criteria

**Code:** run the standards coach agent for advisory feedback, then fix what it
finds. Confirm the gate would pass.

**Visual:** compare against the frame at both breakpoints. Measure rather than
eyeball — read computed values from the DOM and compare to the frame's specs.
Screenshots are for spotting problems, not for confirming numbers.

Report the two separately, each with what you actually checked.

## Step 5 — Update Notion

Via Notion MCP, on the sub-task for this page:

1. **Set the status** to reflect real state. If part of the page is blocked or
   was built from screenshots, the status says so.
2. **Post a comment** covering: what was built, decisions made and why,
   anything deliberately left out, and any assumption a human should confirm.
   Written for someone who was not in the session.
3. **Post the QA checklist** — see below.

Ask which Notion task if you do not have it. Do not create new tasks or change
anything outside the one you were given without being asked.

## Step 6 — QA checklist, in plain English

**Our QA team is non-technical.** The checklist is for them, not for a
developer, and not for the AI.

Every item is something a person can check by looking at the page in a browser.
Never mention code, settings, schema, tokens, or file names.

**Write items like this:**

- [ ] The heading reads "Find Your Formula"
- [ ] There are 3 product cards on desktop, and you can swipe through them on a phone
- [ ] The "Shop Now" button goes to the All Products page
- [ ] Prices show in euros with the € symbol
- [ ] On a phone, nothing is cut off at the right edge and the page does not scroll sideways
- [ ] Every image loads — no grey or empty boxes
- [ ] The dots under the cards move as you swipe

**Never like this:**

- ~~Verify `color_scheme` is exposed in the schema~~
- ~~Confirm `padding_top` renders at 0.75× on mobile~~
- ~~Check `component-product-card` snippet is used~~

Group by what the reviewer is looking at — Desktop, Mobile, Links and buttons,
Text and images. Cover both what should happen and the obvious ways it could be
wrong.

## Step 7 — Record anything that went wrong

If this build involved a real mistake — you built the wrong thing, misread the
design, broke something and had to be re-prompted — record it in the project's
mistake log so the pattern is visible later.

If the project has no mistake log yet, **offer to create one** in the client
repo; do not create it unasked. It belongs in that repo, in a location excluded
from version control, not in Base.

Record: what happened, how it surfaced, what fixed it, and — most useful —
which rule or skill should have caught it and didn't. That last field is what
turns a list of incidents into a queue of standards gaps.

## Closing the loop

When QA logs issues in Notion, `/close-qa-loop` picks them up and resolves them
against these same standards.
