#!/bin/sh
# Render a URL at an exact viewport and save a PNG: a wrapper around render-screenshot.py with the old positional signature.
#
# Usage: render-screenshot.sh <url> <width> <height> <out.png> [wait-ms] [deadline-s]
#   CHROME_BIN overrides the binary. For a mobile viewport call render-screenshot.py directly with --mobile.

URL="$1"; W="$2"; H="$3"; OUT="$4"; WAIT="${5:-6000}"; DEADLINE="${6:-120}"
if [ -z "$URL" ] || [ -z "$W" ] || [ -z "$H" ] || [ -z "$OUT" ]; then
  echo "usage: render-screenshot.sh <url> <width> <height> <out.png> [wait-ms] [deadline-s]" >&2
  exit 2
fi

DIR=$(dirname "$0")
exec python3 "$DIR/render-screenshot.py" "$URL" "$W" "$H" "$OUT" \
  --wait-ms "$WAIT" --deadline "$DEADLINE"
