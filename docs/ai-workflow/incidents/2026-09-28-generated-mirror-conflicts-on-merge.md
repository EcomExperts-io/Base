---
title: "The v2 pull request's only merge conflict was in a generated Cursor mirror file"
date: 2026-09-28
repo: Base
scope: generic
surfaced_by: ci
should_have_caught: .claude/scripts/sync-ai-config.sh
status: harvested
---

# The v2 pull request's only merge conflict was in a generated Cursor mirror file

## What happened

PR #58 (`feature/ai-workflow-v2` → `development`) went CONFLICTING after
`development` gained five commits. The one conflicted file was
`.cursor/rules/schemas.mdc`. v2 had added mobile padding to
`.claude/rules/schemas.md`; PR #59 had added the 50-block limit. The `.md`
merged cleanly with both hunks. Each side had regenerated the `.mdc`, whose
banner carries a checksum of its own content, so the two mirrors differed on
that line and git could not merge them — a conflict in a file nobody edits.

## How it surfaced

GitHub's conflict badge on the pull request, two weeks after it was opened,
which delayed the merge by a further week while the reason was assumed to be
in real code.

## What fixed it

Merge `development` in, regenerate the mirror from `.claude/` with
`sync-ai-config.sh --force`, stage `.cursor/`. The script's checksum guard had
read the conflict markers as a hand edit and refused without `--force`, which
is one more thing to know at the worst moment.

## Which rule or check should have caught it, and why it did not

`multi-session-rebuild.md` already said "any generated mirror — never
hand-merge it; regenerate" — but only in a workflow file read during a
rebuild, and the sync script did not know a conflicted file from an edited
one. Now: the script regenerates a file containing conflict markers without
`--force`, and `living-documents.md` (the rule that loads when `.cursor/` is
touched) says the resolution outright. The underlying cost — a generated tree
committed to git — stays until the team's move off Cursor is complete, by
decision of 15 Sep 2026.
