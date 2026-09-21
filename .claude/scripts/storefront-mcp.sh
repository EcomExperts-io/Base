#!/bin/sh
# Talk to a store's Storefront MCP endpoint — the read-only catalog, policies
# and cart tools Shopify exposes on every store at /api/mcp, no auth required.
#
# Why this exists
# ---------------
# "No invented data" is a rule the review agents enforce after the fact. The
# check that prevents it is asking the store what it has before wiring a
# section to it: does any product carry this metafield, does the collection
# the homepage band links to have products, what are the shipping policies the
# footer should show. Storefront MCP answers those without admin credentials.
#
# A password-protected or development store exposes fewer tools (often only
# policies/FAQs); the tools/list call below says which are available.
#
# Usage:
#   storefront-mcp.sh <store-handle-or-domain> list
#   storefront-mcp.sh <store-handle-or-domain> call <tool> '<json-arguments>'
# Examples:
#   storefront-mcp.sh acme list
#   storefront-mcp.sh acme call search_shop_catalog '{"query":"vitamin","context":"recon"}'
#   storefront-mcp.sh acme call search_shop_policies_and_faqs '{"query":"shipping"}'

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
