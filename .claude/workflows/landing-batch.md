# Workflow — a batch of landing pages, matched to live, with parallel agents

Rebuild a card's worth of landing pages (three to seven pages on a few
templates) on the Base theme, matched to the live site, in one session with
up to five agents. A human starts this; it is not a skill.

Use it when a card lists pages whose reference is **live**
(`reference-map.md`); for a Figma page use `parallel-section-build.md`.

**The one idea.** A landing page is **template content on a section library**.
A batch adds pages, settings and occasionally a section; it almost never adds
a second copy of anything. The first job in every batch is the honest diff —
already built / copy of built / genuinely new.

---

## Part 1 — Orchestrator (you)

### 0. Caps, before anything runs

From the global CLAUDE.md in the home directory:

- **At most 5 agents at once**, read-only ones included: 3 for build waves,
  2 for recon, 5 only when the page pass runs one agent per template.
- **At most 3 headless browsers on the machine.** `live-parity.py` and
  `commerce-check.py` take a run slot (`LIVE_PARITY_SLOTS=3`, never higher)
  and close their Chrome on exit; nothing else may open one. One Chrome pair
  per agent, widths in sequence, never `Promise.all` over pages.
- Stray browsers older than an hour are closed at the start
  (`ps -eo pid,etime,args`); leftovers die by PID, **never `pkill -f`** —
  it kills the other session's runs.
- Agents **cannot write `.md` files or touch git**. They return text; you
  save docs and you commit.
- The store rate-limits: an HTTP 429 means stop the Chrome runs for five
  minutes. Queue measurements as one script with pauses, not a loop.

### 1. Arrive: branch, worktree, dev theme, live theme

```bash
git fetch origin && git worktree add ../<repo>-b<N> -b <ticket>/Task-LandingBatch<N> origin/<project-branch>
```

Cut from the **project branch**, never the trunk: it carries every earlier
batch and the section library, and it moves several times a day (QA rounds,
the parallel batch). Fetch and compare before every push; merge it into
yours early, not only at the end.

```bash
shopify theme push --unpublished --theme "<repo>/<ticket>/Task-LandingBatch<N>" --json --path .
```

Write the id it prints to the `dev-theme-id` file in the `.claude` cache directory (`push-dev-theme.sh --help` names it). Then protect what
must never be written: the live theme's id and the QA theme's id (the
GitHub-synced one, read-only) go in `.claude/protected-themes.txt`, one per
line, and every push goes through `push-dev-theme.sh`, which refuses them,
refuses a theme whose role is not development or unpublished, serialises
pushes, waits 25 s after a new section file, and reads Shopify's rejection
out of the output (the CLI exits 0 on one). A shop allows 100 themes: if the
push says so, stop and ask which merged batch's theme to delete — never
delete one yourself.

```bash
shopify theme pull --live --path <scratchpad>/live-current --force
```

Read-only. Live is newer than any repository every time; the live JSON
templates (with their leading `/* */` comment) give the section keys and the
order the page is assembled in.

Start the batch's **cross-batch log** if another batch runs in parallel
(Part 5), and count the schema locale: `check-json.py locales/*.json` warns
above 3,300 keys. The batch gets a key budget; agents reuse `labels.*` and
`general.*` keys before adding one (`locales.md`).

### 2. Recon — read-only, two agents at most

One recon agent per two or three pages, with Part 2 filled in. They measure
and map; they build nothing. Each returns, per enabled live section in live
order: key, type, exact copy (into a text file per page — claims verbatim),
behaviour, measurements at 393/768/1024/1440 where the nearest built section
differs, and the honest diff: **already built** (name the template and key),
**copy of built** (the exact settings), **genuinely new** (a spec, additive).

Then show the lead a short scope in chat — reuse versus new, the one or two
decisions — and keep going. Decisions and questions go at the end; ask early
only when truly blocked, in one short list.

Confirm each page URL with a HEAD request first. Cards list pages that are
404 or 301 on live; build nothing for those and say so.

### 3. Templates first, then the few new sections

Build the templates under **live's own names** (`page.<live-template>.json`,
odd casing included), so no admin template switch is needed; a page live
serves from the plain page template needs one at go-live — flag it. Content
comes from the recon as fragments, one JSON per agent per template, and:

