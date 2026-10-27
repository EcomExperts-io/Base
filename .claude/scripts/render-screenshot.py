#!/usr/bin/env python3
"""Render a URL at an exact viewport and save a PNG, via the DevTools protocol. CHROME_BIN overrides the binary.

Notes:
- The viewport is set with Emulation.setDeviceMetricsOverride, never --window-size: macOS clamps a headless window
  to about 501px and the capture is then cropped from a page laid out at the wrong width.
- No dependencies on purpose: the small WebSocket client below is enough for CDP, and `websockets` or Playwright
  would put an install step in front of every fork.
- Exits non-zero and writes nothing when Chrome cannot start, the page's innerWidth is not the width asked for,
  or the image is blank. An image that never loaded is a warning on stderr; the file is still written.

Usage: render-screenshot.py <url> <width> <height> <out.png> [--wait-ms N] [--deadline S] [--mobile] [--scale N]
                            [--eval "<js>"] [--eval-settle-ms N]
  --eval runs JavaScript in the settled page before the capture, for states that exist only after an interaction
  (a drawer, a modal, an accordion opened).
"""

import base64
import hashlib
import json
import os
import re
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

CHROME_CANDIDATES = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
)


def find_chrome():
    if os.environ.get("CHROME_BIN"):
        return os.environ["CHROME_BIN"]
    for c in CHROME_CANDIDATES:
        if os.path.isabs(c):
            if os.access(c, os.X_OK):
                return c
        else:
            found = shutil.which(c)
            if found:
                return found
    return None


