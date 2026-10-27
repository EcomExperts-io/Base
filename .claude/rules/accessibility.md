---
description: Accessibility standard (WCAG 2.2 AA) for theme code — what counts as a defect, how serious it is, and the fix expected in each case
paths:
  - "**/*.liquid"
  - "**/*.js"
  - "**/*.css"
  - "assets/**"
  - "sections/**"
  - "snippets/**"
  - "blocks/**"
  - "templates/**"
  - "layout/**"
---

# Accessibility standard

Target: **WCAG 2.2 level AA**, applied to the code in the diff. It
supersedes the accessibility notes in `html-standards.md` where the two differ.

## How to decide

A defect is worth reporting when one of these sentences ends with something
concrete:

- "A screen reader user would hear **…**" / "would not be told **…**"
- "A keyboard user cannot **…**"
- "At 200% zoom, **…**"
- "Someone who cannot distinguish red from green would **…**"

"It would be better if" is not a defect.

**Name the success criterion**, as number and title (`2.4.7 Focus Visible`). A
finding that fails none is not an accessibility finding; GitBot drops it. The
sections below map to the criteria they cover:

| Section | Criteria |
|---|---|
| 1. Controls | 4.1.2 Name, Role, Value · 2.1.1 Keyboard · 2.5.3 Label in Name |
| 2. Accessible names | 4.1.2 Name, Role, Value · 2.4.4 Link Purpose · 1.1.1 Non-text Content |
| 3. Forms | 1.3.1 Info and Relationships · 3.3.1 Error Identification · 3.3.2 Labels or Instructions · 1.3.5 Identify Input Purpose |
| 4. Keyboard, focus and order | 2.1.1 Keyboard · 2.1.2 No Keyboard Trap · 2.4.3 Focus Order · 2.4.7 Focus Visible · 2.4.11 Focus Not Obscured · 2.5.8 Target Size |
| 5. Images, icons, media, frames | 1.1.1 Non-text Content · 1.2.x Time-based Media · 4.1.2 for `<iframe>` titles |
| 6. Structure | 1.3.1 Info and Relationships · 2.4.6 Headings and Labels · 2.4.1 Bypass Blocks · 3.1.1 Language of Page |
| 7. Colour, contrast, zoom, reflow | 1.4.3 Contrast (Minimum) · 1.4.11 Non-text Contrast · 1.4.1 Use of Color · 1.4.4 Resize Text · 1.4.10 Reflow |
| 8. ARIA | 4.1.2 Name, Role, Value · 1.3.1 Info and Relationships · 4.1.3 Status Messages |
| 9. Motion, timing, carousels | 2.3.3 Animation from Interactions · 2.2.2 Pause, Stop, Hide · 2.2.1 Timing Adjustable |

**One finding per criterion per file**, anchored to the first line, the other
lines named in the body. At most eight findings per review, worst first.

**State the severity:**

| Severity | Meaning |
|---|---|
| **Blocker** | A task cannot be completed. Cannot buy, cannot submit, cannot reach a control at all, content unreachable by keyboard, focus trapped with no escape. |
| **Serious** | The task is possible but the experience is wrong or confusing: unlabelled field, unnamed control, wrong heading level, insufficient contrast, state not announced. |
| **Minor** | Real but low impact: redundant alt text, a missing landmark label, decorative SVG not hidden. |

**Every finding carries a fix** — element, attribute, value. "Add an accessible
name" is not a fix; `<button type="button" aria-label="{{ 'general.close' | t }}">` is.

---

## 1. Controls must be real controls

**Defect:** `<div>`, `<span>`, `<li>`, or an `<a>` without `href`, carrying an
`onclick` or a click listener.

Use `<button type="button">`, `<button type="submit">`, `<a href="…">` for
navigation, or a native form control. Anything else needs **all** of: a role,
`tabindex="0"`, key handlers for Enter **and** Space, and a visible focus
style; any one missing is a defect.