```bash
python3 .claude/scripts/assemble-templates.py --fragments <dir> --templates <a,b> --live-path <scratchpad>/live-current [--layout landing] --write
```

It keeps live's order, validates every setting against the section schemas
(ranges on step, select values, `richtext` shape, no `<br>` in
`inline_richtext`, no `t:` value, no unknown setting — each of which Shopify
rejects or drops without a word), and refuses to write on any error. From
here the template file is the source of truth; later edits go straight into
it.

Owner agents (Part 3) build only the genuine gaps, at most three at a time.
Every change to a shared section is **additive** — new settings default to
the old behaviour, existing ids, blocks and markup unchanged, CSS in a marked
`/* Batch N: … */` block at the end of the asset — and is logged in the
cross-batch file before it is made. Prove each extended section at the end
(step 5).

### 4. The page pass — one agent per template

The templates render on the dev theme. Now the page as a whole, against live
at 393, 768, 1024 and 1440 (1920 if time), design and behaviour, with Part 4:

1. **Junctions.** `live-parity.py page` names the first section whose top
   diverges; the per-section spans find the gaps. Live themes space bands
   with margins the next band cancels; fix every junction off by more than
   1.5 px with template settings first.
2. **Whole page and per section.** `live-parity.py page` and `section` at
   the four widths; separate real gaps from noise (video, GIF and marquee
   frames, fractional raster) by freezing both sides; look at the
   side-by-side yourself.
3. **Chrome.** Only the header and announcement parts live really shows.
4. **Hover and click-through.** `live-parity.py hoverstyles` and `states`
   with a real pointer; `commerce-check.py` for any page that adds to cart
   (it blocks analytics and never reaches checkout). Nothing is ever
   submitted on live.
5. **Copy.** Rendered text per section, word for word against live, claims
   and legal lines verbatim and flagged, never edited.

Tablet is **clean** where live's tablet layout is broken; a live bug that
hides content is reproduced, one that breaks function is not copied and is
listed. Tracking, A/B scripts, newsletter attach scripts and site-wide auto
gifts are not ported; list them.

### 5. Regression, gate, PR

For every shared section this batch extended, compare a consumer page
**outside the batch** on the QA theme against the dev theme at defaults:

```bash
python3 .claude/scripts/live-parity.py regress --url "https://<store>/pages/<consumer>" --main-theme <qa-theme-id> --ours-theme <dev-theme-id> --key <section-key> --widths 1440,393 --out .claude/verify/regress-<key>
```

0.0% or the change is not additive. Then merge the project branch into yours
(expect the schema locale and CSS tails to conflict: take the project's
file, re-add your fragments and your tail, brace-balance every changed
stylesheet), run the gate,
push, open the PR into the project branch, and `/gitbot-preflight`. Merge
only when the lead says so, in chat.

### 6. Hand off

Preview links to the lead in chat first, before any Notion comment. Then one
comment on the card — GitHub details, theme name and id, live and preview
links in pairs, dev notes (what was reused, what was new, decisions, live
bugs not copied, what was not ported, what was not covered: tracking, SEO,
speed), open questions, and the QA checklist in plain English
(`build-page-from-figma` Step 6, purchase-path rows included). One sub-task
per real page. Delete the dev theme only when asked; `/record-incident` for
anything a rule should have caught, before the session ends.

---

## Part 2 — Recon brief

Fill in `{{PAGES}}`, `{{LIVE_PATH}}`, `{{OUT}}`, `{{QA_THEME}}`; one brief, all recon agents.

---

You are a read-only recon agent for a landing-page batch on a Base theme. You
measure and map; you build nothing.

**Pages:** `{{PAGES}}` (live URL, live template name). Live theme code, pulled
read-only: `{{LIVE_PATH}}`. Our built pages for comparison render on the QA
theme: `https://<store>/pages/<handle>?preview_theme_id={{QA_THEME}}`.

**Absolute rules.** Nothing touches the live site except page loads and
reading the pulled code — no cart, discount, checkout, newsletter or form
action, no admin writes, no pushes of any kind. No git commands. Write
scratch files under `{{OUT}}/<your-name>/` only; no `.md` files; the report is
a `.txt` there and your final message. One headless Chrome at a time, only
through `live-parity.py` (its slot guard, `LIVE_PARITY_SLOTS=3`), widths in
sequence, no background loops; an HTTP 429 means stop for five minutes. Mark
anything you did not verify **UNVERIFIED**.