class WS:
    """The smallest WebSocket client that can carry CDP: text frames, no extensions, no continuation of sent messages.
    Server frames are reassembled: a screenshot arrives as megabytes of base64 split across frames."""

    def __init__(self, url, timeout=120):
        m = re.match(r"ws://([^:/]+):(\d+)(/.*)", url)
        if not m:
            raise ValueError(f"not a ws:// url: {url}")
        host, port, path = m.group(1), int(m.group(2)), m.group(3)
        self.sock = socket.create_connection((host, port), timeout=timeout)
        self.sock.settimeout(timeout)
        key = base64.b64encode(os.urandom(16)).decode()
        req = (
            f"GET {path} HTTP/1.1\r\nHost: {host}:{port}\r\n"
            f"Upgrade: websocket\r\nConnection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n"
        )
        self.sock.sendall(req.encode())
        buf = b""
        while b"\r\n\r\n" not in buf:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise ConnectionError("handshake closed early")
            buf += chunk
        expect = base64.b64encode(
            hashlib.sha1((key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()).digest()
        ).decode()
        if expect.encode() not in buf:
            raise ConnectionError("websocket handshake rejected")
        self._rest = buf.split(b"\r\n\r\n", 1)[1]
        self._next_id = 0

    def _recv(self, n):
        while len(self._rest) < n:
            chunk = self.sock.recv(65536)
            if not chunk:
                raise ConnectionError("socket closed")
            self._rest += chunk
        out, self._rest = self._rest[:n], self._rest[n:]
        return out

    def send(self, method, params=None):
        self._next_id += 1
        payload = json.dumps(
            {"id": self._next_id, "method": method, "params": params or {}}
        ).encode()
        header = bytearray([0x81])  # FIN + text
        n = len(payload)
        if n < 126:
            header.append(0x80 | n)
        elif n < 1 << 16:
            header.append(0x80 | 126)
            header += struct.pack(">H", n)
        else:
            header.append(0x80 | 127)
            header += struct.pack(">Q", n)
        mask = os.urandom(4)
        header += mask
        masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        self.sock.sendall(bytes(header) + masked)
        return self._next_id

    def recv(self):
        data = b""
        while True:
            b0, b1 = self._recv(2)
            fin, opcode = b0 & 0x80, b0 & 0x0F
            n = b1 & 0x7F
            if n == 126:
                n = struct.unpack(">H", self._recv(2))[0]
            elif n == 127:
                n = struct.unpack(">Q", self._recv(8))[0]
            data += self._recv(n)
            if opcode == 0x8:
                raise ConnectionError("server closed the websocket")
            if fin:
                break
        return json.loads(data)

    def call(self, method, params=None, timeout=120):
        want = self.send(method, params)
        end = time.time() + timeout
        while time.time() < end:
            msg = self.recv()
            if msg.get("id") == want:
                if "error" in msg:
                    raise RuntimeError(f"{method}: {msg['error']}")
                return msg.get("result", {})
        raise TimeoutError(method)

    def wait_event(self, name, timeout=60):
        end = time.time() + timeout
        while time.time() < end:
            try:
                msg = self.recv()
            except socket.timeout:
                return False
            if msg.get("method") == name:
                return True
        return False


def is_blank(png_bytes):
    """A render that painted nothing still writes a valid PNG, a wall of one grey, which diffs like a real result.
    Deliberately narrow: one single colour over the whole sample. Two colours means something painted, and a stricter
    test would reject a legitimately flat band."""
    try:
        import io

        from PIL import Image
    except ImportError:
        return False  # cannot tell; do not block on it
    im = Image.open(io.BytesIO(png_bytes)).convert("RGB")
    w, h = im.size
    seen = {
        im.getpixel((x, y))
        for y in range(0, h, max(1, h // 60))
        for x in range(0, w, max(1, w // 40))
    }
    return len(seen) <= 1


def main(argv):
    if len(argv) < 4:
        print(__doc__.strip().split("Usage:")[1].strip(), file=sys.stderr)
        return 2
    url, width, height, out = argv[0], int(argv[1]), int(argv[2]), argv[3]
    wait_ms = 6000
    deadline = 120
    mobile = "--mobile" in argv
    scale = 1
    eval_js = None
    eval_settle_ms = 1200
    for i, a in enumerate(argv):
        if a == "--wait-ms":
            wait_ms = int(argv[i + 1])
        elif a == "--deadline":
            deadline = int(argv[i + 1])
        elif a == "--scale":
            scale = int(argv[i + 1])
        elif a == "--eval":
            eval_js = argv[i + 1]
        elif a == "--eval-settle-ms":
            eval_settle_ms = int(argv[i + 1])

    chrome = find_chrome()
    if not chrome:
        print("render-screenshot: no Chrome/Chromium found. Set CHROME_BIN.", file=sys.stderr)
        return 1

    port = 0
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    profile = tempfile.mkdtemp()
    proc = subprocess.Popen(
        [
            chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars",
            "--no-first-run", "--no-default-browser-check", "--mute-audio",
            f"--user-data-dir={profile}", f"--remote-debugging-port={port}",
            "about:blank",
        ],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )

    ws = None
    try:
        target = None
        end = time.time() + 20
        while time.time() < end and target is None:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list", timeout=2) as r:
                    for t in json.load(r):
                        if t.get("type") == "page" and t.get("webSocketDebuggerUrl"):
                            target = t["webSocketDebuggerUrl"]
                            break
            except (urllib.error.URLError, socket.timeout, ConnectionError, json.JSONDecodeError):
                time.sleep(0.3)
        if not target:
            print("render-screenshot: Chrome never exposed a debugging target.", file=sys.stderr)
            return 1

        ws = WS(target, timeout=deadline)
        ws.call("Page.enable")
        ws.call("Runtime.enable")

        # The whole point: the viewport, not the window. The window manager
        # cannot overrule this.
        ws.call("Emulation.setDeviceMetricsOverride", {
            "width": width, "height": height,
            "deviceScaleFactor": scale, "mobile": mobile,
        })

        ws.call("Page.navigate", {"url": url})
        ws.wait_event("Page.loadEventFired", timeout=min(deadline, 60))
        time.sleep(wait_ms / 1000.0)

        def evaluate(expression):
            return ws.call("Runtime.evaluate", {
                "expression": expression, "returnByValue": True,
            })["result"].get("value")

        # `loading="lazy"` only fetches near the viewport, so captureBeyondViewport on a taller page writes holes where
        # images never painted. Stretch the viewport over the whole document first (Chrome's texture limit is the cap),
        # let the images land, then put it back.
        page_height = evaluate("String(document.documentElement.scrollHeight)")
        try:
            page_height = int(page_height)
        except (TypeError, ValueError):
            page_height = height
        reach = min(max(page_height, height), 16000)
        if reach > height:
            ws.call("Emulation.setDeviceMetricsOverride", {
                "width": width, "height": reach,
                "deviceScaleFactor": scale, "mobile": mobile,
            })

        # An image has painted once it has intrinsic dimensions. `complete` is not the test: a carousel that clones its
        # slides re-evaluates srcset on the clones and decoded images sit at complete === false indefinitely.
        # naturalWidth === 0 is "nothing there": still fetching if !complete, failed if complete.
        loading = None
        images_deadline = time.time() + min(deadline, 60)
        while time.time() < images_deadline:
            loading = evaluate(
                "String(Array.from(document.images)"
                ".filter(i => !i.complete && i.naturalWidth === 0).length)"
            )
            if loading in (None, "0"):
                break
            time.sleep(0.5)
        broken = evaluate(
            "String(Array.from(document.images)"
            ".filter(i => i.naturalWidth === 0).length)"
        )
        if broken not in (None, "0"):
            print(
                f"render-screenshot: {broken} image(s) have no pixels. The "
                "capture will have blank boxes where they belong — check "
                "whether that is the page or the network before diffing it.",
                file=sys.stderr,
            )

        if reach > height:
            ws.call("Emulation.setDeviceMetricsOverride", {
                "width": width, "height": height,
                "deviceScaleFactor": scale, "mobile": mobile,
            })
            time.sleep(0.4)

        # Put the page into the state being verified, now that the viewport is
        # the one the caller asked for — an overlay sized against the wrong
        # viewport would diff against the wrong design.
        if eval_js:
            result = ws.call("Runtime.evaluate", {
                "expression": eval_js,
                "returnByValue": True,
                "awaitPromise": True,
            })
            thrown = result.get("exceptionDetails")
            if thrown:
                text = thrown.get("exception", {}).get("description") or thrown.get("text")
                print(
                    f"render-screenshot: --eval threw: {text}. Refusing to write a "
                    "screenshot of a state that was never entered.",
                    file=sys.stderr,
                )
                return 1
            time.sleep(eval_settle_ms / 1000)

        # Assert the page agrees about its own width before trusting the pixels.
        got = ws.call("Runtime.evaluate", {
            "expression": "String(document.documentElement.clientWidth)",
            "returnByValue": True,
        })["result"].get("value")
        if got is None or int(got) != width:
            print(
                f"render-screenshot: asked for {width}px of layout, the page reports {got}px. "
                "Refusing to write a screenshot that would diff against the wrong design.",
                file=sys.stderr,
            )
            return 1

        shot = ws.call("Page.captureScreenshot", {
            "format": "png",
            "captureBeyondViewport": True,
            "clip": {"x": 0, "y": 0, "width": width, "height": height, "scale": scale},
        }, timeout=deadline)
        png = base64.b64decode(shot["data"])

        if is_blank(png):
            print(
                "render-screenshot: the capture is blank — the page had not painted. "
                "Raise --wait-ms and try again. Nothing written.",
                file=sys.stderr,
            )
            return 1

        os.makedirs(os.path.dirname(os.path.abspath(out)) or ".", exist_ok=True)
        with open(out, "wb") as fh:
            fh.write(png)
        print(f"rendered {out} {width}x{height} (layout confirmed at {got}px)")
        return 0
    finally:
        if ws:
            try:
                ws.sock.close()
            except OSError:
                pass
        proc.kill()
        proc.wait(timeout=10)
        shutil.rmtree(profile, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
