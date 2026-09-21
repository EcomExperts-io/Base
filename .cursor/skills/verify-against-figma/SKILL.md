---
name: verify-against-figma
description: Compare a rendered theme page or section against its Figma frames at the exact breakpoint widths and produce a measured fidelity report — pixel diff percentage, heatmap, box-by-box table, and what was actually seen. Use proactively after building or changing anything from a Figma design and before reporting it done; also when asked to check fidelity, compare against the design, or audit parity.
---

# verify-against-figma

Evidence, not assertion. This skill ends with files on disk that say how far
the rendered page is from the frame — a number, a heatmap, a table — and one
deliberate look at the side-by-side image. A build is not done until this has
run and its report is newer than the last change to the section.

**Why this exists.** Verification used to be "screenshot both and look", and
the worst failure the workflow has recorded came from it: a section reported as
matching because it measured 614px against a 615px frame while its media column
rendered empty. Agents graded their own work from memory. Here the only things
that count are files this skill wrote.

**The number is a report, not a gate.** Font rasterisation and anti-aliasing
differ between Figma and Chrome; a 4% diff can be a perfect build and a 1%
diff can hide an empty column. Read the percentage with the heatmap and the
table. Gating on a threshold comes later, once two or three builds have shown
what a good number looks like for this theme.

## Inputs — ask, do not guess

- **URL** of the rendered page: the dev server (`/run-theme`, normally
  `http://127.0.0.1:9292/…`) or a preview URL. Confirm it responds:
  `curl -sI <url> | head -1`.
- **Figma file key** and **one node id per breakpoint**, each with the width
  it was designed at: `27:3681@1440 27:5246@390`. Never guess a node id; a
  wrong guess verifies against the wrong design, which is worse than not
  verifying.
- **Slug** for the report directory: the section or page name, e.g.
  `product-ingredients`.
- Optional: a **section selector** when verifying one band of a longer page.

`$ARGUMENTS` may carry all of these: `<url> <fileKey> <node>@<width> [<node>@<width>] --slug <name> [--section <css-selector>]`.

## Steps — per breakpoint

Work in `.claude/verify/<slug>/`. It is gitignored; the report is copied out
at the end if it should be kept.

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
  --figma .claude/verify/<slug>/figma-<width>.png \
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

### 6. Look, once

Open `side-by-side-<width>-preview.png` with the Read tool and write down what
you **see** — not what the numbers say: an empty media column, a heading
wrapping to two lines, a missing hover treatment, a card with the wrong image
ratio, a colour that reads warmer than the frame. Then compare your list with
`worst_bands`. A band the heatmap lights up that you cannot explain is a
finding. Custom elements are a trap here: they default to `display: inline`,
which drops background and vertical padding on screen while `getComputedStyle`
still reports both — the heatmap catches it, the table does not.

## The report

Write both files. `report.json` is what the Stop hook and `/goal` read;
`report.md` is what a human reads.

`.claude/verify/<slug>/report.json`:

```json
{
  "slug": "product-ingredients",
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

`report.md`: the same, readable — one section per breakpoint with the
numbers, the table, the **seen** list, the **unverified** list, and the
verdict. If you fixed something and re-ran, keep both runs; the second is the
evidence, the first is the reason.

If the report belongs in the repo (a page handoff, a parity audit), copy
`report.md` and the preview image to `docs/ai-workflow/verify/<slug>/`.

## Reporting back

Say the numbers. "1440: 3.4% diff, 1 box off (grid gap 20 vs 24), media column
renders; 390: 2.1%, table clean." Never "matches the design". Never a
percentage without the heatmap having been looked at. List what you could not
verify and why — a report that says "box table unverified: no browser tools"
is worth more than a table typed from memory.

## Where this runs

- `build-page-from-figma` Step 4 calls it before the Notion handoff.
- The parallel-section-build orchestrator runs it per section band after
  assembly — agents cannot, because their section is not on a page yet.
- The Stop hook warns when section or snippet files changed and no report is
  newer than the change. It does not block; a refactor has no frame.
- A `/goal` for a build session can reference `diff_pct` and the table
  directly: *"report.json exists for product-ingredients with diff_pct under 5
  at 1440 and 390 and table_off 0, and the pre-commit gate passes"*.
