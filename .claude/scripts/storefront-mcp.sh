#!/bin/sh
# Talk to a store's Storefront MCP endpoint: the read-only catalog, policies and cart tools at /api/mcp, no auth.
#
# Usage:
#   storefront-mcp.sh <store-handle-or-domain> list
#   storefront-mcp.sh <store-handle-or-domain> call <tool> '<json-arguments>'
#   e.g. storefront-mcp.sh acme call search_shop_catalog '{"query":"vitamin","context":"recon"}'
#
# Note: a password-protected or development store exposes fewer tools (often only policies/FAQs); `list` says which.

STORE="$1"; CMD="$2"; TOOL="$3"; ARGS="${4:-{\}}"
if [ -z "$STORE" ] || [ -z "$CMD" ]; then
  echo "usage: storefront-mcp.sh <store> list | call <tool> '<json>'" >&2
  exit 2
fi
case "$STORE" in
  *.*) HOST="$STORE" ;;
  *) HOST="${STORE}.myshopify.com" ;;
esac
URL="https://${HOST}/api/mcp"

case "$CMD" in
  list)
    BODY='{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
    ;;
  call)
    [ -n "$TOOL" ] || { echo "call needs a tool name" >&2; exit 2; }
    BODY=$(printf '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"%s","arguments":%s}}' "$TOOL" "$ARGS")
    ;;
  *) echo "unknown command $CMD" >&2; exit 2 ;;
esac

RESP=$(curl -sS --max-time 30 -X POST "$URL" -H 'content-type: application/json' -d "$BODY") || {
  echo "storefront-mcp: request to $URL failed" >&2
  exit 1
}
if command -v python3 >/dev/null 2>&1; then
  RESP="$RESP" python3 "$(dirname "$0")/storefront-mcp.py"
else
  printf '%s\n' "$RESP"
fi
