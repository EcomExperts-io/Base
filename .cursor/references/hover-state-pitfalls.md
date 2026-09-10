# Hover state pitfalls

Learned while adding hover states across the MiLB homepage sections. Each of
these produces CSS that looks right in review and does nothing (or the wrong
thing) on screen.

## 1. A later hover rule silently undoes a selected state

`[aria-pressed='true']` / `[aria-selected='true']` and `:hover` both weigh
0-2-0. Append the hover rule after the selected rule and hovering the *active*
filter chip or tab reverts it to looking unselected — the exact opposite of what
a hover should communicate.

Guard the hover instead of reordering, so the rule stays correct wherever it
sits in the file:

```css
.teams-carousel__filter:not([aria-pressed='true']):hover { … }
.top-players__tab:not([aria-selected='true']):hover { … }
```

Same idea for controls that must not invite a click: a disabled button needs its
resting values restated under `:hover`, or the generic hover still fires on it.

```css
.product-tile__atc[disabled]:hover { background-color: #000; }   /* 0-2-1 beats 0-1-1 */
.scroll-carousel__arrow[disabled]:hover { /* restate resting */ }
```

## 2. `text-decoration: underline` on hover is a no-op if the link is already underlined

`.product-spotlight__size-guide` sets colour and font but never
`text-decoration: none`, so as an `<a>` it is underlined at rest. The hover
"underline" changed nothing.

Check the *resting* computed value before picking the hover property:

```js
getComputedStyle(el).textDecorationLine   // 'underline' already? pick another property
```

Underline is the right hover only where the base rule sets
`text-decoration: none` (it does on `.hero-strip-card__title a`,
`.teams-carousel__team`, `.fan-gallery__handle`). Where text is white on a
photo, underline is usually the *only* legible option — a colour shift will not
read.

## 3. Composed transforms must be restated, not replaced

An element already centred with `transform: translate(-50%, -50%)` loses its
centring if the hover sets `transform: scale(...)`. It jumps to the corner.

```css
.brand-carousel__logo:hover { transform: translate(-50%, -50%) scale(1.05); }
```

The reduced-motion override has to restate the translate too, not use `none`.

## 4. Wrap hover in `@media (hover: hover)`

On a touch screen `:hover` latches after a tap and leaves the card or button
looking stuck until something else is tapped. Verified: mobile emulation reports
`(hover: hover) → false`, `(pointer: coarse) → true`, so guarded rules go inert.

## 5. Card-driven vs link-driven hover — pick one per card and stick to it

If the card's image zooms on card hover, the title has to move on *card* hover
too. `.auction-card__title a:hover` left the title dead while the image zoomed,
because the `<a>` wraps only the title text. `.product-tile` gets this right for
free: its title's `::after` overlay covers the whole card, so card hover and
link hover are the same event.

Where nothing in the card is a whole-card link, drive from the card and add
`:focus-within` so keyboard users tabbing to the CTA get the same feedback:

```css
.category-tiles__card:hover .category-tiles__image,
.category-tiles__card:focus-within .category-tiles__image { … }
```

Do **not** add hover affordances to non-interactive elements — the carousel
dots are `<span>`s in an `aria-hidden` container, so a hover there advertises a
click that does not exist. Same reason the spotlight's product image has no
hover: it is a plain `div`, not a link.

## 6. Verifying hover in a browser — three traps

1. **Transitions race the assertion.** Immediately after a synthetic hover,
   `getComputedStyle` returns a value mid-transition (or still at rest). A 1s
   wait is not reliably enough either. Inject
   `*, *::before, *::after { transition: none !important; }` and read the hover
   value instantly.
2. **Screenshot coordinates are scaled.** The hover action takes pixels in the
   screenshot frame, not CSS pixels. Convert:
   `scale = screenshotWidth / window.innerWidth`. Confirm the target with
   `document.elementFromPoint(sx / scale, sy / scale)` before trusting a result.
3. **Cross-origin stylesheets cannot be enumerated.** Theme CSS is served from
   `cdn.shopify.com`, so `sheet.cssRules` throws and any audit that walks
   `document.styleSheets` silently finds zero rules. Extract selectors from the
   local files instead and test them with `querySelectorAll`.

Also: when auditing selectors by regex, a rule whose selector spans multiple
lines (a comma list) will lose all but the last line if you take
`prelude.split('\n').pop()`. That hid an entire section's rules from a check
that reported "all good".

