# Overriding a shared component from a section stylesheet

`stylesheet_tag` does not deduplicate, so a section rule cannot rely on loading after a shared component's rule.

## The trap

- **Symptom.** A section's override of a shared component's custom property has no effect — buttons render as white filled pills while the section CSS sets `--button-background: transparent`.
- **Cause.** Every section that renders the component emits its stylesheet again, so a page loads `component-button.css` nine times and the section stylesheet sits *before* most copies; at equal specificity the later copy wins.
  ```
  0: critical.css
  5: component-button.css
  7: component-quick-add.css
  8: section-hero-split.css      <-- the section's own rules
  9: component-button.css        <-- and here comes the component again
  12, 14, 18, 22, 24, 26, 35: component-button.css
  ```
  ```css
  /* assets/section-hero-split.css - link index 8 */
  .hero-strip-card__button { --button-background: transparent; }   /* (0,1,0) */
  /* assets/component-button.css - link indexes 9, 12, 14, 18, 22, 24, 26, 35 */
  .button--outline { --button-background: #fff; }                   /* (0,1,0), later in the document */
  ```

### Why it is easy to misdiagnose

- The `stylesheet_tag` order inside the section's own file looks correct; the duplicates come from sections further down the page, so adding or removing a section in `templates/index.json` changes the outcome.
- `sheet.cssRules` throws `SecurityError` for assets served from `cdn.shopify.com`, so a `document.styleSheets` walk silently returns nothing.
- **Check.** Read the `<link>` order instead.
  ```js
  [...document.querySelectorAll('link[rel=stylesheet]')].map(
    (l, i) => i + ': ' + l.href.split('/').pop().split('?')[0]
  );
  ```

## What to do instead

- **Fix.** Put the change in the component as a variant — one internal source order, identical in every copy — and delete the section's override block.
  ```css
  .button--ghost {
    --button-background: transparent;
    --button-background-hover: #fff;
    --button-color: #fff;
    --button-color-hover: var(--color-foreground);
    --button-border: #fff;
    --button-border-hover: #fff;
  }
  ```

Ranked options when a section needs a shared component to look different:

1. **A variant on the component** — for a reusable treatment ("transparent on a photo"). Document it in the snippet's `@param` list.
2. **A custom property the component reads but does not redeclare on its own element.** A property declared on the element beats any inherited value, whatever the ancestor's specificity or source order — so if the component sets it on itself (`.button--outline { --button-background: #fff }`), an ancestor override does nothing; use option 1 or 3. If the component only reads it, an ancestor declaration is immune to stylesheet order.
3. **Double the class** — `.hero-strip-card__button.button` (0,2,0) beats any single-class component rule regardless of order. Last resort; say why in a comment.

## Related: a size modifier reset by the responsive block

- **Symptom.** Below 750px every size modifier renders at the default box — the pill 36px tall instead of its documented 26px.
- **Cause.** A responsive rule on the base class, later in the same file at equal specificity, resets the modifier's declarations.
  ```css
  .button--pill { padding: 4px 8px 4px 4px; }   /* line 148 */

  @media screen and (max-width: 749px) {
    .button { padding: 9px 16px 9px 14px; }     /* line 165 - later, same specificity */
    .button__icon svg { width: 12px; }
  }
  ```
- **Fix.** Restate the modifier inside the media query, or place the size modifiers after it.
- **Check.** Whenever a modifier's declarations are also on the base class in a later block.
  ```bash
  grep -n "button--pill\|^\s*\.button {" assets/component-button.css
  ```
