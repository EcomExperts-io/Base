# Incidents

One file per thing that went wrong that a rule, gate or check should have
prevented. Created by `/record-incident` at the moment it happened; read by
`doctor.py` (the open count in every session), `check-tooling-drift.py`
(what is waiting to be harvested) and `/harvest` (what goes up to Base).

Each file carries frontmatter a script can read:

| field | values | meaning |
|---|---|---|
| `scope` | `generic` / `client` | the CLAUDE.md test — true in a theme that is not this client's? |
| `surfaced_by` | `theme-500`, `theme-check`, `gate`, `hook`, `review`, `qa`, `designer`, `eyeball`, `verify`, `ci`, `other` | how late it was found |
| `should_have_caught` | a path | the rule, check or skill that should have prevented it |
| `status` | `open` / `harvested` / `client-only` | where it is in the loop |

and four sections: what happened, how it surfaced, what fixed it, and which
rule or check should have caught it and why it did not.

In Base this directory holds the generic incidents Base's own tooling was made
from — the audit of 14 Sep 2026 and the client builds before it. In a client
repo it holds that build's. Incidents do not travel with the tooling overlay;
the rules they produce do.

```bash
python3 .claude/scripts/new-incident.py --list --open
```

## Harvested from client builds

Incidents stay in the client repo; what they taught lands here. One client
rebuild (Sep–Oct 2026) recorded 48 generic incidents, none harvested during
the build. This is where each one went, on 22 Oct 2026.

| Incident | Where it landed in Base |
|---|---|
| dangling paths block the first fork commit | `pull_base_tooling_lib.py` carries the incidents README down (earlier) |
| hot reload blocks the verifier | `theme-verify` server on 9293; CDP renderer (earlier) |
| JSON check crashes on a trailing comma | `check-json.py` fixed (earlier); now self-tested |
| page-width collapses inside a flex section | `sections.md` (earlier) |
| pull script runs on an unknown flag | `check_flags` in `pull-base-tooling.py` (earlier) |
| close() must cancel the request it started | `javascript-standards.md`, AbortController section |
| conventions checker reads CSS comments as code | `blank_css_comments` (earlier); now self-tested |
| `<details>` breaks the box-sizing reset | `html-standards.md` (earlier) |
| file:line citation blocks a commit | `check-rule-links.py` (earlier, incl. ranges and lists) |
| headless cannot render a mobile viewport; width clamp fakes a render | `render-screenshot.py` over CDP, asserting its own width (earlier) |
| lazy images render as blank bands | `render-screenshot.py` waits for pixels (earlier) |
| live-reload off latches an upload error | `run-theme` notes (earlier) |
| mask denominator exceeds the frame | `compare.py` coverage bitmap (earlier) |
| new setting stripped from the template on sync; template setting dropped before the section schema | `templates.md`, `run-theme`, and `template-setting-unknown` in `check-conventions.py` |
| preset-seeded block renders an empty band | `sections.md`, and an advisory in `check-section-contract.py` |
| rating metafield value is a drop, not a number | `liquid.md` |
| fixed sleep reads a stale cart | `javascript-standards.md`, `verify-against-figma` |
| flex child shrinks instead of scrolling; flex min-size beats aspect-ratio; margin collapses out of the section; `[hidden]` defeated by display; accent face loaded without its bold; mixed-font heading lines grow | `css-standards.md` Defensive CSS, long form in `.claude/references/layout-pitfalls.md` |
| overlay states cannot be verified | `--eval` on the renderer (earlier) |
| schema default references a missing key; schema `t:` key with no locale entry | `schema-t-key-missing` and `liquid-t-key-missing` in `check-conventions.py` |
| docs go stale because nothing checks them | `docs-orphan-page` in `check-conventions.py` (the deleted-file case; a rewritten section with an untouched doc page is not checked) |
| formatter glob rewrote the whole theme | `CLAUDE.md`, Commands |
| url setting default fails the whole upload | `run-theme` notes (the blast radius; no rule, as the incident itself concluded) |
| multi-tag URLs must be alphabetical | `liquid.md` |
| `!important` check blanks the comment it looks for (twice) | `check-conventions.py` fixed; three fixtures in `test-checks.py` |
| render-screenshot stalls on a scroll-locked modal | `verify-against-figma` (the workaround; the script is unchanged) |
| article_list `.size` is blank | `liquid.md` |
| visible_if rejected on resource pickers; duplicate product setting rejected; multi-line metafield rejected by a text setting; generic file blank in an image picker | `schemas.md`, "Limits the upload enforces", and two checks in `check-conventions.py` |
| header band held a page menu | `verify-against-figma` inputs |
| product form `id` shadowed; Recharge widget injects into a custom form | `javascript-standards.md`, Product forms |
| band heights matched while positions drifted | `verify-against-figma`, box table |
| closing brace inside an output tag | `liquid.md` |
| schema locale at the 3,400-key cap | `locales.md`, and the count in `check-json.py` |
| duplicated CSS blocks | `css-duplicate-block` in `check-conventions.py` |
| Liquid cart JSON has no discount_codes | `javascript-standards.md`, cart API |

The new checks found two things in Base's own tree on the day they were
written: `templates/product.json` sets `image_ratio` on shop-the-look, which
its schema never defines (the Liquid reads it, so it is always blank), and
nothing else. Not fixed here — see the retrofit ruling in the decisions log.
