---
name: build-page-from-figma
description: Build a store page, section, shared component, overlay or interaction state from a Figma design against Base Theme standards, verify it, and hand it off with the proof. Use when asked to build, rebuild, or implement anything from a Figma frame — a page, a header or footer, a drawer or modal, or a set of states. When the reference is the live site instead, Step 1 routes to build-section-from-live.
argument-hint: <figma-url-or-nodeId> [notion-task]
---

# build-page-from-figma

Figma frame in, Base-standard code out, verified, handed off with the proof.

## Not everything from Figma is a page

A footer, a header with mega-menu panels, a cart drawer, a search overlay:
none belongs to a template, which is how this skill gets bypassed on the work
where the contract, the keys and the handoff matter most. Use it, substituting:

| The skill says | For a component, overlay or state, instead |
|---|---|
| "Which template the result belongs to" | Which page types it renders on. A shared component renders everywhere, so **verify on at least three different page types**. |
| One desktop frame and one mobile frame | A **component frame** for exact specs plus **in-context frames** for behaviour. Numbers from the first, behaviour from the second. |
| Visual fidelity against the frame | Also across **states** — default, open, active, scrolled, empty. A state frame is a specification; build what it shows. |
| The section settings contract | Applies to any section. A snippet rendered from the header is not a section and needs no `presets`. |

- A shared component is on every page, so editing a file another session owns
  is likely here — say so.
- An overlay or drawer needs focus moved in on open and returned on close,
  Escape, no page scroll behind it, and for asynchronous updates a small
  status node with `aria-live="polite"` and `aria-atomic="true"` carrying only
  the status. Never make the whole drawer or result list live.

## Two success criteria, judged separately

**Code style and architecture** against `.claude/rules/`; **visual fidelity**
against the frame. Report them separately — never "matches the design" as if
it covered both.

## Step 1 — Confirm what you are building. Ask; do not guess.

Before any Figma call, state back:

- **Which project / store**
- **Which reference** — **Figma**, **live**, or **both**, recorded per band
  in `docs/ai-workflow/reference-map.md`. Figma is the source of the look and
  never of data; live is the source of behaviour, copy and data, never of code.
  - **Live** → `/build-section-from-live`; its §4 verifies against live and
    its §5 returns to Steps 5–6 here.
  - **Both** → design values from the frame; behaviour, copy and data shape
    from live; verify the look against the frame and the behaviour with
    `live-parity.py states`.
- **Which Figma file** — the file key, confirmed for this project; repo docs
  carry stale keys
- **Which frame** — a node ID, desktop or mobile
- **Which template** the result belongs to
- **The Notion card**, if one was given

If any is missing or ambiguous, **ask**.

**Notion is the functional source; Figma is not.** Default selections,
conditional visibility, edge cases and where a value comes from live in Notion
and nowhere in the frame.

- **Given** → read it first; walk its requirements one by one at verification.
- **Not given** → infer from the design and **state every assumption** in the
  write-up so a human can correct it.

A Figma access error usually means a newer file exists; ask before assuming
a share grant is needed.

## Step 1½ — Check the frame is buildable

`/figma-readiness` on each node before the first `get_design_context` call.
On `send back` do not build: hand the developer the designer's message and
stop unless told to build anyway (record that in the report).

## Step 2 — Fetch the frame by node ID, one frame at a time

**Always pass an explicit `nodeId`.** `get_metadata` with no `nodeId` can
return a single "Cover" page while frames fetch fine by ID — a tool
limitation, not permissions. Node IDs come from a human, a share link
(`?node-id=`) or the project's registry. Never guess one: a wrong guess
silently builds the wrong design.

Desktop and mobile are **separate calls** — separate frames, different specs.

If `get_design_context` fails, fall back to `get_screenshot` plus attached
images and say in the report that you worked from screenshots.

## Step 3 — Build against the standards

`/scaffold-section` for each new section. The rules apply in full; the three
a design-driven build misses most, because no frame shows them:

