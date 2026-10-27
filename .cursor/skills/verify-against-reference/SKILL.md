---
name: verify-against-reference
description: Compare a rendered theme page or section against its reference — a Figma frame at the exact breakpoint widths, or the live storefront section by section — and produce a measured fidelity report: pixel diff percentage, heatmap, box-by-box table, and what was actually seen. Use proactively after building or changing anything from a design or from a live page and before reporting it done; also when asked to check fidelity, compare against the design or against live, or audit parity.
argument-hint: <url> <fileKey> <node>@<width>... --slug <name> | --live <url> --key <section-key>
---

# verify-against-reference

Files on disk — a number, a heatmap, a table — and one deliberate look at the
side-by-side; a build is not done until the report is newer than the last
change. **The number is a report, not a gate:** Figma and Chrome rasterise
fonts differently, so a 4% diff can be perfect and a 1% diff can hide an
empty column; read it with the heatmap and the table. Against live, two
Chrome renders of the same store reach **0%**.

## The reference

Named in the brief and in `docs/ai-workflow/reference-map.md`. If the brief
does not say, ask.

| Reference | What it is the source of | Verified by |
|---|---|---|
| **Figma** | layout, spacing, type, colour, states — never data | the per-breakpoint steps below |
| **Live** | what the section does and looks like today, its copy and its data shape — never its code | `live-parity.py`, section by section |
| **Both** | Figma for the look, live for behaviour, copy and data | the Figma steps for the look; `live-parity.py states` for behaviour |

## Inputs — ask, do not guess

- **URL** of the rendered page: the dev server (`http://127.0.0.1:9292/…`)
  or the development theme's preview URL
  (`https://<store>/<path>?preview_theme_id=<id>`, id from `shopify theme
  list`). Confirm it responds: `curl -sI <url> | head -1`.
- **Figma:** the **file key** and **one node id per breakpoint** with its
  design width: `27:3681@1440 27:5246@390`. Never guess a node id.
- **Live:** the **live page URL** and the **section** on each side — a key
  (`--key`: `[id$="__KEY"]` on live, `[id$="KEY"]` on ours) or two selectors.
- **Slug** for the report directory; optional **section selector** for one
  band of a longer page. A band scoped out — "Header", "Footer" — gets
  `get_metadata` first: confirm each child exists elsewhere.

`$ARGUMENTS` may carry all of these: `<url> <fileKey> <node>@<width> [<node>@<width>] --slug <name> [--section <css-selector>]`
or `--live <live-url> --key <section-key> --widths 1440,393 --slug <name>`.

Work in `.claude/verify/<slug>/`; gitignored, copied out at the end if kept.

## Against a Figma frame — per breakpoint

### 1. The frame, at native size

`get_screenshot` with `maxDimension` at least the frame's longer edge (if
`width` comes back below `original_width`, call again with the larger of
`original_width` and `original_height`). Download:

```bash
curl -sL --max-time 60 -o .claude/verify/<slug>/figma-<width>.png "<image_url>"
```

The URL is short-lived: on an error or an HTML page, call again.

### 2. The page, at the same width and height

```bash
sh .claude/scripts/render-screenshot.sh "<url>" <width> <frame-height> .claude/verify/<slug>/rendered-<width>.png
```

Render against the `theme-verify` server (port 9293, `--live-reload off`, in
`.claude/launch.json`): hot reload holds a connection open and the render
never settles. Without Chrome, use the browser tools at exactly `<width>` and
say so. The renderer refuses a wrong `clientWidth` or a flat-colour capture.

**One section of a page:** `document.querySelector('<section-selector>').getBoundingClientRect().top + window.scrollY`
in the browser tools is the section's top; pass it to `compare.py` as
`--rendered-offset-y` and render `<frame-height>` plus that offset.

**An interaction state** — drawer, modal, mega menu, accordion open —
`--eval` runs JavaScript after the page settles and before the capture:

