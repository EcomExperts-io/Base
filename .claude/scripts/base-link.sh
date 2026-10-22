#!/bin/sh
# Attach Base to a client repo — as a remote, as a worktree, and as a reference
# directory — whether or not the two share any git history.
#
# Usage, run anywhere inside the client repo:   sh .claude/scripts/base-link.sh
# Safe to re-run. Writes only: the remote, the worktree, .claude/.cache/base-link.json
#
# Notes:
#   * A worktree can check out any fetched ref, so `git worktree add <dir>
#     base/development` is a real Base checkout beside the client repo with no
#     merge attempted. /harvest edits and opens Base PRs from it.
#   * `claude --add-dir <that dir>` lets a session read Base as reference. Its
#     rules are NOT loaded from there; the client's own rule copies must win.
#   * The remote is what pull-base-tooling.py reads from and check-tooling-drift.py
#     compares against. Pushing to it is disabled so a stray `git push base`
#     cannot happen; /harvest pushes to Base's URL explicitly.

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