```liquid
{% comment %} Defect — not focusable, not keyboard operable, unnamed {% endcomment %}
<div class="modal__close" onclick="closeModal()">{% render 'icon-close' %}</div>

{% comment %} Expected {% endcomment %}
<button type="button" class="modal__close" aria-label="{{ 'general.close' | t }}">
  {% render 'icon-close' %}
</button>
```

Same family:

- **`<a>` used as a button** — no `href`, or `href="#"`, running JavaScript. It
  is announced as a link and is not activated by Space. *Serious.*
- **`<button>` with no `type` inside a form** submits it. Default is `submit`;
  say `type="button"` when it is not one. *Serious.*
- **Unavailable controls that are still operable.** Sold out, out of stock, not
  selectable: needs `disabled` or `aria-disabled="true"`, not only a CSS class.
  *Serious.*
- **State conveyed only by a class.** Selected, active, expanded, current: each
  needs `aria-pressed`, `aria-selected`, `aria-expanded`, `aria-current`, or a
  native `checked`. A class is invisible to assistive technology. *Serious.*
- **Single-choice sets built from divs** — variant pickers, size and colour
  swatches, filter chips. Use radios, or buttons in a named group. *Blocker* when
  no keyboard path exists to choose a variant.
- **Target size under 24×24 CSS pixels** (WCAG 2.2, 2.5.8) with no spacing to
  compensate. Swatches, close buttons, quantity steppers and pagination are the
  usual offenders. *Serious.*
- **A control that only works on drag** (2.5.7) — a slider or carousel with no
  button or keyboard equivalent. *Blocker.*

## 2. Every control needs an accessible name

**Defect:** an icon-only button, link, or input with no text, no `aria-label`,
no `aria-labelledby`.

- An SVG or `<img>` inside a button does **not** name it. Hide the icon
  (`aria-hidden="true"` on SVG, `alt=""` on img) and name the button.
- **`title` is not an accessible name.** A control named only by `title` is a
  defect. *Serious.*
- A name that is punctuation, an emoji, or "→" is not a name.
- **The visible label must be inside the accessible name** (2.5.3).
  `aria-label="Submit"` on a button reading "Subscribe" breaks voice control,
  which matches what is seen. *Serious.*
- **`aria-label` on a non-interactive element does nothing.** On a plain `<div>`
  or `<span>` with no role it is ignored. *Minor* unless it was the only name.
- **Ambiguous link text** — "Click here", "Read more", "Learn more", "Shop now"
  repeated down a page. Screen reader users list links out of context. Either
  make the text descriptive or extend it with visually hidden text. *Serious.*

```liquid
<a href="{{ article.url }}">
  {{ 'blog.read_more' | t }}
  <span class="visually-hidden">: {{ article.title | escape }}</span>
</a>
```

## 3. Forms

**Defect:** an `<input>`, `<select>` or `<textarea>` with a `placeholder` and no
`<label for="…">`, `aria-label`, or `aria-labelledby`; the placeholder vanishes
once the field is filled. *Serious.*

- **`for` must match a real, unique `id`.** A section or snippet can render more
  than once per page, so ids must be scoped: `id="Newsletter-email-{{ section.id }}"`.
  An unscoped id means the label points at another section's field. *Serious.*
- **Errors must be tied to their field** — `aria-describedby` pointing at the
  message, `aria-invalid="true"` on the field. A paragraph sitting nearby is not
  connected. *Serious.*
- **Messages that appear after submission need a live region** (`role="alert"`,
  or `aria-live="polite"` for success). The region must already be in the DOM
  before the message arrives, or it is not announced. *Serious.*
- **Grouped fields need a group name** — `<fieldset>` + `<legend>`, or
  `role="group"` with a name. *Serious.*
- **Required fields need the `required` attribute**, not only an asterisk.
- **`autocomplete` on personal fields** (1.3.5) — `email`, `name`, `tel`,
  `address-line1`, `postal-code`. *Minor,* real for people using autofill.
- **Never submit a form from a click handler** (`form.submit()`). It bypasses
  native validation, so `required` and `type="email"` are skipped. Use
  `<button type="submit">`. *Serious.*
