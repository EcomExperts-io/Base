---
name: verify-against-reference
description: Compare a rendered theme page or section against its reference — a Figma frame at the exact breakpoint widths, or the live storefront section by section — and produce a measured fidelity report: pixel diff percentage, heatmap, box-by-box table, and what was actually seen. Use proactively after building or changing anything from a design or from a live page and before reporting it done; also when asked to check fidelity, compare against the design or against live, or audit parity.
argument-hint: <url> <fileKey> <node>@<width>... --slug <name> | --live <url> --key <section-key>
---

# verify-against-reference

Evidence, not assertion. This skill ends with files on disk that say how far
the rendered page is from its reference — a number, a heatmap, a table — and
one deliberate look at the side-by-side image. A build is not done until this
has run and its report is newer than the last change to the section.

**Why this exists.** Verification used to be "screenshot both and look", and
the worst failure the workflow has recorded came from it: a section reported as
matching because it measured 614px against a 615px frame while its media column
rendered empty. Agents graded their own work from memory. Here the only things
that count are files this skill wrote.

**The number is a report, not a gate.** Font rasterisation and anti-aliasing
differ between Figma and Chrome; a 4% diff can be a perfect build and a 1%
diff can hide an empty column. Read the percentage with the heatmap and the
table. Against live the bar is different: two Chrome renders of the same store
should reach **0%**, and every remaining pixel is explained by locating it.

## The reference

A page or section has one of three references, named in the brief and in the
repo's reference map (`docs/ai-workflow/reference-map.md`; the older
`figma-frame-map.md` is the same thing with only the Figma columns):

| Reference | What it is the source of | Verified by |
|---|---|---|
| **Figma** | layout, spacing, type, colour, states — never data | the per-breakpoint steps below |
| **Live** | what the section does and looks like today, its copy and its data shape — never its code | `live-parity.py`, section by section |
| **Both** | Figma for the look, live for behaviour, copy and data | the Figma steps for the look; `live-parity.py states` for behaviour |

If the brief does not say which, ask. Guessing verifies against the wrong
thing, which is worse than not verifying.

## Inputs — ask, do not guess

- **URL** of the rendered page: the dev server (`/run-theme`, normally
  `http://127.0.0.1:9292/…`) or the development theme's preview URL
  (`https://<store>/<path>?preview_theme_id=<id>`, id from `shopify theme
  list`). Confirm it responds: `curl -sI <url> | head -1`.
- **Figma:** the **file key** and **one node id per breakpoint**, each with
  the width it was designed at: `27:3681@1440 27:5246@390`. Never guess a
  node id.
- **Live:** the **live page URL** and the **section** on each side — a
  section key (`--key`, matching `[id$="__KEY"]` on live and `[id$="KEY"]`
  on ours) or two CSS selectors.
- **Slug** for the report directory: the section or page name.
- Optional: a **section selector** when verifying one band of a longer page
  against Figma.
- A band you mean to scope out — "Header", "Footer" — gets `get_metadata`
  first: list its children and confirm each exists elsewhere. A blog frame's
  "Header" held the blog's own category nav, which was then built nowhere.

`$ARGUMENTS` may carry all of these: `<url> <fileKey> <node>@<width> [<node>@<width>] --slug <name> [--section <css-selector>]`
or `--live <live-url> --key <section-key> --widths 1440,393 --slug <name>`.

Work in `.claude/verify/<slug>/`. It is gitignored; the report is copied out
at the end if it should be kept.

## Against a Figma frame — per breakpoint

### 1. The frame, at native size

Call the Figma `get_screenshot` tool with `maxDimension` at least the frame's
longer edge (the response reports `original_width`/`original_height`; if the
returned `width` is smaller than `original_width`, call again with
`maxDimension = max(original_width, original_height)`). Download the PNG it
points at:

```bash
curl -sL --max-time 60 -o .claude/verify/<slug>/figma-<width>.png "<image_url>"
```

The URL is short-lived — if the download returns an error or an HTML page,
call `get_screenshot` again for a fresh one. Do not paste the URL into the
report.

### 2. The page, at the same width and height

Render with headless Chrome at the frame's exact width and height so the two
images line up without scrolling:

```bash
sh .claude/scripts/render-screenshot.sh "<url>" <width> <frame-height> .claude/verify/<slug>/rendered-<width>.png
```

