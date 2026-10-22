# The AI Development Workflow

How a Figma design becomes Base Theme–standard code with AI doing the build,
on any client store, by any developer on the team. The vision it serves is in
[`base-theme-ai-workflow-vision.md`](../base-theme-standards/base-theme-ai-workflow-vision.md).

## The intent

> **"Build this page using our Base Theme standards."**

`.claude/rules/` supplies how it must be built; the hooks notice when that
was ignored.

### Two success criteria, never conflated

| | Criterion | Judged against | Evidence |
|---|---|---|---|
| **1** | **Code style and architecture** | `.claude/rules/` — does it look like Base? | the gate: contract, conventions, Theme Check |
| **2** | **Visual fidelity** | The Figma frame, at that breakpoint | `.claude/verify/<slug>/report.json` |

Passing one says nothing about the other — 30 of 31 new sections on one
build were pixel-perfect and shipped with no merchant controls. Report the
two separately, always, with the evidence for each.

### Where each thing comes from

| Source | Provides | Never provides |
|---|---|---|
| **Figma** | Layout, spacing, type scale, colour, radii, breakpoints, states | Prices, review counts, ratings, stock, product copy — a mock showing "4.9 (127 reviews)" is a picture of a number |
| **Notion** | Functional requirements, acceptance criteria, edge cases the design does not show | Design decisions |
| **Shopify** | All real data — objects, metafields, collections, pages, policies — read through the CLI and the store's Storefront MCP endpoint (`/store-recon`); platform facts through the Dev MCP | — |
| **`.claude/rules/`** | How it must be built | What it should look like |

## What runs without you

| When | What | Where it is configured |
|---|---|---|
| Session starts | Doctor status, tooling drift from Base, compliance number, open incidents, the three most-missed rules, and one line naming which of the three situations the repo looks like (fresh rebuild, joining midway, correcting after QA) with the evidence — injected as context | `SessionStart` hook |
| Claude writes a theme file | Settings contract, grep-level conventions, JSON validity on that one file, findings handed straight back | `PostToolUse` hook (~100 ms) |
| Claude tries to end a turn | The same gate over everything changed this turn, plus Theme Check; a **new** file that fails blocks the turn; a section changed with no verify report newer than the change is flagged; a client branch whose GitBot findings have not been read since its last commit is named | `Stop` hook |
| A Shopify command fails | A nudge to `/record-incident` while the details are in context | `PostToolUseFailure` hook |
| A `git push` in a client repo | A nudge to `/gitbot-preflight`: GitBot is reviewing that push, read its findings here and settle each one before the PR | `PostToolUse` hook on Bash |
| A commit | The full pre-commit gate; the Cursor mirror regenerated and staged | `.githooks/pre-commit` (called from husky in client forks) |
| A pull request — into any branch; the fork's trunk is the fork's decision | Base's reusable review workflow, run through a six-line caller in each fork | `.github/workflows/theme-review.yml` |

Modified legacy files are reported, never gated — you answer for what you add.
Where a check is wrong for a theme, say so in the rule; do not disable hooks.

## The workflow

### 0. Arriving on a repo — three commands, whether it is new or someone else's

```bash
sh .claude/scripts/base-link.sh                # Base as remote + worktree + reference dir; no shared history needed
python3 .claude/scripts/pull-base-tooling.py   # three-way overlay; the previous team's edits are kept and listed
npm run setup                                  # hooks, mirror, doctor — or: sh .claude/scripts/setup.sh
```

Then `/recon-theme` (lineage, conventions in use, compliance, what is left)
and `/store-recon` (what the store has). The previous team's conventions win
where they conflict with Base's; the recon writes them into this repo's rule
copies. Build in the order in `.claude/workflows/rebuild-playbook.md`: recon,
foundations, global chrome, shared components, transactional templates,
homepage, long tail.

### 1. A human decides what to build and supplies the inputs

Scope and order are a human call; the AI does not choose what to work on next.

- **The reference** — Figma, live, or both, per band, recorded in
  `docs/ai-workflow/reference-map.md`. Live means the published storefront:
  rebuilt from what it does and shows (`/build-section-from-live`), never from
  its code, and verified with `live-parity.py` to 0%.
- **Figma URL for desktop** and **for mobile** — a specific frame each, with
  `?node-id=` in it. Two frames with different specs, not one responsive one.
- **Notion link** — the sub-task with the functional requirements, when one
  exists. It is the source of truth for behaviour; without one, the AI states
  every assumption it made.
- **What to build**, in words.

### 2. The frame is checked before it is built

