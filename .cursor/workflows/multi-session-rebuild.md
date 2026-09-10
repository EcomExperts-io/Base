# Workflow — rebuilding a whole store across parallel sessions

Rebuild an entire storefront from a Figma file by giving each page or component to
its **own Claude Code session**, each on its own branch and worktree, all merging
into one integration branch that becomes the source of truth.

This is a different scale from `parallel-section-build.md`. That one spawns agents
*inside* one session to build the sections of a single page. This one coordinates
**separate sessions a human drives**, over days, across a whole rebuild.

Used on a 120-team sports store: nine builds — PDP, FAQ, a three-page collection
template, teams directory, team homepage, footer, cart drawer, site header with
five mega-menu panels, search, 404 — plus a parity audit. Eleven sessions, 173
commits onto one integration branch.

**Read this before starting a rebuild, not during one.** Most of what follows is
here because it went wrong the first time.

## Part 1 — Set up before the first session

### 1. Cut an integration branch and treat it as the trunk

Everything merges here; nothing merges to `development` until the rebuild is done.
Cut it from wherever the current work actually is — on a rebuild already in
progress that is **the incumbent developer's branch, not `development`**.

Expect that branch to keep moving. On the build this came from, the incumbent
pushed three more commits mid-rebuild and they had to be merged in twice. Agree
the topology with them before you cut.

### 2. One worktree per session, not one checkout

The first two sessions shared a checkout and immediately corrupted each other's
staging — two agents, one `HEAD`, one index.

```bash
git worktree add ../<repo>-<slug> <branch>
```

**A fresh worktree has no `.husky/_/` (or whatever your hook shim is), so every
commit aborts until you copy it in.** Do that as part of creating the worktree.
Verify `git config core.hooksPath` resolves in the new worktree too.

### 3. Make the commit gate actually work first

Do this before any build session runs, or you will discover it at the worst moment:

- **Test the branch-name pattern against a real branch name you intend to use.** A
  regex allowing three digits met five-digit ticket ids and rejected every branch,
  including the one already in flight.
- **Check which hook the message rule lives in.** A `[TYPE]:` check in
  `prepare-commit-msg` runs *before* the editor opens, so it reads the comment
  template and aborts — meaning only `git commit -m` ever works. It belongs in
  `commit-msg`.
- **Run each blocking check by hand and confirm it inspects something.** A check
  scoped to `git diff --cached` passes vacuously when nothing is staged. Stage a
  real change and watch the file count.

### 4. Fix the collision surface up front

Three files collide across every parallel branch. Decide the convention now:

- **Locale files.** Namespace every key by page — `product_page.*`, `faq.*`,
  `search.*`. Done this way, three branches produced **zero overlapping keys** and
  every conflict was additive. Also forbid reordering existing keys, which turns a
  five-line conflict into a whole-file one.
- **A shared icon set.** Every branch adds icons to the same `case` block. Expect the
  conflict; resolve as a union and keep every arm.
- **Any generated mirror** (`.cursor/**`). Never hand-merge it — resolve by
  regenerating from `.claude/` and re-running the sync script.

### 5. Branch names carry the ticket id

`<client-id>.<ticket-id>/Project-<Name>`, where the ticket id is the project id
from the tracker. It makes every branch traceable without a lookup, and it is
worth checking against the tracker rather than inventing sequential numbers.

## Part 2 — Session brief template

One session per page or component. Fill in and paste. The order matters: research
before code, decisions documented rather than deferred.

