# Hover state pitfalls

Hover, focus and toggled-state CSS that looks right in review and does nothing, or the wrong thing, on screen — and the traps in measuring it.

## 1. A later hover rule silently undoes a selected state

- **Symptom.** Hovering the *active* chip or tab makes it look unselected; a disabled button still lights up.
- **Cause.** `[aria-pressed='true']` / `[aria-selected='true']` and `:hover` both weigh 0-2-0, so whichever is later wins; a generic hover also fires on a `[disabled]` control.
- **Fix.** Guard the hover rather than reordering, and restate resting values under `[disabled]:hover`.
  ```css
  .carousel__filter:not([aria-pressed='true']):hover { … }
  .card-grid__tab:not([aria-selected='true']):hover { … }
  .product-tile__atc[disabled]:hover { background-color: #000; }   /* 0-2-1 beats 0-1-1 */
  .scroll-carousel__arrow[disabled]:hover { /* restate resting */ }
  ```

## 2. `text-decoration: underline` on hover is a no-op if the link is already underlined

- **Symptom.** The hover underline changes nothing.
- **Cause.** The base rule sets colour and font but never `text-decoration: none`, so the `<a>` is underlined at rest. Underline is the right hover only where the base rule removes it; white text on a photo usually has no other legible option.
- **Check.** `getComputedStyle(el).textDecorationLine` — `'underline'` already? pick another property.

## 3. Composed transforms must be restated, not replaced

- **Symptom.** An element centred with `transform: translate(-50%, -50%)` jumps to the corner on hover.
- **Cause.** The hover's `transform: scale(...)` replaces the whole transform list.
- **Fix.** The reduced-motion override restates the translate too, not `none`.
  ```css
  .logo-carousel__logo:hover { transform: translate(-50%, -50%) scale(1.05); }
  ```

## 4. Wrap hover in `@media (hover: hover)`

- **Symptom.** On a touch screen a tapped card or button stays in its hover state until something else is tapped.
- **Cause.** `:hover` latches after a tap. Mobile emulation reports `(hover: hover) → false`, `(pointer: coarse) → true`, so guarded rules go inert there.
- **Fix.** `@media (hover: hover) { .card:hover { … } }`

## 5. Card-driven vs link-driven hover — pick one per card and stick to it

- **Symptom.** The image zooms on card hover while the title stays dead.
- **Cause.** `.auction-card__title a:hover` fires only over the `<a>`, which wraps the title text alone. `.product-tile` gets it free: its title's `::after` overlay covers the whole card, so card hover and link hover are one event.
- **Fix.** Where nothing is a whole-card link, drive from the card and add `:focus-within` for keyboard users; no hover on non-interactive elements (dots that are `<span>`s in an `aria-hidden` container, an image that is a plain `div`).
  ```css
  .category-tiles__card:hover .category-tiles__image,
  .category-tiles__card:focus-within .category-tiles__image { … }
  ```

## 6. Verifying hover in a browser — three traps

1. **Transitions race the assertion.** `getComputedStyle` right after a synthetic hover returns a mid-transition value; a 1s wait is not reliable either. Inject `*, *::before, *::after { transition: none !important; }` and read instantly.
2. **Screenshot coordinates are scaled.** The hover action takes screenshot pixels, not CSS pixels: `scale = screenshotWidth / window.innerWidth`; confirm the target with `document.elementFromPoint(sx / scale, sy / scale)`.
3. **Cross-origin stylesheets cannot be enumerated.** Theme CSS comes from `cdn.shopify.com`, so `sheet.cssRules` throws and a `document.styleSheets` walk finds zero rules. Extract selectors from the local files and test them with `querySelectorAll`.

A regex audit that takes `prelude.split('\n').pop()` keeps only the last line of a multi-line comma selector list and reports "all good".

## 7. A selector matching zero elements is not necessarily wrong

- **Symptom.** A rule matches nothing on the page.
- **Cause.** The template data does not exercise it — no size variants, an empty URL setting, a different `nav_style`, no videos uploaded.
- **Check.** Confirm the class exists in the Liquid, then inject a fixture element with that class anywhere in `<body>` and hover it; the stylesheet is global once loaded.

## 8. A theme-wide `!important` was overriding every button's font size on mobile

- **Symptom.** Below 600px every property from a section's rule applies except `font-size`. `letter-spacing: 0.08em` computes to `1.28px` = 0.08 × 16, naming the font size that actually won.
- **Cause.** The iOS zoom guard in `assets/critical.css` listed `button` in `input, textarea, select, button { font-size: 16px !important; }`. iOS Safari zooms only when a text-entry field under 16px takes focus; buttons never trigger it.
- **Fix.**
  ```css
  @media screen and (max-width: 600px) {
    input, textarea, select { font-size: 16px !important; }   /* button removed */
  }
  ```
