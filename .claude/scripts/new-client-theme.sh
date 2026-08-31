#!/bin/sh
# Start a new client theme from Base, keeping the link back to Base intact.
#
# Why this exists
# ---------------
# BarePerformanceNutritionRebuild was created by copying Base's files into a
# fresh repository. Its root commit is 9475a56; Base's is 0853346. They share no
# history, so there is no `git pull base development` — every Base improvement
# has to be reapplied by hand, forever, and every client fix that belongs
# upstream has to be retyped rather than cherry-picked.
#
# That is the mechanical reason nothing had ever flowed back to Base, and it
# cannot be retrofitted cheaply: merging unrelated histories after the fact
# conflicts on essentially every file.
#
# So the link is established at commit zero, here, or not at all.
#
# What you get
# ------------
#   origin  the client repo, your day-to-day remote
#   base    EcomExperts-io/Base, read-only upstream
#
# Then, forever after:
#   git fetch base && git merge base/development     # pull Base improvements down
#   git cherry-pick <sha>                            # send a generic fix up
#
# Usage, run from a Base clone:
#   sh .claude/scripts/new-client-theme.sh git@github.com:EcomExperts-io/<Repo>.git ../<Dir>

set -e

REMOTE="$1"
TARGET="$2"
# Overridable so the script can be exercised against a local clone in a test.
BASE_URL="${BASE_URL:-https://github.com/EcomExperts-io/Base.git}"

if [ -z "$REMOTE" ] || [ -z "$TARGET" ]; then
  echo "usage: sh .claude/scripts/new-client-theme.sh <client-repo-url> <target-dir>"
  echo "example: sh .claude/scripts/new-client-theme.sh git@github.com:EcomExperts-io/AcmeRebuild.git ../AcmeRebuild"
  exit 1
fi

if [ -e "$TARGET" ]; then
  echo "refusing: $TARGET already exists."
  exit 1
fi

echo "==> cloning Base into $TARGET (full history — this is the point)"
git clone --origin base "$BASE_URL" "$TARGET"
cd "$TARGET"

echo "==> pointing origin at the client repo, keeping base as upstream"
git remote add origin "$REMOTE"
git remote set-url --push base no-pushing-to-base

echo "==> creating the client's development branch from Base's"
git checkout -B development base/development

echo "==> activating the hooks"
git config core.hooksPath .githooks

cat <<'NEXT'

Done. Two remotes, real shared history:

    origin   your client repo   (push here)
    base     EcomExperts-io/Base (fetch only)

Before you build anything, in this order:

  1. npm install                       — installs deps and confirms hooks are on
  2. Confirm rule injection works. Open any .liquid file in Claude Code or
     Cursor and check the rules are actually in context. On Bites Vitamins the
     conventions sat where the tool could not read them for 18 days and nothing
     reported it.
  3. Confirm the hook BLOCKS. Add a section with no padding settings and try to
     commit it. If it commits, you inherited the file and not the protection.
  4. Do the measurement pass and write the answers into .claude/rules/sections.md
     in THIS repo. Base is deliberately generic; the fork is where the numbers
     live:
        - which container class the finished pages use, and its max-width
        - which breakpoint the majority of assets/section-*.css uses
        - the spacing constants the design actually repeats
     Grep for them. Do not copy a number out of Base.
  5. python3 .claude/scripts/report-compliance.py   — record the starting number
     so you can tell later whether you improved it or added to it.
  6. Create docs/mistake-log.md, empty. Add the first entry the first time
     review catches something. It has been asked for since build-page-from-figma
     was written and has never existed.

To pull Base improvements later:   git fetch base && git merge base/development
To send a generic fix upstream:    branch off base/development, cherry-pick, PR to Base

NEXT