```
Read CLAUDE.md and the relevant files in .claude/rules/ first — the rules apply in
full. Invoke /build-page-from-figma and follow it, substituting its non-page
guidance if this is a component, overlay or set of states.

## Step 0 — Read the branch before planning

Fetch the current tip of {{INTEGRATION_BRANCH}} and read what is actually there.
Other sessions have merged since this brief was written, and anything I describe
below is a snapshot. If the branch differs, trust the branch and tell me.

Then cut {{BRANCH}} from that tip. Work in {{WORKTREE}}.

## What to build

Figma file key: {{FILE_KEY}}. Canvas {{CANVAS_NODE}} — never build from the canvas
node; a canvas can hold several frames, variant states and more than one template.

{{FRAME_TABLE — one row per frame: nodeId, what it is, exact size}}
{{PER_FRAME_LINKS}}

Read frames with get_screenshot. Take numbers from get_metadata and
get_variable_defs. **Layer geometry lies** — layers that do not render still carry
absolute positions, so a frame can report overlapping bands or children summing
past its own height and render perfectly. Identify everything visually.

{{DESIGNER_NOTES — quote them; on a rebuild these are often the only functional spec}}

## Step 1 — Reuse research, verified by rendering

Assume most of this is already built and your job is assembly. For each element you
plan to reuse, **render it and look at it** — dev server, screenshot, compare
side by side with the frame. Matching names or similar heights is not evidence.

Report per element: reuse as-is / reuse with new settings / generalise / build new,
with the reason and what you looked at. Lead your final report with this.

{{CANDIDATE_TABLE — existing files worth checking, by element}}

Prefer generalising a near-match through settings and data attributes over copying
it. If you widen a file's scope, rename it in the same change.

## Non-negotiables

- **No invented data.** No seeded sample records, no placeholder headings, no
  hardcoded counts, no fake states. An absent value renders nothing. This is the
  single most common reason a branch gets blocked in review.
- The settings contract on every merchant-addable section, plus a preset.
- Every string a translation key — copy, schema labels, aria-label, alt, schema name.
- Name by function, never by page or client.
- An explicit CSS `display` wherever a class sits on a custom element tag.

## Where a value does not exist yet

Wire the front end to the field it *should* come from, let it render nothing when
absent, and document the exact definition someone must create — name, type, and
which band consumes it. Never invent a fallback, and never resolve a relationship
by guessing at a field that happens to be populated.

## Uncertainty

Do not stall. Pick the option closest to the design, build it, and document the
choice. Your job is front-end fidelity with every varying value wired to a real
source; someone else's job is the backend configuration. Stop and ask only where
proceeding either way would be unsafe or wasted.

## Fidelity

Verify at the exact widths the frames were drawn at. Measure off the DOM, never by
eye. On a tall page, work band by band and say which bands you measured versus only
looked at. A shared component gets checked on at least three page types.

## Report, then hand off

Separately: (1) reuse plan, (2) code and architecture, (3) visual fidelity with
measured numbers, (4) decisions taken, (5) assumptions and what you could not
verify.

Then post the handoff to the tracker **as comments, not page content** — four of
them: backend configuration needed (name, type, consumer, what renders until it
exists) / decisions taken (chosen, rejected, why, how to reverse) / developer
handoff notes / how to test in plain English. Terse, bullets, skimmable in 30
seconds. Written for someone who was not in the session and has to finish the job.

Do not open a PR unless I ask.
```

## Part 3 — Between sessions, the orchestrator's job

### Merge order, and expect conflicts between siblings

`gh pr list --json mergeable` reports each branch against the base **one at a
time**, so all of them can read MERGEABLE and still collide with each other. Check
pairwise before believing it:

```bash
git merge-tree --write-tree <branch-a> <branch-b> | grep ^CONFLICT
```

Merge in due-date order. The first lands clean; the rest need a rebase.

### Review before merging, and verify the findings

Run the review agents. Then **spot-check what they report** — on this build every
blocker was real, but one was flagged as inferred rather than measured, and
verifying it took one command. Two of three branches shipped fabricated content
that reached rendered pages; a review that had not run would have merged all of it.

### Merging a git branch does not deploy anything

The most confusing hour of the build was spent on a preview showing "Could not find
asset" for files that were demonstrably committed. The theme had been connected to
GitHub minutes earlier and had not finished its first sync. Before debugging code,
confirm the sync completed — a partially imported theme renders exactly like broken
code.

Separately: a page template does nothing until a page exists in admin with the
matching handle and that template assigned. Four pages 404'd for that reason alone,
which is not a code defect.

### Audit at the end, across everything

Individual sessions verify their own work and cannot see cross-page inconsistency
or the buttons nobody wired. Budget a parity pass over the integration branch once
everything has merged. Structure it as: how this was checked / what matches / code
defects / template content / store gaps / design questions / what could not be
verified.

## What this costs, honestly

Eleven sessions produced nine builds and a working integration branch. It also
produced, in the tooling layer, **nine files and one rule** — because nobody
harvested as they went, and the skills, agents and scripts were never touched
across 173 commits despite being bypassed and worked around repeatedly.

**Harvest as you go.** A generic trap goes up to Base in the same change that
found it, per CLAUDE.md's "Flowing changes back to Base". Left to the end it is
an archaeology project, and the prompts that drove eleven sessions live in
scratch files that do not survive the session that wrote them.