- **Check.** When one property of a rule loses, read a second em-derived property; its computed value names the real font size.
- Duplicate copies of a shared component's stylesheet are not harmless either: each re-enters the cascade at its own position, so a section's equal-specificity override wins or loses depending on which other sections render — `shared-component-override-pitfalls.md`. Dedupe by filename before comparing rules in a stylesheet dump.

## 9. Two more measurement traps (same root cause as §6.1)

- `dot.style.width = '16px'` measured on the same tick reads 4px: the element's `transition: width`, not a cascade override. Disable transitions before measuring anything that animates, including when testing whether a rule applies at all.
- `document.styleSheets` can yield nothing on a dev-server page. Fetch the stylesheet URL and regex the text.

## 10. An out-of-flow decorative image needs both a floor and a clip

- **Symptom.** When the content column is short (a tab whose collection setting is empty — test the worst content case, not the happy one) the section collapses and the absolutely positioned portrait runs over the next section.
- **Cause.** Out of flow, the portrait contributes nothing to the section's height.
- **Fix.** Both rules; neither is sufficient alone. The floor is derived, not guessed: portrait 696px tall, offset `-46px`, `padding_bottom: 80` gives `R >= 570`; 592 is the frame's own row height.
  ```css
  .card-grid            { overflow: hidden; }   /* hard stop: it can never escape */
  .card-grid__figure    { min-height: 592px; }  /* so it is not visibly cut either */
  ```
  ```
  portrait bottom = padding_top + H + margin + (-46) + 696
  section  bottom = padding_top + H + margin + R + padding_bottom
                              → R >= 696 - 46 - padding_bottom
  ```

## 11. Absolutely positioning a grid child hands its column to the next item

- **Symptom.** Taking the heading out of a two-column header grid (heading | nav) sends the nav to the left edge.
- **Cause.** Auto-placement promotes the remaining child into column 1. `justify-content: flex-end` does nothing — it is a grid, not a flex row. Whenever one grid child leaves the flow, re-check the rest.
- **Fix.**
  ```css
  .card-grid--nav-avatar .card-grid__header { grid-template-columns: minmax(0, 1fr); justify-items: end; }
  ```

## 12. A condensed face in the frame cannot be matched by tracking alone

- **Symptom.** Sizing to the frame's 82px cap height makes the run 844px against the frame's 708px; sizing to the run makes the letters visibly thinner.
- **Cause.** The frame's face is condensed and the loaded family is not, so cap height and text length cannot both match.
- **Fix.** Match the cap height and pull the tracking in — `letter-spacing: -0.055em` lands 727px against 708, within 3% on both axes; say so in the handover rather than leave a magic number.

## 13. `templates/index.json` is editor-owned — pushing it reverts merchant changes

- **Symptom.** A setting switched in the theme editor reverts after a push.
- **Cause.** The file is written by the admin theme editor, and `theme push --only templates/index.json` overwrites it. Sections and assets push freely; JSON templates and `config/settings_data.json` are shared state.
- **Fix.** Pull the remote copy and diff it before pushing.
  ```bash
  shopify theme pull --only templates/index.json && git diff templates/index.json
  ```

## 14. Check whether a fade lives in the asset before recreating it in CSS

- **Symptom.** The frame fades a portrait into the section surface; a CSS fade on top of one baked into the asset would double it.
- **Check.** Sample the asset's alpha by row.
  ```js
  /* mean alpha of non-transparent pixels, bottom 30% of the asset */
  row 503 (70%)  meanAlpha=254
  row 713 (99%)  meanAlpha=253      → no fade in the asset; it is applied in the design
  ```
  To measure it from the render: profile max deviation from the section background per row across the portrait's x-range; a linear fade is a straight ramp and the two stops fall out of a least-squares fit, extrapolated up to the opaque plateau and down to zero (48% → 94% at every breakpoint, so one mask serves all).
- **Fix.** `mask-image` on the portrait, not an overlay gradient in the background colour — an overlay would fade the watermark behind the portrait too.
  ```css
  .card-grid__figure img { -webkit-mask-image: linear-gradient(#000 48%, transparent 94%); mask-image: linear-gradient(#000 48%, transparent 94%); }
  ```

## 15. `width: auto` on a logo hands its size to the srcset candidate