If Chrome is unavailable the script says so; fall back to the browser tools —
set the viewport to exactly `<width>` wide, take the screenshot, save it to the
same path — and note in the report that the render came from the browser tool.

The renderer refuses to write a file when the page's `clientWidth` is not the
width requested, or when the capture is one flat colour. Both happened silently
before it did — a 393 request laid out at 501 and cropped, a blank PNG that
diffed at 40% — so a diff that is good at one breakpoint and bad at the other
is a reason to open the screenshot before the code.

**Verifying one section of a page:** open the page in the browser tools, run
`document.querySelector('<section-selector>').getBoundingClientRect().top +
window.scrollY` to get the section's top, and pass it to `compare.py` as
`--rendered-offset-y`. Render the page tall enough to include the section
(`<frame-height>` plus that offset).

**Which server to render against:** the `theme-verify` one (port 9293,
`--live-reload off`, in `.claude/launch.json`), not the hot-reload dev server.
Hot reload holds a connection open, the renderer waits for the network to
settle, and the render never completes. See `/run-theme`.

**Verifying an interaction state** — a drawer, a modal, a mega menu, an
accordion opened — call `render-screenshot.py` directly with `--eval`, which
runs JavaScript in the page after it has settled at the requested viewport and
before the capture:

```bash
python3 .claude/scripts/render-screenshot.py "<url>" <width> <frame-height> \
  .claude/verify/<slug>/rendered-<width>-open.png \
  --eval "document.querySelector('<opener-selector>').click()" --eval-settle-ms 1200
```

If the expression throws, the script writes nothing and exits non-zero — a
state that was never entered must not be diffed as though it had been. The
frame for that state has its own node id; treat it as one more breakpoint.

A `<dialog>` carrying the theme's `scroll-lock` attribute stalls the capture
(`overflow: hidden` on `html` against `captureBeyondViewport`); remove the
attribute in the `--eval` before opening it. A cart mutation in an `--eval` is
awaited on `cart:change`, never a fixed sleep — mutations queue and each
carries a section render, so a stale read looks exactly like a broken cart.

### 3. Mask what the store supplied

Live data never matches a mock. In the browser tools, paste
`.claude/scripts/measure-boxes.js`, then run `MASKS()` — it returns
`x,y,w,h` for every element carrying `data-verify-mask` (see
`html-standards.md`). Pass each as `--mask`. If the browser tools are not
available, skip masking and say so in the report: an unmasked diff over a
product grid is inflated, and the report must say by what.

### 4. The pixel diff

```bash
python3 .claude/scripts/compare.py \
  --reference .claude/verify/<slug>/figma-<width>.png \
  --rendered .claude/verify/<slug>/rendered-<width>.png \
  --out .claude/verify/<slug> --width <width> --slug <slug> \
  [--rendered-offset-y <top>] [--mask x,y,w,h ...]
```

It prints JSON: `diff_pct`, `compared_height`, `height_delta`, and
`worst_bands` — the y-ranges with the most mismatch, which is where to look
first. It writes `diff-<width>.png` (heatmap), `side-by-side-<width>.png`, and
`side-by-side-<width>-preview.png`.

### 5. The box table — arithmetic, not prose

Pick the elements that carry the layout: the container, each column or card,
the heading, the primary button, one body text, one image box — five to ten
per breakpoint, named after the Figma layers.

- **Figma side:** `get_metadata` for the frame gives every layer's `x y width
  height`. Subtract the frame's own `x y` so the values are frame-relative.
  Type sizes and colours come from `get_variable_defs` or the design context.
  Write `.claude/verify/<slug>/figma-boxes-<width>.json`.
- **Rendered side:** in the browser tools, with `measure-boxes.js` loaded,
  run `MEASURE({ "<layer name>": "<css selector>", … })` at exactly `<width>`
  and save the result as `rendered-boxes-<width>.json`. Subtract the section's
  top if you offset the render.
- Compare:

```bash
python3 .claude/scripts/fidelity-table.py \
  .claude/verify/<slug>/figma-boxes-<width>.json \
  .claude/verify/<slug>/rendered-boxes-<width>.json --tolerance 2 \
  --json .claude/verify/<slug>/table-<width>.json