- **A `<select>` that navigates on change** (3.2.2) — currency, language, sort.
  Changing a value with the keyboard moves through every option, firing
  navigation on each. Needs an explicit Go, or JavaScript that acts on commit,
  not on every change. *Blocker* for keyboard users.

## 4. Keyboard, focus and order

- **`tabindex` greater than 0 is a defect.** Only `0` and `-1`. *Serious.*
- **Focus styling removed with no replacement** — `outline: none`, `outline: 0`,
  or a `:focus` rule that sets nothing visible. Prefer `:focus-visible`. The
  replacement must be visible against its own background (3:1). *Serious.*
- **Anything that opens over the page** — modal, drawer, cart, search, age gate —
  must move focus in, keep focus inside while open, close on `Escape`, and
  return focus to the control that opened it. Missing the Escape route is a
  *Blocker.*
- **`aria-hidden="true"` on anything focusable.** It stays in the tab order but
  is absent from the accessibility tree, so a keyboard user lands somewhere never
  announced. Remove the attribute, or take it out of the tab order with `inert`
  or `tabindex="-1"`. *Serious.*
- **Focus must not be hidden behind sticky UI** (WCAG 2.2, 2.4.11). A sticky
  header, announcement bar or cart bar that covers the focused element is a
  defect. `scroll-margin-top` on focusable content usually fixes it. *Serious.*
- **Content revealed on `:hover` must also appear on `:focus-within`**, and must
  be dismissible without moving the pointer (1.4.13). *Serious.*
- **DOM order must match visual order.** Reordering with `order`, `row-reverse`
  or `grid-area` so that tab order contradicts what is seen is a defect.
  *Serious.*
- **Skip link** to main content where a long header repeats on every page, and it
  must become visible on focus. *Minor,* unless the header is very long.

## 5. Images, icons, media and frames

- **`<img>` with no `alt` attribute at all is a defect** — missing is not the
  same as empty; a screen reader may read the file name. *Serious.*
- Decorative: `alt=""`. Meaningful: text describing purpose, not appearance.
- In Liquid, use the merchant value, escaped: `alt="{{ image.alt | escape }}"`,
  with a sensible fallback. Never output an unescaped alt.
- **A fallback to visible text is the fix.** `alt="{{ settings.image_alt |
  default: settings.headline | escape }}"` — or the title, the product name —
  is correct even when that text setting is optional. That a merchant could
  leave every text field blank is content, not a code defect.
- **Alt text that is the file name, "image", or repeats adjacent visible text**
  is a defect. *Minor.*
- **Product images** take the product title as a fallback, not "product image".
- **Inline SVG**: decorative needs `aria-hidden="true"` and `focusable="false"`;
  meaningful needs `role="img"` plus `<title>` or `aria-label`. *Minor* to
  *Serious* depending on whether it names a control.
- **Icon fonts and CSS `content`** can be announced as stray characters. Keep
  meaning in text, not in a pseudo-element.
- **`<iframe>` needs a `title`** — video embeds, maps, review widgets. *Serious.*
- **Video and audio** need captions for recorded speech, must not autoplay with
  sound, and need controls. *Blocker* for autoplaying audio with no stop.
- **Text baked into an image** (1.4.5) is unreadable to assistive technology and
  blurs when zoomed. Put the text in markup over the image. *Serious.*

## 6. Structure: headings, landmarks, lists, tables

- **One `<h1>` per page.** A change that lets a page end up with **no h1**, or
  with **several**, is a defect — including a theme setting that lets a section
  heading be set to h1 on a template that already has one. *Serious.*
- **Do not skip levels downward**: h2 → h4 is a defect. Returning up to a sibling
  level is fine.
- **Do not use a heading for size**, and do not use a `<p class="h2">` where a
  heading belongs. Level and appearance are separate: keep the level right and
  change the class.
- **An unconstrained heading-level setting is a defect at the point it is added.**
  Offering h1–h6 on every section lets merchants build a broken outline. Reserve
  h1 for the page title; restrict section headings to subordinate levels.
- **Landmarks**: one `<main>` per page, plus `<header>`, `<nav>`, `<footer>`.
  More than one `<nav>` means each needs `aria-label`. *Minor* to *Serious.*
