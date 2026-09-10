# Overriding a shared component from a section stylesheet

## The trap

`stylesheet_tag` does **not** deduplicate. Every section that renders a
`button` emits `component-button.css` again, so the homepage loads it
**nine times**:

```
0: critical.css
5: component-button.css
7: component-quick-add.css
8: section-hero-split.css      <-- the section's own rules
9: component-button.css  <-- and here comes the component again
12, 14, 18, 22, 24, 26, 35: component-button.css
```

A section stylesheet therefore sits **before** most copies of the component's
stylesheet, not after it. Any section rule that tries to beat a component rule
at equal specificity loses to the next section's copy.

This is what made the hero strip's Add-to-Cart buttons render as white filled
pills when the section CSS clearly said otherwise:

```css
/* assets/section-hero-split.css - link index 8 */
.hero-strip-card__button {
  --button-background: transparent;   /* (0,1,0) */
}
```

```css
/* assets/component-button.css - link indexes 9, 12, 14, 18, 22, 24, 26, 35 */
.button--outline {
  --button-background: #fff;          /* (0,1,0), later in the document */
}
```

Both are one class. The component copy at index 9 wins, and seven more copies
follow it.

### Why it is easy to misdiagnose

- The section's `stylesheet_tag` order *inside its own file* looks correct —
  the component is loaded first, the section second. The duplicates come from
  **other sections** further down the page, so nothing in the file you are
  reading explains it.
- Adding a section to, or removing one from, `templates/index.json` can change
  the outcome, because it changes how many later copies exist.
- `document.styleSheets` cannot be introspected to find the winning rule:
  assets are served from `cdn.shopify.com`, so `sheet.cssRules` throws
  `SecurityError` and a CSSOM walk silently returns nothing. Read the
  `<link>` order instead:

```js
[...document.querySelectorAll('link[rel=stylesheet]')].map(
  (l, i) => i + ': ' + l.href.split('/').pop().split('?')[0]
);
```

## What to do instead

**Put the change in the component, as a variant.** The component's own file has
a single internal source order, identical in every copy, so intra-file cascade
is stable. The strip button became a new variant rather than a local override:

```css
.button--ghost {
  --button-background: transparent;
  --button-background-hover: #fff;
  --button-color: #fff;
  --button-color-hover: var(--milb-text);
  --button-border: #fff;
  --button-border-hover: #fff;
}
```

The section stylesheet then declares nothing about the button at all, and both
`.hero-strip-card__button` override blocks were deleted.

Ranked options when a section needs a shared component to look different:

1. **Add or use a variant on the component** — correct when the design is a
   reusable treatment ("transparent on a photo"). Document it in the snippet's
   `@param` list.
2. **Set a custom property the component already reads** — safe, because
   inherited custom properties are not subject to this ordering problem when
   set on an ancestor or via a more specific selector.
3. **Double the class for specificity** — `.hero-strip-card__button.button`
   (0,2,0) beats any single-class component rule regardless of order. A last
   resort: it works, but it hides the reason and the next person will not know
   why the selector is doubled. If you use it, say why in a comment.

Never rely on "my section CSS loads later" — for shared components it does not.

## Related: a size modifier reset by the responsive block

Same cascade family, inside one file. `component-button.css` had:

```css
.button--pill { padding: 4px 8px 4px 4px; }   /* line 148 */

@media screen and (max-width: 749px) {
  .button { padding: 9px 16px 9px 14px; }     /* line 165 - later, same specificity */
  .button__icon svg { width: 12px; }
}
```

The responsive rule targets the **base** class, so below 750px every size
modifier was silently reset to the default box — the pill rendered 36px tall
instead of its documented 26px. Restate the modifier inside the media query, or
place the size modifiers after it.

Check for this whenever a modifier's declarations are also declared on the base
class in a later block:

```bash
grep -n "button--pill\|^\s*\.button {" assets/component-button.css
```