```bash
python3 .claude/scripts/render-screenshot.py "<url>" <width> <frame-height> \
  .claude/verify/<slug>/rendered-<width>-open.png \
  --eval "document.querySelector('<opener-selector>').click()" --eval-settle-ms 1200
```

If the expression throws, nothing is written and the exit is non-zero. The
state's frame has its own node id: one more breakpoint. A `<dialog>` with the
theme's `scroll-lock` attribute stalls the capture — remove it in the `--eval`
first. A cart mutation is awaited on `cart:change`, never a fixed sleep.

### 3. Mask what the store supplied

In the browser tools, paste `.claude/scripts/measure-boxes.js` and run
`MASKS()` — `x,y,w,h` for every `data-verify-mask` element; pass each as
`--mask`. Without the browser tools, say in the report by how much the
unmasked diff is inflated.

### 4. The pixel diff

```bash
python3 .claude/scripts/compare.py \
  --reference .claude/verify/<slug>/figma-<width>.png \
  --rendered .claude/verify/<slug>/rendered-<width>.png \
  --out .claude/verify/<slug> --width <width> --slug <slug> \
  [--rendered-offset-y <top>] [--mask x,y,w,h ...]
```

Prints `diff_pct`, `compared_height`, `height_delta` and `worst_bands`; writes
`diff-<width>.png`, `side-by-side-<width>.png` and `side-by-side-<width>-preview.png`.

### 5. The box table — arithmetic, not prose

Five to ten layout-bearing elements per breakpoint — container, columns or
cards, heading, primary button, body text, image — named after Figma layers.

- **Figma side:** `get_metadata` gives every layer's `x y width height`;
  subtract the frame's own `x y`; type and colour from `get_variable_defs`.
  Write `.claude/verify/<slug>/figma-boxes-<width>.json`.
