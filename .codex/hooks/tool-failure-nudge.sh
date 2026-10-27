#!/bin/sh
# PostToolUseFailure hook — when a Shopify command fails, adds one line of
# context pointing at /record-incident. Does not block.

INPUT=$(cat)
printf '%s' "$INPUT" | python3 -c '
import json, sys
d = json.load(sys.stdin)
cmd = (d.get("tool_input") or {}).get("command", "") or ""
err = str(d.get("tool_use_error", ""))[:400]
hit = ("shopify theme" in cmd) or ("Liquid error" in err) or ("theme check" in cmd) or ("500" in err and "shopify" in cmd)
if not hit:
    sys.exit(0)
msg = ("A Shopify theme command just failed. If the cause is a trap a rule, gate or check should have caught "
       "(a Liquid pattern that 500s, a schema shape the upload rejects, a CLI/Node mismatch), record it now with "
       "/record-incident while the details are in context — do not wait for the end of the build.")
print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUseFailure", "additionalContext": msg}}))
' 2>/dev/null
exit 0
