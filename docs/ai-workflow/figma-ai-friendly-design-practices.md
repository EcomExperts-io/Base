# Designing Figma Files That Build Themselves

**Who this is for:** designers handing work to our development team.

**Why:** we build storefronts by pointing an AI tool at a Figma frame and
having it write the code. A well-structured file builds close to first time; a
loosely structured one costs a round of questions in both directions.

**This is a request, not a rulebook.** If something here is impractical for
how you work, tell us and we'll adapt. There's a four-item short version at
the end; those four carry most of the benefit.

---

## How the tool reads your file

It does **not** look at a picture of your design and interpret it. It reads the
file's *structure* — the same layer tree you see in the left panel: frame names,
layer names, auto-layout settings, spacing values, colour styles, text styles,
component definitions. It reads those as data and turns them into code.

- **Anything you communicated visually but not structurally is invisible to it.**
  Two elements that look aligned but aren't in an auto-layout row read as two
  unrelated boxes at arbitrary coordinates.
- **Names are content, not labels.** `Rectangle 47` tells it nothing;
  `product-card/image` tells it a great deal — see practice 4.
- **Hidden layers are not hidden to it.** An old version left switched off is
  as visible as the current one.

**You are not drawing a picture; you are describing a structure that happens
to be visible.**

---

## The practices

### 1. One canonical file. Kill the old ones.

**Do:** keep exactly one live file per project. When you supersede a file,
delete it or clearly mark it `ARCHIVE — do not use`.

**Why:** we work from links, and links outlive the files they point at. Two
live files means work stops until someone establishes which is the design.

### 2. Give us a direct link to the frame, not the file

**Do:** right-click the frame → **Copy link to selection**. Send that.

**Why:** a link to the whole file gives us a file; a link to a frame carries
the frame's ID. Our tooling cannot reliably list the pages of a large file, so
we cannot browse to your frame — a frame link costs three seconds and removes
that failure.

### 3. One frame per breakpoint, named so we can tell them apart

**Do:** a separate top-level frame for each breakpoint you've designed, at the
real pixel width, with the width in the name:

```
PDP / Desktop 1440
PDP / Mobile 393
```

**Why:** we check the built page against your frame at *exactly* the width the
frame was designed at. If we don't know the intended width, we can't verify
anything.

**Agree the widths with us before you start.** Our themes already have
breakpoints in their CSS — the common ones are 750px and 990px. If you design at
1512 and 375 we can still build it, but we're translating, and translation is
where small mismatches enter.

**Also:** if a breakpoint doesn't exist as a frame, we're inventing it. That's
usually fine for a simple stack and usually wrong for a layout change. If
mobile does something structurally different — a grid becoming a carousel, a
sidebar becoming a drawer — it needs its own frame.

### 4. Name layers and frames for what they are

**Do:** name things after their role. `product-card`, `product-card/image`,
`hero/heading`, `filter-chip/active`. Group related layers under a parent whose
name says what the group is.

**Don't:** ship `Rectangle 47`, `Group 12`, `Frame 1129`, or `image 3 copy 2`.

**Why:** layer names become class names, component names and section names in
the code. `Rectangle 47` tells us a box exists and nothing else — we guess what
it is, and a guess is a question sent back to you.

**Name a component for what it *is*, not the page it first appears on.** We
name code after the design, and a page-based name (`home-hero`,
`about-values`) stops being accurate the first time the component is reused.

Rough guide:

| Instead of | Use |
|---|---|
| `Group 8` | `ingredient-list` |
| `Rectangle 3` | `ingredient-card/background` |
| `Frame 1129` | `PDP / Desktop 1440` |
| `image 3 copy 2` | `ingredient-card/photo` |

### 5. Frames, not groups

**Do:** use a frame when something is a container — a card, a row, a section, a
page.

**Why:** a frame carries layout, clipping and sizing behaviour; a group is a
selection of layers that happen to be together. A frame reads as *"a container
with rules"*, a group as *"things near each other"*. Only one turns into markup
we can trust.

Auto layout is only available on frames, which is the practical tell: if you
can't add auto layout to something, it's a group and probably shouldn't be.

### 6. Auto layout everywhere it could apply