## 7. A selector matching zero elements is not necessarily wrong

Four rules matched nothing because the template data does not exercise them:
no size variants on the spotlight product, an empty `size_guide_url`,
`nav_style: 'text'` instead of `'avatar'`, and no fan videos uploaded yet.
Confirm the class exists in the Liquid, then prove the rule by injecting a
fixture element with that class and hovering it for real — the CSS is global
once the stylesheet loads, so a fixture anywhere in `<body>` exercises it.

## 8. A theme-wide `!important` was overriding every button's font size on mobile

`assets/critical.css` carried the standard iOS zoom guard, but with `button` in
the selector list:

```css
@media screen and (max-width: 600px) {
  input, textarea, select, button { font-size: 16px !important; }
}
```

iOS Safari zooms the viewport when a **text-entry** field smaller than 16px takes
focus. Buttons never trigger it. Including `button` silently forced every button
in the theme to 16px below 600px — the teams filter chips (11.5px), player tabs
(12px), spotlight size chips (14px), product-tile add-to-cart (13px) and any
`<button>`-rendered CTA. `button` is now removed from that selector.

How it presented: every property from the section's own rule applied *except*
`font-size`. The giveaway was the computed `letter-spacing` — declared as
`0.08em`, it computed to `1.28px`, which is 0.08 × **16**, naming the font size
that actually won. **When one property of a rule mysteriously loses, check a
second, em-derived property; its computed value tells you the real font size.**

Note also that `component-scroll-carousel.css` is fetched 8 times on the
homepage (one `stylesheet_tag` per section that renders a carousel). That is
harmless — Shopify serves it from cache — but it makes stylesheet dumps
confusing to read, so dedupe by filename before comparing rules.

## 9. Two more measurement traps (same root cause as §6.1)

- **A transitioned property reads stale even for an inline style you just set.**
  Setting `dot.style.width = '16px'` and measuring on the same tick returned
  4px, which looked exactly like a cascade override. It was the `transition:
  width` on the element. Disable transitions before measuring anything that
  animates — including when testing whether a rule applies at all.
- **`document.styleSheets` can silently yield nothing** on a Shopify dev-server
  page even when the sheets are same-origin-ish. Fetching the stylesheet URL and
  regexing the text is the reliable way to see what is actually being served.

## 10. An out-of-flow decorative image needs both a floor and a clip

Top Players positions its portrait absolutely so it can overlap the heading row
above and the section padding below, as the frame shows. Being out of flow, it
contributes nothing to the section's height — so the moment the content column
was short (a player tab whose collection setting is empty renders a name and
nothing else) the section collapsed and the 696px portrait ran straight over the
next section.

Two rules are needed together, and neither is sufficient alone:

```css
.top-players            { overflow: hidden; }   /* hard stop: it can never escape */
.top-players__figure    { min-height: 592px; }  /* so it is not visibly cut either */
```

The floor is derivable, not guessed. With the portrait offset `-46px` and
`H`px of header above it:

```
portrait bottom = padding_top + H + margin + (-46) + 696
section  bottom = padding_top + H + margin + R + padding_bottom
                            → R >= 696 - 46 - padding_bottom
```

At `padding_bottom: 80` that is `R >= 570`; 592 is the frame's own row height, so
it satisfies the bound and matches the design. Verify on the *worst* content
case, not the happy one — here, the tab with an empty collection.

## 11. Absolutely positioning a grid child hands its column to the next item

The avatar variant moves the heading out of the header and runs it vertically
down the left edge. The header is a two-column grid (heading | nav), so taking
the heading out of flow promoted the **nav** into column 1 and it jumped to the
left edge.

`justify-content: flex-end` does nothing here — the header is a grid, not a flex
row. Collapse the grid instead:

```css
.top-players--nav-avatar .top-players__header {
  grid-template-columns: minmax(0, 1fr);
  justify-items: end;
}
```

Whenever you pull one child of a grid out of flow, re-check what the remaining
children do — auto-placement will shuffle them up.

## 12. A condensed face in the frame cannot be matched by tracking alone

The avatar variant's vertical watermark is set in a condensed bold. Titillium is
not condensed, so cap height and text length could not both be matched: sizing
to the frame's 82px cap made the run 844px against the frame's 708px, and sizing
to the run made the letters visibly thinner.

