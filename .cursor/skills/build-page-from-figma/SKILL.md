---
name: build-page-from-figma
description: Build a store page, section, shared component, overlay or interaction state from a Figma design against Base Theme standards, then update Notion and produce a QA checklist. Use when asked to build, rebuild, or implement anything from a Figma frame — a page, a header or footer, a drawer or modal, or a set of states.
---

# build-page-from-figma

The end-to-end workflow: Figma frame in, Base-standard code out, Notion updated,
QA checklist written for a non-technical reviewer.

## Not everything from Figma is a page

This skill is named for pages because pages came first, but on a full rebuild
**most of the work is not a page**. One client rebuild ran nine builds: four were
pages, and five were a footer, a site header with five mega-menu panels, a cart
drawer, a search overlay with four states, and a set of filter and quick-add
drawers. The skill was bypassed on all five, because Step 1 asks which template
the result belongs to and there is no answer for a footer.

That was the wrong call — the parts that mattered most (the settings contract,
translation keys, verifying both criteria separately, the Notion handoff) apply
just as much. Use the skill; substitute the four steps below where the page
assumptions do not fit.

| The skill says | For a component, overlay or state, instead |
|---|---|
| "Which template the result belongs to" | Which page types it renders on. A shared component renders everywhere, so **verify on at least three different page types**, not one. |
| One desktop frame and one mobile frame | Often a **component frame** for exact specs plus **in-context frames** showing it on real pages. Take numbers from the component frame and behaviour from the in-context ones. |
| Visual fidelity against the frame | Also fidelity across **states** — default, open, active, scrolled, empty. A state frame is a specification, not a suggestion; build what it shows rather than inventing the state. |
| The section settings contract | Still applies to any section. A snippet rendered from the header is not a section and does not need `presets` — but if you add a section, it does. |

Two extra hazards that only appear in this kind of work:

- **A shared component is on every page**, so breaking it breaks all of them. Before
  finishing, open every page type that renders it. This is also the one case where
  editing a file another session owns is likely — say so loudly rather than quietly.
- **An overlay or drawer needs the accessibility work a page does not**: focus moved
  in on open, focus returned to the trigger on close, Escape to close, no page
  scroll behind it. For asynchronous updates that nothing else announces — an
  item added to the cart, a result count changing — add a small dedicated status
  node with `aria-live="polite"` and `aria-atomic="true"`, and write only the
  status into it. Do **not** make the whole drawer or result list live: a screen
  reader would re-announce the entire region on every quantity tick or keystroke.

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

- **The Notion sub-task**, if one was given — it carries the functional
  requirements

If any of these is missing or ambiguous, **ask**. Do not infer a file key from
repo documentation without checking it — on Bites Vitamins a stale file key
appeared in 10 places across the docs against 3 for the correct one, and the
stale one is not readable by the connected account.

### Notion is the functional source; Figma is not

A Figma frame shows what a page looks like, never how it behaves. Requirements
an account manager wrote — default selections, conditional visibility, edge
cases, where a value comes from — live in Notion and exist nowhere in the design.

A Notion link is supplied roughly **60% of the time**.

- **Given** → read it first and treat it as the source of truth for behaviour.
  Walk its requirements individually at verification time.
- **Not given** → infer reasonable behaviour from the design, and **state every
  assumption you made** in your write-up so a human can correct it. Inferring
  silently is the failure to avoid; inferring openly is fine and expected.

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

**Visual:** run `/verify-against-figma` — start the theme with `/run-theme`,
then give the skill the page URL, the file key and each node id with the width
it was designed at. It renders the page at exactly that width, diffs it
against the frame's own export, masks the regions marked `data-verify-mask`,
computes a box-by-box table from `get_metadata` and the DOM, takes one
deliberate look at the side-by-side, and writes
`.claude/verify/<slug>/report.{json,md}`. That report is the evidence. Until
it exists and is newer than your last edit, the page is not verified — the
Stop hook will say so.

Why a script and not your eyes: the workflow's worst recorded failure was a
section reported as built because it measured 614px against a 615px frame
while its media column rendered empty. A measurement is a check on a
screenshot, never a substitute for one, and a table typed from memory is not a
measurement. Custom elements remain the specific trap: they default to
`display: inline`, which drops background and vertical padding on screen while
`getComputedStyle` still reports both — the heatmap catches it, the table does
not.

**Functionality:** walk the Notion requirements one at a time and confirm each.
Say plainly which ones you could not verify and why.

Report all three separately, each with what you actually checked, quoting the
verify report's numbers rather than "matches the design".

**Keep the session honest with a goal.** For a page of any size, set one
before building so a fresh evaluator — not the model doing the work — decides
when it is done:

```text
/goal .claude/verify/<slug>/report.json exists with diff_pct under 5 at every
frame width, table_off is 0, every new section passes
python3 .claude/scripts/check-section-contract.py --files, and
python3 .claude/scripts/check-conventions.py --changed --block exits 0.
Stop after 25 turns if not met and report what remains.
```

## Step 5 — Update Notion

Via Notion MCP, on the sub-task for this page:

1. **Set the status to Quality Inspection**, so QI knows to pick it up. If part
   of the page is blocked, or was built from screenshots because a Figma call
   failed, say so in the comment rather than moving it on quietly.
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
design, broke something and had to be re-prompted, hit a trap a rule should
have named — run `/record-incident` **at the moment it happens**, not at the
end. It writes a committed file under `docs/ai-workflow/incidents/` with the
four fields that matter: what happened, how it surfaced, what fixed it, and
which rule or check should have caught it. That last field is what turns a
list of incidents into a queue of standards gaps; `/harvest` takes a generic
one up to Base from this repo.

The gitignored "mistake log" this replaced was asked for on every build and
created on none — a record nobody can see in a pull request is not a record.

## Closing the loop

When QA logs issues in Notion, `/close-qa-loop` picks them up and resolves them
against these same standards.
