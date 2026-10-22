#!/bin/sh
# PostToolUse hook — runs the mechanical gate on the one file Claude just wrote.
#
# Why this exists
# ---------------
# The pre-commit hook fires when a developer commits, which on an AI build is
# hours after the file was written and long after it left the model's context.
# The most-missed rules in this codebase (a section without padding settings,
# a bare English label, a max-width query) are all decidable the moment the
# file is saved. Returning the finding here puts it in front of the model while
# the file is still open, so it is fixed in the same turn rather than found in
# review — or never.
#
# Budget: under two seconds. Only python checks, only this file, no Theme Check
# (the CLI alone takes longer than that; it runs in the Stop hook instead).
# Never blocks — PostToolUse cannot — and never fails the tool call.

INPUT=$(cat)
ROOT="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null)}"
[ -n "$ROOT" ] || exit 0
cd "$ROOT" || exit 0

FILE=$(printf '%s' "$INPUT" | python3 -c 'import json,sys
d=json.load(sys.stdin); print(d.get("tool_input",{}).get("file_path",""))' 2>/dev/null)
[ -n "$FILE" ] || exit 0

case "$FILE" in
  "$ROOT"/*) REL=${FILE#"$ROOT"/} ;;
  /*) exit 0 ;;
  *) REL=$FILE ;;
esac
case "$REL" in
  sections/*|snippets/*|assets/*|layout/*|templates/*|locales/*|config/*|blocks/*) ;;
  *) exit 0 ;;
esac
[ -f "$REL" ] || exit 0

OUT=""
add() { [ -n "$1" ] && OUT="${OUT}${1}
"; }

add "$(python3 .claude/scripts/check-conventions.py --files "$REL" --quiet 2>&1)"
case "$REL" in
  sections/*.liquid) add "$(python3 .claude/scripts/check-section-contract.py --files "$REL" --quiet 2>&1)" ;;
  templates/*.json|locales/*.json|config/*.json) add "$(python3 .claude/scripts/check-json.py "$REL" --quiet 2>&1)" ;;
esac

[ -n "$OUT" ] || exit 0

printf '%s' "$OUT" | python3 -c 'import json,sys
ctx = sys.stdin.read()[:6000]
print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse",
  "additionalContext": "Base gate on the file you just edited (fix errors now; warnings in a modified legacy file are reported, not required):\n" + ctx}}))'
exit 0
