#!/bin/sh
# Render a URL at an exact viewport and save a PNG.
#
# Usage: render-screenshot.sh <url> <width> <height> <out.png> [wait-ms] [deadline-s]
#
# Notes:
#   * Thin wrapper around render-screenshot.py (Chrome over the DevTools protocol)
#     keeping the old positional signature. CHROME_BIN overrides the binary. For a
#     mobile viewport (touch, mobile UA) call render-screenshot.py directly with --mobile.
#   * The viewport is set with Emulation.setDeviceMetricsOverride, never --window-size:
#     a window size is a hint the window manager may clamp (macOS clamps headless
#     Chrome to about 501px), and the screenshot is then cropped from a page laid
#     out at the wrong width.

URL="$1"; W="$2"; H="$3"; OUT="$4"; WAIT="${5:-6000}"; DEADLINE="${6:-120}"
if [ -z "$URL" ] || [ -z "$W" ] || [ -z "$H" ] || [ -z "$OUT" ]; then
  echo "usage: render-screenshot.sh <url> <width> <height> <out.png> [wait-ms] [deadline-s]" >&2
  exit 2
fi

DIR=$(dirname "$0")
exec python3 "$DIR/render-screenshot.py" "$URL" "$W" "$H" "$OUT" \
  --wait-ms "$WAIT" --deadline "$DEADLINE"
