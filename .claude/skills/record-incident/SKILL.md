---
name: record-incident
description: Turn a problem into an improvement to this repo's own AI setup — record what went wrong, propose the exact rule, check or skill change that would have prevented it, wait for the developer's yes, then apply it in the store's own area. Use proactively the moment a fix lands that a rule, gate or check should have prevented (a theme 500, a blocked turn, a missed verify, a QA or GitBot finding, a design misread, a correction from the developer, a trap that cost more than a few minutes), and whenever asked to record, log or learn from a mistake.
argument-hint: <slug> "<what went wrong>"
---

# record-incident

Record, propose, wait for a yes, apply. Nothing in the setup changes without
the developer's answer, and nothing leaves this repo.

## When

- A Shopify command failed or the theme 500'd on a pattern a rule should name.
- The gate, Theme Check, the verifier, QA or GitBot caught what a rule should
  have prevented.
- The design was misread, or the developer corrected how the work was done.
- A CSS or browser behaviour had to be *measured* to understand.

**Not a learning:** a design change, a new requirement, a bug nothing could
have predicted. A store where everything works records nothing.

## Step 1 — Record

```bash
python3 .claude/scripts/new-incident.py \
  --slug <short-kebab-slug> \
  --title "<one line, what went wrong>" \
  --scope generic|client \
  --surfaced-by theme-500|theme-check|gate|hook|review|qa|designer|eyeball|verify|ci|other \
  --should-have-caught <the rule, check or skill that should have prevented it>
```

`scope`: true in a Shopify theme that is not this client's → `generic`;
otherwise `client`. Generic is a flag for whoever maintains Base. It sends
nothing anywhere, and the fix below still lands in this repo first.

Fill the sections of `docs/ai-workflow/incidents/<date>-<slug>.md`, a few
sentences each, for someone who was not in the session: what happened (file
and line), how it surfaced, what fixed it, which rule or check should have
caught it and why it did not, and the proposed change.

## Step 2 — Propose, and stop

Show the developer, before editing anything:

| | |
|---|---|
| What went wrong | one line |
| The change | the exact text or check entry, and the file it goes in |
| Kind | a rule line, a check, or a new skill |
| Effect | **adds** to the setup, or **changes existing** rules or checks |
| Scope | this store only, or generic (flagged, still applied here) |

Prefer, in this order: a line in a `.claude/rules/this-store-*.md`; a pattern
check in `.claude/this-store/checks.json` when a grep can decide it; a
`.claude/skills/this-store-*/` skill only when it is a procedure neither can
hold. A change that rewrites or removes an existing rule or check is said in
those words, with the reason.

Wait for the answer. No answer is not a yes: leave the file `open`.

## Step 3 — Apply, in the store's own area

On a yes, make the change:

- **A rule** — `.claude/rules/this-store-<topic>.md`, with a `description` and
  a `paths:` glob in its frontmatter; what to do, then what breaks.
- **A check** — an entry in `.claude/this-store/checks.json`:
  `{"id", "files", "pattern", "severity", "why", "rule"}`, `rule` naming the
  `this-store-*.md` it serves. Run it on the file that had the problem and
  confirm it fires.
- **A skill** — `.claude/skills/this-store-<name>/SKILL.md`.

Never edit a file Base ships (`CLAUDE.md`, the other rules, the scripts, the
hooks): Base's copy stops updating the moment this repo changes it.

Then close the record:

```bash
python3 .claude/scripts/new-incident.py --apply docs/ai-workflow/incidents/<file>.md \
  --change <store file>[,<store file>] [--changes-existing "<why>"]
```

On a no:

```bash
python3 .claude/scripts/new-incident.py --decline docs/ai-workflow/incidents/<file>.md --reason "<why nothing changes>"
```

In Base itself there is no store area: the change goes in the rule, check or
skill it belongs to, and `--apply` names that file.

## Step 4 — Commit

One commit, `[LEARN]: <what the setup now prevents>`, holding the record and
the store files.

## What holds it

SessionStart lists open learnings by title. The pull-request gate
(`check-learnings.py --gate`) fails while one recorded in that change is
still `open` (an older one is listed, not blocking), and when
existing store rules or checks change with no `--changes-existing` reason.