```

Without the browser tools the table cannot be produced; the report then lists
the box comparison under **unverified**, not as passed.

Compare spans as well as heights: each band's top to the next band's top.
Negative and collapsing margins move a band whose own height matches — on
one rebuild two exact bands hid a 96px drift of everything below them.

### 6. Look, once

Open `side-by-side-<width>-preview.png` with the Read tool and write down what
you **see** — not what the numbers say: an empty media column, a heading
wrapping to two lines, a missing hover treatment, a card with the wrong image
ratio, a colour that reads warmer than the frame. Then compare your list with
`worst_bands`. A band the heatmap lights up that you cannot explain is a
finding. Custom elements are a trap here: they default to `display: inline`,
which drops background and vertical padding on screen while `getComputedStyle`
still reports both — the heatmap catches it, the table does not.
A hot band sitting on a single line of text is the face before the layout: a
weight the library has no face for renders synthesised, and `getComputedStyle`
reports the weight you asked for (`.claude/references/layout-pitfalls.md`).

## Against live — per section

One command renders both sides in headless Chrome, at every width, and writes
the report. It closes every trap a live comparison has been seen to fall into: the viewport is
emulated and asserted (never `--window-size`), each side has its own Chrome
profile and the theme it rendered is read from `Shopify.theme` and asserted
(a leaked preview cookie makes "live" render our theme), lazy media is forced
and waited for, fixed overlays and popups are hidden, animations finished,
carousels reset, ours is shifted to live's sub-pixel fraction, and each side
is captured twice so motion the freeze did not stop is reported rather than
averaged away.

```bash
python3 .claude/scripts/live-parity.py section \
  --live-url "https://<store>/pages/<handle>" \
  --ours-url "https://<store>/pages/<handle>?preview_theme_id=<dev-theme-id>&view=<suffix>" \
  --key <section-key> --widths 1440,393 --out .claude/verify/<slug>
```

- Our side is the **development theme's preview URL** on the store's own
  domain, so fonts, apps and cookies match. The local dev server works too
  (`--ours-url http://127.0.0.1:9292/…`) with `--ours-theme any`, and the
  report then says our theme was not asserted.
- `--key` is the live section's key; static sections (`#shopify-section-header`)
  take `--live-sel` and `--ours-sel`. A fixed or sticky section also needs
  `--keep-fixed`.
- Iterate at `--widths 1440,393` plus the pair either side of each breakpoint
  live uses (`749,750`); run the full default list once, at the end. Budget
  15–20 s per width.
- **Laptop rules are built in:** one Chrome pair per run, reused for every
  width; at most two runs on the machine (`LIVE_PARITY_SLOTS`); both browsers
  closed on exit. Never start runs in parallel or in the background.

Read `report.md` in `--out`, per width:

- **diff %** and **worst bands** (section-relative y ranges), with
  `status`: `compared`, `hidden-both` (fine — a desktop-only band at 393), or
  `hidden-one-side` (a real difference, 100%).
- **The element table:** every text element and media box, paired live↔ours
  by text or image file, with the box delta and the computed-style delta
  (family, size, line height, weight, letter spacing, colour, transform,
  decoration, background, border, radius, shadow, object-fit, wrap count,
  image file, srcset candidate, and the font Chrome actually painted with).
  Chase layout-style deltas only when a box is off.
- **Unpaired live / ours:** missing copy, changed text, an extra element.
- **unstable L/O:** something still moves on that side; explain it.
- **Notes:** images that never loaded, failed fonts, content painted outside
  the section box (`--include-overflow` captures it).

**Target 0%.** Explain every remaining pixel by locating it — a chat bubble, a
font-fallback glyph. Never wave it off as noise.

The other subcommands, when the section has behaviour:

| Subcommand | Answers |
|---|---|
| `states --steps '[{"do":"click","sel_live":"…","sel_ours":"…"},{"do":"wait","ms":700}]'` | does it match after an interaction (accordion open, slide 2, modal, focus)? A pointer step whose target is covered is refused, so a state never entered is never compared |
| `hoverstyles` | what `:hover` / `:focus-visible` / `:active` change on live, and do we change the same things |
| `motion --trigger click:SEL --el-live … --el-ours … --keyframes` | the same transitions and animations — exact timing from the Web Animations seen, and the sampled curve |
| `page --live-url … --ours-url …` | where on the whole page live and ours start to diverge: per-section top and height, the first section whose top moves |
| `regress --url … --main-theme <id> --ours-theme <id>` | did extending an existing section change it at its defaults, QA-approved theme against ours |

