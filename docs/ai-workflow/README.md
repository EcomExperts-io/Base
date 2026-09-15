# The AI Development Workflow — v2

**What this is:** how we take a Figma design and produce Base Theme–standard
code with AI doing the build, on any client store, by any developer on the
team. Written for someone joining who has never seen it, and for the AI tools
that run it.

**Status: v2, 15 Sep 2026.** v1 shipped client pages and was honest that it
could not run unattended. An audit on 14 Sep measured what that meant in
practice: one operator, forks that could not receive Base's tooling or send
learnings back, about five percent of the rules enforced by anything but the
model's goodwill, verification by eye, and a mistake log that four builds had
asked for and none had created. v2 is the same intent with mechanisms behind
it — hooks that fire whether or not anyone remembers, a report on disk instead
of an assertion, and a queue instead of archaeology. The vision it serves is in
[`base-theme-ai-workflow-vision.md`](../base-theme-standards/base-theme-ai-workflow-vision.md).

---

## The intent

A developer hands the AI a design and says:

> **"Build this page using our Base Theme standards."**

…and the AI already understands **both** what the design is **and** how we
expect it to be implemented — without anyone re-explaining the architecture.

An AI given only a Figma frame produces something that looks right and is
built wrong: it matches the design and skips everything the design cannot
express — merchant settings, translation keys, naming. That is a
missing-context failure, and `.claude/rules/` fixes the context. v2 adds the
other half: a system that notices when the context was ignored.

### Two success criteria, never conflated

| | Criterion | Judged against | Evidence |
|---|---|---|---|
| **1** | **Code style and architecture** | `.claude/rules/` — does it look like Base? | the gate: contract, conventions, Theme Check |
| **2** | **Visual fidelity** | The Figma frame, at that breakpoint | `.claude/verify/<slug>/report.json` |

Passing one says nothing about the other. On Bites Vitamins the pages were
pixel-perfect and 30 of 31 new sections shipped with no merchant controls.
Report the two separately, always, with the evidence for each.

### Where each thing comes from

| Source | Provides | Never provides |
|---|---|---|
| **Figma** | Layout, spacing, type scale, colour, radii, breakpoints, states | Prices, review counts, ratings, stock, product copy — a mock showing "4.9 (127 reviews)" is a picture of a number |
| **Notion** | Functional requirements, acceptance criteria, edge cases the design does not show | Design decisions |
| **Shopify** | All real data — objects, metafields, collections, pages, policies — read through the CLI and the store's Storefront MCP endpoint (`/store-recon`); platform facts through the Dev MCP | — |
| **`.claude/rules/`** | How it must be built | What it should look like |

---

## What runs without you

These fire in every session in every repo that has pulled the tooling. None of
them depend on a person remembering.

| When | What | Where it is configured |
|---|---|---|
| Session starts | Doctor status, tooling drift from Base, compliance number, open incidents, the three most-missed rules — injected as context | `SessionStart` hook |
| Claude writes a theme file | Settings contract, grep-level conventions, JSON validity on that one file, findings handed straight back | `PostToolUse` hook (~100 ms) |
| Claude tries to end a turn | The same gate over everything changed this turn, plus Theme Check; a **new** file that fails blocks the turn; a section changed with no verify report newer than the change is flagged | `Stop` hook |
| A Shopify command fails | A nudge to `/record-incident` while the details are in context | `PostToolUseFailure` hook |
| A commit | The full pre-commit gate; the Cursor mirror regenerated and staged | `.githooks/pre-commit` (called from husky in client forks) |
| A pull request | Base's reusable review workflow, run through a six-line caller in each fork | `.github/workflows/theme-review.yml` |

Modified legacy files are reported, never gated — you answer for what you add.
Where a check is wrong for a theme, the fix is to say so in the rule, not to
disable hooks.

---

## The workflow

### 0. Arriving on a repo — three commands, whether it is new or someone else's

```bash
sh .claude/scripts/base-link.sh                # Base as remote + worktree + reference dir; no shared history needed
python3 .claude/scripts/pull-base-tooling.py   # three-way overlay; the previous team's edits are kept and listed
npm run setup                                  # hooks, mirror, doctor
```

Then `/recon-theme` (lineage, the conventions actually in use, compliance,
what is built and what is left) and `/store-recon` (what the store has). The
previous team's conventions win where they conflict with Base's — half the
theme already uses them — and the recon writes them into this repo's rule
copies. Build in the dependency order in
`.claude/workflows/rebuild-playbook.md`: recon,
foundations, global chrome, shared components, transactional templates,
homepage, long tail.

### 1. A human decides what to build

Scope and order are a human call. The AI does not choose what to work on next.

### 2. The human supplies the inputs

- **Figma URL for desktop** and **for mobile** — a specific frame each, with
  `?node-id=` in it. Two different frames with different specs, not one
  responsive artifact.
- **Notion link** — the sub-task with the functional requirements, when one
  exists (roughly 60% of the time). When it does, it is the source of truth
  for behaviour; when it does not, the AI states every assumption it made.
- **What to build**, in words.

### 3. The frame is checked before it is built

