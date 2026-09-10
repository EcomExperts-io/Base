# VitePress docs: Liquid/Vue mustache gotchas

When writing docs in `docs/` (VitePress), remember VitePress pages are Vue-rendered.

## ✅ Safe patterns

- Put Liquid examples inside fenced code blocks:

```liquid
<div>{{ product.title }}</div>
```

- Put JSON schema inside fenced code blocks:

```json
{ "name": "Example" }
```

## ⚠️ Common “blank page” cause

If you include Liquid mustaches in normal text (including **inline code**), Vue may try to evaluate them and the page can render blank.

**Bad (can break rendering):**

- `BrandStory-{{ section.id }}`

**Good (escape mustaches like existing docs do):**

- `BrandStory-\{\{ section.id \}\}`
- `color-\{\{ section.settings.color_scheme \}\}`

## ⚠️ Another common docs pitfall: section scripts that run unconditionally

When documenting sections, watch for inline `<script>` tags that query the DOM **outside** the section’s render guard (e.g. the markup is inside `{% if ... %}` but the script is not).

- This can throw on pages where the section doesn’t render (for example `document.querySelector(...)` returning `null` and then accessing `.offsetHeight`).
- Fix by guarding for missing elements:

```js
const el = document.querySelector('.some-element');
if (el) {
  // safe to read layout
}
```
