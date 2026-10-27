# Workflow — a batch of landing pages, matched to live, with parallel agents

Rebuild a card's worth of landing pages (three to seven, on a few templates)
matched to live, in one session with up to five agents. A human starts this;
for a Figma page use `parallel-section-build.md`.

**The one idea.** A landing page is **template content on a section library**:
a batch adds pages, settings and occasionally a section, never a second copy.
The first job is the honest diff — already built / copy of built / new.

---

## Part 1 — Orchestrator (you)

### 0. Caps, before anything runs

- **At most 5 agents at once**, read-only ones included: 3 for build waves,
  2 for recon, 5 only when the page pass runs one agent per template.
- **At most 3 headless browsers on the machine.** `live-parity.py` and
  `commerce-check.py` take a run slot (`LIVE_PARITY_SLOTS=3`, never higher)
  and close their Chrome on exit. One Chrome pair per agent, widths in
  sequence, never `Promise.all` over pages. Stray browsers older than an hour
  die by PID at the start (`ps -eo pid,etime,args`), **never `pkill -f`**.
- Agents **cannot write `.md` files or touch git**; you save docs and commit.
  An HTTP 429 means stop the Chrome runs for five minutes.

### 1. Arrive: branch, worktree, dev theme, live theme

```bash
git fetch origin && git worktree add ../<repo>-b<N> -b <ticket>/Task-LandingBatch<N> origin/<project-branch>
```

Cut from the **project branch**, never the trunk: it carries every earlier
batch and the library, and moves daily. Merge it into yours early and often.

```bash
shopify theme push --unpublished --theme "<repo>/<ticket>/Task-LandingBatch<N>" --json --path .
```

Write the id it prints to the `dev-theme-id` file in the `.claude` cache
directory (`push-dev-theme.sh --help` names it). The live and QA theme ids go
in `.claude/protected-themes.txt`, one per line; every push goes through
`push-dev-theme.sh`, which refuses them and any theme not development or
unpublished, serialises pushes, waits 25 s after a new section file, and
reads Shopify's rejection out of the output (the CLI exits 0 on one). At the
100-theme cap, ask which merged batch's theme to delete — never delete one.

```bash
shopify theme pull --live --path <scratchpad>/live-current --force
```

Read-only. The live JSON templates (leading `/* */` comment included) give
the section keys and the assembly order.

Start the **cross-batch log** if another batch runs in parallel (Part 5), and
count the schema locale (`check-json.py locales/*.json` warns above 3,300 keys) to set the key budget.

### 2. Recon — read-only, two agents at most

One recon agent per two or three pages, with Part 2 filled in; they return
the per-section map and the honest diff. Show the lead a short scope in chat
— reuse versus new, the one or two decisions — and keep going; ask only when
blocked. A HEAD request first: a page that is 404 or 301 on live gets nothing.

### 3. Templates first, then the few new sections

Build the templates under **live's own names** (`page.<live-template>.json`,
odd casing included), so no admin switch is needed; a page on the plain page
template needs one at go-live — flag it. Recon content comes as fragments:

```bash
python3 .claude/scripts/assemble-templates.py --fragments <dir> --templates <a,b> --live-path <scratchpad>/live-current [--layout landing] --write
```

It keeps live's order, validates every setting against the section schemas
(ranges on step, select values, `richtext` shape, no `<br>` in
`inline_richtext`, no `t:` value, no unknown setting — Shopify rejects or
drops each silently), refuses to write on any error, and from then on the
template file is the source of truth.

Owner agents (Part 3) build only the genuine gaps, at most three at a time.
Every change to a shared section is **additive** — new settings default to
the old behaviour, existing ids, blocks and markup unchanged, CSS in a marked
`/* Batch N: … */` tail — logged in the cross-batch file first; proved in step 5.

### 4. The page pass — one agent per template

With the templates on the dev theme, one agent per template takes the page
as a whole against live at 393, 768, 1024 and 1440 (1920 if time), in the
order Part 4 lists. Tablet is **clean** where live's tablet layout is broken;
a live bug that hides content is reproduced, one that breaks function is
listed, not copied. Tracking, A/B scripts, newsletter attach scripts and
site-wide auto gifts are not ported; list them.

### 5. Regression, gate, PR

For every shared section this batch extended, compare a consumer page
**outside the batch** on the QA theme against the dev theme at defaults:

```bash
python3 .claude/scripts/live-parity.py regress --url "https://<store>/pages/<consumer>" --main-theme <qa-theme-id> --ours-theme <dev-theme-id> --key <section-key> --widths 1440,393 --out .claude/verify/regress-<key>
```