- **Symptom.** Logos render tiny — a 500x97 file at 135x26, a 500x372 file at 98x73.
- **Cause.** With `width: auto` a replaced element takes its intrinsic size, which with a `srcset` is the chosen candidate's; for an SVG that is the file's own dimensions, because `image_url: width:` does not resize SVGs. `max-width` only caps.
  ```css
  .logo-carousel__logo { width: auto; max-width: 180px; height: auto; }
  ```
- **Fix.** A definite box, and `object-fit: contain` fits the mark.
  ```css
  .logo-carousel__logo { width: 37.5%; height: 19.25%; object-fit: contain; }
  ```

### Deriving the box when the frame's own numbers do not fit

A container's declared size in Figma is not necessarily the box the artwork occupies: a 150x150 instance rendered a mark at 150x112 where the frame shows 103x77. Measure two or more marks with different aspects and solve for the one box that explains all of them — aspects 1.34 → 103x77 (height-limited), 5.17 → 150x29 and 4.44 → 150x34 (width-limited) are all one 150x77 box, and the same ratio (120x61.6 on mobile) predicts the mobile marks to the pixel.

## 16. An inline custom property cannot be overridden by a stylesheet — re-declare it on a child

- **Symptom.** A section stylesheet cannot change `--carousel-gap` per breakpoint.
- **Cause.** The shared snippet sets it in a `style` attribute, which beats any stylesheet.
- **Fix.** Re-declare it on a descendant the consumers inherit from — the track, whose slides read the same variable.
  ```css
  @media screen and (min-width: 750px) { .logo-carousel .scroll-carousel__track { --carousel-gap: 16px; } }
  ```

## 17. An author `display` declaration silently disables the `hidden` attribute

- **Symptom.** A play button appears to do nothing; the JS sets `hidden` on the cover and the button and calls `play()`.
- **Cause.** `[hidden] { display: none }` is a UA rule; any author `display` on the same element beats it, whatever the specificity.
  ```css
  .video-card__cover { display: block; }   /* cover never hid: it kept covering the video */
  .video-card__play  { display: flex; }    /* button never hid either */
  ```
- **Fix.** Whenever a script toggles `hidden` on an element you gave a `display`, add the `[hidden]` rule in the same commit.
  ```css
  .video-card__cover[hidden],
  .video-card__video[hidden],
  .video-card__play[hidden] { display: none; }
  ```
  A static `height: 100%` video under a cover still occupying 100% of a fixed-`aspect-ratio`, `overflow: hidden` box is laid out below it and clipped away; it must overlay:
  ```css
  .video-card__video { position: absolute; inset: 0; z-index: 2; }
  ```
- **Check.** Confirm the markup renders before suspecting the JS — `curl` the dev server and grep with a generous window, an `image_tag` srcset is ~700 characters; `{{ a == b }}` is not valid Liquid output, use `blank={% if x == blank %}YES{% else %}NO{% endif %} sources={{ x.sources.size }}`; then assert on the media element, `video.paused === false`, `currentTime > 0` and `readyState === 4` together prove playback.

## 18. Adding quick-add to a section that posts a variant directly

- **Symptom.** A section posts `selected_or_first_available_variant.id` straight to `/cart/add`, so a multi-variant product is added without the shopper choosing.
- **Fix.** Gate on the product tile's test.
  ```liquid
  assign has_options = false
  if product.variants_count > 1
    assign has_options = true
  endif
  if variant.quantity_rule.min > 1 or variant.quantity_rule.max != null or variant.quantity_rule.increment > 1
    assign has_options = true
  endif
  ```
  1. **Load the assets** — `component-quick-add.css`, `component-quick-add.js`, `component-modal-opener.js`; without them the opener is an inert button, no error.
  2. **`data-product-url` goes on the button**, not the `<modal-opener>`: `show()` reads it off the button passed to `modal.show(button)`. `component-button` accepts no arbitrary attributes, so write the opener longhand with the same `button button--<variant> button--<size>` classes.
  3. **Ids carry a section/block id** — `QuickAdd-{{ product.id }}` collides when one product sits in two blocks; pass `section.id | append: '-' | append: block.id` as `uid` to `component-quick-add-modal`.
- **Check.** After clicking the opener, `[id^=QuickAddInfo-]` goes from empty to ~28k characters with `product-info`, a variant picker and an add-to-cart. A `{% if product.available %}` wrapper renders no button at all for a sold-out product, unlike the tile's disabled "Sold out".

## 19. Native `<dialog>` for a popup, and the two things that bite

