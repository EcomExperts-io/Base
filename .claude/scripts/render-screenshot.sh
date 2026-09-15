#!/bin/sh
# Render a URL at an exact viewport in headless Chrome and save a PNG.
#
# Why this exists
# ---------------
# "Check at 1440, not desktop-ish" was a rule nobody could follow mechanically:
# the browser tools return an image into the conversation, not a file, and
# without a file there is no pixel diff. Chrome's own headless mode renders at
# any window size and writes the PNG directly, with no install beyond the Chrome
# already on every developer machine. Height is the frame's height, so a
# full-page render lines up with the Figma export without scrolling.
#
# Chrome is run in the background and killed once the PNG exists (or after the
# deadline), because headless Chrome has been seen to write the screenshot and
# then never exit — the first version of this script hung a session on exactly
# that. macOS has no `timeout`, so the deadline is a poll loop here.
#
# Usage: render-screenshot.sh <url> <width> <height> <out.png> [wait-ms] [deadline-s]
#   wait-ms     virtual time budget for fonts and images (default 4000)
#   deadline-s  give up and kill Chrome after this many seconds (default 45)
#
# CHROME_BIN overrides the binary. Exit 1 if Chrome is missing or no PNG came out.

URL="$1"; W="$2"; H="$3"; OUT="$4"; WAIT="${5:-4000}"; DEADLINE="${6:-45}"
if [ -z "$URL" ] || [ -z "$W" ] || [ -z "$H" ] || [ -z "$OUT" ]; then
  echo "usage: render-screenshot.sh <url> <width> <height> <out.png> [wait-ms] [deadline-s]" >&2
  exit 2
fi

CHROME="${CHROME_BIN:-}"
for c in "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
         "$(command -v google-chrome 2>/dev/null)" \
         "$(command -v google-chrome-stable 2>/dev/null)" \
         "$(command -v chromium 2>/dev/null)" \
         "$(command -v chromium-browser 2>/dev/null)"; do
  [ -n "$CHROME" ] && break
  [ -n "$c" ] && [ -x "$c" ] && CHROME="$c"
done
if [ -z "$CHROME" ]; then
  echo "render-screenshot: no Chrome/Chromium found. Install Google Chrome or set CHROME_BIN." >&2
  echo "                   Fallback: take the screenshot with the browser tool and save it to $OUT." >&2
  exit 1
fi

mkdir -p "$(dirname "$OUT")"
rm -f "$OUT"
PROFILE=$(mktemp -d)
# A throwaway profile so this never collides with the Chrome the developer has open.
"$CHROME" --headless=new --disable-gpu --hide-scrollbars --no-first-run --no-default-browser-check \
  --user-data-dir="$PROFILE" --force-device-scale-factor=1 \
  --window-size="${W},${H}" --virtual-time-budget="$WAIT" \
  --screenshot="$OUT" "$URL" >/dev/null 2>&1 &
PID=$!

elapsed=0
while [ "$elapsed" -lt "$DEADLINE" ]; do
  if [ -s "$OUT" ]; then
    # The PNG is written whole at the end of the render; give Chrome a moment to
    # close the file on its own, then stop waiting for a process that may never exit.
    sleep 1
    break
  fi
  if ! kill -0 "$PID" 2>/dev/null; then
    break
  fi
  sleep 1
  elapsed=$((elapsed + 1))
done
kill "$PID" 2>/dev/null; pkill -P "$PID" 2>/dev/null; wait "$PID" 2>/dev/null
rm -rf "$PROFILE"

if [ ! -s "$OUT" ]; then
  echo "render-screenshot: Chrome produced no image for $URL within ${DEADLINE}s" >&2
  exit 1
fi
if command -v python3 >/dev/null 2>&1; then
  python3 - "$OUT" <<'PY' 2>/dev/null || echo "rendered $OUT"
import sys
try:
    from PIL import Image
    im = Image.open(sys.argv[1])
    print(f"rendered {sys.argv[1]} {im.width}x{im.height}")
except Exception:
    print(f"rendered {sys.argv[1]}")
PY
else
  echo "rendered $OUT"
fi