0.0% or the change is not additive. Merge the project branch into yours (the
schema locale and CSS tails conflict: the project's file plus your fragments
and tail, brace-balanced), gate, push, PR into the project branch,
`/gitbot-preflight`. Merge only when the lead says so, in chat.

### 6. Hand off

Preview links to the lead in chat first. Then one comment on the card:
GitHub details, theme name and id, live and preview links in pairs, dev notes
(reused, new, decisions, live bugs not copied, not ported, not covered),
open questions, and the QA checklist (`build-page-from-figma` Step 6,
purchase-path rows included). One sub-task per real page. Delete the dev
theme only when asked; `/record-incident` before the session ends.

---

## Part 2 — Recon brief

Fill in `{{PAGES}}`, `{{LIVE_PATH}}`, `{{OUT}}`, `{{QA_THEME}}`; one brief, all recon agents.

---

You are a read-only recon agent for a landing-page batch on a Base theme: you
measure and map, you build nothing. Read `CLAUDE.md` and `.claude/rules/` first.

**Pages:** `{{PAGES}}` (live URL, live template name). Live theme code, pulled
read-only: `{{LIVE_PATH}}`. Our built pages: `https://<store>/pages/<handle>?preview_theme_id={{QA_THEME}}`.

**Absolute rules.** Nothing touches the live site except page loads and
reading the pulled code — no cart, discount, checkout, newsletter or form
action, no admin writes, no pushes. No git. Scratch files under
`{{OUT}}/<your-name>/` only; no `.md` files; the report is a `.txt` there and
your final message. One headless Chrome at a time, only through
`live-parity.py` (`LIVE_PARITY_SLOTS=3`), widths in sequence, no background
loops; stop five minutes on a 429. Mark what you did not verify **UNVERIFIED**.

**Per enabled live section, in live order:** key, live type, exact copy
(from the live HTML into `text-<handle>.txt`; desktop and phone variants;
claims, footnotes and attributions verbatim), behaviour (sliders, accordions,
tabs, anchors, sticky bars, hover, video, anything hidden by viewport or
UTM), per-handle differences where two handles share a template. Then the
**honest diff**: (a) already built — name the template and key; (b) copy of
built — same section, new content: the exact settings; (c) genuinely new —
nothing in `sections/` and `docs/sections/*.md` does it: an additive spec
(where it extends, setting names, defaults); read the section schemas before
declaring a gap. Measure live at 393/768/1024/1440 only where the nearest built section differs.

**Also:** the offer (products, variants, selling plans, prices, line
properties, discount codes, what the buttons add), the chrome live shows,
every image and where it lives, every claim and odd line verbatim.

**Report** (plain text, under 250 lines): headlines (reuse vs new, counts);
the section table per template; the copy diff; offer, cart and chrome; gaps
with specs; assets; unverified items; real questions. Reply with a 40-line
summary: the headline gaps and the decisions the lead must take.

---

## Part 3 — Owner brief

Fill in `{{BATCH}}`, `{{DEV_THEME}}`, `{{FRAGMENTS}}`, `{{LOG}}`, `{{BUDGET}}`; one brief, all owner agents, each with its own file list.

---

