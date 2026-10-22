# Scroll-carousel pitfalls

Traps in a CSS scroll-snap `<scroll-carousel>` (snippet plus custom element) and in measuring one. Base itself uses Swiper from `layout/theme.liquid`; this applies to a theme that built its own.

## 1. `ResizeObserver` on the track does not fire when images load

- **Symptom.** Progress-thumb width, grab cursor and "is this scrollable" keep their first-paint value — `cursor: grab` with zero overflow, or 289px of overflow and no grab cursor.
- **Cause.** `scrollWidth` grows as images decode, but the track's own box never changes size, so an observer on the track alone never re-fires.
- **Fix.**
  ```js
  this.track.addEventListener('load', this.onResize, true); // capture: img load does not bubble
  window.addEventListener('load', this.onResize);
  this.resizeObserver.observe(this.track);
  for (const slide of this.slides) this.resizeObserver.observe(slide);
  ```

## 2. `scroll-behavior: smooth` makes `scrollLeft` read stale

- **Symptom.** A script sets `scrollLeft` and asserts on the readout: "the counter never advances", when the counter is fine.
- **Cause.** Under `scroll-behavior: smooth` the assignment starts an animation; `scrollLeft` read on the same tick returns the old value.
- **Fix.** The drag handler does the same through an `is-dragging` class, so the track follows the pointer 1:1.
  ```js
  const prev = track.style.scrollBehavior;
  track.style.scrollBehavior = 'auto';
  /* set scrollLeft, call update(), assert */
  track.style.scrollBehavior = prev;
  ```

## 3. A count baked into Liquid goes stale the moment slides are filtered

- **Symptom.** The counter reads `6/6` while the filtered carousel shows zero slides.
- **Cause.** `data-total="{{ slide_count }}"` is right at first paint and never updated by filters or tabs.
- **Fix.** Mark which case applies rather than guessing in JS:
  - **Auto total** (override left at 0): emit `data-total-auto` and count slides that have a box, `offsetWidth > 0 || offsetHeight > 0` — a `display: none` slide has neither.
  - **Explicit total** (typed, or `collection.all_products_count`): show it verbatim; never recount.
  - Dots: one per scrollable page, `ceil(scrollWidth / clientWidth)`, not one per slide — with 3.3 slides in view, slide-count dots outnumber the positions the track can reach.

## 4. Pointer drag: exclude touch, and suppress the click it would trigger

- **Symptom.** A drag that ends over a slide's `<a>` navigates; the browser's native image-drag fights the gesture.
- **Cause.** A pointer drag ends with a click. Touch already scrolls natively with momentum, so a JS drag is for mouse and pen only.
- **Fix.** Return early on `pointerType === 'touch'`, `preventDefault()` on `dragstart`, and suppress the click in the capture phase, gated on distance (the completed-drag form is in §11).
  ```js
  onClickCapture(event) {
    if (this.dragDistance <= 5) return; // real click, let it through
    event.preventDefault();
    event.stopPropagation();
    this.dragDistance = 0;
  }
  ```

## 5. Zero overflow is not always a bug

- **Symptom.** Nothing scrolls at one breakpoint.
- **Cause.** `per_view` equals the block count, so the slides exactly fill the track. It scrolls as soon as a block is added, and on mobile where `per_view_mobile` is smaller.
- **Check.** Compare `per_view` to the block count before changing anything.

## 6. Min-content width silently inflates carousel cards (two layers)

- **Symptom.** Titles spill out of their card into the next slide, and the card's image renders wider than the card itself.
- **Cause.** An item's automatic minimum size overrides the width you set, at two levels, and fixing one leaves the other. A flex slide with `flex: 0 0 auto` and an explicit `width` still has `min-width: auto`, so a `white-space: nowrap` title widens it. Inside it, a `display: grid` tile with only `grid-template-rows` set has an implicit `auto` column, also floored by min-content, so the media at `width: 100%` of that column outgrows the tile.
- **Fix.**
  ```css
  .scroll-carousel__slide { min-width: 0; }                 /* let the computed width win */
  .product-tile { grid-template-columns: minmax(0, 1fr); }
  ```
- **Check.** `media.width > tile.width` means a track is sized by content; `getComputedStyle(el).gridTemplateColumns` names the real column widths.

## 7. `grid-row` without `grid-column` creates an implicit column

- **Symptom.** Overlaying the add-to-cart on the image shrinks the media by exactly the button's width; `gridTemplateColumns` reads `"260.453px 40px"` on a 300px card.
- **Cause.** Row 1 / column 1 is already occupied by the media, so auto-placement puts the action in a new implicit column that takes its width out of column 1. Explicitly placed items resolve before auto-placed ones, so pinning only some children moves the problem.
  ```css
  .product-tile__action { grid-row: 1; align-self: end; justify-self: end; }   /* lands in an implicit column 2 */
  ```