1. **The merchant settings contract** — `padding_top`, `padding_bottom`,
   `padding_top_mobile`, `padding_bottom_mobile`, `color_scheme`, plus a
   preset. A frame shows one spacing value because it can only show one.
2. **Translation keys** — the frame's English copy is not an instruction to
   hardcode it, including in brand-new files with no `| t` nearby.
3. **Naming by function** — the Figma file is organised by page; the section
   is named by what it is.

Extract real values from the frame; where one exists as a theme token, use it.

## Step 4 — Verify both criteria

**Code:** run the `shopify-pr-reviewer` agent over the diff and fix what it
finds. Confirm the gate would pass.

**Visual:** `/run-theme`, then `/verify-against-reference` with the page URL,
the file key and each node id at the width it was designed at. It writes
`.claude/verify/<slug>/report.{json,md}`; until that exists and is newer than
your last edit the page is not verified, and the Stop hook says so.

**Functionality:** walk the Notion requirements one at a time; say which you
could not verify and why. If the change touches the purchase path — product
form, quick add, selling plans, cart drawer or page, discount codes,
localization — run `commerce-check.py` (the functional half of
`/verify-against-reference`) at 393, 768, 1024 and 1440 and quote its report;
a person then walks the three rows it cannot: logged in, Safari, checkout.

**GitBot:** in a client repo, after the push, `/gitbot-preflight` settles
every finding — fixed, or flagged with the developer's reason — before the
pull request.

**Self-test:** with the `agentic-os` plugin, `/qa-precheck` is the QI's own
run on the preview before the hand-off. Give it
`.claude/verify/<slug>/report.json` and `commerce-check.py`'s report: their
reference, pages and widths are its plan, and their numbers go in its
one-line result.

Report code, visual and functionality separately, quoting the verify report's
numbers.

Set a goal before building, so a fresh evaluator decides when it is done:

```text
/goal .claude/verify/<slug>/report.json exists with diff_pct under 5 at every
frame width, table_off is 0, every new section passes
python3 .claude/scripts/check-section-contract.py --files, and
python3 .claude/scripts/check-conventions.py --changed --block exits 0.
Stop after 25 turns if not met and report what remains.
```

## Step 5 — Hand off

The Notion card, the hand-off comment, QI bugs, Slack and branch names belong
to the `agentic-os` plugin; Base supplies the proof:

- the gate: `check-conventions.py --changed --block` and
  `check-section-contract.py --files`, passed or what remains;
- `.claude/verify/<slug>/report.json`: `diff_pct` and `box_off` per width,
  and what it lists as `unverified`;
- `commerce-check.py`'s report: passed, failed, skipped, and the three rows
  a person walked;
- GitBot's open, fixed and flagged, from `/gitbot-preflight`;
- every assumption, and anything blocked or built from screenshots.

**With the plugin:** `/handoff`, given the list above for its _Dev checks_
and _Known gaps_. It posts on approval and never changes the card's status.

**Without it:** show the draft; on approval post one comment on the card, for
someone who was not in the session: what was built, decisions and why, what
was left out, the proof above, then 4 to 10 numbered steps to QA. Each step
names the page, the width and logged in or out, then the action and `Expect:`
the result — something a non-technical reviewer checks in a browser, never
code, settings, schema or file names. A page that sells includes the purchase
path: add, change the quantity, remove, a discount code, a country switch,
again logged in, again in Safari on an iPhone. Then set the status to Quality
Inspection. Ask which card if you do not have it; create none, and change
nothing else.

## Step 6 — Record anything that went wrong

A real mistake — the wrong thing built, a design misread, a re-prompt, a trap
a rule should have named — is `/record-incident` **at the moment it happens**.
It records what happened and which rule or check should have caught it,
proposes the change to this repo's own setup, and applies it on the
developer's yes.

When the QI logs bugs on the card, `/close-qa-loop` picks them up.
