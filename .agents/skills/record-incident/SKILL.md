---
name: record-incident
description: Record an incident — a fix that a rule, gate or check should have prevented — as a structured, committed file in docs/ai-workflow/incidents/ while the details are still in context. Use proactively the moment such a fix lands (a theme 500, a skipped Theme Check, a convention breach that reached review, a design misread, a trap that cost more than a few minutes), and whenever asked to record, log or note a mistake, trap or lesson.
argument-hint: <slug> "<what went wrong>"
---

# record-incident

Write it down at the moment of failure, when the details are in context, as
a committed file a pull request can show.

## When to record

- A Shopify command failed or the theme 500'd on a pattern a rule should name.
- A gate, Theme Check or review caught what a rule should have prevented.
- The design was misread, or something it could not show was inferred wrongly.
- A CSS or browser behaviour had to be *measured* to understand.
- A tool did not behave as documented.

**Not an incident:** a design change, a new requirement, a normal bug nothing
could have predicted. Every entry must be real.

## Steps

1. **Apply the CLAUDE.md test** for `scope`: true in a theme that is not this
   client's → `generic`; otherwise `client`; unsure → `generic`.

2. **Create the file**, then fill the four sections:

   ```bash
   python3 .claude/scripts/new-incident.py \
     --slug <short-kebab-slug> \
     --title "<one line, what went wrong>" \
     --scope generic|client \
     --surfaced-by theme-500|theme-check|gate|hook|review|qa|designer|eyeball|verify|ci|other \
     --should-have-caught <the rule, check or skill path that should have prevented it>
   ```

   It prints the path: `docs/ai-workflow/incidents/<date>-<slug>.md`.

3. **Fill the four sections**, a few sentences each, for someone who was not
   in the session:
   - **What happened** — the symptom and the cause, with the file and line.
   - **How it surfaced** — who or what noticed, and how late.
   - **What fixed it** — the change, and how it was verified.
   - **Which rule or check should have caught it, and why it did not** — if
     nothing could have, say so; if a rule exists and was not followed, say
     which and why (not loaded? too vague? contradicted by legacy code?).

4. **Leave `status: open`.** The drift check and the doctor count open
   incidents; `/harvest` marks a generic one `harvested`. A `client` incident
   that will never go up: `new-incident.py --set-status <file> client-only`.

5. **Commit it with the fix**, in the same change.

## Where it goes from here

SessionStart prints the open count; `check-tooling-drift.py` lists the rule
edits an incident led to; `/harvest <incident-file>` opens the Base pull
request from this repo. Incidents stay in the repo that recorded them; the
rule they produce is what travels.
