#!/bin/sh
# PostToolUse hook on Bash — after a `git push` in a client repo, adds one line
# of context pointing at /gitbot-preflight. Does not block; silent in Base,
# which GitBot does not review.

INPUT=$(cat)
ROOT="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null)}"
[ -n "$ROOT" ] || exit 0
cd "$ROOT" || exit 0
case "$(git remote get-url origin 2>/dev/null)" in *EcomExperts-io/Base*) exit 0 ;; esac

printf '%s' "$INPUT" | python3 -c '
import json, sys
d = json.load(sys.stdin)
cmd = (d.get("tool_input") or {}).get("command", "") or ""
if "git push" not in cmd or "--dry-run" in cmd:
    sys.exit(0)
msg = ("That push is being reviewed by GitBot — every push on every branch of a client repo is, and it posts in "
       "the repo Slack channel in one to two minutes. Read the findings from here with /gitbot-preflight "
       "(review, then get_findings) and settle each one, fix or flag, before the pull request.")
print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": msg}}))
' 2>/dev/null
exit 0
