#!/bin/sh
# Attach Base to a client repo — as a remote, as a worktree, and as a reference
# directory — whether or not the two share any git history.
#
# Why this exists
# ---------------
# The audit of 14 Sep 2026 found that none of the four client forks could pull
# Base's tooling down or send a fix up: three had no `base` remote at all, and
# the one that did shared no common ancestor, so `git merge base/development`
# would conflict on every file. The forks were created by copying files into
# fresh repositories, and that cannot be repaired after the fact.
#
# It does not need repairing. Two things work without shared history:
#
#   * A WORKTREE can check out any fetched ref. `git worktree add <dir>
#     base/development` gives you a real Base checkout beside the client repo
#     — editable, branchable, pushable — with no merge ever attempted. That is
#     what /harvest edits and opens Base PRs from.
#   * `claude --add-dir <that dir>` lets a session read Base as reference
#     while working in the client. Its rules are NOT loaded from there; the
#     client's own rule copies carry the measured specifics and must win.
#
# The remote itself is what pull-base-tooling.py reads tooling from, and what
# check-tooling-drift.py compares against. Pushing to it is disabled here so a
# stray `git push base` cannot happen; /harvest pushes to Base's URL explicitly.
#
# Usage, run anywhere inside the client repo:   sh .claude/scripts/base-link.sh
# Safe to re-run. Writes only: the remote, the worktree, .claude/.cache/base-link.json

set -e
cd "$(git rev-parse --show-toplevel)"
BASE_URL="${BASE_URL:-https://github.com/EcomExperts-io/Base.git}"

if git remote get-url origin 2>/dev/null | grep -q "EcomExperts-io/Base"; then
  echo "This checkout is Base itself — nothing to link."
  exit 0
fi

echo "==> base remote"
if git remote get-url base >/dev/null 2>&1; then
  echo "    already present: $(git remote get-url base)"
else
  git remote add base "$BASE_URL"
  echo "    added base -> $BASE_URL"
fi
git remote set-url --push base no-pushing-to-base
git fetch --quiet --tags base development
echo "    fetched base/development ($(git rev-parse --short base/development))"

echo "==> worktree"
NAME=$(basename "$PWD")
WT="$(dirname "$PWD")/${NAME}-base"
if git worktree list --porcelain | grep -Fq "worktree $WT"; then
  echo "    already present: $WT"
elif [ -e "$WT" ]; then
  echo "    $WT exists but is not a worktree of this repo — leaving it alone."
  echo "    Move it aside and re-run, or set WT_DIR to another path."
else
  if git show-ref --verify --quiet refs/heads/base-tooling; then
    git worktree add "$WT" base-tooling
  else
    git worktree add -b base-tooling "$WT" base/development
  fi
  echo "    created $WT on branch base-tooling (tracks base/development)"
fi

mkdir -p .claude/.cache
printf '{\n  "worktree": "%s",\n  "remote": "base",\n  "url": "%s"\n}\n' "$WT" "$BASE_URL" > .claude/.cache/base-link.json

cat <<NEXT

Linked. From here:

  Pull Base's tooling into this repo (three-way: your local edits are kept):
      python3 .claude/scripts/pull-base-tooling.py

  See what has drifted either way:
      python3 .claude/scripts/check-tooling-drift.py

  Read Base as reference in a session, without loading its rules:
      claude --add-dir "$WT"

  Send a generic fix or rule up to Base from inside this repo:
      /harvest <incident-or-rule-file>     (edits and pushes from $WT)

The worktree is a full Base checkout. Keep it current with:
      git -C "$WT" pull --ff-only
NEXT