- **Symptom.** The only existing modal, `component-product-media-modal.js`, fakes one with an `open` attribute and `body.overflow-hidden`; copying it hand-rolls what `<dialog>` provides.
- **Fix.** `showModal()` gives focus trapping, Escape and `::backdrop` for free, so the element only wires open, close and click-outside.
  ```js
  onOpen()  { this.dialog.showModal(); }          /* showModal, not show */
  onClose() { this.dialog.close(); }
  onDialogClick(event) {                          /* the dialog box is the area
    if (event.target === this.dialog) this.dialog.close();   around the content */
  }
  ```
  1. **A dialog inside a `<form>` submits it.** Trigger and close button need `type="button"`, or opening a size chart adds the product to the cart.
  2. **`dialog.matches(':modal')`** proves it reached the top layer — immune to an ancestor's `overflow: hidden` or transform.
- **Check.** A `submit` listener on the form stays at `0` through open/close/backdrop/image clicks. In a hidden browser pane `dlg.open` and `:modal` are readable but a real Escape key press does not arrive; report Escape as native, not exercised.

## 20. Computing a date in Liquid (delivery estimates)

- **Symptom.** A delivery estimate needs today plus N days, and Liquid has no date arithmetic.
- **Cause.** `date: '%s'` returns a **string**, so it must be coerced before adding to it.
- **Fix.**
  ```liquid
  assign stamp = 'now' | date: '%s' | plus: 0        {%- comment -%} string -> number {%- endcomment -%}
  assign stamp = days | times: 86400 | plus: stamp
  assign day   = stamp | date: '%e' | strip | plus: 0   {%- comment -%} %e is space-padded {%- endcomment -%}
  assign month = stamp | date: '%b'
  ```
  Ordinals need the teens exception or you get "11st" and "13rd"; the four suffixes live in `en.default.json` under `general.date.ordinal.*` so a translator can blank them.
  ```liquid
  assign suffix = 'general.date.ordinal.th' | t
  assign teens = day | modulo: 100
  if teens < 11 or teens > 13
    assign ones = day | modulo: 10
    case ones
      when 1 …'st'  when 2 …'nd'  when 3 …'rd'
    endcase
  endif
  ```
- **Check.** Drive the days setting through 0 / 1 / 2 / 10 / 12 / 30 (none / nd / rd / teens / teens / month rollover) against `new Date(Date.now() + n*86400000)` in UTC.
- **Caveats for the merchant.** computed server-side per render, so the full-page cache can leave it minutes stale around midnight, and `'now'` is UTC, not the shop's timezone. Where the line is already `font-weight: 700`, pin the emphasised date to 700 too, or `<strong>` makes the browser synthesise a heavier face.

## 21. `* { margin: 0 }` breaks the centring of every native `<dialog>`

- **Symptom.** A `showModal()` dialog sits in the top-left corner: `position: fixed`, `inset: 0px 0px 0px 0px`, `margin: 0px 0px 0px 0px`.
- **Cause.** The UA centres with `dialog:modal { margin: auto }` plus `position: fixed; inset: 0`; the reset at the top of `assets/critical.css`, `* { box-sizing: border-box; margin: 0; }`, outranks it, so the auto margins never resolve.
- **Fix.** Every `<dialog>` restores the margin explicitly.
  ```css
  .my-dialog { margin: auto; }   /* centred: margin resolves to e.g. 45px 270px */
  ```

### Give a media dialog a definite width

- **Symptom.** A dialog wrapping an image collapses to the image's intrinsic width, and a `width: 100%` image inside has nothing to fill.
- **Cause.** `max-width` alone leaves the box at `fit-content` — the same circularity as §15.
- **Fix.** Scrolling on an inner wrapper, or an absolutely positioned close button scrolls away with a tall image; no `display: flex` on the dialog, or it overrides `dialog:not([open]) { display: none }` and renders permanently (§17).
  ```css
  .my-dialog  { width: min(92vw, 900px); max-height: 90vh; overflow: hidden; }
  .my-dialog__scroll { max-height: 90vh; overflow: auto; }   /* not on the dialog */
  ```

### Checking centring: use the layout width, not `innerWidth`

`window.innerWidth` includes the scrollbar and reports a false 7–8px offset; `document.documentElement.clientWidth` is what layout centres within.

### `naturalWidth` is not the file's size

A hidden or undecoded image reports a stale `naturalWidth` (170 for a 1600x1833 file); the `width`/`height` attributes `image_tag` emits come from Shopify's image object and are the reliable source size.
