# Equal-height column pitfalls

Making an image column and a content card the same height: three traps that pass a casual DOM check.

## 1. `height: 100%` on an in-flow image feeds its aspect ratio back into the row

- **Symptom.** The row is exactly as tall as the image column is *wide*; the card follows the image instead of the image filling the card.
- **Cause.** During the intrinsic sizing pass the parent height is still indefinite, so `height: 100%` behaves as `auto` and resolves from the image's aspect ratio, and that becomes the row's height. `min-height: 0` + `max-height: 100%` cap the used height, but the intrinsic contribution has already been made.
- **Fix.** Take the photo out of flow, desktop only — stacked on mobile there is no row to match and the photo needs its own ratio.
  ```css
  .product-spotlight__media { position: relative; }
  .product-spotlight__image { position: absolute; inset: 0; width: 100%; height: 100%; }
  ```

## 2. A duplicate selector later in the same media block silently eats the fix

- **Symptom.** Editing a rule changes nothing, or the measurement gets worse.
- **Cause.** The same selector appears twice inside one `min-width` block; the later copy wins on source order.
- **Check.** Count the selector before editing; more than one hit inside one breakpoint means consolidate first, patch second.
  ```bash
  grep -n "feature-band__image-wrapper" assets/section-feature-band.css
  ```

## 3. Fixed padding makes a ratio-preferring card *grow* as the column narrows

- **Symptom.** A card with `aspect-ratio: 1 / 1` gets taller as the window gets narrower.
- **Cause.** `aspect-ratio` is only a preferred size, so the card outgrows 1:1 to fit its content. Fixed padding leaves less room for the text as the column narrows, the text wraps more, and the card grows.
- **Fix.** Percentage padding resolves against the element's own width (vertical padding included); derive each from the frame (`98 / 672 = 14.6%`) and floor it so it cannot collapse on a small tablet.
  ```css
  padding: clamp(32px, 11.9%, 80px) clamp(24px, 14.6%, 98px) clamp(20px, 7.15%, 48px);
  ```

## Verifying

Measure both boxes at several widths. `diff` must be 0 at every width and the shared height should fall as the window narrows; a `diff` that grows with narrowing is trap 1 or 3. `documentElement.clientWidth`, not `innerWidth` — see `scroll-carousel-pitfalls.md` for why they disagree.

```js
window.__probe = () => {
  const r = (e) => (e ? Math.round(e.getBoundingClientRect().height) : null);
  const card = r(document.querySelector('.feature-band__card'));
  const image = r(document.querySelector('.feature-band__image-wrapper'));
  return { w: document.documentElement.clientWidth, card, image, diff: image - card };
};
```
