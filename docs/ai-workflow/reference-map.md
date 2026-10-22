# Reference map

One row per band of every page in scope, written by `/recon-theme` on arrival
and kept current by whoever changes the scope. (Older forks carry the same
table as `figma-frame-map.md`, with only the Figma columns.) A rebuild has
three kinds of reference, and the band's reference decides which skill builds
it and which half of `/verify-against-reference` proves it:

| Reference | Source of | Built with | Verified by |
|---|---|---|---|
| **Figma** | the look — layout, spacing, type, colour, states; never data | `/build-page-from-figma` | the frame at each breakpoint |
| **Live** | what the band does, says and holds today; never its code | `/build-section-from-live` | `live-parity.py` to 0% |
| **Both** | look from Figma; behaviour, copy and data shape from live | `/build-page-from-figma`, routing the behaviour to live | the frame for the look, `live-parity.py states` for behaviour |

This file in Base is the template. A fork fills it in; Base's own copy stays
empty.

## Bands

| Page | Band | Reference | Figma desktop | Figma mobile | Live URL · section key | In scope | Note |
|---|---|---|---|---|---|---|---|
| | | figma / live / both | `node:id` · W×H | `node:id` · W×H | `https://…/pages/…` · `key_AbC123` | yes / no / later | |

Rules for the table:

- A Figma cell carries the node id **and the frame's exact size**; the verify
  skill renders at that width and height, and a wrong guess verifies the wrong
  design.
- A live cell carries the page URL and the section key (`[id$="__KEY"]` on
  live), or a selector for a static section (`#shopify-section-header`).
- "Both" rows say in the note which behaviour comes from live (a carousel's
  autoplay, a toggle's default, a form's validation copy).
- Scope changes edit this table in the same change that made them.
