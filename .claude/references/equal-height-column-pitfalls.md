# Equal-height column pitfalls

Traps hit making the image column and the content card the same height in
`team-feature` and `product-spotlight`. All three cost real debugging time and
none of them show up in a casual DOM check.

## 1. `height: 100%` on an in-flow image feeds its aspect ratio back into the row

The spotlight image column was `height: 100%` inside a stretched grid row. That
looks like "fill whatever the row gives me", but during the **intrinsic sizing
pass** the parent height is still indefinite, so `height: 100%` behaves as
`auto` and resolves from the image's aspect ratio instead. A square photo in an
820px column reported **820px tall**, that became the row's height, and the card
was then forced to follow the image rather than the other way round.

Symptom: the row is exactly as tall as the image column is **wide**.

Fix — take the photo out of flow so it cannot contribute a height at all:

```css
.product-spotlight__media {
  position: relative;
}

.product-spotlight__image {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}
```

The row is then sized by the card alone and the photo fills the result.
`min-height: 0` + `max-height: 100%` is **not** enough — those cap the used
height but the intrinsic contribution has already been made.

Keep this desktop-only. Stacked on mobile there is no row to match, and the
photo needs its own ratio to have any height.

## 2. A duplicate selector later in the same media block silently eats the fix

A two-column feature section's stylesheet had **two** rules for the same
image-wrapper class inside one `min-width: 750px` block, ~25 lines apart. Adding
`aspect-ratio: auto` to the first one was a complete no-op — the second
(`aspect-ratio: 1 / 1`) won on source order. The measurement said the change had
made things *worse*, which sent the diagnosis in the wrong direction.

Before editing a rule in a long media block, grep the selector across the whole
file and count:

```bash
grep -n "team-feature__image-wrapper" assets/section-team-feature.css
```

More than one hit inside the same breakpoint means consolidate first, patch
second.

## 3. Fixed padding makes a ratio-preferring card *grow* as the column narrows

`.team-feature__card` is `aspect-ratio: 1 / 1` with `padding: 80px 98px 48px`.
`aspect-ratio` is only a *preferred* size, so the card outgrows 1:1 to fit its
content. With the padding fixed, a narrowing column leaves less and less room
for the text, it wraps more, and the card got **taller** as the window got
smaller — 653px at 1280 up to 855px at 760. Exactly backwards from what
"scales down with the window" means.

Percentage padding resolves against the element's own **width** (vertical
padding included), so it keeps the frame's proportions at every width:

```css
padding: clamp(32px, 11.9%, 80px) clamp(24px, 14.6%, 98px) clamp(20px, 7.15%, 48px);
```

Derive each percentage from the frame: `98 / 672 = 14.6%` at 1440. The clamp
floors stop it collapsing on a small tablet.

## Verifying

Measure both boxes at several widths rather than eyeballing one. Install a probe
and step the viewport down through the breakpoint:

```js
window.__probe = () => {
  const r = (e) => (e ? Math.round(e.getBoundingClientRect().height) : null);
  const card = r(document.querySelector('.team-feature__card'));
  const image = r(document.querySelector('.team-feature__image-wrapper'));
  return { w: document.documentElement.clientWidth, card, image, diff: image - card };
};
```

Use `documentElement.clientWidth`, not `innerWidth` — see
`scroll-carousel-pitfalls.md` for why the two disagree in the hidden pane.
`diff` must be 0 at every width, and the shared height should fall as the
window narrows. A `diff` that grows with narrowing is trap 1 or 3.
