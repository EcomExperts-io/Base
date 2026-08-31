---
description: Keeping the documentation that guides this work — docs/, .claude/rules, skills, agents and workflows — correct as you learn, without being asked
paths:
  - "docs/**"
  - ".claude/**"
  - ".cursor/**"
  - "CLAUDE.md"
---

# Living Documents

## What this replaced, and why

This rule used to be called `prompts-and-references.md`. It was **always-apply**
— injected into every task on every file type — and it was entirely about
`.cursor/prompts/` and `.cursor/references/`. Two problems with that:

- Those two directories hold **one file each in Base and do not exist at all in
  a client fork**, so in a client theme the rule spent its always-apply budget
  describing paths that were not there.
- It referred to "the Horizon theme". This is Base.

The principle underneath it is worth keeping. The scope was wrong. It now
applies to the documentation that actually guides the work, and only when you
are in it.

## The principle

The files in `docs/`, `.claude/rules/`, `.claude/skills/`, `.claude/agents/`,
`.claude/workflows/` and `CLAUDE.md` are **living documents**. They describe
what we currently believe is correct, which means they are wrong the moment
something is learned and not written down.

- Update them as new cases are encountered.
- When you discover a pattern, edge case, or solution while working an issue,
  fix the relevant file in the same change.
- If something in them does not work as described, correct it immediately
  rather than working around it.
- Add examples from real implementations. This codebase's rules are written
  incident-first — "30 of 31 sections shipped without…" — because a rule with
  the failure attached gets followed and a rule without one gets skimmed.
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
| Something true only of this client's theme | that theme's rule copy, not Base |

## The one hard constraint

`.claude/` is canonical. `.cursor/rules/*.mdc`, `.cursor/rules/examples/`,
`.cursor/skills/`, `.cursor/agents/` and `.cursor/workflows/` are **generated**
by `.claude/scripts/sync-ai-config.sh`. Edit the `.claude/` copy and run the
script; never edit under `.cursor/`.

Generated `.mdc` files carry a checksum, so a hand-edit there is detected and
the sync refuses to clobber it — but the skills and examples are plain copies
with no such protection and a hand-edit is simply lost.

Two hand-maintained copies is how the Bites Vitamins conventions ended up
somewhere Claude Code could not read them for the first 18 days of the build.