- **Lists must be lists.** A row of `<div>`s that reads as a list should be
  `<ul>`/`<li>` so the count is announced. *Minor.*
- **Data tables** — size charts, order history, specifications — need `<th>` with
  `scope`, and a `<caption>` or accessible name. A table used purely for layout
  needs `role="presentation"`. *Serious.*
- **`<html lang>`** must be set and must follow the active locale, not be
  hardcoded `en` on a translated storefront. *Serious.*
- **Unique, descriptive `<title>` per page.** *Minor.*
- **Duplicate `id` anywhere on the page** breaks every association pointing at
  it. *Serious.*

## 7. Colour, contrast, zoom and reflow

- **Text below 4.5:1 against its background is a defect.** Large text — 24px, or
  19px bold — may go to 3:1. *Serious.*
- **Interface components and states need 3:1**: input borders, focus rings, icons
  that carry meaning, chart and swatch boundaries.
- **Check this wherever a colour is hardcoded in the diff** — an inline `style`,
  a `{% style %}` block, or a literal hex in CSS. Compute the ratio and state it
  in the finding. Where colours come from a merchant colour scheme, do not guess;
  but a hardcoded colour against a known scheme background is fair game.
- **A template's `custom_css` does not fix a section's colour**; the section
  ships the failing default to every other template. Fix it in the section:
  a colour that passes, or a colour setting whose default passes and whose
  `info` states the contrast it needs. A brand colour that cannot change is a
  decision for the Lead and AM, not a reason to leave the section failing.
- **Colour must not be the only cue** (1.4.1). Sale prices, errors, required
  fields, selected and sold-out states, links inside body copy: each needs text,
  an icon, underline, or shape as well. *Serious.*
- **The viewport meta must not block zoom** — `user-scalable=no`,
  `maximum-scale=1`. *Blocker* for low-vision users.
- **Reflow at 320px** (1.4.10): no horizontal scrolling of the page at 320px
  wide. Fixed pixel widths on containers, and `white-space: nowrap` on long
  copy, are the usual causes. *Serious.*
- **Fixed heights on text containers** clip content at 200% zoom. Prefer
  `min-height`. *Serious.*
- **Text spacing** (1.4.12): the layout must survive increased line height and
  letter spacing without clipping.

## 8. ARIA

A native element beats ARIA; wrong ARIA is worse than none.

- **`aria-*` pointing at an id that does not exist is a defect.** Check
  `aria-labelledby`, `aria-describedby`, `aria-controls` against the ids in the
  same file — and remember a repeated section needs scoped ids. *Serious.*
- **A role that contradicts the element** — `role="button"` on an `<a href>`,
  `role="list"` on a `<table>`. *Serious.*
- **`aria-expanded` that is set once and never updated** always reports
  "collapsed". It must change with the state. *Serious.*
- **`aria-live` regions must exist before the content changes.** A region
  inserted together with its message is not announced. *Serious.*
- **Never put `aria-hidden` or `role="presentation"` on interactive content.**
- The attribute is **`role`**, not `aria-role`.

## 9. Motion, timing and carousels

- **Motion** — animation or transition of position, size or rotation
  (`transform`, `translate`, `scale`, `rotate`, `top`/`left`, scroll-linked
  effects), parallax, and auto-advancing carousels — must be disabled under
  `@media (prefers-reduced-motion: reduce)`. *Serious.*
- **Opacity fades and colour transitions are not motion** (2.3.3 covers
  movement) and need no reduced-motion override. Do not report them, and do
  not report a reduced-motion block as incomplete for leaving them running.
  A transition that combines both is a finding only for its motion part.
- **Anything that moves or auto-updates for more than five seconds needs a pause
  control** (2.2.2) — auto-rotating slideshows, scrolling announcement bars,
  marquees. *Serious.*
- Content flashing more than three times per second is a *Blocker.*
- **Carousels** need: real buttons for previous and next, keyboard access to
  every slide, a pause control when it auto-advances, and slides that are not
  hidden from assistive technology while visible.
