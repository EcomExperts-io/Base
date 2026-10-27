# Workflow — rebuilding a whole store across parallel sessions

Rebuild an entire storefront from a Figma file by giving each page or
component to its **own Claude Code session**, on its own branch and worktree,
all merging into one integration branch. `parallel-section-build.md` spawns
agents inside one session; this coordinates **separate sessions a human
drives**, over days. Read it before starting a rebuild.

## Part 1 — Set up before the first session

### 1. Cut an integration branch and treat it as the trunk

Everything merges here; nothing merges to `development` until the rebuild is
done. Cut it from wherever the current work is — on a rebuild in progress,
**the incumbent developer's branch** — and agree the topology with them first.

### 2. One worktree per session — two in one checkout corrupt each other's staging

```bash
git worktree add ../<repo>-<slug> <branch>
```

A fresh worktree has no `.husky/_/` (or whatever the hook shim is), so every
commit aborts until you copy it in; verify `git config core.hooksPath` resolves.

### 3. Make the commit gate actually work first

- **Test the branch-name pattern against a real branch name.** A regex
  allowing three digits rejects five-digit ticket ids.
- **Check which hook the message rule lives in.** A `[TYPE]:` check in
  `prepare-commit-msg` runs before the editor opens and aborts on the comment
  template, so only `git commit -m` ever works. It belongs in `commit-msg`.
- **Run each blocking check by hand with a real change staged.** A check
  scoped to `git diff --cached` passes vacuously when nothing is staged.

### 4. Fix the collision surface up front

Three files collide across every parallel branch; decide the convention now:

- **Locale files.** Namespace every key by page — `product_page.*`, `faq.*`,
  `search.*` — so every conflict is additive; forbid reordering existing
  keys, which turns a five-line conflict into a whole-file one.
- **A shared icon set.** Every branch adds to the same `case` block; resolve
  as a union and keep every arm.
- **Any generated mirror** (`.cursor/**`). Never hand-merge; regenerate from
  `.claude/` with the sync script.

### 5. Branch names carry the ticket id

`<client-id>.<ticket-id>/Project-<Name>`, the ticket id read from the tracker, not invented.

## Part 2 — Session brief template

One session per page or component. Fill in and paste.

```
Read CLAUDE.md and the relevant files in .claude/rules/ first — the rules apply in
full. Invoke /build-page-from-figma and follow it, substituting its non-page
guidance if this is a component, overlay or set of states.

## Step 0 — Read the branch before planning

Fetch the current tip of {{INTEGRATION_BRANCH}} and read what is there. Other
sessions have merged since this was written; if the branch differs, trust it and tell me.

Then cut {{BRANCH}} from that tip and work in {{WORKTREE}}.

## What to build

Figma file key: {{FILE_KEY}}. Canvas {{CANVAS_NODE}} — never build from the canvas
node; a canvas can hold several frames, variant states and more than one template.

{{FRAME_TABLE — one row per frame: nodeId, what it is, exact size}}
{{PER_FRAME_LINKS}}

Read frames with get_screenshot; numbers from get_metadata and get_variable_defs.
**Layer geometry lies** — layers that do not render still carry absolute positions,
so a frame can report overlapping bands and render perfectly. Identify everything visually.

{{DESIGNER_NOTES — quote them; on a rebuild these are often the only functional spec}}

## Step 1 — Reuse research, verified by rendering

Assume most of this is already built and your job is assembly. For each element you
plan to reuse, **render it and look at it** side by side with the frame; matching
names or similar heights is not evidence. Report per element: reuse as-is / reuse
with new settings / generalise / build new, with the reason and what you looked at;
lead your final report with this.

{{CANDIDATE_TABLE — existing files worth checking, by element}}

Prefer generalising a near-match through settings and data attributes over copying
it. If you widen a file's scope, rename it in the same change.

## Where a value does not exist yet

Wire the front end to the field it *should* come from, render nothing when absent,
and document the exact definition someone must create — name, type, consumer. Never
invent a fallback or guess at a field that happens to be populated.

## Uncertainty

Do not stall: pick the option closest to the design, build it, document the choice.
Ask only where proceeding either way would be unsafe or wasted.

## Fidelity

Verify at the exact widths the frames were drawn at, measured off the DOM. On a
tall page, say which bands you measured versus only looked at. A shared component
gets checked on at least three page types.

## Report, then hand off

Separately: (1) reuse plan, (2) code and architecture, (3) visual fidelity with
measured numbers, (4) decisions taken, (5) assumptions and what you could not verify.

Then post the handoff to the tracker **as comments, not page content** — four:
backend configuration needed (name, type, consumer, what renders until it exists) /
decisions taken (chosen, rejected, why, how to reverse) / developer handoff notes /
how to test in plain English. Terse bullets, for someone who was not in the session.

Do not open a PR unless I ask.
```

## Part 3 — Between sessions, the orchestrator's job

### Merge order, and expect conflicts between siblings

`gh pr list --json mergeable` reports each branch against the base **one at a
time**, so all can read MERGEABLE and still collide. Check pairwise first:

```bash
git merge-tree --write-tree <branch-a> <branch-b> | grep ^CONFLICT
```

Merge in due-date order; the first lands clean, the rest need a rebase.

### Review before merging, and verify the findings

Run `shopify-pr-reviewer`, then **spot-check what it reports**: a finding
inferred rather than measured is verified with one command before it is acted on.

### Merging a git branch does not deploy anything

A preview showing "Could not find asset" for committed files is a
GitHub-connected theme that has not finished its first sync; confirm the sync
before debugging code. A page template does nothing until a page exists in
admin with the matching handle and that template; that 404 is not a code defect.

### Audit at the end, across everything

Sessions cannot see cross-page inconsistency or the buttons nobody wired.
Budget a parity pass over the merged integration branch, structured as: how
checked / what matches / code defects / template content / store gaps /
design questions / what could not be verified.

## Harvest as you go

A generic trap goes up to Base in the same change that found it (CLAUDE.md,
"Flowing changes between Base and the forks"); session scratch files do not survive.