Matching the cap height and pulling the tracking in (`-0.055em`) landed 727px
against 708 — within 3% on both axes, which is as close as the available family
gets. Worth stating in the handover rather than leaving it as an unexplained
magic number.

## 13. `templates/index.json` is editor-owned — pushing it reverts merchant changes

The file's own header says it "may be updated by the Shopify admin theme
editor". A `theme push --only templates/index.json` silently overwrites whatever
a merchant changed there. A `nav_style` switched in the theme editor was reverted
by a later push of this file.

Before pushing that file, pull the remote copy and diff it. Push section and
asset files freely; treat JSON templates and `config/settings_data.json` as
shared state.

## 14. Check whether a fade lives in the asset before recreating it in CSS

The frame fades the Top Players portrait out into the section surface at the
bottom. Before adding it, check which layer owns it — sampling the asset's alpha
by row settled it in one pass:

```js
/* mean alpha of non-transparent pixels, bottom 30% of the asset */
row 503 (70%)  meanAlpha=254
row 713 (99%)  meanAlpha=253      → no fade in the asset; it is applied in the design
```

Had the fade been baked in, adding a CSS one would have doubled it.

Measuring the fade from the render: profile `max deviation from the section
background` per row across the portrait's x-range. A linear fade shows as a
straight ramp, and the two stops fall out of a least-squares fit — extrapolate
the ramp up to the opaque plateau for the start, and down to zero for the end.
Both Top Players variants and the mobile frame gave the same shape (48% → 94%),
so one mask serves every breakpoint.

Use `mask-image` on the portrait, not an overlay gradient in the section
background colour: the watermark sits *behind* the portrait, and an overlay
would fade that too. The frame keeps the watermark uniform. Ship
`-webkit-mask-image` alongside for older Safari.

## 15. `width: auto` on a logo hands its size to the srcset candidate

The brand logos rendered tiny. The CSS was:

```css
.brand-carousel__logo { width: auto; max-width: 180px; height: auto; }
```

With `width: auto` a replaced element takes its intrinsic size, and with a
`srcset` present that is the size of whichever candidate the browser picked —
which for an **SVG** is just the file's own dimensions, because Shopify's
`image_url: width:` does not resize SVGs. Measured before the fix:

| logo | file | rendered |
|---|---|---|
| New Era | 500x372 | 98x73 |
| Champion | 500x97 | 135x**26** |
| Nike | 500x117 | 135x32 |

`max-width` only caps; it never scales anything up. Give the logo a **definite
box** and let `object-fit: contain` fit the mark:

```css
.brand-carousel__logo { width: 37.5%; height: 19.25%; object-fit: contain; }
```

### Deriving the box when the frame's own numbers do not fit

Figma reported a 150x150 instance, but sizing a 150x150 box was wrong: it
rendered New Era at 150x112 where the frame shows 103x77. Measuring all three
marks in the render and solving for one box that fits them settled it —

| mark | aspect | frame render | fits 150x77? |
|---|---|---|---|
| New Era | 1.34 | 103x77 | height-limited -> 103x77 |
| Champion | 5.17 | 150x29 | width-limited -> 150x29 |
| Nike | 4.44 | 142x32 | width-limited -> 150x34 |

So the effective box is **150 x 77**, not the square instance — the artwork
inside each instance carries its own padding. The same ratio held on mobile
(120 x 61.6), and predicting the mobile marks from it matched the render to the
pixel, which is what confirmed the model.

**Lesson:** a container's declared size in Figma is not necessarily the box the
artwork occupies. Measure two or more marks with different aspects and solve for
the box that explains both.

## 16. An inline custom property cannot be overridden by a stylesheet — re-declare it on a child

`component-scroll-carousel.liquid` sets `--carousel-gap` in a `style` attribute,
so a section stylesheet cannot change it per breakpoint. Re-declare it on a
descendant that the consumers inherit from — here the track, whose slides read
the same variable:

```css
@media screen and (min-width: 750px) {
  .brand-carousel .scroll-carousel__track { --carousel-gap: 16px; }
}
```

That gave the frame's 8px mobile / 16px desktop gaps without adding a parameter
to the shared snippet.

## 17. An author `display` declaration silently disables the `hidden` attribute

The fan gallery's play button appeared to do nothing. The JS was correct — it
set `hidden` on the cover and the button and called `play()` — but two CSS rules
outranked the UA stylesheet's `[hidden] { display: none }`:

