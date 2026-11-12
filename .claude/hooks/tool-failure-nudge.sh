#!/bin/sh
# PostToolUseFailure hook — when a Shopify command fails, notes it for the
# learning loop and adds one line of context pointing at /record-incident.
# Does not block; the Stop hook holds the turn once until it is answered.

INPUT=$(cat)
ROOT="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null)}"
[ -n "$ROOT" ] && cd "$ROOT" 2>/dev/null
printf '%s' "$INPUT" | python3 -c '
import json, os, subprocess, sys
d = json.load(sys.stdin)
cmd = (d.get("tool_input") or {}).get("command", "") or ""
err = str(d.get("tool_use_error", ""))[:400]
hit = ("shopify theme" in cmd) or ("Liquid error" in err) or ("theme check" in cmd) or ("500" in err and "shopify" in cmd)
if not hit:
    sys.exit(0)
if os.path.isfile(".claude/scripts/check-learnings.py"):
    subprocess.run([sys.executable, ".claude/scripts/check-learnings.py", "--signal", "shopify",
                    "a Shopify command failed: " + " ".join(cmd.split())[:160]], capture_output=True)
msg = ("A Shopify theme command just failed. If the cause is a trap a rule, gate or check of this repo should have "
       "caught (a Liquid pattern that 500s, a schema shape the upload rejects, a CLI/Node mismatch), run "
       "/record-incident now, while the details are in context, and show the developer the proposed change. "
       "If there is nothing to learn, dismiss it: python3 .claude/scripts/check-learnings.py --dismiss \"<why>\"")
print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUseFailure", "additionalContext": msg}}))
' 2>/dev/null
exit 0