**Do:** use auto layout for anything that's a row, column, stack, or grid. Set
real gap and padding values.

**Why:** auto layout is how you tell us *"these things relate, and this is the
space between them."* Absolutely-positioned layers only tell us where things
happened to land, and we cannot tell an intentional 24px gap from a 23px
accident. This is the highest-leverage item on the list.

**Set the sizing deliberately too** — `Fill`, `Hug`, or a fixed value on each
element. This is how you tell us what happens at a width you did not draw:

| Sizing | What we build |
|---|---|
| **Fill** | Stretches with its container — flexible width |
| **Hug** | Shrinks to fit its content |
| **Fixed** | A hard width or height we should not change |

Left at the default, everything looks intentional at your artboard width and we
have no idea which of the three you meant — the biggest source of "fine on
desktop, wrong on a laptop".

**Stick to a spacing scale.** Multiples of 4 or 8 are ideal. When gaps are 23,
24 and 25px across a design we cannot tell a deliberate value from a nudge.

### 7. Components for anything appearing more than once

**Do:** make it a component, use instances, and use variants for its states —
default, hover, selected, disabled, empty.

**Why:** three copies of a card tell us there are three cards. One component
with three instances tells us there is *one card, used three times* — which is
how we build it. It also gives us the states, which are otherwise invisible.

**Don't detach instances.** A detached instance looks like a component and
isn't one — we read it as a one-off and rebuild it as a one-off. If an instance
needs to differ, use a variant or a component property.

**Icons especially.** Make each icon a component with a real name — `icon/cart`,
`icon/chevron-right`. Our themes already ship a set of icon files, so a named
icon lets us reuse the one we have. An unnamed icon flattened into a shape gets
re-exported every time it appears.

### 8. Named styles and variables, not raw values

**Do:** define **variables** where you can — `color/brand/mint`,
`space/gutter` — and text styles for type. Apply them rather than typing values.
Variables are better than styles for us because they carry a name *and* can hold
different values per mode.

**Why:** our themes are built on named design tokens. A named style maps
straight onto ours. A raw hex means we guess whether `#1F6F6B` is the brand
green, a one-off, or a slightly-off paste; an unstated type scale means we
measure headings across frames to recover what the file could have stated.

**Set line height as a number, not `Auto`.** Figma's `Auto` line height resolves
differently per font and doesn't correspond to any CSS value, so we have to pick
one. A stated `140%` or `24px` removes the guess. Same for letter spacing.

If your file uses light and dark modes, or per-brand colour sets, variables with
modes map almost directly onto how our themes handle colour schemes. Worth
mentioning up front.

### 9. Tell us the container width and the gutters

**Do:** set a layout grid on your frames, and state the maximum content width
and the side margins at each breakpoint.

**Why:** every page we build sits inside a container with a maximum width and a
side gutter, and those two numbers are the backbone of the layout. Inferred by
measuring where content happens to stop, they come out slightly wrong on every
section.

Concretely, we want: *content maxes out at 1280px, 60px side margins on desktop,
16px on mobile.* Three numbers, and the whole page frame is settled.

### 10. Keep text as real text

**Do:** leave copy as editable text layers.

**Don't:** outline text, flatten it into a shape, or paste it as an image.

**Why:** an outlined heading is a vector drawing to us. The words, font, size,
weight, line height and letter spacing are gone. If a font renders wrong for
you in Figma, tell us rather than outlining around it — see practice 15.

### 11. Real images, not screenshots of an interface

**Do:** place images as actual image fills, at roughly 2× the size they display
at.

**Don't:** paste a screenshot of a UI in place of designing it, and don't use a
grey placeholder rectangle where a real image belongs.

**Why:** we export assets straight from the frame. A screenshot of an interface
gives us a picture where structure should be, so the whole region has to be
rebuilt from guesswork. An undersized image looks fine on your screen and
blurry on a retina display.

A grey rectangle is fine as long as it is *labelled* as a placeholder, so we know
to leave the space rather than shipping a grey box.

**Mark what should be exported, and as what.** Icons and logos as SVG, photos as
PNG or WebP. Setting Figma's export options on those layers tells us exactly
which pieces are assets, and SVG-vs-raster is a decision you'll make better
than we will.

