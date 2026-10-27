# Layout pitfalls — declarations that report correct and render wrong

`getComputedStyle` returns the written value and the box is wrong: measure the box, not the style. Short form in `css-standards.md`, "Defensive CSS".

## 1. A flex child of a scrolling panel shrinks instead of letting it scroll

- **Symptom.** In a flex-column drawer (header, scrolling body, footer) a header declared `block-size: 56px` measures 51.8px and an `aspect-ratio` banner measures short; everything below sits a few pixels low, only at the height where the panel is meant to scroll.
- **Cause.** Flex resolves shrinking before overflow: every item with the default `flex-shrink: 1` gives up space before anything overflows, and `overflow-y: auto` on the body does not protect its siblings.
- **Fix.** The body is the only thing allowed to give.
  ```css
  .drawer__header, .drawer__footer, .drawer__body > * { flex: 0 0 auto; }
  ```

## 2. A flex item's automatic minimum size beats `aspect-ratio`

- **Symptom.** A media box sized by `aspect-ratio` renders at the height of the uploaded photograph, on one crop and not another.
- **Cause.** A flex item's automatic minimum is `min-height: auto`, which resolves to the content's size and wins over `aspect-ratio` wherever the drawn box is shorter than the image's natural height at that width.
- **Fix.** `min-inline-size: 0` for a row.
  ```css
  .media { aspect-ratio: 393 / 215; min-block-size: 0; }
  ```

## 3. `height: 100%` on an in-flow image feeds its aspect ratio back into the row

- **Symptom.** A two-column band (image | card) is exactly as tall as the image column is *wide*; the card follows the image instead of the image filling the card.
- **Cause.** During intrinsic sizing the parent height is indefinite, so `height: 100%` behaves as `auto`, resolves from the image's aspect ratio, and becomes the row's height. `min-height: 0` and `max-height: 100%` cap the used height after the contribution is made.
- **Fix.** Take the photo out of flow on desktop; stacked on mobile there is no row to match.
  ```css
  .split__media { position: relative; }
  .split__image { position: absolute; inset: 0; width: 100%; height: 100%; }
  ```
- **Check.** Measure both boxes at several widths; the difference must be 0 at every width and the shared height should fall as the window narrows. Use `documentElement.clientWidth`, not `innerWidth` (§13).

## 4. Fixed padding makes a ratio-preferring card grow as the column narrows

- **Symptom.** A card with `aspect-ratio: 1 / 1` gets taller as the window gets narrower.
- **Cause.** `aspect-ratio` is only a preferred size; as the column narrows, fixed padding leaves less room, the text wraps more, and the card outgrows 1:1.
- **Fix.** Percentage padding resolves against the element's own width (vertical included); derive each value from the frame and floor it.
  ```css
  padding: clamp(32px, 11.9%, 80px) clamp(24px, 14.6%, 98px) clamp(20px, 7.15%, 48px);
  ```

## 5. A child's margin collapses out through the section

- **Symptom.** A block with `margin-block: 90px` lands where the design wants it, but the section box measures 90px shorter and starts 90px lower than its frame.
- **Cause.** The section's block padding is a merchant range that starts at 0; with no padding, border or formatting context between them, the child's margin collapses through the custom element, through `.page-width` and out of the wrapper.
- **Fix.** Padding on the child (`display: flow-root` on the wrapper also works).
  ```css
  .cart-empty { padding-block: 90px; }   /* not margin-block */
  ```

## 6. An author `display` disables the `hidden` attribute

- **Symptom.** `el.hidden === true` and the element still renders; a play button's cover never hides.
- **Cause.** `[hidden] { display: none }` is a UA rule; any author `display` on the same element beats it, whatever the specificity.
- **Fix.** Whenever a script toggles `hidden` on an element you gave a `display`, add the `[hidden]` rule in the same change. A video under a cover in a fixed-`aspect-ratio`, `overflow: hidden` box must overlay, not stack.
  ```css
  .video-card__cover { display: block; }
  .video-card__cover[hidden], .video-card__play[hidden] { display: none; }
  .video-card__video { position: absolute; inset: 0; z-index: 2; }
  ```

## 7. An out-of-flow decorative image needs both a floor and a clip

- **Symptom.** When the content column is short (test the worst content case, not the happy one) the section collapses and the absolutely positioned portrait runs over the next section.
- **Cause.** Out of flow, the portrait contributes nothing to the section's height.
- **Fix.** Both rules; neither is sufficient alone. Derive the floor: `R >= image height + offset - padding_bottom`.
  ```css
  .card-grid          { overflow: hidden; }    /* it can never escape */
  .card-grid__figure  { min-height: 592px; }   /* and is not visibly cut */
  ```

