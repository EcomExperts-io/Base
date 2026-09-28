#!/bin/sh
# PostToolUseFailure hook — when a Shopify command fails, ask whether a rule
# should have prevented it.
#
# Why this exists
# ---------------
# Every incident that later became a rule in this repo first surfaced as a
# failing command: a theme upload 500ing on a two-step range, a template
# rendering a `t:` key, Theme Check dying on Node 20. None was recorded at the
# time — the mistake log the workflow asked for existed in zero client repos.
# The moment of failure is the only moment the details are all in context, so
# this is where the nudge goes. It adds one line of context; it does not block.

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
