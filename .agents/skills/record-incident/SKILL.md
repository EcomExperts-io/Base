---
name: record-incident
description: Record an incident — a fix that a rule, gate or check should have prevented — as a structured, committed file in docs/ai-workflow/incidents/ while the details are still in context. Use proactively the moment such a fix lands (a theme 500, a skipped Theme Check, a convention breach that reached review, a design misread, a trap that cost more than a few minutes), and whenever asked to record, log or note a mistake, trap or lesson.
---

# record-incident

Write it down now, in the shape the harvest can read.

**Why this exists.** The v1 workflow asked for a "mistake log" — gitignored, in
the client repo, created only if the AI offered and someone said yes. Across
four client builds the count of logs was zero, and every incident that mattered
became a Base rule anyway: weeks later, by one person, as archaeology. The
record has to be made at the moment of failure, because that is the only moment
all the details are in context, and it has to be committed, because a file
nobody can see in a pull request does not exist.

## When to record

- A Shopify command failed or the theme 500'd because of a pattern a rule
  should have named.
- A gate, Theme Check or review caught something after the code was written
  that a rule should have prevented before.
- The design was misread, or something the design could not show was inferred
  wrongly and had to be redone.
- A CSS or browser behaviour had to be *measured* to understand.
- A tool did not behave as documented (Figma page listing, a CLI on the wrong
  Node, a hook that never fired).

**Not an incident:** a design change, a new requirement, a normal bug in new
code that nothing could reasonably have predicted. Do not inflate the queue;
it is only useful if every entry is real.

## Steps

1. **Apply the CLAUDE.md test** to decide `scope`: would this be true in a
   Shopify theme that is not this client's? Yes → `generic`. No → `client`.
   When unsure, `generic` — the harvest decides for real.

2. **Create the file** — one command, then fill the four sections:

   ```bash
   python3 .claude/scripts/new-incident.py \
     --slug <short-kebab-slug> \
     --title "<one line, what went wrong>" \
     --scope generic|client \
     --surfaced-by theme-500|theme-check|gate|hook|review|qa|designer|eyeball|verify|ci|other \
     --should-have-caught <the rule, check or skill path that should have prevented it>
   ```

   It prints the path: `docs/ai-workflow/incidents/<date>-<slug>.md`.

3. **Fill the four sections**, each a few sentences, written for someone who
   was not in the session:
   - **What happened** — the symptom and the cause, with the file and line.
   - **How it surfaced** — who or what noticed, and how late.
   - **What fixed it** — the change, and how it was verified.
   - **Which rule or check should have caught it, and why it did not** — the
     field that turns an incident into a standards gap. If nothing could have,
     say so; if a rule exists and was not followed, say which and why (not
     loaded? too vague? contradicted by legacy code?).

4. **Leave `status: open`.** The drift check and the doctor count open
   incidents; `/harvest` moves a generic one to Base and marks it
   `harvested`. A `client` incident that will never go up is marked
   `client-only` with `new-incident.py --set-status <file> client-only`.

5. **Commit it with the fix**, in the same change. An incident committed
   beside the code it describes is reviewable; one written at the end of the
   build is not written.

## Where it goes from here

- The Stop hook's SessionStart context prints the open count every session.
- `check-tooling-drift.py` lists local rule edits; an incident that led to a
  rule edit in this repo is a harvest candidate by construction.
- `/harvest <incident-file>` opens the Base pull request from inside this
  repo — no history repair, no copying files by hand.

Incidents are excluded from the tooling overlay on purpose: they belong to the
repo that recorded them. What travels to Base is the rule the incident produces.