## 8. Absolutely positioning a grid child hands its column to the next item

- **Symptom.** Taking the heading out of a two-column header grid (heading | nav) sends the nav to the left edge.
- **Cause.** Auto-placement promotes the remaining child into column 1; `justify-content: flex-end` does nothing in a grid.
- **Fix.** Re-declare the grid for the remaining children.
  ```css
  .card-grid--nav-only .card-grid__header { grid-template-columns: minmax(0, 1fr); justify-items: end; }
  ```

## 9. `width: auto` on a logo hands its size to the srcset candidate

- **Symptom.** Logos render tiny or at odd sizes; a 500×97 file at 135×26.
- **Cause.** With `width: auto` a replaced element takes its intrinsic size — the chosen `srcset` candidate's, or for an SVG the file's own dimensions (`image_url: width:` does not resize SVGs). `max-width` only caps.
- **Fix.** A definite box, and `object-fit: contain` fits the mark. When the frame's container is not the artwork's box, measure two marks with different aspects and solve for the one box that explains both.
  ```css
  .logo-carousel__logo { width: 37.5%; height: 19.25%; object-fit: contain; }
  ```

## 10. An inline custom property cannot be overridden by a stylesheet

- **Symptom.** A section stylesheet cannot change `--carousel-gap` per breakpoint.
- **Cause.** The shared snippet sets it in a `style` attribute, which beats any stylesheet.
- **Fix.** Re-declare it on a descendant the consumers inherit from.
  ```css
  @media screen and (min-width: 750px) { .logo-carousel .scroll-carousel__track { --carousel-gap: 16px; } }
  ```

## 11. A font weight the library never loaded, and the probe that lies about it

- **Symptom.** `font-weight: 600` text renders lighter and narrower than the frame; `getComputedStyle` says `600`; a hot band in the heatmap sits on one line of text.
- **Cause.** `snippets/css-variables.liquid` loaded no bold face, so the browser synthesised one; `font_modify: 'weight', '600'` emits nothing when the library has no such face. `document.fonts.check()` returns `true` for every weight — it asks whether the family can render the text, not whether the face is loaded.
- **Fix.** Load the face, or render the weight the library has and say so beside the `font_face` calls.
  ```liquid
  {{ settings.type_accent_font | font_modify: 'weight', 'bold' | font_face: font_display: 'swap' }}
  ```
- **Check.**
  ```js
  [...document.fonts].filter(f => f.family === 'Family').map(f => f.weight + ' ' + f.status)
  ```

## 12. A span in a second font grows the line

- **Symptom.** A five-line heading at `line-height: 32.5px` measures 168.5px, not 162.5; every span reports the inherited line height.
- **Cause.** An `<em>` in a second family inherits the line height, but its inline box is placed by that family's own ascent and descent, which poke out of the strut.
- **Fix.** `line-height: 1` still grows the line in desktop Chrome; `0` is what normalize.css gives `sub` and `sup`.
  ```css
  .heading em { line-height: 0; }
  ```
  A condensed face in the frame cannot be matched by an unloaded regular one: match the cap height, pull tracking in (`letter-spacing: -0.055em`), and say so in the handover.

## 13. Native `<dialog>`: the reset, the form, and the width

- **Symptom.** A `showModal()` dialog sits in the top-left corner; opening a size chart adds the product to the cart; a dialog wrapping an image collapses to the image's width.
- **Cause.** The UA centres with `dialog:modal { margin: auto }`, and `* { margin: 0 }` in `critical.css` outranks it. A button inside a `<form>` defaults to `type="submit"`. `max-width` alone leaves the box at `fit-content`.
- **Fix.** `showModal()` (never `show()`) gives focus trapping, Escape and `::backdrop`; the element wires open, close and click-outside only.
  ```css
  .my-dialog { margin: auto; width: min(92vw, 900px); max-height: 90vh; overflow: hidden; }
  .my-dialog__scroll { max-height: 90vh; overflow: auto; }   /* scroll on an inner wrapper, not the dialog */
  ```
  Trigger and close buttons take `type="button"`. No `display: flex` on the dialog itself, or it overrides `dialog:not([open]) { display: none }` (§6).
- **Check.** `dialog.matches(':modal')` proves it reached the top layer. Centre against `document.documentElement.clientWidth`, not `window.innerWidth` (which includes the scrollbar). `naturalWidth` on a hidden image is stale; the `width`/`height` attributes `image_tag` emits are the reliable source size.