```css
.fan-card__cover { display: block; }   /* cover never hid: it kept covering the video */
.fan-card__play  { display: flex; }    /* button never hid either */
```

`[hidden]` is a *UA* rule, so any author `display` on the same element beats it,
whatever the specificity. Every element whose visibility is toggled by the
attribute needs it restated:

```css
.fan-card__cover[hidden],
.fan-card__video[hidden],
.fan-card__play[hidden] { display: none; }
```

This is the same trap as `.scroll-carousel__dot[hidden]` in the carousel. **If
you set `display` on an element and any script toggles `hidden` on it, add the
`[hidden]` rule in the same commit.**

The second half of the bug: `.fan-card__video` was static and `height: 100%`
inside a fixed-`aspect-ratio`, `overflow: hidden` media box. With the cover
still occupying its 100%, the revealed video was laid out *below* it and clipped
away — so even a working `play()` was invisible. It needed to overlay, not follow:

```css
.fan-card__video { position: absolute; inset: 0; z-index: 2; }
```

### Debugging notes

- Confirm the branch renders before suspecting the JS. `curl` the dev server and
  dump the element — but give the grep a generous window: a Shopify `image_tag`
  srcset is ~700 characters, and a 1400-char window made it look like the video
  markup was missing entirely.
- `{{ a == b }}` is not valid Liquid output — a comparison needs
  `{% if %}`. Useful debug line for a `video` setting:
  `blank={% if x == blank %}YES{% else %}NO{% endif %} sources={{ x.sources.size }}`
- Assert on the media element, not on appearances:
  `video.paused === false`, `currentTime > 0` and `readyState === 4` together
  prove it is really playing.

## 18. Adding quick-add to a section that posts a variant directly

Three sections built their own add-to-cart and posted
`selected_or_first_available_variant.id` straight to `/cart/add`, so a
multi-variant product was added without the shopper choosing — the hero strip
and Team Feature were fixed; anything new should follow the same shape.

The gate is the product tile's test, and it belongs in all of them:

```liquid
assign has_options = false
if product.variants_count > 1
  assign has_options = true
endif
if variant.quantity_rule.min > 1 or variant.quantity_rule.max != null or variant.quantity_rule.increment > 1
  assign has_options = true
endif
```

Three things to get right:

1. **Load the assets.** The section needs `component-quick-add.css`,
   `component-quick-add.js` and `component-modal-opener.js`. Without them the
   opener is an inert button — no error, just nothing.
2. **`data-product-url` goes on the button**, not the `<modal-opener>`.
   `ModalOpener` calls `modal.show(button)` and `show()` reads the attribute off
   that button to fetch the form. `component-button` accepts no arbitrary
   attributes, so the opener is written out longhand wearing the same
   `button button--<variant> button--<size>` classes — the
   appearance is unchanged and worth asserting (background + font-size).
3. **Ids must carry a section/block id.** The tile's `QuickAdd-{{ product.id }}`
   collides the moment one product is picked in two blocks, which the hero does.
   `component-quick-add-modal` takes a `uid` for this; pass
   `section.id | append: '-' | append: block.id`.

Assert the whole path, not just the markup: after clicking the opener the
dialog's `[id^=QuickAddInfo-]` should go from empty to ~28k characters and
contain `product-info`, a variant picker and an add-to-cart.

**Watch the availability gate.** These sections wrap the control in
`{% if product.available %}`, so a sold-out product renders **no button at all**
— unlike the product tile, which shows a disabled "Sold out". Worth knowing
before concluding the quick-add "did not apply" to a card.

## 19. Native `<dialog>` for a popup, and the two things that bite

`.claude/rules/html-standards.md` says to use `<dialog>` for modals — but there
is **no house dialog helper** to copy. The only modal in this theme is
`component-product-media-modal.js`, which fakes one with an `open` attribute
and a `body.overflow-hidden` class. Don't copy it: the same rules say to use
native `<dialog>` and not to hand-roll overlays.

`showModal()` gives focus trapping, Escape and `::backdrop` for free, so the
element only wires open, close and click-outside:

```js
onOpen()  { this.dialog.showModal(); }          /* showModal, not show */
onClose() { this.dialog.close(); }
onDialogClick(event) {                          /* the dialog box is the area
  if (event.target === this.dialog) this.dialog.close();   around the content */
}
```

Two things to get right:

