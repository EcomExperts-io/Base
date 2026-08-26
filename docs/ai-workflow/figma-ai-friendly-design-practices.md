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
  nothing. One called `product-card/image` tells it a great deal.

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

**Also:** if a breakpoint doesn't exist as a frame, we're inventing it. That's
usually fine for a simple stack, and usually wrong for anything with a layout
change. If mobile does something structurally different — a grid becoming a
carousel, a sidebar becoming a drawer — it needs its own frame.

### 4. Auto layout everywhere it could apply

**Do:** use auto layout for anything that's a row, column, stack, or grid. Set
real gap and padding values.

**Why:** auto layout is how you tell us *"these things relate, and this is the
space between them."* Absolutely-positioned layers only tell us where things
happened to land, and we cannot tell an intentional 24px gap from a 23px
accident.

This is the highest-leverage item on the list. Auto layout converts almost
directly into the code we write; absolute positioning converts into guesswork
plus a question for you.

### 5. Components for anything appearing more than once

**Do:** make it a component, use instances, and use variants for its states —
default, hover, selected, disabled, empty.

**Why:** three copies of a card tell us there are three cards. One component
with three instances tells us there is *one card, used three times* — which is
exactly how we build it. It also means we get the states, which are otherwise
invisible: we cannot see a hover state that only exists in your head.

### 6. Named colour and text styles, not raw values

**Do:** define styles or variables — `Brand/Mint`, `Heading/H2` — and apply them.

**Why:** our themes are built on named design tokens. A named style maps
straight onto ours. A raw hex means we guess whether `#1F6F6B` is the brand
green, a one-off, or a slightly-off paste.

**What happened without it:** we reverse-engineered a type system by measuring
headings across frames and inferring a scale from 35px on mobile to 45px on
desktop. That was an afternoon of measurement to recover information the file
could have simply stated.

### 7. Real content, and mark anything that isn't

**Do:** use plausible real content. Where a value will come from live data —
prices, review counts, stock — say so, in a comment on the frame.

**Why:** this one is genuinely dangerous. A design showing *"4.9 (127 reviews)"*
is a picture of a number. We have a hard rule that such values come from the
live store and never from a design, but the rule only helps when we can tell
which values are which. Lorem, on the other hand, gives us nothing to check the
build against — and a heading sized for `Lorem ipsum dolor` frequently breaks on
the real sentence.

### 8. Annotate behaviour the design can't show — this is the big one

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

**What happened without it:** a filter bar was designed as a row of dropdown
chips. Structurally that implies opening one should close any other — otherwise
adjacent panels visually collide. But no frame or note in the file said so. We
couldn't safely infer it, shipped the simpler behaviour, and logged an open
question that needed the designer's answer days later. **One comment would have
resolved it in the original session.** This is the single cheapest thing on this
list and the one that saves the most back-and-forth.

### 9. Web-ready licensed fonts, at handoff

**Do:** send the licensed **web** font files — `.woff2` — along with the design.

**Why:** a font that works in Figma may not be licensed for a website, and
desktop formats often aren't web formats.

**What happened without it:** a handoff included trial desktop `.otf` files.
Not web-ready, not licensed for production. The site rendered in a fallback
font, which reads as a bug to everyone who sees it, and the real files had to be
sourced separately while the build waited.

### 10. Don't hand over empty frames

**Do:** if a page isn't designed yet, leave it off the list rather than shipping
a named empty frame.

**Why:** an empty frame named `Header / Mega Menu` is ambiguous in the worst
way — we can't tell "not designed yet" from "deliberately minimal" from "this is
a mistake." That exact frame stalled a piece of work while we asked.

---

## What we can't get from a design, however good it is

So expectations are shared:

- **Behaviour**, unless you annotate it — see #8.
- **Real data.** Prices, inventory, reviews and product copy come from the
  store. Your numbers are placeholders by definition, which is why #7 matters.
- **Merchant controls.** Our storefronts let the shop owner adjust spacing,
  colour schemes and content per section. A frame shows one spacing value
  because a frame can only show one — we add the control regardless. If a
  section's background is *deliberately* fixed and must never change, that's
  worth a note.
- **What happens between your breakpoints.** You give us 1440 and 393; real
  browsers are also 1280 and 834. We make sensible choices there, and if a
  specific in-between width matters, it needs its own frame.
- **Anything at all about a page you didn't design.** We will ask rather than
  invent.

---

## The short version

If you do only three things:

1. **Auto layout** instead of absolute positioning.
2. **A direct frame link** per breakpoint, with the width in the name.
3. **A comment describing behaviour** the frame can't show.

Those three remove most of the questions we'd otherwise send back to you.

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