`/figma-readiness` scores the frame from `get_metadata`: default layer names,
hidden leftovers, width in the frame name, components used, text as text — and
writes the message to send the designer if it is not green. The four-item
version designers get is
[`figma-handoff-checklist.md`](./figma-handoff-checklist.md).

### 4. The AI fetches the design — one frame at a time, by node ID

Always by explicit `nodeId`; never by listing a file's pages, which is
unreliable on large files. Never guess a node id — a wrong one silently builds
the wrong design.

### 5. The AI builds against Base Theme standards

`/scaffold-section` for each new section. The rules apply in full; the three a
design-driven build most reliably misses — the settings contract, translation
keys, naming by function — are now also the three the per-edit gate reports
the moment they are missed. Live values are marked `data-verify-mask` so the
verifier can ignore them.

### 6. The AI verifies — both criteria, separately, with evidence

**Visual:** `/run-theme`, then `/verify-against-figma`: the frame exported at
native size, the page rendered at the exact width and height, live regions
masked, a pixel diff with heatmap and worst bands, a box table computed from
`get_metadata` and the DOM, one deliberate look at the side-by-side, and
`report.{json,md}` on disk. The number is read with the heatmap and the
table; it is a report, not yet a gate.

**Code:** the gate has already run on every file; the standards coach gives
advisory feedback; `shopify-pr-reviewer` gates before a human sees the PR and
quotes the verify report.

**Functionality:** each Notion requirement walked and confirmed, or named as
unverified.

A `/goal` set at the start lets a fresh evaluator — not the model doing the
work — decide when all three hold.

### 7. The AI reports back in Notion and hands off to QI

On the sub-task: a comment for someone who was not in the session; the QA
checklist in plain English for a non-technical reviewer; status set to
Quality Inspection.

### 8. Anything that went wrong is recorded when it happens

`/record-incident` — a committed file under `docs/ai-workflow/incidents/` with
`scope`, `should_have_caught` and `status`. Not at the end of the build; at
the moment. The doctor counts the open ones every session.

### 9. The loop closes, in both directions

QI logs issues → `/close-qa-loop` fixes them against the same standards.
Generic incidents and rule edits → `/harvest` opens the Base pull request from
inside the client repo, using the Base worktree. `check-tooling-drift.py`
lists what is waiting either way from the first day of the build.

---

## A typical run, start to finish

> Build the product-ingredients section using our Base Theme standards.
> File key `emfC8d9CtGm0Ewfb8p3LgZ`. Desktop `14840:13393@1440`, mobile
> `14840:13701@393`. Requirements: `notion.so/…/PDP-rebuild-2a4f`.
> Run /figma-readiness first; set a /goal.

The AI scores the frame (green), reads the Notion task, fetches both frames by
id, scaffolds the section — contract, keys, function name — and as it writes
each file the gate reports what is off, which it fixes in the same turn. It
starts the theme, runs the verifier: 1440 at 3.4% with one box off (grid gap
20 vs 24), 393 at 2.1% clean; fixes the gap, re-runs, both under 3. Walks the
two Notion requirements. Sets the Notion status, posts the comment and the QA
checklist. The turn ends because the goal evaluator says so, not because the
model felt done. The report is on disk; the reviewer will quote it.

---

## What this workflow does not do yet

Stated plainly, so v2 does not become permanent either:

- **Verification is reported, not gated.** Diff thresholds wait for two or
  three real builds' worth of numbers.
- **Base does not yet pass its own report** — 22 of 46 sections. The retrofit
  needs a ruling (Decisions Log, Open); until then every fork inherits the
  gap and the gate stops it growing.
- **No company-owned Figma template file.** Readiness is checked; the file
  designers copy from does not exist yet. The first build uses a client frame.
- **No Admin API writes.** A page template with no page in admin is still
  "inert until someone creates it" — `/store-recon` names it, nothing creates it.
- **The observed first build has not happened.** `first-build.md` is the
  acceptance test; it has not been run by anyone but its author.

---

## Reference

| | |
|---|---|
| Start here, new developer | [`first-build.md`](./first-build.md) |
| Conventions | `.claude/rules/` — start with `CLAUDE.md` |
| Arrive on a repo | `base-link.sh`, `pull-base-tooling.py`, `npm run setup`, `/recon-theme`, `/store-recon` |
| Order of attack | `.claude/workflows/rebuild-playbook.md` |
| Check a frame | `/figma-readiness` · designers: [`figma-handoff-checklist.md`](./figma-handoff-checklist.md) |
| Build a page or component | `/build-page-from-figma` |
| New section | `/scaffold-section` |
| Run the theme | `/run-theme` |
| Verify against the design | `/verify-against-figma` |
| Record / send up | `/record-incident` · `/harvest` |
| Close QA issues | `/close-qa-loop` |
| Machine and repo health | `python3 .claude/scripts/doctor.py` · `check-tooling-drift.py` · `report-compliance.py` · `check-conventions.py --all` |
| Advisory grading / merge gate | `shopify-standards-coach` · `shopify-pr-reviewer` |
| Architecture references | Collection & PDP · Header, Cart Engine & Search — in `docs/base-theme-standards/` |
| Rulings and open questions | `docs/base-theme-standards/base-theme-decisions-log.md` |
| Designers, long form | [`figma-ai-friendly-design-practices.md`](./figma-ai-friendly-design-practices.md) |
