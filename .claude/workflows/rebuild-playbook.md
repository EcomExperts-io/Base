# Workflow — the order of attack for a store rebuild

What to build first, what to carry, and what to do when you arrive in the
middle. A human starts this; it is not a skill.

Order by **dependency**, not by page: every page depends on the foundations
and the chrome, and a store where those are right can have its pages rebuilt
in any order. **Commerce before content**: a storefront is a shop. The purchase
path is stage 2, it has its own check, and that check runs green at the close
of every stage after it — a page that breaks the cart is not done.

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
| **0 · Recon** | `/recon-theme --live-url` (the live feature inventory: apps, popups, markets, page builder), `/store-recon`, the reference map (one row per band: which reference — Figma, live or both — node ids with exact size, live URL and section key) | You cannot wire a value to a field that does not exist, verify against a frame you cannot address, or build a product form an app will inject into | The gap table is complete; every band names its reference |
| **1 · Foundations** | Tokens (`css-variables.liquid`), typography, container width and gutters, breakpoints, colour schemes, `settings_schema.json` | Every section reads these; a wrong container costs a pass over every section later | `get_variable_defs` mapped to tokens; one breakpoint set, `min-width` only; no raw hex |
| **2 · Commerce path** | The cart engine (untouched), cart drawer and cart page, the product form and buy box (variants, quantity, selling plans), quick add, discount codes, localization and markets, the checkout handoff | It is the shop. Every later stage renders on top of it, and a bug here reaches the client as "doesn't add" — the one class of defect a storefront cannot carry | `commerce-check.py` green at every width; `window.Cart` for every mutation (the gate flags a raw `/cart/add`); line properties survive a change; `cart:change` awaited, never a sleep; logged in and out walked by hand; `docs/base-theme-standards.md` §3 |
| **3 · Global chrome** | Header + navigation, footer, search overlay, announcement bar | On every page, the largest accessibility surface, the first thing the client sees on every preview | `docs/base-theme-standards.md` §3; overlay a11y (dialog role, focus in and back, Escape, live region outside the swapped region) |
| **4 · Shared components** | Product card, price, buttons, badges, forms, pagination | Consumed by PDP, collection, search, recommendations — build once here or four times later | Shared-vs-section decision test; `data-verify-mask` on live values; renamed if scope widened |
| **5 · Transactional templates** | PDP (the bands around the buy box), Collection, Search | They exercise every component from stage 4 and the Section Rendering pattern | `docs/base-theme-standards.md` §2; filters as real forms; `pushState` vs `replaceState`; the commerce check still green |
| **6 · Homepage and content** | Homepage, landing pages (`landing-batch.md` when they are matched to live), about, FAQ | *Assembly*, not construction — Base ships 20+ content sections; building the homepage first is how page-named sections happen | Presets reused via `templates/*.json` before anything new is written; name by function; a landing page that adds to cart runs the commerce check |
| **7 · Long tail** | Blog, article, account, 404, password, gift card | Template main sections, low design variance, often Base's as-is | Contract exemptions declared with a Liquid comment mentioning `presets` |

Stages 1–4 decide what can be carried. Put the review agents on them hardest.

**Closing a stage, from 2 onward:**

```bash
python3 .claude/scripts/commerce-check.py --url "<dev theme product URL>" --discount-code <a real code> --market <a second market>
```

Green at 393, 768, 1024 and 1440, then the two rows it cannot automate — a
person logged in, and Safari on an iPhone and a Mac — walked and recorded in
the stage's handoff. The Stop hook names a change to the purchase path that
has no commerce report newer than it. Then record the close, so the next
session is told where the rebuild stands:

```bash
python3 .claude/scripts/where-are-we.py --close-stage 2 "commerce path"
```

It writes the progress record (`progress.json` under `docs/ai-workflow/`); commit it with the stage's work.

## Per stage

- **One brief per build**, from `multi-session-rebuild.md` Part 2 (whole
  rebuild) or `parallel-section-build.md` Part 2 (one page's sections). Both
  start with `/build-page-from-figma`, which starts with `/figma-readiness`.
- **Verify before hand-off**: `/verify-against-reference` per frame, report on
  disk, numbers quoted in the handoff. The Stop hook reminds; the reviewer
  reads the report.
- **Record as you go**: `/record-incident` the moment a fix lands that a rule
  should have prevented. `/harvest` the generic ones before the stage closes,
  not at the end of the build.
- **Gate**: `shopify-pr-reviewer` over the diff before a human sees the PR.

## Inheriting mid-rebuild

Every session start prints one line from `where-are-we.py`: which of the
three situations the repo looks like — a fresh rebuild, joining midway,
correcting after QA — and why, from the state document's age, the verify
reports, the stages recorded as closed, the branch name and the recent
commits. It is a reading, not a ruling; the person who knows better runs
what fits. Everything above applies; two things change.

1. **Stage 0 produces a "carry" verdict, not a plan** — `/recon-theme` ends
   with carry-as-is / carry-with-fixes / rebuild / missing. Argue with it in
   the state document, not in code.
2. **The "missing" list is your build order**, sorted by the stage table. If
   the previous team built the homepage and no header, the header comes next
   regardless of what the tracker says — the tracker is told why.

Do not "fix" what the recon finds in stage 0. Record it; if a rule should have
prevented it, `/record-incident`; fix it in the stage it belongs to.

## Budget

Recon is a day. Foundations and chrome are the slow stages — a header with
mega-menu panels or a cart drawer with states is about two sessions each — and
they are the stages a page-first order skips and pays for later.
