#!/bin/sh
# PostToolUse hook — runs the mechanical gate on the one file Claude just wrote.
#
# Budget: under two seconds. Only python checks, only this file, no Theme Check
# (the CLI alone takes longer than that; it runs in the Stop hook instead).
# Never blocks — PostToolUse cannot — and never fails the tool call.
#
# Output: on a theme file, always one message — the findings, or one line
# naming the file, the checks run and "0 findings". On any other file, nothing.
# The repository is the one that holds the edited file, so a file in a git
# worktree is checked against that worktree, not against CLAUDE_PROJECT_DIR.

INPUT=$(cat)
FILE=$(printf '%s' "$INPUT" | python3 -c 'import json,sys
d=json.load(sys.stdin); print(d.get("tool_input",{}).get("file_path",""))' 2>/dev/null)
[ -n "$FILE" ] || exit 0

ROOT=""
case "$FILE" in
  /*) ROOT=$(git -C "$(dirname "$FILE")" rev-parse --show-toplevel 2>/dev/null) ;;
esac
[ -n "$ROOT" ] || ROOT="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null)}"
[ -n "$ROOT" ] || exit 0
cd "$ROOT" || exit 0

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

CHECKS="conventions"
add "$(python3 .claude/scripts/check-conventions.py --files "$REL" --quiet 2>&1)"
case "$REL" in
  sections/*.liquid)
    CHECKS="$CHECKS, section contract"
    add "$(python3 .claude/scripts/check-section-contract.py --files "$REL" --quiet 2>&1)" ;;
  templates/*.json|locales/*.json|config/*.json)
    CHECKS="$CHECKS, JSON validity"
    add "$(python3 .claude/scripts/check-json.py "$REL" --quiet 2>&1)" ;;
esac

if [ -z "$OUT" ]; then
  HEAD_LINE="Base gate ran on $REL ($CHECKS): 0 findings."
else
  HEAD_LINE="Base gate ran on $REL ($CHECKS). Fix errors now; warnings in a modified legacy file are reported, not required:"
fi

printf '%s\n%s' "$HEAD_LINE" "$OUT" | python3 -c 'import json,sys
ctx = sys.stdin.read().strip()[:6000]
print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": ctx}}))'
exit 0