- **Swiper manages its own arrow state.** On `<button>` elements passed to
  `navigation`, Swiper sets `disabled` and `aria-disabled` at each end of the
  track; do not report their disabled state. A `<div>` arrow, or one Swiper
  does not drive, is still a defect (section 1).
- **Countdown timers and auto-closing popups** need a way to extend or dismiss.

## 10. Patterns that recur in themes

- **Accordion / FAQ** — `<button>` inside the heading, `aria-expanded` updated,
  `aria-controls` pointing at the panel, panel hidden with `hidden` or
  `display:none` rather than opacity. Do not nest a button inside a heading that
  is itself a button.
- **Tabs** — `role="tablist"` / `tab` / `tabpanel`, arrow-key movement,
  `aria-selected`, one stop in the tab order.
- **Drawer, cart and search overlays** — section 4's focus contract in full.
- **Variant and size pickers** — section 1. Sold-out values must be
  programmatically unavailable, not just greyed. The group needs a name.
- **Quantity steppers** — real buttons, a labelled number input, and the value
  announced when it changes.
- **Cart count and "added to cart"** — a live region, or the update is silent.
- **Predictive search** — `role="combobox"` wiring, results count announced,
  results reachable by arrow keys.
- **Sticky headers and announcement bars** — 2.4.11, and they must not cover
  content at 200% zoom.
- **Newsletter and contact forms** — section 3 in full.
- **Product media galleries** — thumbnails are controls; the active one needs a
  programmatic state.

## 11. Shopify and Liquid specifics

- **Scope ids with `section.id` or `block.id`.** A section can appear twice on a
  page, and duplicate ids break every `for` and `aria-*` association. *Serious.*
- **Never emit merchant or customer input into an attribute unescaped.** Use
  `| escape`. Both a correctness and an accessibility defect.
- **Inline `onclick` that interpolates a Liquid value is a defect.** An
  apostrophe (`Men's`) breaks the handler silently. Use `data-` attributes and a
  listener. *Blocker* when it breaks the control.
- **Storefront-facing text must be translatable.** A hardcoded English string in
  a section, snippet, or schema label is a defect on a localized storefront; it
  belongs in `locales/*.json` behind `| t`. This includes accessible names, alt
  text fallbacks, and visually hidden text. *Serious.*
- **New section settings that can produce inaccessible output are defects when
  the setting is added** — an unconstrained heading-level picker, a colour picker
  with no contrast guidance, a toggle that can remove a label or an alt text.
- **`.visually-hidden` must keep the element in the accessibility tree**: the
  clip-rect pattern, never `display: none` or `visibility: hidden`.
- **`{% render %}` with an `id` argument** is how a repeated snippet stays
  unique; a snippet that hardcodes ids cannot be rendered twice.

---

## What not to report

- Anything on a line the diff does not touch, or in a removed line.
- Decorative images correctly marked `alt=""`.
- A WCAG criterion cited with no concrete user impact.
- Contrast where the colours come from merchant settings you cannot see.
- A missing `<label>` where an adequate `aria-label` or `aria-labelledby` exists.
- Anything needing a guess about merchant content, product data, or copy.
- Naming, structure or style preferences with no accessibility consequence.
- Speculation about JavaScript elsewhere in the theme, unless the diff shows it.
- **Untranslated or hardcoded English text.** That is a localization defect
  (`localization.md`), reported by the main review, not here.
- **Unescaped merchant output or any injection concern.** That is security,
  reported by the main review, not here.
- Copy and wording. An accessible name that exists but reads badly is not a defect.

Never describe a change as ADA compliant, WCAG compliant, or certified; a
review reports defects, it does not certify a storefront.

## Quick check before opening a PR

1. Tab through the change. Can you reach everything, see where you are, and get
   back out of anything that opened?
2. Is every control a `<button>` or `<a href>`, and does every one have a name?
3. Does every input have a `<label>`, and every image an `alt`?
4. Are the heading levels still in order, with exactly one h1?
5. Are hardcoded colours at least 4.5:1, and is colour never the only cue?
6. Does it still work at 200% zoom and 320px wide?