`page` is the one to run first on a page that drifts: it names the first
section whose top diverges, and the per-section spans find the negative and
collapsing margins a height comparison hides.

## Functional — the purchase path

A pixel report cannot say whether the cart works. When the change touches the
purchase path — the product form, quick add, selling plans, the cart drawer
or page, discount codes, localization — run the commerce check against the
development theme and quote its numbers:

```bash
python3 .claude/scripts/commerce-check.py --url "<dev theme product page URL>" \
  --widths 393,768,1024,1440 [--discount-code <code>] [--market <CC>] --out .claude/verify/commerce
```

Per width it submits the real product form and reads the result from the
engine's `cart:change` (never a sleep), checks the drawer opened and the count
updated, changes the quantity through the stepper link and asserts the line's
properties and plan survived, applies a discount code and reads `/cart.js`
for it, removes the line and expects the empty state, and switches market
through the localization form and back. It refuses a page that rendered the
live theme, blocks analytics hosts, never reaches checkout, and empties the
cart at the end.

Three rows it cannot automate are written into the report as such, and a
person walks them: **logged in** (add, change, remove as a customer — log in
once in the browser pane; the script enters no credentials), **Safari** on an
iPhone and a Mac (WebKit: `dvh`, date inputs, `:has()`, sticky bars), and
the **checkout handoff**. The QA checklist carries the same three rows in
plain English.

## The report

Write both files. `report.json` is what the Stop hook and `/goal` read;
`report.md` is what a human reads.

`.claude/verify/<slug>/report.json`:

```json
{
  "slug": "product-ingredients",
  "reference": "figma",
  "url": "http://127.0.0.1:9292/products/example",
  "fileKey": "…",
  "generated": "2026-09-15T10:42:00",
  "frames": [
    {
      "nodeId": "27:3681", "width": 1440, "diff_pct": 3.4, "compared_height": 1180,
      "height_delta": 12, "masks": 4, "table_off": 1, "table_missing": 0,
      "worst_bands": [{"y0": 640, "y1": 760, "mismatch_pct": 41.2}],
      "seen": ["ingredient grid gap renders 20px, frame says 24px"],
      "unverified": []
    }
  ],
  "verdict": "close — one spacing defect, fixed and re-run below",
  "render_source": "headless-chrome"
}
```

Against live, `"reference": "live"`, `"liveUrl"` in place of `fileKey`, and one
`frames` entry per width copied from `live-parity.py`'s own `report.json`:
`width`, `diff_pct`, `status`, `box_off` (paired elements outside tolerance),
`unpaired`, `unstable`, `worst_bands`, plus `seen` and `unverified` as above.
One shape, so `verify-status.py` and a `/goal` read either.

`report.md`: the same, readable — one section per breakpoint with the
numbers, the table, the **seen** list, the **unverified** list, and the
verdict. If you fixed something and re-ran, keep both runs; the second is the
evidence, the first is the reason.

If the report belongs in the repo (a page handoff, a parity audit), copy
`report.md` and the preview image to `docs/ai-workflow/verify/<slug>/`.

## Reporting back

Say the numbers. "1440: 3.4% diff, 1 box off (grid gap 20 vs 24), media column
renders; 390: 2.1%, table clean." Against live: "1440: 0.0%, 393: 0.4% — the
chat bubble, masked on neither side." Never "matches the design" or "matches
live". Never a percentage without the heatmap having been looked at. List what
you could not verify and why — a report that says "box table unverified: no
browser tools" is worth more than a table typed from memory.

## Where this runs

- `build-page-from-figma` Step 4 calls it before the Notion handoff;
  `build-section-from-live` §4 calls the live half.
- The parallel-section-build orchestrator runs it per section band after
  assembly — agents cannot, because their section is not on a page yet.
- The Stop hook warns when section or snippet files changed and no report is
  newer than the change, and when a purchase-path file changed and no commerce
  report is newer than it. It does not block; a refactor has no reference.
- A `/goal` for a build session can reference `diff_pct` and the table
  directly: *"report.json exists for product-ingredients with diff_pct under 5
  at 1440 and 390 and table_off 0, and the pre-commit gate passes"* — or, for
  live, *"diff_pct 0 at every width and unpaired 0"*.
