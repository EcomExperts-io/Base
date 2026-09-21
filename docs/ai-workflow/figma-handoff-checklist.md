# Figma handoff — the one-page version

Four things. If you do only these, our build tool reads your file correctly
first time, and you get fewer questions back. The full reasoning and the other
twelve practices are in
[`figma-ai-friendly-design-practices.md`](./figma-ai-friendly-design-practices.md).

## Before you send the link

| Do this | What we check, automatically, before we build |
|---|---|
| **Auto layout** on every row, column, card and section, with `Fill` / `Hug` / fixed set deliberately | Whether elements are laid out or merely placed — absolutely positioned boxes read as unrelated |
| **Name layers for what they are** — `product-card/image`, not `Rectangle 47` | The share of layers still carrying a default name. Over 20% and the frame comes back to you |
| **One frame per breakpoint, width in the name** — `PDP / Desktop 1440`, `PDP / Mobile 393` | That the frame's name contains its own width, and that a sibling frame exists for the other breakpoint |
| **A comment for anything that happens rather than looks** — what is open by default, hover, empty states, whether one accordion closes the others | Text or comments beside the frame describing behaviour; interactive components without any get a question, not a build |

Two more that cost nothing:

- **Delete hidden layers** before handoff. We read the layer tree, not the
  picture — a hidden old version is as visible to the tool as the current one.
- **Use variables** for colour, spacing and type. A named variable maps
  straight onto our theme's tokens; a raw hex is a guess.

## What we send back

Running our readiness check on a frame produces a short list like this — the
same list you would get from us as a question, only before we have spent a day
on it:

```
Figma readiness — Default header (329:26263, 1440×110)
  20 layers, depth 5.  Overall: SEND BACK

  send back layer naming        60.0% of layers carry a default name   (practice 4)
  warn      hidden layers       3 hidden                               (practice 12)
  ask       frame width in name "Default header" (frame is 1440px wide) (practice 3)
  pass      components used     3 instance(s) of components            (practice 7)

  Largest default-named layers — the ones to rename first:
    638:21435      Frame 1261153641   241×48
    639:22646      Frame 1261153642   526×48
```

Green means we build. Anything else means one round of renaming and a comment
or two — ten minutes for you, a day saved for both of us.

## What no frame can tell us

Behaviour, real data (prices, counts, stock), merchant controls (we add
spacing and colour settings to every section regardless of what the frame
shows), what happens between your breakpoints, and whether your colours pass
contrast. We will ask rather than invent.
