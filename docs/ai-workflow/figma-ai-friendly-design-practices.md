# Designing Figma Files That Build Themselves

**Who this is for:** designers handing work to our development team.

**Why you're reading it:** we now build a lot of our storefronts by pointing an
AI tool at a Figma frame and having it write the code. When a file is structured
well, that works remarkably closely to first time. When it isn't, we spend the
day guessing at your intent and coming back with questions — and you spend the
day answering them.

**What's in it for you:** fewer revision rounds, and a build that matches what
you drew rather than someone's approximation of it. Every item below is here
because its absence cost us real time on a real project, not because it's tidy.

**This is a request, not a rulebook.** Some of it may not fit how you work. If
something here is impractical, tell us and we'll adapt — the point is a shared
understanding, not compliance.

Sixteen items is more than anyone adopts at once. There's a four-item short
version at the end if you'd rather start there — those four carry most of the
benefit.

---

## First, how the tool actually reads your file

Worth knowing, because it explains everything that follows.

It does **not** look at a picture of your design and interpret it. It reads the
file's *structure* — the same layer tree you see in the left panel. Frame names,
layer names, auto-layout settings, spacing values, colour styles, text styles,
component definitions. It reads those as data and turns them into code.

Two consequences:

- **Anything you communicated visually but not structurally is invisible to it.**
  Two elements that look aligned but aren't actually in an auto-layout row read
  as two unrelated boxes at arbitrary coordinates.
- **Names are content, not labels.** A layer called `Rectangle 47` tells it
  nothing. One called `product-card/image` tells it a great deal — see practice
  4, which is the cheapest item on this list and one of the most valuable.
- **Hidden layers are not hidden to it.** It reads the tree, so an old version
  left switched off is as visible as the current one.

The single most useful mental model: **you are not drawing a picture, you are
describing a structure that happens to be visible.**

---

## The practices

### 1. One canonical file. Kill the old ones.

**Do:** keep exactly one live file per project. When you supersede a file,
delete it or clearly mark it `ARCHIVE — do not use`.

**Why:** we work from links, and links outlive the files they point at.

**What happened without it:** on one project, two files existed — an old one and
the current one. The old link ended up in ten places across our own
documentation against three for the correct one, and our tooling couldn't even
open the old file. Work stopped while we established which was real. Nothing was
wrong with either design; we simply couldn't tell which was the design.

### 2. Give us a direct link to the frame, not the file

**Do:** right-click the frame → **Copy link to selection**. Send that.

**Why:** a link to the whole file gives us a file. A link to a frame tells us
which frame — the link carries the frame's ID.

**What happened without it:** our tooling's own "list the pages in this file"
feature is unreliable on large files — on one of ours it reports a single
"Cover" page and nothing else, even though frames on other pages open perfectly
when linked directly. So we genuinely cannot browse to your frame. A whole
review stalled with nothing to do but ask for a link. Frame links cost you three
seconds and remove the entire failure mode.

### 3. One frame per breakpoint, named so we can tell them apart

**Do:** a separate top-level frame for each breakpoint you've designed, at the
real pixel width, with the width in the name:

```
PDP / Desktop 1440
PDP / Mobile 393
```

**Why:** we check the built page against your frame at *exactly* the width the
frame was designed at. A 1440 frame gets checked at 1440. If we don't know the
intended width, we can't verify anything — and "looks about right on my screen"
is how mismatches ship.

**Agree the widths with us before you start.** Our themes already have
breakpoints in their CSS — the common ones are 750px and 990px. If you design at
1512 and 375 we can still build it, but we're translating, and translation is
where small mismatches enter. Designing at widths that line up with ours, or
telling us early that yours are different, removes that.

**Also:** if a breakpoint doesn't exist as a frame, we're inventing it. That's
usually fine for a simple stack, and usually wrong for anything with a layout
change. If mobile does something structurally different — a grid becoming a
carousel, a sidebar becoming a drawer — it needs its own frame.

### 4. Name layers and frames for what they are

**Do:** name things after their role. `product-card`, `product-card/image`,
`hero/heading`, `filter-chip/active`. Group related layers under a parent whose
name says what the group is.

**Don't:** ship `Rectangle 47`, `Group 12`, `Frame 1129`, or `image 3 copy 2`.

**Why:** layer names are the closest thing we get to your intent. They become
class names, component names and section names in the code, so a good name
propagates all the way through to the file we create and the CSS we write. A
name like `Rectangle 47` tells us a box exists and nothing else — we then guess
what it is, and a guess is a question sent back to you.

There is a second-order effect worth knowing about. **We tend to name code after
whatever the design called it.** On the Bites Vitamins build, the Figma file was
organised by page, so sections ended up named `home-hero`, `about-values`,
`focus-causes` — named for the page they first appeared on rather than what they
do. That naming stopped being accurate the first time a section was reused, and
it came directly from how the file was structured. Name a component for what it
*is* and that name survives being used somewhere else.

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

