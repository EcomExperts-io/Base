# Incidents

One file per fix that a rule, gate or check should have prevented, created by
`/record-incident` the moment it happens and read by `doctor.py` (the open
count every session), `check-tooling-drift.py` (what is waiting to be
harvested) and `/harvest` (what goes up to Base).

Frontmatter a script can read:

| field | values |
|---|---|
| `scope` | `generic` (true in a theme that is not this client's) / `client` |
| `surfaced_by` | `theme-500`, `theme-check`, `gate`, `hook`, `review`, `qa`, `designer`, `eyeball`, `verify`, `ci`, `other` |
| `should_have_caught` | the rule, check or skill that should have prevented it |
| `status` | `open` / `harvested` / `client-only` |

Four sections: what happened, how it surfaced, what fixed it, which rule or
check should have caught it and why it did not.

```bash
python3 .claude/scripts/new-incident.py --list --open
```

An incident lives in the repo where it happened and does not travel with the
tooling overlay; the rule it produces does. Once harvested, the incident file
is deleted — its lesson is in the rule, and the story has no reader. This
README is the one file in the directory that the overlay carries down, so the
directory exists in a fork on arrival.

## Where harvested incidents landed

| Incident | Where it landed in Base |
|---|---|
| dangling paths block the first fork commit | `pull_base_tooling_lib.py` carries this README down |
| hot reload blocks the verifier | `theme-verify` server on 9293; CDP renderer |
| JSON check crashes on a trailing comma | `check-json.py`, self-tested |
| page-width collapses inside a flex section | `sections.md` |
| pull script runs on an unknown flag | `check_flags` in `pull-base-tooling.py` |
| close() must cancel the request it started | `javascript-standards.md`, AbortController |
| conventions checker reads CSS comments as code | `blank_css_comments`, self-tested |
| `<details>` breaks the box-sizing reset | `html-standards.md` |
| file:line citation blocks a commit | `check-rule-links.py` |
| headless cannot render a mobile viewport; width clamp fakes a render | `render-screenshot.py` over CDP, asserting its own width |
| lazy images render as blank bands | `render-screenshot.py` waits for pixels |
| live-reload off latches an upload error | `run-theme` notes |
| mask denominator exceeds the frame | `compare.py` coverage bitmap |
| template setting dropped before the section schema | `templates.md`, `run-theme`, `template-setting-unknown` check |
| preset-seeded block renders an empty band | `sections.md`; advisory in `check-section-contract.py` |
| rating metafield value is a drop, not a number | `liquid.md` |
| fixed sleep reads a stale cart | `javascript-standards.md`, `verify-against-reference` |
| flex child shrinks; flex min-size beats aspect-ratio; margin collapses out; `[hidden]` defeated by display; unloaded bold face; mixed-font lines grow | `css-standards.md` Defensive CSS; `.claude/references/layout-pitfalls.md` |
| overlay states cannot be verified | `--eval` on the renderer |
| schema default references a missing key; `t:` key with no locale entry | `schema-t-key-missing`, `liquid-t-key-missing` checks |
| docs go stale because nothing checks them | `docs-orphan-page` check (deleted-file case only) |
| formatter glob rewrote the whole theme | `CLAUDE.md`, Commands |
| url setting default fails the whole upload | `run-theme` notes |
| multi-tag URLs must be alphabetical | `liquid.md` |
| `!important` check blanks the comment it looks for | `check-conventions.py`; three fixtures |
| render-screenshot stalls on a scroll-locked modal | `verify-against-reference` |
| article_list `.size` is blank | `liquid.md` |
| visible_if rejected on resource pickers; duplicate product setting; multi-line metafield in a text setting; generic file blank in an image picker | `schemas.md`, "Limits the upload enforces"; two checks |
| header band held a page menu | `verify-against-reference` inputs |
| product form `id` shadowed; subscription widget injects into a custom form | `javascript-standards.md`, Product forms |
| band heights matched while positions drifted | `verify-against-reference`, box table |
| closing brace inside an output tag | `liquid.md` |
| schema locale at the 3,400-key cap | `locales.md`; the count in `check-json.py` |
| duplicated CSS blocks | `css-duplicate-block` check |
| Liquid cart JSON has no discount_codes | `javascript-standards.md`, cart API |
| hooks never ran in forks; inheritance claim was stale; mistake log never created; verified by height alone; headless Chrome writes then hangs; generated mirror conflicts on merge; `t:` key in a template value; two-step range fails upload; Theme Check skipped on Node 20 | the tooling overlay and CI caller; the drift report; `/record-incident`; `verify-against-reference`; the CDP renderer; `sync-ai-config.sh`; `check-conventions.py`; `run-theme` |
