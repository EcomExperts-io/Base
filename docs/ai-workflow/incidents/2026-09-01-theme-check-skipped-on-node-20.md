---
title: "Theme Check silently skipped on machines whose default Node was 20"
date: 2026-09-01
repo: Base
scope: generic
surfaced_by: ci
should_have_caught: .claude/scripts/check-theme-staged.py
status: harvested
---

# Theme Check silently skipped on machines whose default Node was 20

## What happened

The Shopify CLI imports `enableCompileCache` from `node:module`, which does not
exist before Node 22, so on a Node 20 machine the CLI dies at startup. The
pre-commit wrapper treats a CLI that cannot start as a skip — correctly, since
an environment problem must not block a commit — but a skip and a pass look
the same in a terminal. The team's default Node is 20 on most machines, with
24 installed under nvm and unused.

## How it surfaced

A CI draft on Node 20 went green by never having run the check. Locally,
nobody noticed the one-line skip message under the commit output.

## What fixed it

CI pins Node 22 and fails the job if the index is empty. `check-theme-staged.py`
now prepends the newest Node 22+ under `~/.nvm` when the PATH node is too old
and always prints which Node it ran on; `doctor.py` reports the mismatch with
the `nvm alias default` fix; the SessionStart hook prints it every session.

## Which rule or check should have caught it, and why it did not

The wrapper itself, by saying loudly what it could not do. A gate that cannot
be told apart from a skip is the failure the CI workflow was written to remove;
the same standard now applies locally.
