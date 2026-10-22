# Layout pitfalls — declarations that report correct and render wrong

Six traps measured on a client rebuild (Sep–Oct 2026). In each of them
`getComputedStyle` returned the value the author wrote, the DOM reported the
state the author intended, and the page was wrong. None is visible in source
and none is caught by a grep: a pixel diff or a box measurement found every
one. The short form is in `css-standards.md`, "Defensive CSS". This is the
long form, for when the symptom comes back.

Two already in the rules belong to the same family: a custom element's default
`display: inline` (`rules-of-engagement.md`) and `.page-width` shrink-wrapping
inside a flex section (`sections.md`). The habit that finds all of them is the
same — measure the box, do not read the style.

## 1. A flex child of a scrolling panel shrinks instead of letting it scroll

**Symptom.** A drawer is a flex column: header, scrolling body, footer. The
header, declared `block-size: 56px`, measured 51.8px at 393; a gift banner
sized by `aspect-ratio: 423 / 90` measured 84px on desktop and 33px at 393.
Everything below the header sat 4.2px low.

**Cause.** Flex resolves shrinking *before* overflow. When the line is
over-constrained every item with the default `flex-shrink: 1` gives up space,
and only what is left overflows — `overflow-y: auto` on the body does not
protect the siblings. A box with no content (an `aspect-ratio` banner) has
nothing to resist with and shrinks first. It only appears at the height where
the design intends the panel to scroll, which is the state the design is about.

**Fix.** `flex: 0 0 auto` on the header, the footer, and every direct child of
the scrolling body, so the body is the only thing that can give.

**Found by** the box table: `Drawer Header frame y0 h56 | mine y0 h51.8`.

## 2. A flex item's automatic minimum size beats `aspect-ratio`

**Symptom.** A media box drawn 393×215 with `aspect-ratio` rendered 294.75px
tall — the height of the photograph the merchant had uploaded.

**Cause.** A flex item's automatic minimum is `min-height: auto`, which
resolves to the content's size and wins over `aspect-ratio`. The override is
merchant data, so the same code measures right against one upload and wrong
against another, and it only bites where the drawn box is shorter than the
image's natural height at that width — the mobile crop, every time. Desktop
looked right.

**Fix.** `min-block-size: 0` beside the `aspect-ratio` (`min-inline-size: 0`
for a row).

## 3. A child's margin collapses out through the section

**Symptom.** An empty-cart block with `margin-block: 90px` landed where the
design wanted it, but the *section* box measured 90px shorter and started 90px
lower than its frame. Every screenshot looked right.

**Cause.** The section's block padding is a merchant range that starts at 0,
and with no padding, border or formatting context between them the child's
margin collapses through the custom element, through `.page-width` and out of
the wrapper. Collapse is correct CSS; the page even looks right in one column.
Only the section's own box is wrong, which is what the fidelity crop is taken
from.

**Fix.** `padding-block` on the child instead of `margin-block`. `display:
flow-root` on the wrapper also works; padding is the smaller change.

## 4. `[hidden]` does nothing once the component sets its own `display`

**Symptom.** Six upsell cards rendered where one should; `card.hidden` was
`true` on five.

**Cause.** `.cart-drawer__upsell-card { display: flex }` is an author rule and
outranks the UA sheet's `[hidden] { display: none }` at any specificity. The
attribute is set, the DOM reports it, and it has no effect.

**Fix.** `.cart-drawer__upsell-card[hidden] { display: none; }` next to the
component's own `display`.

## 5. A font weight the library never loaded, and the probe that lies about it

**Symptom.** A link set in `font-weight: 600` on the accent family rendered
lighter and narrower than the frame; `getComputedStyle` said `600`.

**Cause.** `snippets/css-variables.liquid` loaded the family's regular and
italic faces and no bold, so the browser synthesised one. `font_modify:
'weight', '600'` emits nothing when the library has no such face, silently.
`document.fonts.check('600 16px "Family"')` returns `true` for every weight —
it answers whether the family can render the text, not whether the face is
loaded.

**Fix.** Load the face: `{{ settings.type_accent_font | font_modify: 'weight',
'bold' | font_face: font_display: 'swap' }}`. Prove it with
`[...document.fonts].filter(f => f.family === 'Family').map(f => f.weight + ' '
+ f.status)`. If the library has no 600, the design's semibold renders at 700
and the residual is a library limit — write that beside the `font_face` calls.

**Found by** a hot band in the heatmap sitting on one line of text.

## 6. A span in a second font grows the line

**Symptom.** A five-line heading at `line-height: 32.5px` measured 168.5px,
not 162.5; a byline at 14/20 measured 21. Every span reported the inherited
line height.

**Cause.** An `<em>` in a second family inherits the line height, but its
inline box is placed by that family's own ascent and descent, which poke out of
the strut by a couple of pixels per line that holds one.

**Fix.** `line-height: 0` on the span, the same treatment normalize.css gives
`sub` and `sup`. `line-height: 1` measured right in one browser and still grew
the line in desktop Chrome; `0` measured right in both.

**Found by** the box table, twice on two pages of one build.