**Per enabled live section, in live order:** key, live type, exact copy
(extract per section from the live HTML into `text-<handle>.txt`; desktop and
phone variants where they differ; claims, footnotes and quote attributions
verbatim), behaviour (sliders, accordions, tabs, anchors, sticky bars, hover,
video, anything that hides by viewport or UTM), per-handle differences where
two handles share a template. Then the **honest diff**: (a) already built —
an existing template carries the same content: name the template and key;
(b) copy of built — same section, new content: give the exact settings;
(c) genuinely new — nothing in `sections/` and `docs/sections/*.md` does it:
give an additive spec (where it extends, setting names, defaults). Read the
section schemas before declaring a gap. Measure live at 393/768/1024/1440
only where the nearest built section differs.

**Also:** the offer (products, variants, selling plans, prices, line
properties, discount codes, what the buttons add), the chrome live really
shows, every image and where it lives, and a compliance list — every claim
and every odd line, copied verbatim.

**Report** (plain text, under 250 lines): headlines (reuse vs new, counts);
the section table per template; the copy diff; offer, cart and chrome; gaps
with specs; assets; unverified items and real questions. Reply with a
40-line summary: the headline gaps and the decisions the lead must take.

---

## Part 3 — Owner brief

Fill in `{{BATCH}}`, `{{DEV_THEME}}`, `{{FRAGMENTS}}`, `{{LOG}}`, `{{BUDGET}}`; one brief, all owner agents, each with its own file list.

---

You own one section (or one template's content) in landing batch `{{BATCH}}`.
Other agents own others; stay inside your files. Read `CLAUDE.md`,
`.claude/rules/`, the recon report for your pages, and
`docs/sections/<name>.md` plus the schema for every section you touch.

**How we work.** Template content is per-page data. A different look is an
existing setting. A new setting only when no existing one reaches live's
measured numbers, and **additive**: it defaults to the old behaviour, existing
ids, blocks and markup unchanged, inserted next to the related setting (not
at the end of the array — the parallel batch appends there, and that keeps
the merge clean). CSS only in a `/* Batch {{BATCH}}: <what> */` block at the end
of the asset, mobile-first `min-width` queries at the breakpoints the theme
settled on. A **new section** only when nothing equivalent exists, written
generic — no page names in logic. Before the first edit of a shared file,
append one line to `{{LOG}}`: `[B{{BATCH}}] <time> PLANNED <file> <what>`;
read what the parallel batch logged and reuse its setting if it already
added the thing you need. Re-read a shared file right before editing it;
small exact-string edits, never whole-file rewrites.

**Locale.** Schema labels are `t:` keys. Reuse `labels.*` and `general.*`
first; new keys go only in `{{FRAGMENTS}}/<your-id>.json`
(`{"schema": {...}, "storefront": {...}}`, see `merge-locale-fragments.py`).
Your budget is `{{BUDGET}}` keys; report the exact count, and propose the
cheapest cut rather than overspend.

**Pushing.** Only through `sh .claude/scripts/push-dev-theme.sh --fragments
{{FRAGMENTS}} <paths>` to the dev theme `{{DEV_THEME}}`; read its output —
it fails on a rejection. Test your bands in a throwaway template
`templates/page.zzt-<your-id>.json`, previewed with `&view=zzt-<your-id>`.
Never leave the dev theme broken; other agents share it. Never push anywhere
else.

**Proof.** `live-parity.py section` per band at 1440 and 393 (768 and 1024
once at the end): target 0.0–0.5%; one deliberate look at the side-by-side.
Tablet clean where live's tablet is broken. One Chrome pair at a time through
the slot guard; `LIVE_PARITY_SLOTS=3`; pause two minutes between consecutive
runs of a loop; stop five minutes on a 429.

**Gates before you report:** `check-conventions.py --changed --block`,
`check-section-contract.py --files`, `check-json.py`,
`check-docs-interpolation.py`; a `range` on-step with at most 101 steps; no
`<br>` in `inline_richtext`; claims verbatim (asterisks, trademark signs,
curly quotes, double spaces where live has them). No git. No `.md` files —
return the docs text for every section you extended as a block per file.
Nothing touches live; click tests only with `commerce-check.py` or
`live-parity.py states`, never a form submitted on the real store.

**Report** (under 120 lines): per band — section and settings used, diff at
1440/393, what remains and why; every file changed, one line each, logged;
new settings with defaults; locale key count; consumers of each extended
section (`grep -l '"type": "<name>"' templates/*.json`); docs blocks;
UNVERIFIED items; real questions.

---

## Part 4 — Page-pass brief

Fill in `{{TEMPLATE}}`, `{{HANDLES}}`, `{{DEV_THEME}}`, `{{LOG}}`; one agent per template.

---

The template `{{TEMPLATE}}` renders on the dev theme `{{DEV_THEME}}` for the
handles `{{HANDLES}}`. Your job is the **page**: make it match live as a
whole at 393, 768, 1024 and 1440 (1920 if time), design and behaviour. Read
`CLAUDE.md`, the recon report, and `.claude/skills/verify-against-reference/SKILL.md`.

**The template file is the source of truth** — edit `templates/page.{{TEMPLATE}}.json`
directly; never re-run assemblers. Own only your template. A section file
changes only when a template setting cannot do it, additive, CSS in a
`/* Batch flow: <your-id> */` tail, logged first in `{{LOG}}`, and never a
shared section's default look (the orchestrator proves 0.0% on a consumer
outside the batch at the end).

