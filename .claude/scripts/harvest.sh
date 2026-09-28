#!/bin/sh
# The git mechanics of sending a generic learning up to Base from inside a
# client repo, without shared history and without copying files by hand.
#
# Why this exists
# ---------------
# CLAUDE.md said "branch off development here, make the change generic, open
# the PR". From a client repo that meant: find a Base checkout, remember which
# rule to edit, retype the paragraph, commit, push, open the PR, come back and
# mark the incident. Nobody did it during a build, so nothing flowed up until
# someone did it as a separate project. This makes the mechanics two commands
# around the one step that needs judgment (the edit itself):
#
#   harvest.sh start <slug>                         -> a branch in the Base worktree
#   ...edit the rule/reference in the worktree, commit there...
#   harvest.sh open <slug> "<title>" <body-file> [--no-pr]   -> push + PR
#
# The worktree is the one base-link.sh created (a checkout of base/development
# beside this repo). Pushing goes to Base's URL explicitly because the `base`
# remote has pushing disabled — a stray `git push base` must never happen, an
# explicit harvest push should.
#
# BASE_URL and BASE_REPO are overridable so the script can be exercised against
# a local bare clone in a test.

set -e
ROOT=$(git rev-parse --show-toplevel)
cd "$ROOT"
BASE_URL="${BASE_URL:-https://github.com/EcomExperts-io/Base.git}"
BASE_REPO="${BASE_REPO:-EcomExperts-io/Base}"
CLIENT=$(basename "$ROOT" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]/-/g')
CMD="$1"; SLUG="$2"

usage() {
  echo "usage: harvest.sh start <slug>"
  echo "       harvest.sh open <slug> \"<pr title>\" <body-file> [--no-pr]"
  exit 2
}
[ -n "$CMD" ] && [ -n "$SLUG" ] || usage
SLUG=$(printf '%s' "$SLUG" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]/-/g')
BRANCH="harvest/${CLIENT}-${SLUG}"

WT=$(python3 -c 'import json,sys
try: print(json.load(open(".claude/.cache/base-link.json"))["worktree"])
except Exception: print("")' 2>/dev/null)
if [ -z "$WT" ] || [ ! -d "$WT" ]; then
  echo "harvest: no Base worktree recorded. Run:  sh .claude/scripts/base-link.sh" >&2
  exit 1
fi

case "$CMD" in
  start)
    git fetch --quiet base development
    if [ -n "$(git -C "$WT" status --porcelain)" ]; then
      echo "harvest: the Base worktree at $WT has uncommitted changes — commit or discard them first." >&2
      exit 1
    fi
    git -C "$WT" checkout -q -B "$BRANCH" base/development
    echo "WORKTREE=$WT"
    echo "BRANCH=$BRANCH"
    echo ""
    echo "Edit the rule or reference under $WT, keep it generic (strip this client's"
    echo "numbers, keep the incident), then commit THERE. Base's own checks run on that"
    echo "commit through its pre-commit hook. Then:"
    echo "    sh .claude/scripts/harvest.sh open $SLUG \"<title>\" <body-file>"
    ;;
  open)
    TITLE="$3"; BODY="$4"; NOPR=0
    for a in "$@"; do [ "$a" = "--no-pr" ] && NOPR=1; done
    [ -n "$TITLE" ] && [ -r "$BODY" ] || usage
    CUR=$(git -C "$WT" rev-parse --abbrev-ref HEAD)
    if [ "$CUR" != "$BRANCH" ]; then
      echo "harvest: worktree is on $CUR, expected $BRANCH — run start first." >&2
      exit 1
    fi
    AHEAD=$(git -C "$WT" rev-list --count base/development..HEAD)
    if [ "$AHEAD" -eq 0 ]; then
      echo "harvest: nothing committed on $BRANCH beyond base/development." >&2
      exit 1
    fi
    if [ -n "$(git -C "$WT" status --porcelain)" ]; then
      echo "harvest: uncommitted changes in $WT — commit them first." >&2
      exit 1
    fi
    # Base's structural invariants, from inside Base — a harvest must not be the
    # commit that breaks the rule system it is trying to improve.
    (cd "$WT" && python3 .claude/scripts/check-ai-config.py) || exit 1
    git -C "$WT" push "$BASE_URL" "HEAD:refs/heads/$BRANCH"
    echo "pushed $BRANCH ($AHEAD commit(s)) to $BASE_URL"
    if [ "$NOPR" -eq 1 ]; then
      echo "--no-pr: not opening a pull request."
      exit 0
    fi
    if ! command -v gh >/dev/null 2>&1; then
      echo "harvest: gh is not installed — open the PR by hand: $BRANCH -> development on $BASE_REPO" >&2
      exit 1
    fi
    URL=$(gh pr create -R "$BASE_REPO" --base development --head "$BRANCH" --title "$TITLE" --body-file "$BODY")
    echo "PR_URL=$URL"
    ;;
  *) usage ;;
esac