You own one section (or one template's content) in landing batch `{{BATCH}}`;
stay inside your files. Read `CLAUDE.md`, `.claude/rules/`, the recon report
for your pages, and `docs/sections/<name>.md` plus the schema of every section you touch.

**How we work.** Template content is per-page data. A different look is an
existing setting. A new setting only when no existing one reaches live's
measured numbers, and **additive**: defaults to the old behaviour, existing
ids, blocks and markup unchanged, inserted next to the related setting (not
at the end of the array — the parallel batch appends there). CSS only in a
`/* Batch {{BATCH}}: <what> */` block at the end of the asset. A **new
section** only when nothing equivalent exists. Before the first edit of a
shared file, append to `{{LOG}}`: `[B{{BATCH}}] <time> PLANNED <file> <what>`,
and reuse what the parallel batch already logged. Re-read a shared file right
before editing it; small exact-string edits, never whole-file rewrites.

**Locale.** Reuse `labels.*` and `general.*` keys first; new keys go only in
`{{FRAGMENTS}}/<your-id>.json` (`{"schema": {...}, "storefront": {...}}`, see
`merge-locale-fragments.py`). Budget `{{BUDGET}}` keys; report the exact
count and propose the cheapest cut rather than overspend.

**Pushing.** Only through `sh .claude/scripts/push-dev-theme.sh --fragments
{{FRAGMENTS}} <paths>` to the dev theme `{{DEV_THEME}}`; read its output, it
fails on a rejection. Test your bands in a throwaway template
`templates/page.zzt-<your-id>.json` (`&view=zzt-<your-id>`). Never leave the
dev theme broken; other agents share it.

**Proof.** `live-parity.py section` per band at 1440 and 393 (768 and 1024
once at the end): target 0.0–0.5%; one deliberate look at the side-by-side.
Tablet clean where live's tablet is broken. One Chrome pair at a time,
`LIVE_PARITY_SLOTS=3`; two minutes between runs; stop five minutes on a 429.

**Gates before you report:** `check-conventions.py --changed --block`,
`check-section-contract.py --files`, `check-json.py`,
`check-docs-interpolation.py`; a `range` on-step with at most 101 steps; no
`<br>` in `inline_richtext`; claims verbatim (asterisks, trademark signs,
curly quotes, double spaces). No git. No `.md` files — return the docs text
for every extended section as a block per file. Nothing touches live; click
tests only with `commerce-check.py` or `live-parity.py states`.

**Report** (under 120 lines): per band — section and settings used, diff at
1440/393, what remains and why; every file changed, one line each; new
settings with defaults; locale key count; consumers of each extended section
(`grep -l '"type": "<name>"' templates/*.json`); docs blocks; UNVERIFIED; questions.

---

## Part 4 — Page-pass brief

Fill in `{{TEMPLATE}}`, `{{HANDLES}}`, `{{DEV_THEME}}`, `{{LOG}}`; one agent per template.

---

The template `{{TEMPLATE}}` renders on the dev theme `{{DEV_THEME}}` for the
handles `{{HANDLES}}`. Your job is the **page**: match live as a whole at
393, 768, 1024 and 1440 (1920 if time), design and behaviour. Read `CLAUDE.md`,
the recon report, and `.claude/skills/verify-against-reference/SKILL.md`.

**The template file is the source of truth** — edit `templates/page.{{TEMPLATE}}.json`
directly; never re-run assemblers. Own only your template. A section file
changes only when a setting cannot do it: additive, CSS in a
`/* Batch flow: <your-id> */` tail, logged in `{{LOG}}`, never a shared default look.

**In order, per page:**
1. **Junctions** — `live-parity.py page` at the four widths; fix every
   junction off by more than 1.5 px with template settings first.
2. **Whole page and per section** — `page` and `section`; separate real gaps
   from noise (video, GIF, marquee, fractional raster) by freezing both
   sides; look at the side-by-side yourself.
3. **Chrome** — header, announcement and footer against live at the four
   widths; report differences, edit none of them.
4. **Hover and click-through** — `hoverstyles` and `states` with a real
   pointer: every link, button, card, tab, arrow; accordions; carousel arrows,
   dots and swipe at 393; anchors; sticky elements. `commerce-check.py` if the
   page adds to cart; nothing is submitted on live.
5. **Detail** — gutters at every width, every section on the phone, images
   (alt text, no layout shift), console errors against live, exact copy
   including claims, links, superscripts and attributions; app widgets load.
6. Push through `push-dev-theme.sh` and re-measure; stop when what remains is
   explained noise or a decided difference. About 75 minutes.

**Rules.** Nothing touches live. No git, no `.md`. One Chrome at a time
through the slot guard, `LIVE_PARITY_SLOTS=3`, pauses between runs, stop on a
429. Decided differences (tablet clean where live is broken, function-breaking
live bugs, chrome as live shows it, scripts not ported) are listed, not "fixed".

**Report** (under 100 lines): per page and width, the whole-page diff, the
junctions fixed and what remains and why; every template and section change
with exact setting names; the hover and click-through table live against
ours; decided differences; live bugs not copied; UNVERIFIED; real blockers.

---

## Part 5 — When two batches run at once

One file both sessions can see, `CROSS-BATCH-<N><M>.md`, lines formatted
`[B<N>] <date> <time> <file> <what>`:

- First line of each batch: session started, branch, dev theme id, locale key count, budget.
- Before any edit of a shared section, asset or snippet: `PLANNED <file>
  <setting>`; the other batch reuses the setting rather than adding a twin.
- Findings the other batch needs: a shared live key already built, a
  measured breakpoint, a decision taken.
- Whoever finishes first merges first; the second merges the project tip
  again (locale: project's plus your fragments, recounted; CSS and JS tails:
  project's file plus your marked tail). When both need the same change to a
  shared file, one carries the other's patch verbatim and says so in the log.

---

## Budget

Six to nine hours for three pages on a built library, most of it the page
pass; a store's first batch is two days — it builds the library.