- **Fix.** Pin every child that shares the cell.
  ```css
  .product-tile__media,
  .product-tile__info,
  .product-tile__action { grid-column: 1; }
  ```

## 8. Progress-thumb travel must be measured against the bar, not the track

- **Symptom.** The thumb overshoots the end of its bar on the last slide and sits on top of the counter.
- **Cause.** Mixed reference widths: `--carousel-thumb-width` is a percentage of the bar, while the offset was `ratio * (1 - visibleFraction) * track.clientWidth` in pixels of the track. The counter and the flex gap make the bar narrower than the track, so at `ratio: 1` the thumb runs past by `(1 - visibleFraction) * (trackWidth - barWidth)`.
- **Fix.** Publish only the 0..1 position from JS and let CSS do the arithmetic in the bar's units; an inset (`left`), not `translateX`, because a translate percentage resolves against the thumb and an inset against the bar.
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
- **Check.** Assert at 0 and at max only: `scroll-snap-type: x mandatory` snaps `scrollLeft = max * 0.5` to the nearest snap point and the thumb legitimately reads unmoved.

## 9. Dot index must come from scroll *progress*, not scrollLeft ÷ viewport

- **Symptom.** The last dot never lights; at the end of the track the indicator sits on the middle dot of three.
- **Cause.** Total travel is `scrollWidth - clientWidth`, not `pages × clientWidth`. At `scrollWidth 823`, `clientWidth 343` the track travels 1.4 viewports while `ceil()` counts 3 dots, so `scrollLeft / clientWidth` tops out at 1 — whenever `per_view` is fractional. Same root cause as §8: a position computed against one length and applied to another.
  ```js
  const pages = Math.ceil(scrollWidth / clientWidth);      // 3
  const page  = Math.round(scrollLeft / clientWidth);      // tops out at 1
  ```
- **Fix.** 0 maps to the first dot and 1 to the last by construction; no clamp needed.
  ```js
  const ratio = scrollable > 0 ? scrollLeft / scrollable : 0;
  const page  = Math.round(ratio * (pages - 1));
  ```
- **Check.** Sample 0 / 25 / 50 / 75 / 100 %: monotonic, starts at 0, ends at `pages - 1`.

## 10. A hidden browser pane will not commit programmatic scrolls

- **Symptom.** `track.scrollLeft = 137` reads back `0` on a live, overflowing track — via `scrollBy`/`scrollTo` too, with snap disabled. Assigning the *end* position happens to persist, which makes it look intermittent.
- **Cause.** The Browser pane is hidden, so the scroller never commits. Nothing is wrong with the page.
- **Fix.** Check `tabs_context` (or `document.documentElement.clientWidth` being 0 when un-emulated) before blaming the handler, and test scroll-derived logic by feeding the position in.
  ```js
  Object.defineProperty(track, 'scrollLeft', { get: () => value, set: () => {}, configurable: true });
  carousel.update();
  /* assert on the indicator, then: */ delete track.scrollLeft;
  ```

## 11. `setPointerCapture` on pointerdown steals every click inside the track

- **Symptom.** A button inside the track responds to the keyboard but not the mouse — space works, click does not.
- **Cause.** While pointer capture is active the following `click` is dispatched at the capturing element, so it never reaches the button; and the track enters drag mode on a plain press.
  ```js
  this.track.setPointerCapture?.(event.pointerId);   /* on pointerdown: retargets the click */
  this.track.classList.add('is-dragging');            /* drag mode on a plain press */
  ```
- **Fix.** A press is not a drag: record the origin on pointerdown and claim the pointer only once movement passes the threshold.
  ```js
  onPointerDown(event) { this.dragOriginX = event.clientX; this.dragOriginScroll = this.track.scrollLeft; }   /* no capture, no is-dragging yet */
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
  Tie click-suppression to a completed drag, not a lingering distance — a drag that ends outside the track leaves a stale `dragDistance` and the next click gets eaten:
  ```js
  onPointerUp() { this.suppressClick = this.dragDistance > DRAG_THRESHOLD; }
  onClickCapture(e) { if (!this.suppressClick) return; this.suppressClick = false; e.preventDefault(); e.stopPropagation(); }
  ```
- **Check.** Every interactive control inside the track — add-to-cart, quick-add openers, size chips, links: a plain click and a 3px jitter never set `is-dragging` and deliver the click; a 40px+ drag engages on move and the click is suppressed.

## See also

- `hover-state-pitfalls.md` — hover and focus states, and why measuring a hover needs transitions disabled first.
