---
description: Keeping the documentation that guides this work — docs/, .claude/rules, skills, agents and workflows — correct as you learn, without being asked
paths:
  - "docs/**"
  - ".claude/**"
  - ".cursor/**"
  - "CLAUDE.md"
---

# Living Documents

## The principle

The files in `docs/`, `.claude/rules/`, `.claude/skills/`, `.claude/agents/`,
`.claude/workflows/`, `.claude/references/` and `CLAUDE.md` are **living
documents**. They describe what we currently believe is correct, which means
they are wrong the moment something is learned and not written down.

- Update them as new cases are encountered.
- When you discover a pattern, edge case, or solution while working an issue,
  fix the relevant file in the same change.
- If something in them does not work as described, correct it immediately
  rather than working around it.
- Attach the consequence that makes a rule strict as one clause — what
  breaks — never the story of which build, who found it or when.
- Remove information that has gone stale.

**Do not wait to be asked.** Maintaining these is part of completing a task,
not a follow-up to it.

## Where a learning goes

| What you learned | Where it goes |
|---|---|
| A convention this theme follows | the matching `.claude/rules/*.md` |
| A trap in Liquid, Shopify or the platform, generic to any theme | the matching rule, **and up to Base** — see CLAUDE.md, "Flowing changes back to Base" |
| How a specific section or snippet works | `docs/sections/` or `docs/snippets/` |
| A step in a procedure someone invokes | the matching `.claude/skills/*/SKILL.md` |
| A CSS or browser trap you had to **measure** to find — a cascade order, a layout feedback loop, a state that reports correctly and renders wrong | `.claude/references/*-pitfalls.md`, **and up to Base** |
| Something true only of this client's theme | that theme's rule copy, not Base |
| A fix that a rule, gate or check **should have prevented** | `/record-incident` → `docs/ai-workflow/incidents/`, committed, the moment it happens; then `/harvest` if it is generic |

**The incident comes first.** The rule paragraph is written from the incident,
not the other way round, and an incident recorded at the end of a build is an
incident not recorded: record it the moment it happens, as a committed file a
script can count and a pull request can show.

The line between a rule and a reference: a **rule** is what to do, is scoped by
a `paths` glob and is injected automatically. A **reference** is symptom, cause
and fix for a trap too situational to inject on every task — the first thing to
read when the symptom appears. Rules stay short because references exist.

## The one hard constraint

`.claude/` is canonical. `.cursor/rules/*.mdc`, `.cursor/rules/examples/`,
`.cursor/skills/`, `.cursor/agents/`, `.cursor/workflows/`,
`.cursor/references/` and `.cursor/hooks/` are **generated** by
`.claude/scripts/sync-ai-config.sh`, and so are the Codex copies:
`.agents/skills/`, `.codex/hooks/`, `.codex/agents/` and `AGENTS.md`. Edit the `.claude/` copy; the pre-commit
hook regenerates the mirror and stages it, so there is no command to remember
— and never edit under `.cursor/`.

Generated `.mdc` files carry a checksum, so a hand-edit there is detected and
the sync refuses to clobber it — but the skills and examples are plain copies
with no such protection and a hand-edit is simply lost.

**A merge conflict under `.cursor/` is never resolved by hand.** Two branches
that each edited a rule and regenerated its `.mdc` collide on the checksum
line every time; the `.md` merges cleanly, the mirror does not. Resolve the
`.md` if git asks, then run `sh .claude/scripts/sync-ai-config.sh` — it
detects conflict markers in a generated file and regenerates it — and stage
`.cursor/`.
