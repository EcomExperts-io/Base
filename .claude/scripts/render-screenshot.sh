#!/bin/sh
# Render a URL at an exact viewport and save a PNG.
#
# This is now a thin wrapper around render-screenshot.py, which drives Chrome
# over the DevTools protocol. Everything that already calls this script keeps
# working and gets the fix without changing its arguments.
#
# What the fix is. This script used to pass --window-size to headless Chrome.
# That is a *window* size and the window manager may overrule it: on macOS
# Chrome clamps the window to about 501px wide, lays the page out at 501, and
# then crops the screenshot to the width that was asked for. The image came out
# the right size with the wrong page inside it, nothing errored, and a
# homepage's worth of mobile diffs came back plausible and meaningless. See
# docs/ai-workflow/incidents/2026-09-16-headless-cannot-render-a-mobile-viewport.md
#
# Emulation.setDeviceMetricsOverride sets the viewport instead, which the
# window manager has no say in. The Python version also asks the page how wide
# it thinks it is and refuses to write a file when the answer is wrong, and
# refuses to write a blank capture — the other way this used to fail quietly.
#
# Usage: render-screenshot.sh <url> <width> <height> <out.png> [wait-ms] [deadline-s]
#
# CHROME_BIN overrides the binary. For a mobile viewport (touch, mobile UA)
# call render-screenshot.py directly with --mobile; this wrapper keeps the old
# positional signature.

URL="$1"; W="$2"; H="$3"; OUT="$4"; WAIT="${5:-6000}"; DEADLINE="${6:-120}"
if [ -z "$URL" ] || [ -z "$W" ] || [ -z "$H" ] || [ -z "$OUT" ]; then
  echo "usage: render-screenshot.sh <url> <width> <height> <out.png> [wait-ms] [deadline-s]" >&2
  exit 2
fi

DIR=$(dirname "$0")
exec python3 "$DIR/render-screenshot.py" "$URL" "$W" "$H" "$OUT" \
  --wait-ms "$WAIT" --deadline "$DEADLINE"
