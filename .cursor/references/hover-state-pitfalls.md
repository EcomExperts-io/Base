# Hover state pitfalls

Hover, focus and toggled-state CSS that reads right and renders wrong, and the traps in measuring it.

## 1. A later hover rule silently undoes a selected state

- **Symptom.** Hovering the *active* chip or tab makes it look unselected; a disabled button still lights up.
- **Cause.** `[aria-pressed='true']` and `:hover` both weigh 0-2-0, so whichever is later wins; a generic hover also fires on a `[disabled]` control.
- **Fix.** Guard the hover rather than reordering, and restate resting values under `[disabled]:hover`.
  ```css
  .carousel__filter:not([aria-pressed='true']):hover { … }
  .product-tile__atc[disabled]:hover { background-color: #000; }   /* 0-2-1 beats 0-1-1 */
  ```

## 2. `text-decoration: underline` on hover is a no-op if the link is already underlined

- **Symptom.** The hover underline changes nothing.
- **Cause.** The base rule never sets `text-decoration: none`, so the `<a>` is underlined at rest.
- **Check.** `getComputedStyle(el).textDecorationLine` — already `'underline'`? Pick another property.

## 3. Composed transforms must be restated, not replaced

- **Symptom.** An element centred with `transform: translate(-50%, -50%)` jumps to the corner on hover.
- **Cause.** The hover's `transform: scale(...)` replaces the whole transform list.
- **Fix.** Restate the translate in the hover and in the reduced-motion override.
  ```css
  .logo-carousel__logo:hover { transform: translate(-50%, -50%) scale(1.05); }
  ```

## 4. Wrap hover in `@media (hover: hover)`

- **Symptom.** On a touch screen a tapped card stays in its hover state until something else is tapped.
- **Cause.** `:hover` latches after a tap. Mobile emulation reports `(hover: hover)` false, so guarded rules go inert there.
- **Fix.** `@media (hover: hover) { .card:hover { … } }`

## 5. Card-driven versus link-driven hover — pick one per card

- **Symptom.** The image zooms on card hover while the title stays dead.
- **Cause.** `.card__title a:hover` fires only over the `<a>`, which wraps the title text alone; a card whose link's `::after` covers the whole card gets one event for both.
- **Fix.** Where nothing is a whole-card link, drive from the card and add `:focus-within` for keyboard users; no hover on non-interactive elements.
  ```css
  .category-tiles__card:hover .category-tiles__image,
  .category-tiles__card:focus-within .category-tiles__image { … }
  ```

## 6. Measuring hover in a browser

- **Transitions race the assertion.** `getComputedStyle` right after a synthetic hover returns a mid-transition value; `el.style.width = '16px'` read on the same tick reads the old value. Inject `*, *::before, *::after { transition: none !important; }` and read instantly.
- **Screenshot coordinates are scaled.** `scale = screenshotWidth / window.innerWidth`; confirm the target with `document.elementFromPoint(sx / scale, sy / scale)`.
- **Cross-origin stylesheets cannot be enumerated.** Theme CSS comes from `cdn.shopify.com`, so `sheet.cssRules` throws and a `document.styleSheets` walk finds nothing. Fetch the stylesheet text and test selectors with `querySelectorAll`; a regex audit that keeps only the last line of a multi-line selector list reports "all good".

## 7. A selector matching zero elements is not necessarily wrong

- **Symptom.** A rule matches nothing on the page.
- **Cause.** The template data does not exercise it — no size variants, an empty URL setting, a different `nav_style`.
- **Check.** Confirm the class exists in the Liquid, then inject a fixture element with that class anywhere in `<body>` and hover it; the stylesheet is global once loaded.

## 8. A fade may live in the asset

- **Symptom.** The frame fades a portrait into the section surface; a CSS fade on top of one baked into the asset doubles it.
- **Check.** Sample the asset's alpha by row; opaque to the bottom means the fade is applied in the design.
- **Fix.** `mask-image` on the image, not an overlay gradient, which would also fade anything behind it.
  ```css
  .card-grid__figure img { -webkit-mask-image: linear-gradient(#000 48%, transparent 94%); mask-image: linear-gradient(#000 48%, transparent 94%); }
  ```
