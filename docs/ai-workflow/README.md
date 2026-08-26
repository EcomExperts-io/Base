# The AI Development Workflow — v1

**What this is:** how we take a Figma design and produce Base Theme–standard
code with AI doing the build. Written for someone joining the team who has never
seen this process, and for the AI tools that run it.

**Status: v1.** This describes what we actually do today, not a finished
process. It works well enough to ship client pages; it is not yet reliable
enough to run unattended. The intent is to refine it toward roughly 95%
first-pass accuracy using results from real projects. Where it falls short,
that gets recorded (see [Recording mistakes](#7-record-what-went-wrong)) rather
than worked around silently.

---

## The intent

The goal is that a developer can hand the AI a design and a set of
requirements and say:

> **"Build this page using our Base Theme standards."**

…and the AI already understands **both** what the design is **and** how we
expect that design to be implemented — without anyone re-explaining the
architecture every time.

That second half is the part that took work. An AI given only a Figma frame will
produce something that looks right and is built wrong: it will match the design
faithfully and quietly skip everything the design cannot express — merchant
settings, translation keys, naming conventions. That is not a model failure, it
is a missing-context failure, and it is what `.claude/rules/` and this workflow
exist to fix.

### Two success criteria, never conflated

Every build is judged on two independent axes:

| | Criterion | Judged against |
|---|---|---|
| **1** | **Code style and architecture** | `.claude/rules/` — does it look like Base? |
| **2** | **Visual fidelity** | The Figma frame — does it match, at that breakpoint? |

**Passing one says nothing about the other.** A page can be pixel-perfect and
breach every convention we have. On the Bites Vitamins build that is precisely
what happened: visual fidelity was good, and 30 of 31 new sections shipped with
no merchant controls at all. Report the two separately, always.

### Where each thing comes from

| Source | Provides | Never provides |
|---|---|---|
| **Figma** | Layout, spacing, type scale, colour, radii, breakpoints, states | Prices, review counts, ratings, stock, product copy — a mock showing "4.9 (127 reviews)" is a picture of a number |
| **Notion** | Functional requirements, acceptance criteria, edge cases the design does not show | Design decisions |
| **Shopify** | All real data — objects, settings, metafields | — |
| **`.claude/rules/`** | How it must be built | What it should look like |

---

## The workflow

### 1. A human decides what to build

Scope and order are a human call, not the AI's. PDP before homepage, one section
instead of a page, mobile only — whatever the project needs. The AI does not
choose what to work on next.

### 2. The human supplies the inputs

Pasted into the prompt:

- **Figma URL for desktop** — a specific frame, with `?node-id=` in it
- **Figma URL for mobile** — *separately*. These are two different frames with
  different specs, not one responsive artifact.
- **Notion link** — the sub-task carrying the functional requirements. Present
  roughly 60% of the time.
- **What to build**, in words: "the PDP", "just the ingredients section".

**On the Notion link.** When it exists, it is the source of truth for
functionality and the AI follows it. When it does not, the AI infers reasonable
behaviour from the design and **states every assumption it made** in its
write-up, so a human can correct it. Inferring silently is the failure mode to
avoid.

### 3. The AI fetches the design — one frame at a time, by node ID

Always addressed by explicit `nodeId`. **Never** by asking Figma to list a
file's pages: `get_metadata` without a `nodeId` is unreliable on our files — on
the Bites Vitamins file it returns only a single "Cover" page while frames on
other pages fetch perfectly well when addressed directly. That is a tool
limitation, not a permissions problem, and it has already blocked one audit.

If a Figma call fails on access, the first question is whether there is a newer
file — a stale file key appears in 10 places across the Bites docs against 3 for
the correct one. Do not guess a node ID to get unblocked: a wrong guess silently
builds the wrong design, which is worse than reporting a block.

### 4. The AI builds against Base Theme standards

Using `/scaffold-section` for each new section rather than hand-rolling the
shape. The rules apply in full. The three a design-driven build most reliably
misses, because none of them appear in a Figma frame:

1. **Merchant settings** — `padding_top`, `padding_bottom`, `color_scheme`, plus
   a preset. A frame shows one spacing value because a frame can only show one.
2. **Translation keys** — the copy is English because the designer wrote it in
   English. That is not an instruction to hardcode it.
3. **Naming by function** — Figma files are organised by page, so page-named
   sections feel natural. Name by what the section *is*.

### 5. The AI verifies — both criteria, separately

**Visual fidelity, against the actual rendered page:**

- Run the dev server and open the page in the browser tools.
- Pull the Figma frame's own screenshot via the Figma MCP screenshot tool.
- **Set the viewport to the exact breakpoint the frame was designed at** — if
  the desktop frame is 1440 wide, check at 1440, not "desktop-ish".
- Compare rendered against frame at that width, then repeat for mobile.
- **Measure, don't eyeball.** Read computed values from the DOM — spacing, font
  size, colour — and compare to the frame's specs. Screenshots are for spotting
  problems; numbers are for confirming they are fixed.

**Code and architecture:**

- Run the `shopify-standards-coach` agent and fix what it raises.
- Confirm the pre-commit gate would pass.

**Functionality:** walk the Notion requirements one by one and confirm each,
or say plainly which could not be verified and why.

### 6. The AI reports back in Notion and hands off to QI

On the sub-task, via Notion MCP:

1. **Post a comment** covering what was built, decisions taken and why, anything
   deliberately left out, and every assumption a human should confirm — written
   for someone who was not in the session.
2. **Post the QA checklist** — plain English, for a non-technical reviewer. Our
   QA team does not read code, so no item mentions settings, schema, tokens or
   filenames. *"On a phone you can swipe through the product cards"*, not
   *"verify the carousel track uses scroll-snap"*.
3. **Set the status to Quality Inspection.**

QI then checks the work against that checklist and logs any issues on the same
task.

### 7. Record what went wrong

If the build involved a real AI error — wrong thing built, design misread,
something broken that needed re-prompting — it gets recorded in the client
project's mistake log: what happened, how it surfaced, what fixed it, and **which
rule or skill should have caught it and didn't.** That last field is what turns
a list of incidents into a queue of standards gaps.

The log lives in the **client repo**, excluded from version control — not in
Base. The AI offers to create it; it does not create it unasked.

### 8. The loop closes

QI logs issues in Notion. `/close-qa-loop` picks them up, fixes them against
these same standards, comments back on the task, and updates the status. Issues
that turn out to be AI errors from step 4 feed step 7.

---

## A typical run, start to finish

A developer decides the PDP comes before the homepage. What that actually looks
like:

### What the human types

> Build the PDP using our Base Theme standards.
>
> Desktop: `figma.com/design/emfC8d9CtGm0Ewfb8p3LgZ/…?node-id=14840-13393`
> Mobile: `figma.com/design/emfC8d9CtGm0Ewfb8p3LgZ/…?node-id=14840-13701`
> Requirements: `notion.so/…/PDP-rebuild-2a4f`

### What the AI does

**Confirms the brief before touching anything.** States back: the project, the
Figma file key, both node IDs and which is which, the Notion task, and that the
target is `templates/product.json`. Asks if any of it is ambiguous rather than
assuming.

**Reads the Notion task.** Finds requirements the design does not show — say,
*"subscription option must default to the 30-day plan"* and *"hide the bundle
upsell when the cart already contains a bundle"*. These are functional truths
that exist nowhere in Figma. Notes that the design shows a review count but the
task says reviews come from Judge.me, so that number is real data and comes from
the app, never from the mock.

**Fetches each frame by node ID, separately.** Desktop at 1440, mobile at 393.
Pulls real values — the 45px heading, the 24px gutter — rather than
approximating.

**Builds.** `/scaffold-section` for `product-ingredients` and
`product-how-it-works`. Each gets `padding_top`, `padding_bottom`,
`color_scheme` and a preset, even though the frame shows one spacing value and
one background — because the merchant still needs to change them. Every string
is a `t:` key, `aria-label`s included. Sections named for what they are, not
`pdp-ingredients`.

**Verifies.** Dev server up, browser at exactly 1440 next to the desktop frame's
screenshot. Reads computed spacing off the DOM and compares to the frame —
catches the ingredient grid at 20px where the design says 24. Fixes, re-measures.
Repeats at 393. Walks the two Notion requirements and confirms both. Runs the
standards coach; it flags a `component-*` file loaded by two unrelated sections,
which gets renamed.

**Reports.** A Notion comment: what was built, that the subscription default came
from the task rather than the design, that the review count is wired to Judge.me
and renders blank without it, and one open question — the design shows no empty
state for ingredients, so it currently renders nothing and someone should confirm
that is right.

**Then the QA checklist**, in QI's language:

- [ ] The ingredients section shows all 6 ingredients on desktop, and you can swipe through them on a phone
- [ ] The subscription option is selected by default, set to 30 days
- [ ] The star rating and review count match what the reviews app shows
- [ ] The "Add to Cart" price updates when you change quantity
- [ ] On a phone nothing is cut off at the right edge and the page does not scroll sideways
- [ ] Every ingredient image loads — no grey boxes

**Sets the status to Quality Inspection.** QI reviews against that list and logs
two issues: a heading wrapping awkwardly at 768px, and a button going to the
wrong collection. `/close-qa-loop` picks both up, fixes them, comments back, and
updates the task. The wrong link was an AI error, so it goes in the mistake log
with the note that no rule covers verifying link targets against requirements —
a real gap, now visible.

---

## What this workflow does not do yet

Stated plainly, because pretending otherwise is how v1 becomes permanent:

- **It is not unattended.** A developer reviews the output. Complex pages —
  Collection, PDP, Homepage — need more hand-holding than simple ones.
- **The design half is undone.** Getting designers to structure Figma files so
  MCP extracts them unambiguously is half the original problem and no document
  covers it yet.
- **Figma page listing is unreliable**, so node IDs come from humans.
- **Pixel-perfect verification is manual comparison**, not an automated diff.
- **Nothing aggregates the mistake logs across projects.** They are local to
  each client repo, so patterns only surface if someone goes looking.

---

## Reference

| | |
|---|---|
| Conventions | `.claude/rules/` — start with `CLAUDE.md` |
| Build a page | `/build-page-from-figma` |
| New section | `/scaffold-section` |
| Close QA issues | `/close-qa-loop` |
| Accessibility audit | `/accessibility-review` |
| Advisory grading | `shopify-standards-coach` agent |
| Merge gate | `shopify-pr-reviewer` agent |
| Architecture rulebook | `docs/base-theme-standards/base-theme-architecture-reference-collection-pdp.md` |
| Pass/fail checklist | `docs/base-theme-standards/base-theme-compliance-checklist.md` |
| Rulings and open questions | `docs/base-theme-standards/base-theme-decisions-log.md` |
| The durable why | `docs/base-theme-standards/base-theme-ai-workflow-vision.md` |
