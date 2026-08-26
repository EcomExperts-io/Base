# Base Theme — Decisions Log
 
**What this is:** a running log of architecture questions raised against
the Base Theme Architecture Reference, and their rulings. This is
cross-project — decisions here apply to any future client build, not
just Bites Vitamins. Project-specific findings (e.g. "does the Bites
Vitamins build follow this?") live in that project's own audit doc.
 
---
 
## Resolved
 
**Q: When behavior is needed on several pages, does it become one shared
`component-*` file or a `section-*` file per page?**
**A (Naish, Aug 2026):** Apply a test rather than a blanket preference.

> Is the behavior and appearance genuinely the *same* thing everywhere,
> differing only in configuration values?
> - **Yes** → one shared `component-*`, built so consumers configure it
>   via data attributes and CSS custom properties.
> - **No** → separate `section-*` files.

Both answers already exist in the codebase and both are correct in their
own context. Base's three product carousels (Featured Products, Related
Products, Featured Collections v2) are separate files because each wraps
Swiper with genuinely different configuration — three carousels sharing a
library, not one carousel duplicated. A scroll-snap-plus-dots carousel
used by several content sections is the opposite case: identical behavior
and markup contract, only the cards and values differ.

**How this relates to Moemen's earlier position.** On Aug 3, 2026 Moemen
flagged `section-about-carousel.js` in the Bites Vitamins build as an
architecture mismatch, and the Collection Page Audit's revised leaning was
option B — give each page its own carousel file. Naish's ruling is that
the DRY cost of duplicating genuinely identical behavior is not worth
paying. These are reconcilable rather than opposed: the compliance
checklist's item A3 already carved out an exception for "a genuine atomic
UI primitive", and the test above is how to tell whether you are in it.
The shared-primitive answer is that exception being applied, not
overridden.

Everyone agrees the original state was wrong. The disagreement was only
ever about the remedy, and it turns on whether a given carousel is one
thing or several — which the test answers.

**Still open for Moemen:** whether he accepts the test as stated, and
specifically whether a configurable scroll-snap carousel qualifies as an
atomic primitive in his view. Recorded here so it is visible in the PR
rather than settled quietly.

**Consequences already applied:** checklist item A3 rewritten from a
blanket preference for duplication to the test above;
`.claude/rules/naming-conventions.md` carries the test plus guidance on
building a primitive that absorbs later designs; both review agents check
naming against actual scope.

---

**Q: Should product-card JS handle swiping between photos of a *single*
product?**
**A (Moemen):** Base's current product card doesn't have this behavior
at all. If it's ever added, it belongs in the product-card JS file, not
a section file. Confirmed this is specifically about single-product
photo swipe — not about carousels of multiple different products (see
below).
 
**Q: Where does swiping between *multiple different products*
(a container-level carousel) belong — card or section?**
**A: Section-level**, based on direct precedent — Base implements this
pattern independently in three places (Featured Products, Related
Products, Featured Collections v2). `component-product-card.js` never
touches carousel/swipe logic in any of them; it only handles card-local
behavior (swatch → image swap).
- This principle transfers to new pages that need a multi-product
  carousel, even where Base's own version of that page has no carousel
  at all (e.g. Base's Collection page is grid + pagination + infinite
  scroll, never a carousel — but the *ownership* principle still applies
  once a carousel is required by a design).
- Status nuance: resolved as a transferable principle from repeated
  Base precedent. Not yet separately re-confirmed by Moemen for the
  specific case of a collection page needing a carousel — treat as
  provisionally settled unless he raises an objection.
 
**Q: `CollectionCarousel` and `CollectionInfo` now both live in
`section-collection.js` — doesn't that violate the one-file-one-class
convention above?**
**A:** Yes, deliberately — this is a named exception, not a new default.
Base's `section-*.js` files (`FeaturedProducts`,
`RelatedProductsCarousel`, `FeaturedCollectionsV2`) confirmed zero
exceptions to one file/one class/one custom element per section. But
none of those sections also do AJAX section-rendering of their own
markup, so none of them needed to answer "how does nested JS survive an
innerHTML swap?" Collection already has a working answer to that
sitting in the same file: `component-product-card.js`'s `<product-card>`
survives every filter/sort/page fetch for free because it's a
separately *registered* custom element — the browser auto-upgrades it
when `CollectionInfo.fetchSection` replaces the grid's innerHTML, no
glue code required. Folding the carousel into `CollectionInfo` as plain
methods would forfeit that and require inventing a manual re-init call
that has no precedent anywhere in this codebase. Keeping
`CollectionCarousel` as its own `customElements.define` — just
relocated into `section-collection.js` instead of its own file — reuses
that exact mechanism instead. Scoped to this file only; not a signal to
start putting multiple classes in other section files.
---
 