**Why:** a frame carries layout, clipping and sizing behaviour. A group is just
a selection of layers that happen to be together. To us, a frame reads as *"this
is a container with rules"* and a group reads as *"these things are near each
other."* Only one of those turns into markup we can trust.

Auto layout is only available on frames, which is the practical tell: if you
find you can't add auto layout to something, it's a group and probably shouldn't
be.

### 6. Auto layout everywhere it could apply

**Do:** use auto layout for anything that's a row, column, stack, or grid. Set
real gap and padding values.

**Why:** auto layout is how you tell us *"these things relate, and this is the
space between them."* Absolutely-positioned layers only tell us where things
happened to land, and we cannot tell an intentional 24px gap from a 23px
accident.

This is the highest-leverage item on the list. Auto layout converts almost
directly into the code we write; absolute positioning converts into guesswork
plus a question for you.

**Set the sizing deliberately too** — `Fill`, `Hug`, or a fixed value on each
element. This is how you tell us what happens at a width you did not draw:

| Sizing | What we build |
|---|---|
| **Fill** | Stretches with its container — flexible width |
| **Hug** | Shrinks to fit its content |
| **Fixed** | A hard width or height we should not change |

Left at the default, everything looks intentional at your artboard width and we
have no idea which of the three you meant. This is the single biggest source of
"it's fine on desktop but wrong on a laptop."

**Stick to a spacing scale.** Multiples of 4 or 8 are ideal. When gaps are 23,
24 and 25px across a design we cannot tell a deliberate value from a nudge, and
we end up either copying the accident or asking you about every one.

### 7. Components for anything appearing more than once

**Do:** make it a component, use instances, and use variants for its states —
default, hover, selected, disabled, empty.

**Why:** three copies of a card tell us there are three cards. One component
with three instances tells us there is *one card, used three times* — which is
exactly how we build it. It also means we get the states, which are otherwise
invisible: we cannot see a hover state that only exists in your head.

**Don't detach instances.** A detached instance looks exactly like a component
and isn't one — the link to the master is gone. We read it as a one-off and
rebuild it as a one-off, so the shared component you carefully made doesn't get
used. If an instance needs to differ, use a variant or a component property
rather than detaching it.

**Icons especially.** Make each icon a component with a real name — `icon/cart`,
`icon/chevron-right`. Our themes already ship a set of icon files, so a named
icon lets us reuse the one we have instead of exporting a near-duplicate. An
unnamed icon flattened into a shape gets re-exported every time it appears.

### 8. Named styles and variables, not raw values

**Do:** define **variables** where you can — `color/brand/mint`,
`space/gutter` — and text styles for type. Apply them rather than typing values.
Variables are better than styles for us because they carry a name *and* can hold
different values per mode.

**Why:** our themes are built on named design tokens. A named style maps
straight onto ours. A raw hex means we guess whether `#1F6F6B` is the brand
green, a one-off, or a slightly-off paste.

**What happened without it:** we reverse-engineered a type system by measuring
headings across frames and inferring a scale from 35px on mobile to 45px on
desktop. That was an afternoon of measurement to recover information the file
could have simply stated.

**Set line height as a number, not `Auto`.** Figma's `Auto` line height resolves
differently per font and doesn't correspond to any CSS value, so we have to pick
one and you may not agree with the pick. A stated `140%` or `24px` removes the
guess. Same for letter spacing — if it matters, state it.

If your file uses light and dark modes, or per-brand colour sets, variables with
modes map almost directly onto how our themes handle colour schemes. Worth
mentioning up front if you have them.

### 9. Tell us the container width and the gutters

**Do:** set a layout grid on your frames, and state the maximum content width
and the side margins at each breakpoint.

**Why:** every page we build sits inside a container with a maximum width and a
side gutter, and those two numbers are the backbone of the layout. If we have to
infer them by measuring where content happens to stop, we get them slightly
wrong in a way that shows up on every single section.

Concretely, we want: *content maxes out at 1280px, 60px side margins on desktop,
16px on mobile.* Three numbers, and the whole page frame is settled.

**What happened without it:** on Bites Vitamins the side gutters were
inconsistent across sections because each was measured independently from its own
frame. It eventually needed a dedicated pass to unify them into a single value
the whole theme reads from.

### 10. Keep text as real text

**Do:** leave copy as editable text layers.

**Don't:** outline text, flatten it into a shape, or paste it as an image.

**Why:** an outlined heading is a vector drawing to us. We cannot read the words,
the font, the size, the weight, the line height or the letter spacing — all of
which we need, and all of which are simply gone. It looks identical to you and
carries none of the information.

If a font renders wrong for you in Figma, that is worth telling us rather than
outlining around it — see the font item below.

### 11. Real images, not screenshots of an interface

**Do:** place images as actual image fills, at roughly 2× the size they display
at.

