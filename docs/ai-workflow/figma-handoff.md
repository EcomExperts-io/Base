# Figma handoff

For designers handing work to the development team. We build by pointing an
AI tool at your frame; it reads the file's **structure** — layer names, auto
layout, variables, components — not the picture. Anything communicated
visually but not structurally is invisible to it; a hidden layer is as
visible as a shown one.

## The four that matter most

| Do this | What we check, automatically, before we build |
|---|---|
| **Auto layout** on every row, column, card and section, with `Fill` / `Hug` / fixed set deliberately | Whether elements are laid out or merely placed; absolutely positioned boxes read as unrelated |
| **Name layers for what they are** — `product-card/image`, not `Rectangle 47` | The share of layers carrying a default name; over 20% and the frame comes back |
| **One frame per breakpoint, width in the name** — `PDP / Desktop 1440`, `PDP / Mobile 393` | That the name carries the width, and a sibling frame exists for the other breakpoint |
| **A comment for anything that happens rather than looks** — open by default, hover, empty states, whether one accordion closes the others | Text or comments beside the frame; an interactive component without any gets a question, not a build |

## What we send back

Our readiness check on a frame produces:

```
Figma readiness — Default header (329:26263, 1440×110)
  20 layers, depth 5.  Overall: SEND BACK

  send back layer naming        60.0% of layers carry a default name   (practice 4)
  warn      hidden layers       3 hidden                               (practice 12)
  ask       frame width in name "Default header" (frame is 1440px wide) (practice 3)
  pass      components used     3 instance(s) of components            (practice 7)

  Largest default-named layers — the ones to rename first:
    638:21435      Frame 1261153641   241×48
```

Green means we build; anything else means one round of renaming and a
comment or two. The practice numbers refer to the list below.

## The sixteen practices

1. **One canonical file.** Delete or mark `ARCHIVE` a superseded file; two live
   files stop work until someone says which is the design.
2. **Link to the frame, not the file.** Right-click → Copy link to selection.
   The tool cannot reliably list a large file's pages.
3. **One frame per breakpoint, named with its width.** We verify the build at
   exactly that width. Agree the widths with us first (our breakpoints are
   usually 750 and 990). A breakpoint with no frame is one we invent; fine for
   a simple stack, wrong for a layout change.
4. **Name layers and frames for their role.** `ingredient-card/photo`, not
   `image 3 copy 2`. Names become class and section names. Name a component
   for what it is, not the page it first appears on.
5. **Frames, not groups,** for anything that is a container. A frame carries
   layout and sizing; a group is layers that happen to be near each other.
6. **Auto layout everywhere it applies,** with real gap and padding, sizing
   set to `Fill`, `Hug` or fixed on each element (that is how we know what
   happens at a width you did not draw), and a 4 or 8 px spacing scale.
7. **Components for anything appearing more than once,** with variants for
   states (default, hover, selected, disabled, empty). Do not detach
   instances. Make each icon a named component (`icon/cart`) so we reuse the
   icon file we already have.
8. **Variables and text styles, not raw values.** A named variable maps onto
   our tokens; a raw hex is a guess. Set line height and letter spacing as
   numbers, not `Auto`. Modes map onto our colour schemes.
9. **State the container width and gutters** at each breakpoint — "content
   maxes out at 1280, 60 px side margins on desktop, 16 on mobile."
10. **Keep text as text.** An outlined heading is a vector; its font, size and
    spacing are gone.
11. **Real images as image fills,** at about 2× display size, exports marked
    (SVG for icons and logos, PNG or WebP for photos). A grey placeholder is
    fine if it is labelled as one. Never a screenshot of an interface.
12. **Delete hidden layers and old versions.** We read the layer tree, so a
    hidden earlier version can end up in the build.
13. **Real content, and mark what is not.** Say in a comment which values come
    from the store (prices, review counts, stock); they never come from the
    design. Include one realistically long instance of any variable-length
    text.
14. **Annotate behaviour the design cannot show** — this is the big one. What
    is open or selected by default; click, hover and focus; whether one
    accordion closes the others; empty states; conditional visibility;
    scroll and animation. A wired prototype counts; say so.
15. **Licensed web fonts** (`.woff2`) with the design. Desktop and trial
    formats are not web fonts, and a fallback face reads as a bug.
16. **No empty frames.** An empty `Header / Mega Menu` cannot be told from
    "not designed yet" or "deliberately minimal"; leave it off the list.

## What no frame can tell us

Behaviour, unless annotated. Real data — prices, inventory, reviews, copy
come from the store. Merchant controls — every section gets spacing and
colour settings regardless of the frame; if a background is deliberately
fixed, say so. What happens between your breakpoints; a width that matters
needs its own frame. Whether your colours pass contrast. We ask rather than invent.

The development side of this is [`README.md`](./README.md).
