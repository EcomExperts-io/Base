#!/usr/bin/env python3
"""Pixel-compare a reference image — a Figma frame export, or a live-site render — against ours, as a number.

Usage
-----
  compare.py --reference figma-1440.png --rendered rendered-1440.png --out .claude/verify/<slug>
             [--reference-label Figma] [--width 1440] [--rendered-offset-y 0]
             [--mask x,y,w,h ...] [--threshold 32] [--slug name]

--figma is accepted as a synonym for --reference. For a live section the
verify skill uses live-parity.py instead, which renders both sides itself;
this script is for a reference that already exists as an image.

Writes <out>/diff-<width>.png, <out>/side-by-side-<width>.png (and a -preview
scaled for reading), <out>/compare-<width>.json; prints the JSON summary.
Coordinates for --mask are in the compared image's frame: rendered pixels
after --rendered-offset-y has been applied, which equals the frame's own
coordinates when the offsets line up.

Notes:
- The number is a report, not a gate. Font rasterisation, anti-aliasing and
  image compression differ between Figma and Chrome, so a 4% diff can be a
  perfect build and a 1% diff can hide an empty column. Read it with the
  heatmap and the box table (fidelity-table.py), never alone.
- Live data never matches a mock. Pass --mask for every region that comes from
  the store (the verify skill collects them from `data-verify-mask`); those
  pixels are excluded on both sides.
"""

import json
import os
import sys

try:
    from PIL import Image, ImageChops, ImageDraw
except ImportError:
    print(json.dumps({"error": "Pillow is not installed: python3 -m pip install --user pillow"}))
    sys.exit(2)


def arg(argv, name, default=None, cast=str):
    if name in argv:
        return cast(argv[argv.index(name) + 1])
    return default


def args_all(argv, name):
    return [argv[i + 1] for i, a in enumerate(argv) if a == name and i + 1 < len(argv)]


def channel_max_diff(a, b):
    """Per-pixel max over RGB channels of |a-b|, as an L image."""
    d = ImageChops.difference(a, b)
    r, g, bl = d.split()
    return ImageChops.lighter(ImageChops.lighter(r, g), bl)


def bands(mask, min_row_pct=20.0, min_rows=6):
    """Contiguous y-ranges where more than min_row_pct of the row mismatches."""
    w, h = mask.size
    profile = mask.resize((1, h), Image.BOX)  # BOX average per row
    rows = [profile.getpixel((0, y)) / 255 * 100 for y in range(h)]
    out, start = [], None
    for y, pct in enumerate(rows + [0.0]):
        if pct >= min_row_pct and start is None:
            start = y
        elif pct < min_row_pct and start is not None:
            if y - start >= min_rows:
                avg = sum(rows[start:y]) / (y - start)
                out.append({"y0": start, "y1": y, "rows": y - start, "mismatch_pct": round(avg, 1)})
            start = None
    out.sort(key=lambda b: b["rows"] * b["mismatch_pct"], reverse=True)
    return out[:5]