`/figma-readiness` scores the frame from `get_metadata` — default layer names,
hidden leftovers, width in the name, components, text as text — and writes the
designer's message if it is not green. Designers get [`figma-handoff-checklist.md`](./figma-handoff-checklist.md).

### 3. The AI fetches the design — one frame at a time, by node ID

Always by explicit `nodeId`, never by listing a file's pages (unreliable on
large files), and never guessed — a wrong id silently builds the wrong design.

### 4. The AI builds against Base Theme standards

`/scaffold-section` for each new section. The rules apply in full; the per-edit
gate reports the settings contract, translation keys and naming by function the
moment they are missed. Live values are marked `data-verify-mask`.

### 5. The AI verifies — both criteria, separately, with evidence

**Visual:** `/run-theme`, then `/verify-against-reference`: the frame at
native size, the page rendered at the exact width and height, live regions
masked, a pixel diff with heatmap and worst bands, a box table from
`get_metadata` and the DOM, one look at the side-by-side, `report.{json,md}`
on disk. Against live, `live-parity.py` renders both sides itself — viewport
and theme asserted, lazy media forced, overlays hidden, animations frozen —
and pairs every element with its computed style. The number is read with the
heatmap and the table; it is a report, not a gate.

**Code:** the gate has already run on every file; `shopify-pr-reviewer` gates
before a human sees the PR and quotes the verify report.

**Functionality:** each Notion requirement walked and confirmed, or named as
unverified. On the purchase path, `commerce-check.py` walks add, change,
discount, remove and market switch at four widths on the development theme,
reading each result from the cart engine's own event; the three rows it cannot
automate — logged in, Safari, checkout — are walked by a person and written
down. A `/goal` set at the start lets a fresh evaluator — not the model doing
the work — decide when all three hold.

### 6. Hand-off, and the loop in both directions

On the Notion sub-task: a comment for someone who was not in the session, the
QA checklist in plain English, status set to Quality Inspection. QI logs
issues → `/close-qa-loop` fixes them against the same standards.

Anything a rule, gate or check should have prevented → `/record-incident` the
moment it happens: a committed file under `docs/ai-workflow/incidents/` with
`scope`, `should_have_caught` and `status`; the doctor counts the open ones.
Generic incidents and rule edits → `/harvest` opens the Base pull request from
inside the client repo. `check-tooling-drift.py` lists what is waiting either way.

## A typical prompt

> Build the product-ingredients section using our Base Theme standards.
> File key `emfC8d9CtGm0Ewfb8p3LgZ`. Desktop `14840:13393@1440`, mobile
> `14840:13701@393`. Requirements: `notion.so/…/PDP-rebuild-2a4f`.
> Run /figma-readiness first; set a /goal.

## What this workflow does not do yet

- **Verification is reported, not gated.** No diff threshold is set.
- **Base does not pass its own compliance report** (`report-compliance.py`);
  the retrofit is an open ruling in the decisions log. The gate stops the gap growing.
- **No company-owned Figma template file** for designers to copy from.
- **No Admin API writes.** A page template with no page in admin is inert;
  `/store-recon` names it, nothing creates it.

## Reference

| | |
|---|---|
| Start here, new developer | [`first-build.md`](./first-build.md) |
| Conventions | `.claude/rules/` — start with `CLAUDE.md` |
| Arrive on a repo | `base-link.sh`, `pull-base-tooling.py`, `npm run setup` (or `setup.sh`), `/recon-theme`, `/store-recon` |
| Order of attack | `.claude/workflows/rebuild-playbook.md` |
| A batch of landing pages matched to live | `.claude/workflows/landing-batch.md` — assembly with `assemble-templates.py`, pushes through `push-dev-theme.sh` |
| Check a frame | `/figma-readiness` · designers: [`figma-handoff-checklist.md`](./figma-handoff-checklist.md) |
| Build a page or component | `/build-page-from-figma` |
| New section | `/scaffold-section` |
| Run the theme | `/run-theme` |
| Verify against the design | `/verify-against-reference` |
| Record / send up | `/record-incident` · `/harvest` |
| Close QA issues | `/close-qa-loop` |
| Machine and repo health | `python3 .claude/scripts/doctor.py` · `check-tooling-drift.py` · `report-compliance.py` · `check-conventions.py --all` |
| Merge gate | `shopify-pr-reviewer` |
| Architecture references | Collection & PDP · Header, Cart Engine & Search — in `docs/base-theme-standards/` |
| Rulings and open questions | `docs/base-theme-standards/base-theme-decisions-log.md` |
| Designers, long form | [`figma-ai-friendly-design-practices.md`](./figma-ai-friendly-design-practices.md) |