**Don't:** paste a screenshot of a UI in place of designing it, and don't use a
grey placeholder rectangle where a real image belongs.

**Why:** we export assets straight from the frame. A screenshot of an interface
gives us a picture where structure should be — nothing in it can be extracted,
so the whole region has to be rebuilt from guesswork. An undersized image looks
fine on your screen and blurry on a retina display.

A grey rectangle is fine as long as it is *labelled* as a placeholder, so we know
to leave the space rather than shipping a grey box.

**Mark what should be exported, and as what.** Icons and logos as SVG, photos as
PNG or WebP. Setting Figma's export options on those layers tells us exactly
which pieces are assets rather than us deciding, and SVG-vs-raster is a decision
you'll make better than we will.

### 12. Delete hidden layers and old versions

**Do:** clear out hidden layers, superseded variants and abandoned explorations
before handover.

**Why:** we read the layer tree, not the rendered picture, so hidden layers are
just as visible to us as the ones you can see. A hidden earlier version of a
section is indistinguishable from a deliberate one, and it can end up in the
build. If something must stay in the file for reference, put it well outside the
handover frame.

### 13. Real content, and mark anything that isn't

**Do:** use plausible real content. Where a value will come from live data —
prices, review counts, stock — say so, in a comment on the frame.

**Why:** this one is genuinely dangerous. A design showing *"4.9 (127 reviews)"*
is a picture of a number. We have a hard rule that such values come from the
live store and never from a design, but the rule only helps when we can tell
which values are which. Lorem, on the other hand, gives us nothing to check the
build against — and a heading sized for `Lorem ipsum dolor` frequently breaks on
the real sentence.

**Show us the long case.** For anything holding variable-length content —
product titles, headings, review quotes — include one instance with realistically
long text, or say what the maximum is. A card that fits a three-word title and
breaks on a twelve-word one is the most common visual bug we ship, and the frame
gave us no way to see it coming.

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
moments is invisible in it, and behaviour is most of the work.

**A prototype counts.** If you have already wired interactions in Figma's
prototype mode, that is behaviour documentation and we can read it — say so and
we will. It is often less work than writing the comments, and it captures
transitions a comment would struggle to describe.

**What happened without it:** a filter bar was designed as a row of dropdown
chips. Structurally that implies opening one should close any other — otherwise
adjacent panels visually collide. But no frame or note in the file said so. We
couldn't safely infer it, shipped the simpler behaviour, and logged an open
question that needed the designer's answer days later. **One comment would have
resolved it in the original session.** This is the single cheapest thing on this
list and the one that saves the most back-and-forth.

### 15. Web-ready licensed fonts, at handoff

**Do:** send the licensed **web** font files — `.woff2` — along with the design.

**Why:** a font that works in Figma may not be licensed for a website, and
desktop formats often aren't web formats.

**What happened without it:** a handoff included trial desktop `.otf` files.
Not web-ready, not licensed for production. The site rendered in a fallback
font, which reads as a bug to everyone who sees it, and the real files had to be
sourced separately while the build waited.

### 16. Don't hand over empty frames

**Do:** if a page isn't designed yet, leave it off the list rather than shipping
a named empty frame.

**Why:** an empty frame named `Header / Mega Menu` is ambiguous in the worst
way — we can't tell "not designed yet" from "deliberately minimal" from "this is
a mistake." That exact frame stalled a piece of work while we asked.

---

## What we can't get from a design, however good it is

So expectations are shared:

- **Behaviour**, unless you annotate it — see practice 14.
- **Real data.** Prices, inventory, reviews and product copy come from the
  store. Your numbers are placeholders by definition, which is why practice 13
  matters.
- **Merchant controls.** Our storefronts let the shop owner adjust spacing,
  colour schemes and content per section. A frame shows one spacing value
  because a frame can only show one — we add the control regardless. If a
  section's background is *deliberately* fixed and must never change, that's
  worth a note.
- **What happens between your breakpoints.** You give us 1440 and 393; real
  browsers are also 1280 and 834. We make sensible choices there, and if a
  specific in-between width matters, it needs its own frame.
- **Whether your colours pass contrast.** We check accessibility on the built
  page and will raise it, but by then the palette is decided and changing it is
  a design conversation. Checking contrast on text and interactive elements while
  designing is much cheaper than after we've built it.
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

Numbers 1 and 2 cost you nothing extra if you do them as you design, and they
are the two that most change the quality of what we build.

---

## Honest note on status

This document is aspirational. It describes the conditions under which our AI
build workflow works close to first-time rather than after several rounds of
correction — and we're aware that's us asking you to change how you work to
suit our tooling.

It's written down so the request is explicit and reviewable rather than arriving
as a stream of one-off questions. If a practice here doesn't survive contact
with how you actually design, say so and we'll drop it.

Related, for the development side: [`README.md`](./README.md) — the build
workflow this feeds into.
