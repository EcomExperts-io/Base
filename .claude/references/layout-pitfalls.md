# Layout pitfalls — declarations that report correct and render wrong

Six traps where `getComputedStyle` returns the written value and the box is wrong — measure the box, do not read the style. Short form: `css-standards.md`, "Defensive CSS".

## 1. A flex child of a scrolling panel shrinks instead of letting it scroll

- **Symptom.** In a flex-column drawer (header, scrolling body, footer) a header declared `block-size: 56px` measures 51.8px and an `aspect-ratio` banner measures short; everything below sits a few pixels low. Only at the height where the panel is meant to scroll.
- **Cause.** Flex resolves shrinking before overflow. Every item with the default `flex-shrink: 1` gives up space before anything overflows — `overflow-y: auto` on the body does not protect the siblings, and a box with no content (an `aspect-ratio` banner) has nothing to resist with and shrinks first.
- **Fix.** The body is the only thing allowed to give.
  ```css
  .drawer__header, .drawer__footer, .drawer__body > * { flex: 0 0 auto; }
  ```

## 2. A flex item's automatic minimum size beats `aspect-ratio`

- **Symptom.** A media box sized by `aspect-ratio` renders at the height of the uploaded photograph — on the mobile crop, while desktop looks right.
- **Cause.** A flex item's automatic minimum is `min-height: auto`, which resolves to the content's size and wins over `aspect-ratio`. It bites only where the drawn box is shorter than the image's natural height at that width, so the same code measures right against one upload and wrong against another.
- **Fix.** `min-inline-size: 0` for a row.
  ```css
  .media { aspect-ratio: 393 / 215; min-block-size: 0; }
  ```

## 3. A child's margin collapses out through the section

- **Symptom.** A block with `margin-block: 90px` lands where the design wants it, but the section box measures 90px shorter and starts 90px lower than its frame. Screenshots look right; the fidelity crop does not.
- **Cause.** The section's block padding is a merchant range that starts at 0; with no padding, border or formatting context between them the child's margin collapses through the custom element, through `.page-width` and out of the wrapper.
- **Fix.** `display: flow-root` on the wrapper also works; padding is the smaller change.
  ```css
  .cart-empty { padding-block: 90px; }   /* not margin-block */
  ```

## 4. `[hidden]` does nothing once the component sets its own `display`

- **Symptom.** Elements with `el.hidden === true` still render.
- **Cause.** An author `display: flex` outranks the UA sheet's `[hidden] { display: none }` at any specificity.
- **Fix.**
  ```css
  .cart-drawer__upsell-card { display: flex; }
  .cart-drawer__upsell-card[hidden] { display: none; }
  ```

## 5. A font weight the library never loaded, and the probe that lies about it

- **Symptom.** Text in `font-weight: 600` on the accent family renders lighter and narrower than the frame; `getComputedStyle` says `600`; a hot band in the heatmap sits on one line of text.
- **Cause.** `snippets/css-variables.liquid` loaded the family's regular and italic faces and no bold, so the browser synthesised one. `font_modify: 'weight', '600'` emits nothing when the library has no such face. `document.fonts.check('600 16px "Family"')` returns `true` for every weight — it answers whether the family can render the text, not whether the face is loaded.
- **Fix.** If the library has no 600 the semibold renders at 700; write that beside the `font_face` calls.
  ```liquid
  {{ settings.type_accent_font | font_modify: 'weight', 'bold' | font_face: font_display: 'swap' }}
  ```
- **Check.**
  ```js
  [...document.fonts].filter(f => f.family === 'Family').map(f => f.weight + ' ' + f.status)
  ```

## 6. A span in a second font grows the line

- **Symptom.** A five-line heading at `line-height: 32.5px` measures 168.5px, not 162.5; a byline at 14/20 measures 21. Every span reports the inherited line height.
- **Cause.** An `<em>` in a second family inherits the line height, but its inline box is placed by that family's own ascent and descent, which poke out of the strut by a couple of pixels per line that holds one.
- **Fix.** `line-height: 1` still grows the line in desktop Chrome; `0` is what normalize.css gives `sub` and `sup`.
  ```css
  .heading em { line-height: 0; }
  ```