def main(argv):
    figma_path = arg(argv, "--reference") or arg(argv, "--figma")
    ref_label = arg(argv, "--reference-label", "Figma")
    rendered_path = arg(argv, "--rendered")
    out_dir = arg(argv, "--out", ".claude/verify/unnamed")
    if not figma_path or not rendered_path:
        print(__doc__)
        return 2
    width_label = arg(argv, "--width", None, int)
    offset_y = arg(argv, "--rendered-offset-y", 0, int)
    threshold = arg(argv, "--threshold", 32, int)
    slug = arg(argv, "--slug", os.path.basename(out_dir.rstrip("/")))
    masks = []
    for m in args_all(argv, "--mask"):
        try:
            x, y, w, h = (int(float(v)) for v in m.split(","))
            masks.append((x, y, w, h))
        except ValueError:
            print(f"ignoring malformed --mask {m!r} (want x,y,w,h)")

    a = Image.open(figma_path).convert("RGB")
    b = Image.open(rendered_path).convert("RGB")
    width_label = width_label or a.width
    scaled = False
    if b.width != a.width:
        b = b.resize((a.width, round(b.height * a.width / b.width)), Image.LANCZOS)
        scaled = True
    if offset_y:
        b = b.crop((0, offset_y, b.width, b.height))

    h = min(a.height, b.height)
    a2, b2 = a.crop((0, 0, a.width, h)), b.crop((0, 0, a.width, h))
    # Count the pixels actually covered rather than adding up rectangle areas.
    # Masks overlap (a carousel's cloned slides) and hang off the edges (a slide
    # half out of frame), so the sum of w*mh can exceed the compared area.
    # A coverage bitmap cannot lie about either.
    covered = Image.new("1", (a.width, h), 0)
    cover_draw = ImageDraw.Draw(covered)
    for (x, y, w, mh) in masks:
        for im in (a2, b2):
            ImageDraw.Draw(im).rectangle((x, y, x + w, y + mh), fill=(128, 128, 128))
        cover_draw.rectangle((x, y, x + w, y + mh), fill=1)

    mism = channel_max_diff(a2, b2).point(lambda v: 255 if v > threshold else 0)
    mismatched = mism.histogram()[255]
    total = a.width * h
    masked_px = covered.histogram()[255] if masks else 0
    denom = max(1, total - masked_px)
    diff_pct = round(100.0 * mismatched / denom, 2)

    # Heatmap: both images greyed and blended, mismatch painted red.
    base = Image.blend(a2.convert("L").convert("RGB"), b2.convert("L").convert("RGB"), 0.5)
    base = Image.eval(base, lambda v: int(v * 0.55 + 90))
    red = Image.new("RGB", base.size, (214, 48, 40))
    heat = base.copy()
    heat.paste(red, mask=mism)

    gap = 24
    sbs = Image.new("RGB", (a.width * 3 + gap * 2, h + 40), (238, 241, 244))
    draw = ImageDraw.Draw(sbs)
    for i, (im, label) in enumerate(((a2, f"{ref_label} {width_label}"), (b2, "Rendered"),
                                     (heat, f"Mismatch {diff_pct}%"))):
        x0 = i * (a.width + gap)
        sbs.paste(im, (x0, 40))
        draw.text((x0 + 8, 12), label, fill=(23, 33, 43))

    os.makedirs(out_dir, exist_ok=True)
    diff_png = os.path.join(out_dir, f"diff-{width_label}.png")
    sbs_png = os.path.join(out_dir, f"side-by-side-{width_label}.png")
    prev_png = os.path.join(out_dir, f"side-by-side-{width_label}-preview.png")
    heat.save(diff_png)
    sbs.save(sbs_png)
    preview_w = 1800
    if sbs.width > preview_w:
        sbs.resize((preview_w, round(sbs.height * preview_w / sbs.width)), Image.LANCZOS).save(prev_png)
    else:
        sbs.save(prev_png)

    result = {
        "slug": slug,
        "width": width_label,
        "reference": {"kind": ref_label, "path": figma_path, "size": [a.width, a.height]},
        "figma": {"path": figma_path, "size": [a.width, a.height]},
        "rendered": {"path": rendered_path, "size_original": list(Image.open(rendered_path).size),
                     "scaled_to_figma_width": scaled, "offset_y": offset_y},
        "compared_height": h,
        "height_delta": (b.height + offset_y) - a.height,
        "threshold": threshold,
        "masks": len(masks),
        "diff_pct": diff_pct,
        "worst_bands": bands(mism),
        "outputs": {"heatmap": diff_png, "side_by_side": sbs_png, "preview": prev_png},
        "read_with": "the heatmap and fidelity-table.py — the percentage alone proves nothing",
    }
    with open(os.path.join(out_dir, f"compare-{width_label}.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