1. **A dialog placed inside a `<form>` will submit it.** The spotlight's size
   guide sits inside the product form, so both the trigger and the close button
   need `type="button"` — without it, opening the size chart adds the product to
   the cart. Assert it: attach a `submit` listener to the form, drive open/close/
   backdrop/image clicks, and check the counter is still `0`.
2. **`dialog.matches(':modal')`** is the check that it really reached the top
   layer — that is what makes it immune to an ancestor's `overflow: hidden` or
   transform, which this section has.

Verifying in a hidden browser pane: `dlg.open` and `:modal` are readable, but a
real **Escape key press does not arrive** (same as clicks and scrolls). Escape is
UA behaviour for `showModal()` and is not ours to break — say it is native rather
than claiming it was exercised.

## 20. Computing a date in Liquid (delivery estimates)

Shopify Liquid has no date arithmetic, but `date: '%s'` plus integer maths gets
there. The one non-obvious step is that `%s` returns a **string**, so it has to
be coerced before adding to it:

```liquid
assign stamp = 'now' | date: '%s' | plus: 0        {%- comment -%} string -> number {%- endcomment -%}
assign stamp = days | times: 86400 | plus: stamp
assign day   = stamp | date: '%e' | strip | plus: 0   {%- comment -%} %e is space-padded {%- endcomment -%}
assign month = stamp | date: '%b'
```

English ordinals need the teens exception, or you get "11st" and "13rd":

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

Put the four suffixes in `en.default.json` under `general.date.ordinal.*` rather
than inline — they are theme-authored strings, and a translator for a language
without ordinals can blank them.

**Test the branches, not just one render.** Driving the days setting through
0 / 1 / 2 / 10 / 12 / 30 exercises none / nd / rd / teens / teens / month-rollover
in six page loads, and each is checkable against
`new Date(Date.now() + n*86400000)` in UTC.

**Caveats worth telling the merchant:** the date is computed server-side per
render, so Shopify's brief full-page cache can leave it a few minutes stale
around midnight, and `'now'` is UTC rather than the shop's local timezone. Both
are immaterial for a shipping estimate, but they are the reason not to promise
"always exactly right".

Where the receiving line is already `font-weight: 700`, pin the emphasised date
to 700 as well — leaving it to `<strong>` makes the browser hunt for a heavier
face than the bold one loaded and synthesise it.

## 21. `* { margin: 0 }` breaks the centring of every native `<dialog>`

A `showModal()` dialog is centred by the UA rule `dialog:modal { margin: auto }`
combined with `position: fixed; inset: 0`. `assets/critical.css` opens with

```css
* {
  box-sizing: border-box;
  margin: 0;
}
```

which outranks the UA rule, so `margin` computes to `0px`, the auto margins never
resolve and the dialog sits in the **top-left corner** of the viewport. Confirmed
by reading it back: `position: fixed`, `inset: 0px 0px 0px 0px`,
`margin: 0px 0px 0px 0px`.

Every `<dialog>` added to this theme needs the margin restored explicitly:

```css
.my-dialog { margin: auto; }   /* centred: margin resolves to e.g. 45px 270px */
```

### Give a media dialog a definite width

`max-width` alone leaves the box at `fit-content`, so a dialog wrapping an image
collapses to that image's intrinsic width — and an image at `width: 100%` inside
it then has nothing to fill. Same circularity as the brand-logo bug in §15.

```css
.my-dialog  { width: min(92vw, 900px); max-height: 90vh; overflow: hidden; }
.my-dialog__scroll { max-height: 90vh; overflow: auto; }   /* not on the dialog */
```

Put the scrolling on an inner wrapper, not the dialog: with `overflow: auto` on
the dialog itself, an absolutely-positioned close button scrolls away with a tall
image. And do **not** put `display: flex` on the dialog — that overrides the UA's
`dialog:not([open]) { display: none }` and the dialog renders permanently (the
same trap as §17).

### Checking centring: use the layout width, not `innerWidth`

`window.innerWidth` includes the scrollbar. Comparing a dialog's centre against
it reports a false 7–8px offset. `document.documentElement.clientWidth` is the
number the layout actually centres within.

### `naturalWidth` is not the file's size

A hidden/undecoded image reports a stale `naturalWidth` (170 for a file Shopify
describes as 1600x1833). The `width`/`height` **attributes** that `image_tag`
emits come from Shopify's image object and are the reliable source size — check
those before concluding an asset is too small.
