# Workflow — the order of attack for a store rebuild

What to build first, what to carry, and what to do when you arrive in the
middle. A human starts this; it is not a skill.

**Why this exists.** The v1 vision ordered work by page: Collection, then PDP,
then "header, mega menu, cart engine later". The first full rebuild proved that
wrong — five of nine builds were a footer, a header with five mega-menu panels,
a cart drawer, a search overlay and a set of drawers, every page depended on
them, and none had a standard to build against. Order by **dependency**, not by
page. A store where the foundations and the chrome are right can have its pages
rebuilt in any order; a store where they are wrong makes every page a
renegotiation.

## Arriving — the same three commands whether the repo is new or six months old

```bash
sh .claude/scripts/base-link.sh                   # Base as remote + worktree + reference dir; no shared history needed
python3 .claude/scripts/pull-base-tooling.py      # three-way overlay: the previous team's edits are kept and listed
```

then, in a session, `/recon-theme` (what is built, what they settled on, what
is left) and `/store-recon` (what the store has). Read both documents before
the first line of code. If the repo has a `.cursor/` but no `.claude/`, the
overlay installs `.claude/` and regenerates `.cursor/` from it; if both exist
and disagree, the drift report says so and a human picks.

**The previous team's conventions win where they conflict with Base's** — half
the theme already uses them. Record them in this repo's rule copies (the recon
does this), not in Base.

## The dependency order

| Stage | Build | Why here | Review emphasis |
|---|---|---|---|
| **0 · Recon** | `/recon-theme`, `/store-recon`, the Figma frame map (one row per frame: node id, what it is, exact size, per-frame link) | You cannot wire a value to a field that does not exist, or verify against a frame you cannot address | The gap table is complete; every frame has an id |
| **1 · Foundations** | Tokens (`css-variables.liquid`), typography, container width and gutters, breakpoints, colour schemes, `settings_schema.json` | Every section reads these; a wrong container costs a pass over every section later | `get_variable_defs` mapped to tokens; one breakpoint set, `min-width` only; no raw hex |
| **2 · Global chrome** | Header + navigation, footer, cart drawer, search overlay, announcement bar | On every page, the largest accessibility surface, the first thing the client sees on every preview | The header/cart/search reference; overlay a11y (dialog role, focus in and back, Escape, live region outside the swapped region); the cart engine untouched |
| **3 · Shared components** | Product card, price, buttons, badges, forms, quick-add, pagination | Consumed by PDP, collection, search, recommendations — build once here or four times later | Shared-vs-section decision test; `data-verify-mask` on live values; renamed if scope widened |
| **4 · Transactional templates** | PDP, Collection, Search, Cart page | They exercise every component from stage 3 and the Section Rendering pattern | The Collection & PDP reference; filters as real forms; `pushState` vs `replaceState` |
| **5 · Homepage and content** | Homepage, landing pages, about, FAQ | *Assembly*, not construction — Base ships 20+ content sections; building the homepage first is how page-named sections happen | Presets reused via `templates/*.json` before anything new is written; name by function |
| **6 · Long tail** | Blog, article, account, 404, password, gift card | Template main sections, low design variance, often Base's as-is | Contract exemptions declared with a Liquid comment mentioning `presets` |

Stages 1–3 decide what can be carried. Put the review agents on them hardest.

## Per stage

- **One brief per build**, from `multi-session-rebuild.md` Part 2 (whole
  rebuild) or `parallel-section-build.md` Part 2 (one page's sections). Both
  start with `/build-page-from-figma`, which starts with `/figma-readiness`.
- **Verify before hand-off**: `/verify-against-figma` per frame, report on
  disk, numbers quoted in the handoff. The Stop hook reminds; the reviewer
  reads the report.
- **Record as you go**: `/record-incident` the moment a fix lands that a rule
  should have prevented. `/harvest` the generic ones before the stage closes,
  not at the end of the build.
- **Gate**: `shopify-standards-coach` (advisory) then `shopify-pr-reviewer`
  (gate) before a human sees the PR. Both remember what recurs.

## Inheriting mid-rebuild

Everything above applies; two things change.

1. **Stage 0 produces a "carry" verdict, not a plan** — `/recon-theme` ends
   with carry-as-is / carry-with-fixes / rebuild / missing. Argue with it in
   the state document, not in code.
2. **The "missing" list is your build order**, sorted by the stage table. If
   the previous team built the homepage and no header, the header comes next
   regardless of what the tracker says — the tracker is told why.

Do not "fix" what the recon finds in stage 0. Record it; if a rule should have
prevented it, `/record-incident`; fix it in the stage it belongs to.

## What this costs, honestly

Recon is a day. Foundations and chrome are the slow stages — a header with
mega-menu panels and a cart drawer with states took two sessions each on the
MiLB build — and they are the stages a page-first order skips and pays for
later. Homepage last feels wrong to everyone until the second rebuild.
