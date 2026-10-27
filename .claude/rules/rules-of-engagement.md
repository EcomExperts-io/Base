---
description: Core engagement rules that apply to all work in this theme, regardless of file type
---

# Rules of Engagement

## Theme Structure

- `layout/theme.liquid` stays at 200–300 lines; markup is extracted into
  named snippets and sections.
- Snippets compose modals and reusable UI fragments.

## JavaScript Practices

- No `document.addEventListener('DOMContentLoaded', ...)`: wrap the markup in
  a custom element that extends `HTMLElement`, registered once with
  `customElements.define`, initialising in `connectedCallback` and cleaning up
  in `disconnectedCallback`.
- Never add jQuery. Native browser APIs, or Alpine.js (already in
  `theme.liquid`) for light state.

### Always set `display` on a custom element that carries section styling

A custom element defaults to `display: inline`, which paints no background
around block children and ignores vertical padding while `getComputedStyle()`
still reports both:

```css
.product-reviews {
  display: block; /* <product-reviews> is a custom element; without this the grey band never paints */
  background-color: #f4f4f4;
  padding: 60px 0;
}
```

Verify by comparing the element's box height to its inner wrapper's, not by
reading the computed style.

## Formatting and Code Hygiene

- Match the surrounding file's indentation and spacing; never mix tabs and spaces.
- No commented-out code and no "temporary" comments in a commit.