### 12. Delete hidden layers and old versions

**Do:** clear out hidden layers, superseded variants and abandoned explorations
before handover.

**Why:** we read the layer tree, not the rendered picture, so hidden layers are
as visible to us as the ones you can see. A hidden earlier version of a section
is indistinguishable from a deliberate one, and it can end up in the build. If
something must stay in the file for reference, put it well outside the handover
frame.

### 13. Real content, and mark anything that isn't

**Do:** use plausible real content. Where a value will come from live data —
prices, review counts, stock — say so, in a comment on the frame.

**Why:** a design showing *"4.9 (127 reviews)"* is a picture of a number. We
have a hard rule that such values come from the live store and never from a
design, but the rule only helps when we can tell which values are which.
Lorem gives us nothing to check the build against, and a heading sized for
`Lorem ipsum dolor` frequently breaks on the real sentence.

**Show us the long case.** For anything holding variable-length content —
product titles, headings, review quotes — include one instance with realistically
long text, or say what the maximum is. A card that fits a three-word title and
breaks on a twelve-word one is the most common visual bug we ship.

### 14. Annotate behaviour the design can't show — this is the big one

**Do:** leave a Figma comment, or a text layer beside the frame, for anything
that *happens* rather than *looks*:

- What's selected or open by default
- What happens on click, hover, focus
- Whether opening one accordion closes the others
- What shows when there's no data — no reviews, no products, empty search
- What's hidden or shown conditionally
- Scroll, snap, or animation behaviour

**Why:** a frame is one moment. Everything about how a page *behaves* between
moments is invisible in it, and behaviour is most of the work. A row of
dropdown chips implies that opening one closes the others — but without a note
we cannot safely infer it, and we ship the simpler behaviour. One comment is
the cheapest thing on this list and the one that saves the most back-and-forth.

**A prototype counts.** If you have already wired interactions in Figma's
prototype mode, that is behaviour documentation and we can read it — say so.
It captures transitions a comment would struggle to describe.

### 15. Web-ready licensed fonts, at handoff

**Do:** send the licensed **web** font files — `.woff2` — along with the design.

**Why:** a font that works in Figma may not be licensed for a website, and
desktop formats (`.otf`, trial files) are not web formats. Without the real
files the site renders in a fallback font, which reads as a bug to everyone
who sees it.

### 16. Don't hand over empty frames

**Do:** if a page isn't designed yet, leave it off the list rather than shipping
a named empty frame.

**Why:** an empty frame named `Header / Mega Menu` is ambiguous in the worst
way — we can't tell "not designed yet" from "deliberately minimal" from "this is
a mistake", and work stops while we ask.

---

## What we can't get from a design, however good it is

- **Behaviour**, unless you annotate it — see practice 14.
- **Real data.** Prices, inventory, reviews and product copy come from the
  store. Your numbers are placeholders by definition — practice 13.
- **Merchant controls.** Our storefronts let the shop owner adjust spacing,
  colour schemes and content per section. A frame shows one spacing value
  because a frame can only show one — we add the control regardless. If a
  section's background is *deliberately* fixed and must never change, that's
  worth a note.
- **What happens between your breakpoints.** You give us 1440 and 393; real
  browsers are also 1280 and 834. We make sensible choices there, and if a
  specific in-between width matters, it needs its own frame.
- **Whether your colours pass contrast.** We check accessibility on the built
  page and will raise it, but by then the palette is decided. Checking contrast
  on text and interactive elements while designing is much cheaper.
- **Anything at all about a page you didn't design.** We will ask rather than
  invent.

---

## The short version

If you do only four things:

1. **Auto layout** instead of absolute positioning, with `Fill` / `Hug` / fixed
   set deliberately.
2. **Meaningful layer names** — `ingredient-card`, not `Group 8`.
3. **A direct frame link** per breakpoint, with the width in the name.
4. **A comment describing behaviour** the frame can't show.

Those four remove most of the questions we'd otherwise send back to you.
Numbers 1 and 2 cost you nothing extra if you do them as you design.

Related, for the development side: [`README.md`](./README.md) — the build
workflow this feeds into.
