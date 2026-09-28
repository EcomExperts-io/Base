#!/usr/bin/env python3
"""Pretty-print a Storefront MCP JSON-RPC response handed over in $RESP.

The companion of storefront-mcp.sh, which does the HTTP. Kept as a file rather
than an inline `python3 -c` because the quoting inside a shell script made the
first version unreadable and, once, syntactically wrong.
"""

import json
import os
import sys


def main():
    try:
        d = json.loads(os.environ.get("RESP", ""))
    except json.JSONDecodeError:
        print("storefront-mcp: the endpoint did not return JSON (password page? wrong host?)")
        return 1
    if "error" in d:
        print("error:", json.dumps(d["error"]))
        return 1
    r = d.get("result", {})
    if "tools" in r:
        for t in r["tools"]:
            desc = (t.get("description") or "").strip().splitlines()
            print(f"{t['name']:<36} {(desc[0] if desc else '')[:90]}")
        return 0
    for c in r.get("content", []):
        if c.get("type") == "text":
            txt = c["text"]
            try:
                print(json.dumps(json.loads(txt), indent=2)[:6000])
            except (json.JSONDecodeError, TypeError):
                print(txt[:6000])
    return 0


if __name__ == "__main__":
    sys.exit(main())
