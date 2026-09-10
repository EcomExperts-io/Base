# Scroll-carousel pitfalls

Learned while wiring a shared `<scroll-carousel>` primitive — a snippet plus its
custom element, using CSS scroll-snap rather than a library — across a client
homepage. All of these produce code that *looks* correct in a DOM inspection and
is wrong on screen or in a measurement script.

**Base has no such primitive.** Carousels here use Swiper, loaded from
`layout/theme.liquid`. Read this when a client theme has built a scroll-snap
carousel of its own, or before building one: the traps are in scroll-snap and in
measuring it, not in any particular implementation.

## 1. `ResizeObserver` on the track does not fire when images load

A carousel's `scrollWidth` grows as its images decode, but the track's own box
never changes size — so an observer watching only the track never re-fires. Any
state derived from `scrollWidth` (progress-thumb width, a grab cursor, "is this
scrollable at all") silently keeps its first-paint value.

Symptom seen: one carousel showed `cursor: grab` with zero overflow while
another had 289px of overflow and no grab cursor — stale in both directions.

Fix: observe the slides as well as the track, and re-measure on image load.

```js
this.track.addEventListener('load', this.onResize, true); // capture: img load does not bubble
window.addEventListener('load', this.onResize);
this.resizeObserver.observe(this.track);
for (const slide of this.slides) this.resizeObserver.observe(slide);
```

## 2. `scroll-behavior: smooth` makes `scrollLeft` read stale

Assigning `track.scrollLeft = x` under `scroll-behavior: smooth` starts an
animation; reading `scrollLeft` back on the same tick returns the **old** value.
A verification script that sets a scroll position and immediately asserts on the
readout will report "the counter never advances" when the counter is fine.

When measuring, force it off first:

```js
const prev = track.style.scrollBehavior;
track.style.scrollBehavior = 'auto';
/* set scrollLeft, call update(), assert */
track.style.scrollBehavior = prev;
```

The same applies in the component: the drag handler sets `scroll-behavior: auto`
via an `is-dragging` class so the track tracks the pointer 1:1 instead of easing
behind it.

## 3. A count baked into Liquid goes stale the moment slides are filtered

`data-total="{{ slide_count }}"` is correct at first paint and wrong forever
after, in any section that shows and hides slides (league filters, player tabs).
The teams carousel read `6/6` while displaying zero teams.

Two separate cases, so mark which one applies rather than guessing in JS:

- **Auto total** — the merchant left the override at 0. Emit `data-total-auto`
  and count slides that currently have a box (`offsetWidth > 0 || offsetHeight > 0`);
  a `display: none` slide has neither, which is exactly the test needed.
- **Explicit total** — the merchant typed one, or it comes from live data such
  as `collection.all_products_count`. Show it verbatim; never recount.

Related: dot indicators should be one-per-scrollable-page
(`ceil(scrollWidth / clientWidth)`), not one-per-slide. With 3.3 slides in view,
slide-count dots outnumber the positions the track can actually reach.

## 4. Pointer drag: exclude touch, and suppress the click it would trigger

Touch already scrolls natively with momentum no JS can improve on, so return
early on `pointerType === 'touch'` rather than reimplementing it.

Every slide is usually wrapped in an `<a>`, so a drag ends with a click that
would navigate. Suppress it in the **capture** phase, gated on distance so a
genuine click still works:

```js
onClickCapture(event) {
  if (this.dragDistance <= 5) return; // real click, let it through
  event.preventDefault();
  event.stopPropagation();
  this.dragDistance = 0;
}
```

Also `preventDefault()` on `dragstart`, or the browser's native image-drag
fights the gesture.

## 5. Zero overflow is not always a bug

With `per_view` equal to the number of blocks (6 teams at `columns_desktop: 6`,
4 auction cards at `per_view: 4`) the slides exactly fill the track and there is
genuinely nothing to scroll at that breakpoint. Confirm against the block count
before "fixing" it; it starts scrolling as soon as a merchant adds one more block,
and it still scrolls on mobile where `per_view_mobile` is smaller.

## See also

- `hover-state-pitfalls.md` — hover/focus states on these same sections, including
  why measuring a hover needs transitions disabled first.

## 8. Min-content width silently inflates carousel cards (two layers)

Symptom on the MiLB homepage: product titles spilled out of their card into the
next slide, and the card's image rendered *wider than the card itself*. Both are
the same root cause at two different levels — an item's **automatic minimum
size** overriding the width you set — and fixing only one leaves the other.

**Layer 1 — the flex slide.** `.scroll-carousel__slide` sets an explicit
`width` with `flex: 0 0 auto`, but a flex item's default `min-width: auto` means
it will not shrink below min-content. A slide holding a `white-space: nowrap`
title takes the title's full width instead:

```css
.scroll-carousel__slide { min-width: 0; }   /* let the computed width win */
```

**Layer 2 — the card's own grid.** `.product-tile` is `display: grid` with only
`grid-template-rows` set. The implicit column is `auto`, which is also floored
by its items' min-content contribution, so the column grew to the nowrap
title's width and the media (`width: 100%` of that column) came out wider than
the tile:

```css
.product-tile { grid-template-columns: minmax(0, 1fr); }
```

Diagnose it by comparing a child's width to its parent's — if
`media.width > tile.width`, a track is being sized by content, not by your
declaration. `getComputedStyle(el).gridTemplateColumns` names the real column
widths and is the fastest confirmation.

## 9. `grid-row` without `grid-column` creates an implicit column

Overlaying the add-to-cart on the image by moving it into row 1 looked right:

```css
.product-tile__action { grid-row: 1; align-self: end; justify-self: end; }
```

But row 1 / column 1 was already occupied by the media, so auto-placement put
the action in a **new implicit column** — and that column took its width out of
column 1, shrinking the media by exactly the button's width (40px here).
`gridTemplateColumns` read back `"260.453px 40px"` on a 300px card.

Pin every child that shares a cell to the same column:

```css
.product-tile__media,
.product-tile__info,
.product-tile__action { grid-column: 1; }
```

Pinning only *some* of them moves the problem rather than fixing it: pinning the
action alone pushed the media (which has its own `grid-row: 1`) into column 2,
because explicitly-placed items are resolved before auto-placed ones.

## 10. Measuring a section against a Figma frame

Render the frame once at 1:1 and measure the PNG rather than eyeballing crops:

- Find full-bleed section bands by sampling a single gutter column down the
  render and grouping runs of identical colour.
- Get element boxes with a bounding-box scan thresholded against the section
  background. **Restrict the y-range first** — a scan over a whole section
  merges the heading, the portrait and the body copy into one meaningless box.
  A row-profile (count of on-pixels per row) shows where the real bands are.
- Text size is more reliably matched by *width* than by cap height: measure the
  design's text width, render at a guess, then scale
  `font-size × design_width / rendered_width`. This landed the heading (31px)
  and the player name (58px) in one correction each.
- A cutout with a soft alpha fade has no measurable hard edge, so anchor on the
  silhouette **width** and derive the render height from the intrinsic aspect.
- In the browser, `document.documentElement.clientWidth` is the number to
  compare against the frame width — a scrollbar makes a 1440 window lay out at
  1425 and every x will be 15px out. Emulate 1455 to lay out at 1440.

## 11. Progress-thumb travel must be measured against the bar, not the track

The thumb overshot the end of its bar on the last slide and sat on top of the
"6/6" counter. Cause: mixed reference widths.

- `--carousel-thumb-width` was a **percentage of the bar** (the thumb is
  absolutely positioned inside `.scroll-carousel__bar`).
- the offset was computed in **pixels of the track**:
  `ratio * (1 - visibleFraction) * track.clientWidth`.

The counter and the flex gap make the bar narrower than the track, so at
`ratio: 1` the thumb ran past the bar by
`(1 - visibleFraction) * (trackWidth - barWidth)` — 45px in the Top Players
section (bar 695 vs track 772).

Fix: publish only the 0..1 position from JS and let CSS do the arithmetic in the
bar's own units, so the two terms can never disagree:

```js
this.style.setProperty('--carousel-thumb-width', `${visibleFraction * 100}%`);
this.style.setProperty('--carousel-thumb-ratio', `${ratio}`);
```

```css
.scroll-carousel__bar { overflow: hidden; }          /* overshoot impossible */
.scroll-carousel__bar-thumb {
  left: calc(var(--carousel-thumb-ratio, 0) * (100% - var(--carousel-thumb-width, 30%)));
  width: var(--carousel-thumb-width, 30%);
}
```

Use an inset (`left`), not `translateX`: a translate percentage resolves against
the **thumb**, an inset percentage against the **bar**. Transitioning `left`
rather than `transform` is fine here — the rule already transitioned `width`,
which triggers layout anyway.

**Testing note:** don't assert on a mid-scroll position by assigning
`scrollLeft = max * 0.5`. With `scroll-snap-type: x mandatory` the browser snaps
that assignment to the nearest snap point, so the thumb legitimately reads as
unmoved and the test looks like a bug. Assert at 0 and at max, which are both
snap points.

## 12. Dot index must come from scroll *progress*, not scrollLeft ÷ viewport

The last dot never lit up. At the end of the teams carousel the indicator sat on
the middle dot of three.

```js
const pages = Math.ceil(scrollWidth / clientWidth);      // 3
const page  = Math.round(scrollLeft / clientWidth);      // tops out at 1
```

A track's total travel is `scrollWidth - clientWidth`, not `pages × clientWidth`.
Six teams at 2.5 per view give `scrollWidth 823`, `clientWidth 343`: the track
travels 480px — **1.4 viewports** — while `ceil()` counts 3 dots. So
`scrollLeft / clientWidth` can only ever reach 1, and the final dot is
unreachable. The shortfall appears whenever the last page is partial, i.e.
whenever `per_view` is fractional.

Drive it from the ratio the component already computes, so 0 maps to the first
dot and 1 maps to the last by construction:

```js
const ratio = scrollable > 0 ? scrollLeft / scrollable : 0;
const page  = Math.round(ratio * (pages - 1));
```

The clamp (`Math.min(page, pages - 1)`) becomes unnecessary — `ratio <= 1`
guarantees it. Verify by sampling 0 / 25 / 50 / 75 / 100 %: the sequence must be
monotonic, start at 0 and end at `pages - 1`.

Same root cause as the progress-thumb bug in §11: a position computed against
one length and applied to another. When a control tracks scroll, ask what its
0-to-1 range actually is.

## 13. A hidden browser pane will not commit programmatic scrolls

`track.scrollLeft = 137` read back `0` on an element with `scrollWidth 823`,
`clientWidth 343`, `overflow-x: auto` and a live layout — with scroll-snap
disabled, and via `scrollBy`/`scrollTo` too. Nothing was wrong with the page:
the Browser pane was hidden, so the scroller never committed.

Two consequences:

- **Do not conclude a scroll handler is broken** from a programmatic scroll that
  does not move. Check `tabs_context` (or `document.documentElement.clientWidth`
  being 0 when un-emulated) first.
- **Test scroll-derived logic by feeding the position in**, not by scrolling.
  Spoofing the accessor on the instance exercises the real shipped code:

```js
Object.defineProperty(track, 'scrollLeft', { get: () => value, set: () => {}, configurable: true });
carousel.update();
/* assert on the indicator, then: */ delete track.scrollLeft;
```

Assigning to the *end* position happens to persist (it is already a valid snap
position and often a no-op), which is what made this look intermittent.

## 14. `setPointerCapture` on pointerdown steals every click inside the track

The fan gallery's play button responded to the keyboard but not the mouse. The
cause was in the carousel's drag, not the video: `onPointerDown` claimed the
pointer immediately.

```js
onPointerDown(event) {
  this.dragging = true;
  this.track.setPointerCapture?.(event.pointerId);   /* <- retargets the click */
  this.track.classList.add('is-dragging');            /* <- drag mode on a plain press */
}
```

**While pointer capture is active, the `click` that follows is dispatched at the
capturing element**, so it never reached the button — and the track entered drag
mode the instant the mouse went down. Keyboard activation bypasses pointer
events entirely, which is the tell: *space works, click does not.*

A press is not a drag. Record the origin on pointerdown, and only claim the
pointer once movement passes the threshold:

```js
onPointerDown(event) {
  this.pendingDrag = true;            /* no capture, no is-dragging yet */
  this.dragOriginX = event.clientX;
  this.dragOriginScroll = this.track.scrollLeft;
}

onPointerMove(event) {
  if (!this.dragging) {
    if (this.dragDistance <= DRAG_THRESHOLD) return;
    this.dragging = true;
    this.track.setPointerCapture?.(event.pointerId);  /* only now */
    this.track.classList.add('is-dragging');
  }
  this.track.scrollLeft = this.dragOriginScroll - delta;
}
```

Also tie click-suppression to a **completed drag**, not to a lingering distance:

```js
onPointerUp() { this.suppressClick = this.dragDistance > DRAG_THRESHOLD; }
onClickCapture(e) { if (!this.suppressClick) return; this.suppressClick = false; e.preventDefault(); e.stopPropagation(); }
```

Keying off `dragDistance` alone leaves a stale value behind whenever a drag ends
outside the track (no click follows), and the *next* click gets eaten.

**Any interactive control inside a draggable track is affected** — add-to-cart
buttons, quick-add openers, size chips, links. Assert all three cases:

| gesture | is-dragging on press | drag engages | click delivered |
|---|---|---|---|
| plain click | no | no | yes |
| 3px jitter | no | no | yes |
| 40px+ drag | no | yes (on move) | no, suppressed |