## Open
 
- **Collection filters — single-open-desktop accordion:** current
  `<collection-filters>` custom element (Aug 5, 2026 rewrite) treats all
  filter groups as independent — any number open at once, both
  breakpoints — matching Base's own `component-filters-sidebar.liquid`
  pattern exactly. The desktop filter bar in the approved Figma
  (`emfC8d9CtGm0Ewfb8p3LgZ`, node `13438:4321`) renders as a row of
  independent horizontal dropdown chips, not Base's vertical stacked
  accordion — which structurally implies opening one should probably
  close any other open one (adjacent dropdown panels would otherwise
  visually collide), but no frame or annotation in the file actually
  specifies that behavior. Confirmed by layout inference, not by an
  explicit spec — needs a yes from Neeraj before single-open-desktop
  exclusivity ships. Until then, independent-per-group is the shipped
  behavior (a deliberate simplification, not a placeholder bug).
- **`updateFilters` global scope:** uses
  `document.querySelectorAll('collection-info .js-filter')` — could two
  `collection-info` instances on one page cross-contaminate facets?
- **Infinite scroll vs. filter/URL pipeline:** is infinite scroll
  intentionally disconnected from the filter/URL pipeline (separate
  pipeline, doesn't update the URL, resets from page 1 on filter change),
  or is this a gap worth fixing?
- **Search page pattern:** does Base consider the Search page the same
  architectural pattern as Collection, for future faceted-listing pages?
- **Responsive layout switch (grid desktop / carousel mobile):** no Base
  precedent exists either way — Base's own collection page never
  switches its rendering mode by breakpoint. Being worked through via
  the Bites Vitamins Collection Page audit; will get logged here once
  a pattern is settled, since it'll likely recur on future client builds.
---
 
## Minor / Low-Stakes (team can decide, no need to loop in Moemen)
 
- Click delegation uses `matches()` instead of `closest()` — icon clicks
  inside filter badges may not register.
- `CollectionInfo.form` getter looks like dead code (queries a nested
  `collection-info` that doesn't exist).
- Internal docs (`section-collection.md`, etc.) reference IDs that
  differ from the actual source — treat code as source of truth until
  docs are updated.
- `featured-products.liquid` duplicates card markup instead of using
  the shared `component-product-card` snippet.
---
 
## Change Log
 
- **Aug 3, 2026** — Moemen's Base Theme code review flagged
  `section-about-carousel.js` and `collection-filters.js` in the Bites
  Vitamins build as architecture mismatches vs. Base Theme standard.
- **Aug 4, 2026** — Base Theme Collection/PDP architecture recon
  completed (see Architecture Reference doc).
- **Aug 4, 2026** — Moemen confirmed card-level photo-swipe behavior
  (not currently built, but belongs in card JS if added).
- **Aug 4, 2026** — Container-level carousel ownership resolved as a
  transferable principle from Base precedent (see Resolved, above).
- **Aug 5, 2026** — Confirmed the Bites Vitamins Collection page's
  shared carousel component (`section-about-carousel.js`) was built by
  an AI model before Base Theme standards existed for this project, and
  its accompanying `.cursor/references/shared-page-sections.md` is a
  post-hoc AI rationalization, not a reviewed team decision — it should
  not be treated as precedent. See Bites Vitamins Collection Page Audit
  for the resulting fix options.
- **Aug 5, 2026** — Collection's dedicated carousel component
  (`section-collection-carousel.js` / `<collection-carousel>`) folded
  back into `section-collection.js` (see Resolved, above) —
  `CollectionCarousel` stays a separate registered custom element for
  AJAX-survival reasons, but the file is now consolidated. Filter drawer
  Alpine block simplified to a single `drawerOpen` boolean; body scroll
  lock moved from JS to a CSS `:has()` rule matching Base's
  `component-filters-drawer.liquid`; accordion/outside-click/Escape/
  focus-restoration logic moved into a new, real, registered
  `<collection-filters>` custom element (`component-collection-filters.js`)
  with a reactive `matchMedia` `change` listener, fixing the live-resize
  bug. Single-open-desktop exclusivity intentionally not implemented
  pending confirmation (see Open, above).
- **Aug 26, 2026** — Shared-vs-section-owned resolved as a decision test
  rather than a blanket preference (see Resolved, above). Compliance
  checklist item A3 rewritten accordingly; new checklist Section E added
  covering schema and merchant controls, which had no coverage before and
  is part of why the Bites Vitamins audits missed the settings contract.
- **Aug 26, 2026** — These standards docs migrated from the Bites
  Vitamins repo into Base, where forks can inherit them. Project-specific
  audits stay in the client repo.