**In order, per page:**

1. **Junctions** — `live-parity.py page` at the four widths: per-section top,
   height and span, live against ours; fix every junction off by more than
   1.5 px with template settings first.
2. **Whole page and per section** — `page` and `section`; separate real gaps
   from noise by freezing both sides; look at the side-by-side yourself.
3. **Chrome** — header, announcement and footer against live at the four
   widths; report differences, do not edit `layout/`, the header or the
   footer.
4. **Hover and click-through** — `hoverstyles` and `states` with a real
   pointer: every link, button, card, tab, arrow; accordions open and close;
   carousels' arrows, dots and swipe at 393; anchors land where live's do;
   sticky elements. `commerce-check.py` if the page adds to cart.
5. **Detail** — gutters at every width, every section on the phone, images
   (alt text, no layout shift), console errors against live, exact copy per
   section word for word including claims, links, superscripts and
   attributions; app widgets load.
6. Push every change through `push-dev-theme.sh` and re-measure; stop when
   what remains is explained noise or a decided difference. About 75 minutes.

**Rules.** Nothing touches live. No git, no `.md`. One Chrome at a time
through the slot guard, `LIVE_PARITY_SLOTS=3`, pauses between runs, stop on a
429. Decided differences (tablet clean where live is broken, live bugs that
break function not copied, chrome only as live shows it, scripts not ported)
are listed, not "fixed" back to live.

**Report** (under 100 lines): per page and width, the whole-page diff, the
junctions fixed and what remains and why; every template and section change
with exact setting names; the hover and click-through table live against
ours; differences kept and decided; live bugs not copied; claims copied as
live; UNVERIFIED items; open questions that are real blockers.

---

## Part 5 — When two batches run at once

One file, in the workspace both sessions can see, named for both batches
(`CROSS-BATCH-<N><M>.md`). Format: `[B<N>] <date> <time> <file> <what>`.

- The first line of each batch: session started, branch, dev theme id, locale
  key count, budget.
- Before any edit of a shared section, asset or snippet: `PLANNED <file>
  <setting>`. The other batch reads the log and reuses the setting rather
  than adding a twin.
- Findings the other batch needs: a shared live key already built, a
  measured breakpoint, a decision taken.
- Whoever finishes first merges first; the second merges the project tip
  again and resolves: the schema locale is the project's plus your fragments,
  recounted; CSS and JS tails are the project's file plus your own marked
  tail, brace-balanced.

Identical hunks merge cleanly, so when both batches need the same change to a
shared file, one carries the other's patch verbatim and says so in the log.

---

## Budget

Six to nine hours for three pages on a built library, most of it the page
pass. The first batch of a store is two days: it builds the library the later
batches reuse, and the recon is longer because nothing is built yet.