- **Rendered side:** `MEASURE({ "<layer name>": "<css selector>", … })` with
  `measure-boxes.js` loaded, at exactly `<width>`, saved as
  `rendered-boxes-<width>.json` (minus the section's top if offset).

```bash
python3 .claude/scripts/fidelity-table.py \
  .claude/verify/<slug>/figma-boxes-<width>.json \
  .claude/verify/<slug>/rendered-boxes-<width>.json --tolerance 2 \
  --json .claude/verify/<slug>/table-<width>.json
```

Without the browser tools the table goes under **unverified**, not passed.
Compare spans as well as heights: collapsing and negative margins move a band
whose own height matches.

### 6. Look, once

Open `side-by-side-<width>-preview.png` with the Read tool and write down
what you **see** — an empty media column, a heading wrapping, a missing hover
— then compare with `worst_bands`; a hot band you cannot explain is a finding.
The table misses a custom element at its default `display: inline` and a
synthesised font weight (`.claude/references/layout-pitfalls.md`).

## Against live — per section

One command renders both sides in headless Chrome at every width: viewport
and rendered theme (`Shopify.theme`) asserted, a Chrome profile per side (a
leaked preview cookie makes "live" render ours), lazy media forced, overlays
hidden, animations finished, carousels reset, each side captured twice.

```bash
python3 .claude/scripts/live-parity.py section \
  --live-url "https://<store>/pages/<handle>" \
  --ours-url "https://<store>/pages/<handle>?preview_theme_id=<dev-theme-id>&view=<suffix>" \
  --key <section-key> --widths 1440,393 --out .claude/verify/<slug>
```

- Our side is the **development theme's preview URL** on the store's domain,
  so fonts, apps and cookies match. The dev server
  (`--ours-url http://127.0.0.1:9292/…`) needs `--ours-theme any`, unasserted.
- Static sections (`#shopify-section-header`) take `--live-sel` and
  `--ours-sel`; fixed or sticky also `--keep-fixed`.
- Iterate at `--widths 1440,393` plus the pair either side of each live
  breakpoint (`749,750`); the full default list once, at the end.
- **Laptop rules are built in:** one Chrome pair per run, reused for every
  width; `LIVE_PARITY_SLOTS` caps concurrent runs; both closed on exit. Never
  in parallel or in the background.

Read `report.md` in `--out`, per width: **diff %** and **worst bands** with
`status` (`compared`; `hidden-both`, fine; `hidden-one-side`, a real
difference); **the element table** — every text element and media box paired
live↔ours, with the box delta and the computed-style delta (family, size,
line height, weight, letter spacing, colour, transform, decoration,
background, border, radius, shadow, object-fit, wrap count, image file,
srcset candidate, painted font), chased only when a box is off; **unpaired
live / ours**; **unstable L/O** (explain what still moves); **notes** —
unloaded images, failed fonts, overflow (`--include-overflow` captures it).
**Target 0%**, every remaining pixel located — never "noise".

The other subcommands, when the section has behaviour:

| Subcommand | Answers |
|---|---|
| `states --steps '[{"do":"click","sel_live":"…","sel_ours":"…"},{"do":"wait","ms":700}]'` | does it match after an interaction (accordion open, slide 2, modal, focus)? A pointer step whose target is covered is refused, so a state never entered is never compared |
| `hoverstyles` | what `:hover` / `:focus-visible` / `:active` change on live, and do we change the same things |
| `motion --trigger click:SEL --el-live … --el-ours … --keyframes` | the same transitions and animations — exact timing from the Web Animations seen, and the sampled curve |
| `page --live-url … --ours-url …` | where on the whole page live and ours start to diverge: per-section top and height, the first section whose top moves |
| `regress --url … --main-theme <id> --ours-theme <id>` | did extending an existing section change it at its defaults, QA-approved theme against ours |

`page` first on a page that drifts: it names the first section whose top moves.

## Functional — the purchase path

When the change touches the product form, quick add, selling plans, the cart
drawer or page, discount codes or localization, run it and quote its numbers:

```bash
python3 .claude/scripts/commerce-check.py --url "<dev theme product page URL>" \
  --widths 393,768,1024,1440 [--discount-code <code>] [--market <CC>] --out .claude/verify/commerce
```

Per width it submits the real product form and reads the result from
`cart:change`, checks the drawer and count, changes quantity and asserts
properties and plan survived, applies a discount code and reads `/cart.js`,
removes the line, switches market and back. It refuses a page that rendered
the live theme, blocks analytics, never reaches checkout, empties the cart.

Three rows it cannot automate go in the report and a person walks them:
**logged in** (log in once in the browser pane; the script enters no
credentials), **Safari** on iPhone and Mac (`dvh`, date inputs, `:has()`,
sticky bars), the **checkout handoff**. The QA checklist carries the same.

## The report

`report.json` is what the Stop hook and `/goal` read; `report.md` is for a
human. `.claude/verify/<slug>/report.json`:

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
`frames` entry per width from `live-parity.py`'s own `report.json`: `width`,
`diff_pct`, `status`, `box_off`, `unpaired`, `unstable`, `worst_bands`, plus
`seen` and `unverified`. One shape, so `verify-status.py` reads either.

`report.md`: one section per breakpoint — numbers, table, **seen**,
**unverified**, verdict; if you fixed and re-ran, keep both runs. A page
handoff or parity audit copies it and the preview to `docs/ai-workflow/verify/<slug>/`.

## Reporting back

Say the numbers: "1440: 3.4% diff, 1 box off (grid gap 20 vs 24), media column
renders; 390: 2.1%, table clean." Live: "1440: 0.0%, 393: 0.4% — the chat
bubble, masked on neither side." Never "matches the design"; never a
percentage without the heatmap looked at. List what you could not verify.

## Where this runs

- `build-page-from-figma` Step 4; `build-section-from-live` §4 for the live
  half; the parallel-section-build orchestrator per band after assembly.
- The Stop hook warns when section or snippet files changed with no newer
  report, or a purchase-path file with no newer commerce report; never blocks.
- A `/goal` can name `diff_pct` and the table: *"report.json exists for
  product-ingredients with diff_pct under 5 at 1440 and 390 and table_off 0,
  and the pre-commit gate passes"* — for live, *"diff_pct 0 at every width
  and unpaired 0"*.
