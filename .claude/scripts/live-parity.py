#!/usr/bin/env python3
"""live-parity.py — compare a section (or a page) on LIVE against OURS, pixel for pixel, in headless Chrome.

Why this exists
---------------
When the brief is "match the live site", the reference is a storefront, not a
Figma frame: it moves, it lazy-loads, it has popups and a preview cookie that
can make "live" render our own theme. Base's verify skill compared a frame PNG
against a render; this compares two renders of the same page, section by
section, with every trap the Pique rebuild fell into closed below. Ported from
Pique's landing-page workspace (Oct 2026), where it took 21 batches of pages to
0%. The verify-against-reference skill carries the copy-paste examples.

Laptop rules are built in: one live+ours Chrome pair per run, reused for every
width, loaded one after the other; at most LIVE_PARITY_SLOTS (default 2) runs
on the machine, a third waits and says so; both Chromes are closed when the run
ends, on Ctrl-C and on SIGTERM too.

Subcommands (every one writes report.json + report.md + PNGs into --out):
  section      section box, element inventory (boxes + computed styles, paired live<->ours), pixel diff per width
  regress      `section`, but the "live" side is the QA-approved main theme (--main-theme <id>)
  page         every top-level .shopify-section: top/height per side, first divergence, full-page diff
  states       replay steps (hover/click/scroll/wait/press/eval) on both sides, then compare the section
  hoverstyles  force :hover / :focus-visible / :active on every interactive element, compare the deltas
  motion       sample properties every N ms after a trigger on both sides; --keyframes dumps @keyframes

Guarantees (each one is a trap somebody fell into; see render-screenshot.py and the incidents it cites):
  * the viewport is set with Emulation.setDeviceMetricsOverride (never --window-size); the page's own
    innerWidth/clientWidth must equal the requested width or that width is refused;
  * each side runs in its OWN Chrome with its OWN --user-data-dir, and the theme each side rendered is
    read from Shopify.theme and asserted (a leaked preview cookie makes live render our theme);
  * lazy media is forced (loading=eager, lazysizes unveil, stepped scroll driven from Python), fonts and
    images are waited for, images that never load are recorded;
  * fixed/sticky overlays outside the section are hidden (preview bar, chat, popups) unless --keep-fixed;
  * animations are finished/paused, carousels stopped and reset, videos paused at t=0 (--freeze);
  * ours is shifted so its section top has the same sub-pixel fraction as live's (--align-fraction);
  * each side is captured twice and self-diffed, so motion that the freeze did not stop is reported;
  * it exits non-zero with a message instead of writing a plausible wrong result.
"""

import argparse
import base64
import collections
import datetime
import difflib
import fcntl
import hashlib
import io
import json
import math
import os
import re
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import threading
import time
import traceback
import urllib.error
import urllib.parse
import urllib.request

try:
    from PIL import Image, ImageChops, ImageDraw
except ImportError:  # pragma: no cover
    print("live-parity: Pillow is required (python3 -m pip install --user pillow)", file=sys.stderr)
    sys.exit(2)



def _repo_root():
    r = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else os.getcwd()


# Run slots live under the repo's cache so every session on this checkout
# shares the same cap (the laptop overheats past three browsers).
SLOTS_DIR = os.path.join(_repo_root(), ".claude", ".cache", "parity-slots")
# Our development theme's id: from --ours-theme, else the preview_theme_id in
# --ours-url, else "any" (the theme assertion is then off on our side — say so).
DEV_THEME_ID = None
DEFAULT_WIDTHS = "320,375,393,640,641,749,750,768,1024,1199,1200,1440,1920"
CHROME_MAJOR = "154"
UA_DESKTOP = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
              f"Chrome/{CHROME_MAJOR}.0.0.0 Safari/537.36")
UA_MOBILE = ("Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) "
             f"Chrome/{CHROME_MAJOR}.0.0.0 Mobile Safari/537.36")
CHROME_CANDIDATES = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "google-chrome", "google-chrome-stable", "chromium", "chromium-browser",
)

# Exit codes — a caller can tell "the tool failed" (>= 2) from "the tool ran" (0).
EXIT_OK, EXIT_DIFF, EXIT_USAGE, EXIT_CHROME, EXIT_SELECTOR, EXIT_VIEWPORT, EXIT_THEME, EXIT_BLANK, EXIT_NAV, \
    EXIT_WIDTH_ERRORS, EXIT_INTERNAL = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10


class Fatal(Exception):
    """Stops the whole run: nothing trustworthy can be produced (wrong theme, selector absent, no Chrome)."""

    def __init__(self, msg, code=EXIT_INTERNAL):
        super().__init__(msg)
        self.code = code


class WidthError(Exception):
    """Refuses one width (wrong viewport, blank capture); other widths still run; exit is non-zero."""

    def __init__(self, msg, code=EXIT_WIDTH_ERRORS):
        super().__init__(msg)
        self.code = code


LOG_LOCK = threading.Lock()
QUIET = False


def log(*parts):
    if QUIET:
        return
    with LOG_LOCK:
        print("[live-parity %s]" % time.strftime("%H:%M:%S"), *parts, file=sys.stderr, flush=True)


# ----------------------------------------------------------------------------------------------------------------
# CDP client (adapted from REPO/.claude/scripts/render-screenshot.py). Differences: frames are parsed only once
# complete, so a socket timeout never desynchronises the stream; events are buffered, not dropped.
# ----------------------------------------------------------------------------------------------------------------
class CDP:
    def __init__(self, ws_url, timeout=60):
        m = re.match(r"ws://([^:/]+):(\d+)(/.*)", ws_url)
        if not m:
            raise ValueError(f"not a ws:// url: {ws_url}")
        host, port, path = m.group(1), int(m.group(2)), m.group(3)
        self.sock = socket.create_connection((host, port), timeout=timeout)
        key = base64.b64encode(os.urandom(16)).decode()
        req = (f"GET {path} HTTP/1.1\r\nHost: {host}:{port}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
               f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n")
        self.sock.sendall(req.encode())
        buf = b""
        while b"\r\n\r\n" not in buf:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise ConnectionError("websocket handshake closed early")
            buf += chunk
        expect = base64.b64encode(hashlib.sha1((key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()).digest())
        if expect not in buf:
            raise ConnectionError("websocket handshake rejected")
        self._rest = bytearray(buf.split(b"\r\n\r\n", 1)[1])
        self._frag = None
        self._next_id = 0
        self.events = collections.deque(maxlen=20000)

    def close(self):
        try:
            self.sock.close()
        except OSError:
            pass

    def _send_frame(self, opcode, payload):
        header = bytearray([0x80 | opcode])
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

    def send(self, method, params=None):
        self._next_id += 1
        payload = json.dumps({"id": self._next_id, "method": method, "params": params or {}}).encode()
        self._send_frame(0x1, payload)
        return self._next_id

    def _parse(self):
        buf = self._rest
        if len(buf) < 2:
            return None
        b0, b1 = buf[0], buf[1]
        n, off = b1 & 0x7F, 2
        if n == 126:
            if len(buf) < 4:
                return None
            n, off = struct.unpack(">H", bytes(buf[2:4]))[0], 4
        elif n == 127:
            if len(buf) < 10:
                return None
            n, off = struct.unpack(">Q", bytes(buf[2:10]))[0], 10
        mask = None
        if b1 & 0x80:
            if len(buf) < off + 4:
                return None
            mask, off = bytes(buf[off:off + 4]), off + 4
        if len(buf) < off + n:
            return None
        payload = bytes(buf[off:off + n])
        del buf[:off + n]
        if mask:
            payload = bytes(c ^ mask[i % 4] for i, c in enumerate(payload))
        return b0 & 0x80, b0 & 0x0F, payload

    def _recv_msg(self, deadline):
        while True:
            fr = self._parse()
            if fr is None:
                remaining = deadline - time.time()
                if remaining <= 0:
                    raise socket.timeout("cdp recv deadline")
                self.sock.settimeout(remaining)
                chunk = self.sock.recv(1 << 20)
                if not chunk:
                    raise ConnectionError("Chrome closed the DevTools socket")
                self._rest += chunk
                continue
            fin, op, payload = fr
            if op == 0x9:
                self._send_frame(0xA, payload)
                continue
            if op == 0xA:
                continue
            if op == 0x8:
                raise ConnectionError("Chrome closed the DevTools websocket")
            if op in (0x1, 0x2):
                self._frag = bytearray(payload)
            elif op == 0x0 and self._frag is not None:
                self._frag += payload
            if fin and self._frag is not None:
                data, self._frag = bytes(self._frag), None
                return json.loads(data)

    def call(self, method, params=None, timeout=60):
        want = self.send(method, params)
        deadline = time.time() + timeout
        while True:
            try:
                msg = self._recv_msg(deadline)
            except socket.timeout:
                raise TimeoutError(f"CDP {method} gave no answer in {timeout}s")
            if msg.get("id") == want:
                if "error" in msg:
                    raise RuntimeError(f"CDP {method}: {msg['error'].get('message')} {msg['error'].get('data', '')}")
                return msg.get("result", {})
            if "method" in msg:
                self.events.append(msg)

    def wait_event(self, name, timeout=30, pred=None):
        for m in list(self.events):
            if m.get("method") == name and (pred is None or pred(m.get("params", {}))):
                self.events.remove(m)
                return m.get("params", {})
        deadline = time.time() + timeout
        while True:
            try:
                msg = self._recv_msg(deadline)
            except socket.timeout:
                return None
            if msg.get("method") == name and (pred is None or pred(msg.get("params", {}))):
                return msg.get("params", {})
            if "method" in msg:
                self.events.append(msg)

    def pump(self, seconds):
        """Read (and buffer) events for `seconds` — the socket must be drained while we sleep."""
        deadline = time.time() + seconds
        while True:
            try:
                msg = self._recv_msg(deadline)
            except socket.timeout:
                return
            if "method" in msg:
                self.events.append(msg)


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


# ----------------------------------------------------------------------------------------------------------------
# Concurrency guard: agents share one laptop. Each run holds one slot; at most LP_PARITY_SLOTS (default 2) runs at once.
# ----------------------------------------------------------------------------------------------------------------
class Slot:
    def __init__(self, n=None):
        self.n = n or int(os.environ.get("LIVE_PARITY_SLOTS", "2"))
        self.fh = None

    def __enter__(self):
        d = SLOTS_DIR
        os.makedirs(d, exist_ok=True)
        waited = 0
        while True:
            for i in range(self.n):
                fh = open(os.path.join(d, f"slot-{i}.lock"), "w")
                try:
                    fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    fh.write(f"{os.getpid()} {time.ctime()}\n")
                    fh.flush()
                    self.fh = fh
                    if waited:
                        log(f"got run slot {i} after {waited}s")
                    return self
                except OSError:
                    fh.close()
            if waited % 30 == 0:
                log(f"all {self.n} run slots busy (other agents are comparing); waiting…")
            time.sleep(3)
            waited += 3

    def __exit__(self, *exc):
        if self.fh:
            try:
                fcntl.flock(self.fh, fcntl.LOCK_UN)
                self.fh.close()
            except OSError:
                pass


OPEN_BROWSERS = set()


def close_all_browsers(*_):
    for b in list(OPEN_BROWSERS):
        try:
            b.close()
        except Exception:
            pass


def _on_signal(signum, frame):
    close_all_browsers()
    sys.exit(128 + signum)


class Browser:
    """One headless Chrome with its own profile — one per side, so the preview cookie cannot leak. The same pair
    serves every width of a run (the laptop overheated when every width started new processes)."""

    def __init__(self, label):
        self.chrome = find_chrome()
        if not self.chrome:
            raise Fatal("no Chrome/Chromium found; set CHROME_BIN", EXIT_CHROME)
        self.profile = tempfile.mkdtemp(prefix=f"lpp-{label}-")
        self.cdp = None
        self.proc = None
        self.version = None
        OPEN_BROWSERS.add(self)
        self._start()

    def _stop_process(self):
        try:
            if self.cdp:
                self.cdp.close()
        except Exception:
            pass
        self.cdp = None
        if self.proc and self.proc.poll() is None:
            try:
                os.killpg(self.proc.pid, 9)  # the whole group: renderer/GPU/network helpers too
            except OSError:
                try:
                    self.proc.kill()
                except OSError:
                    pass
            try:
                self.proc.wait(timeout=15)
            except Exception:
                pass

    def _start(self):
        chrome = self.chrome
        try:
            os.remove(os.path.join(self.profile, "DevToolsActivePort"))
        except OSError:
            pass
        args = [
            chrome, "--headless=new", "--remote-debugging-port=0", f"--user-data-dir={self.profile}",
            "--no-first-run", "--no-default-browser-check", "--hide-scrollbars", "--mute-audio", "--disable-gpu",
            "--force-color-profile=srgb", "--disable-background-timer-throttling", "--disable-renderer-backgrounding",
            "--disable-backgrounding-occluded-windows", "--disable-component-update", "--disable-sync",
            "--disable-default-apps", "--disable-extensions", "--lang=en-US", "--accept-lang=en-US",
            "--disable-features=Translate,OptimizationHints,MediaRouter,DialMediaRouteProvider,PaintHolding",
            "--window-size=1920,1200", "about:blank",
        ]
        self.proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        port_file = os.path.join(self.profile, "DevToolsActivePort")
        port = None
        end = time.time() + 30
        while time.time() < end:
            if os.path.exists(port_file):
                try:
                    port = int(open(port_file).read().split()[0])
                    break
                except (ValueError, IndexError, OSError):
                    pass
            if self.proc.poll() is not None:
                break
            time.sleep(0.1)
        if not port:
            self._stop_process()
            raise Fatal("Chrome did not start (no DevToolsActivePort)", EXIT_CHROME)
        target = None
        end = time.time() + 20
        while time.time() < end and not target:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list", timeout=3) as r:
                    for t in json.load(r):
                        if t.get("type") == "page" and t.get("webSocketDebuggerUrl"):
                            target = t["webSocketDebuggerUrl"]
                            break
            except (urllib.error.URLError, socket.timeout, ConnectionError, json.JSONDecodeError):
                time.sleep(0.3)
        if not target:
            self._stop_process()
            raise Fatal("Chrome never exposed a page target", EXIT_CHROME)
        self.cdp = CDP(target, timeout=60)
        # Batch 0: nothing a page fires may reach the store's cart, discount or marketing endpoints (same block as Batch 15):
        # every run, both sides. A page can apply its discount code on load.
        try:
            self.cdp.call("Network.enable")
            self.cdp.call("Network.setBlockedURLs", {"urls": [
                "*/cart/add*", "*/cart/update*", "*/cart/change*", "*/cart/clear*", "*/checkout*", "*/discount/*", "*kmail-lists.com*",
                "*klaviyo.com/client*", "*google-analytics.com*", "*analytics.google.com*", "*googleadservices.com*", "*doubleclick.net*",
                "*facebook.com/tr*", "*connect.facebook.net*", "*criteo*", "*elevar*", "*googletagmanager.com*"]})
        except Exception:
            pass
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=3) as r:
                self.version = json.load(r).get("Browser")
        except Exception:
            pass

    def close(self):
        self._stop_process()
        shutil.rmtree(self.profile, ignore_errors=True)
        OPEN_BROWSERS.discard(self)


# ----------------------------------------------------------------------------------------------------------------
# In-page library. Runs in an ISOLATED world (pristine built-ins; the page cannot break or see it). Page-JS
# objects (Swiper instances, jQuery, Shopify.theme) are reached with small main-world snippets instead.
# ----------------------------------------------------------------------------------------------------------------
JS_LIB = r"""
(() => {
  const norm = (s) => (s || '').replace(/[\u200B-\u200D\uFEFF\u00AD]/g, '').replace(/\u00A0/g, ' ').replace(/\s+/g, ' ').trim();
  const r3 = (n) => Math.round(n * 1000) / 1000;
  const SKIP = new Set(['SCRIPT','STYLE','TEMPLATE','NOSCRIPT','LINK','META','HEAD','TITLE','BR','WBR','SOURCE','TRACK','PARAM','COL','COLGROUP']);
  const STRUCT = new Set(['H1','H2','H3','H4','H5','H6','P','LI','A','BUTTON','LABEL','SUMMARY','DT','DD','FIGCAPTION','BLOCKQUOTE','TD','TH','LEGEND','CAPTION','OPTION']);
  const MEDIA = new Set(['IMG','VIDEO','SVG','INPUT','TEXTAREA','SELECT','IFRAME','CANVAS','OBJECT','EMBED']);
  const INTERACTIVE = 'a[href], button, summary, [role="button"], [role="tab"], input, select, textarea, label[for], [tabindex]:not([tabindex="-1"]), .swiper-button-next, .swiper-button-prev, .slick-arrow, .flickity-prev-next-button, [class*="arrow"]';
  const own = (el) => { let s = ''; for (const n of el.childNodes) if (n.nodeType === 3) s += n.nodeValue; return norm(s); };
  const four = (a, b, c, d) => (a === b && b === c && c === d) ? a : (a === c && b === d) ? a + ' ' + b : (b === d) ? a + ' ' + b + ' ' + c : [a, b, c, d].join(' ');
  const col = (c) => (c === 'rgba(0, 0, 0, 0)' ? 'transparent' : c);
  const border = (cs) => four(...['Top','Right','Bottom','Left'].map((s) => {
    const st = cs['border' + s + 'Style'], w = cs['border' + s + 'Width'];
    return (st === 'none' || st === 'hidden' || parseFloat(w) === 0) ? 'none' : w + ' ' + st + ' ' + col(cs['border' + s + 'Color']);
  }));
  const srcKey = (u) => {
    if (!u) return '';
    try { u = new URL(u, location.href).pathname; } catch (e) {}
    let b = u.split('/').pop() || '';
    b = decodeURIComponent(b).toLowerCase();
    b = b.replace(/_(\d+x\d*|x\d+|\d+x|pico|icon|thumb|small|compact|medium|large|grande|original|master)(?=[._@])/g, '');
    b = b.replace(/@\dx(?=\.)/, '').replace(/_crop_[a-z]+/, '');
    return b;
  };
  const textLines = (el) => {
    const rects = [];
    const tw = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    const rg = document.createRange();
    for (let n = tw.nextNode(); n; n = tw.nextNode()) {
      if (!n.nodeValue.trim()) continue;
      rg.selectNodeContents(n);
      for (const r of rg.getClientRects()) if (r.width > 0.5 && r.height > 0.5) rects.push([r.top, r.bottom]);
    }
    rects.sort((a, b) => a[0] - b[0]);
    let lines = 0, bottom = -1e9;
    for (const [t, b] of rects) { if (t >= bottom - 1) { lines++; bottom = b; } else bottom = Math.max(bottom, b); }
    return lines;
  };
  const effOpacity = (el) => { let o = 1; for (let a = el; a && a.nodeType === 1; a = a.parentElement) { o *= parseFloat(getComputedStyle(a).opacity); if (o === 0) return 0; } return r3(o); };
  const clipped = (el, r, root) => {
    for (let a = el.parentElement; a && a !== document.documentElement; a = a.parentElement) {
      const cs = getComputedStyle(a);
      if (cs.overflowX !== 'visible' || cs.overflowY !== 'visible' || (cs.clipPath && cs.clipPath !== 'none')) {
        const ar = a.getBoundingClientRect();
        const ox = cs.overflowX !== 'visible', oy = cs.overflowY !== 'visible';
        if ((ox && (r.right <= ar.left + 0.5 || r.left >= ar.right - 0.5)) || (oy && (r.bottom <= ar.top + 0.5 || r.top >= ar.bottom - 0.5))) return true;
      }
      if (a === root) break;
    }
    return false;
  };
  // Chrome 154 reports letter-spacing as authored ('-1%', 'normal'); ours may say '-0.36px' for the same thing.
  const lspx = (cs) => {
    const v = cs.letterSpacing;
    if (v === 'normal') return '0px';
    if (v.endsWith('%')) return r3(parseFloat(v) * parseFloat(cs.fontSize) / 100) + 'px';
    if (v.endsWith('em')) return r3(parseFloat(v) * parseFloat(cs.fontSize)) + 'px';
    return r3(parseFloat(v)) + 'px';
  };
  const styleOf = (el, cs, kind) => {
    const s = {
      'font-family': norm(cs.fontFamily.split(',')[0].replace(/["']/g, '')).toLowerCase(),
      'font-size': cs.fontSize, 'line-height': cs.lineHeight, 'font-weight': cs.fontWeight, 'font-style': cs.fontStyle,
      'letter-spacing': lspx(cs), 'color': col(cs.color), 'text-transform': cs.textTransform,
      'text-align': cs.textAlign, 'text-decoration-line': cs.textDecorationLine,
      'background-color': col(cs.backgroundColor), 'border': border(cs),
      'border-radius': four(cs.borderTopLeftRadius, cs.borderTopRightRadius, cs.borderBottomRightRadius, cs.borderBottomLeftRadius),
      'opacity': cs.opacity, 'box-shadow': cs.boxShadow,
      'padding': four(cs.paddingTop, cs.paddingRight, cs.paddingBottom, cs.paddingLeft),
      'margin': four(cs.marginTop, cs.marginRight, cs.marginBottom, cs.marginLeft),
      'gap': (cs.rowGap === cs.columnGap ? cs.rowGap : cs.rowGap + ' ' + cs.columnGap), 'display': cs.display,
    };
    if (kind === 'media' || kind === 'bg') { s['object-fit'] = cs.objectFit; s['object-position'] = cs.objectPosition; }
    if (cs.backgroundImage && cs.backgroundImage !== 'none') {
      s['background-image'] = cs.backgroundImage.replace(/url\(["']?([^"')]+)["']?\)/g, (m, u) => 'url(' + srcKey(u) + ')');
      s['background-size'] = cs.backgroundSize; s['background-position'] = cs.backgroundPosition;
    }
    return s;
  };
  const lib = {};
  lib.find = (sel) => {
    let all;
    try { all = document.querySelectorAll(sel); } catch (e) { return { error: 'bad-selector', message: String(e) }; }
    if (!all.length) {
      const near = Array.from(document.querySelectorAll('.shopify-section, [id^="shopify-section"]')).map((e) => e.id).filter(Boolean);
      return { error: 'not-found', count: 0, sections: near.slice(0, 80) };
    }
    const el = all[0];
    const r = el.getBoundingClientRect();
    const cs = getComputedStyle(el);
    return { count: all.length, id: el.id, tag: el.tagName.toLowerCase(), cls: String(el.className || '').slice(0, 120),
             x: r.left + scrollX, y: r.top + scrollY, w: r.width, h: r.height, display: cs.display, visibility: cs.visibility,
             rendered: el.getClientRects().length > 0 && r.width > 0 && r.height > 0,
             scrollY: scrollY, scrollX: scrollX, innerWidth: innerWidth, innerHeight: innerHeight,
             clientWidth: document.documentElement.clientWidth, docHeight: document.documentElement.scrollHeight };
  };
  lib.viewport = () => ({ innerWidth, innerHeight, clientWidth: document.documentElement.clientWidth,
    scale: (window.visualViewport ? visualViewport.scale : 1), dpr: devicePixelRatio,
    scrollWidth: document.documentElement.scrollWidth, docHeight: document.documentElement.scrollHeight,
    ua: navigator.userAgent, mobileMq: matchMedia('(pointer: coarse)').matches });
  lib.eager = () => {
    let n = 0;
    for (const el of document.querySelectorAll('img[loading="lazy"], iframe[loading="lazy"]')) { el.loading = 'eager'; n++; }
    return n;
  };
  lib.images = (sel) => {
    const root = sel ? document.querySelector(sel) : null;
    const scope = root || document;
    const imgs = Array.from(scope.querySelectorAll('img'));
    const pending = imgs.filter((i) => !i.complete && i.naturalWidth === 0 && (i.currentSrc || i.src));
    const broken = imgs.filter((i) => i.complete && i.naturalWidth === 0 && (i.currentSrc || i.src) && !/^data:/.test(i.currentSrc || i.src));
    const partial = imgs.filter((i) => !i.complete && i.naturalWidth > 0);
    return { total: imgs.length, pending: pending.length, partial: partial.length,
             broken: broken.map((i) => (i.currentSrc || i.src).slice(0, 200)),
             pendingSrc: pending.slice(0, 10).map((i) => (i.currentSrc || i.src).slice(0, 200)) };
  };
  lib.fonts = () => {
    const faces = [];
    document.fonts.forEach((f) => faces.push({ family: f.family.replace(/["']/g, ''), weight: f.weight, style: f.style, status: f.status }));
    return { status: document.fonts.status, faces };
  };
  lib.hideOverlays = (sel, keepFixed, pageMode) => {
    if (!document.getElementById('lpp-hide-style')) {
      const st = document.createElement('style');
      st.id = 'lpp-hide-style';
      st.textContent = '[data-lpp-hidden]{visibility:hidden!important;opacity:0!important;pointer-events:none!important;}';
      (document.head || document.documentElement).appendChild(st);
    }
    const root = sel ? document.querySelector(sel) : null;
    const KNOWN = ['#preview-bar-iframe', '#PBarNextFrameWrapper', 'iframe[src*="preview_bar"]', '#admin-bar-iframe',
      '#shopify-pc__banner', '#shopify-pc__prefs', '#gorgias-chat-container', '#chat-button', '#dummy-chat-button-iframe',
      '#attentive_overlay', '#attentive_creative', '.needsclick[class*="kl-private"]', 'div[class*="kl-private-reset"]',
      '[id^="alia-"]', '[class^="alia-"]', '#onetrust-consent-sdk', '.cc-window', '#launcher', '#hubspot-messages-iframe-container',
      'iframe[title*="chat" i]', 'iframe[id*="chat" i]', '#okendo-reviews-modal', '.okeReviews-reviewsModal'];
    const hidden = [];
    const mark = (el, why) => {
      if (el.hasAttribute('data-lpp-hidden')) return;
      if (root && (el === root || el.contains(root) || root.contains(el))) return;
      el.setAttribute('data-lpp-hidden', why);
      hidden.push({ why, tag: el.tagName.toLowerCase(), id: el.id || '', cls: String(el.className && el.className.baseVal !== undefined ? el.className.baseVal : el.className || '').slice(0, 80) });
    };
    for (const s of KNOWN) { try { document.querySelectorAll(s).forEach((el) => mark(el, 'known')); } catch (e) {} }
    if (!keepFixed) {
      for (const el of document.body ? document.body.querySelectorAll('*') : []) {
        const p = getComputedStyle(el).position;
        if (pageMode) {
          // full page: keep sticky (in flow) and fixed bars at the top (announcement, header); hide the rest
          if (p === 'fixed') { const r = el.getBoundingClientRect(); if (!(r.top <= 150 && r.height > 0 && r.height <= 250 && r.width >= 0.8 * innerWidth)) mark(el, p); }
          continue;
        }
        if (p === 'fixed' || p === 'sticky') mark(el, p);
      }
      for (const el of document.documentElement.children) {
        if (el !== document.body && el !== document.head) { const p = getComputedStyle(el).position; if (p === 'fixed' || p === 'sticky') mark(el, p); }
      }
    }
    const b = getComputedStyle(document.body);
    return { hidden, count: hidden.length, bodyPosition: b.position, bodyOverflow: b.overflow, htmlOverflow: getComputedStyle(document.documentElement).overflow };
  };
  lib.finishAnimations = () => {
    let finished = 0, paused = 0, failed = 0;
    for (const a of document.getAnimations()) {
      try {
        const t = a.effect && a.effect.getComputedTiming ? a.effect.getComputedTiming() : null;
        if (t && isFinite(t.endTime)) { a.finish(); finished++; }
        else { a.pause(); a.currentTime = 0; paused++; }
      } catch (e) { failed++; }
    }
    return { finished, paused, failed };
  };
  lib.inventory = (sel, opts) => {
    opts = opts || {};
    const root = document.querySelector(sel);
    if (!root) return { error: 'not-found' };
    const rr = root.getBoundingClientRect();
    const out = [];
    const counts = { hidden: 0, clipped: 0, transparent: 0 };
    const all = [root, ...root.querySelectorAll('*')];
    let idx = 0;
    for (const el of all) {
      el.removeAttribute('data-lpp-i');
      const tag = el.tagName.toUpperCase();
      if (SKIP.has(tag)) continue;
      if (el.closest('svg') && tag !== 'SVG') continue;
      if (tag === 'SVG' && el.parentElement && el.parentElement.closest('svg')) continue;
      const rects = el.getClientRects();
      if (!rects.length) continue;
      const r = el.getBoundingClientRect();
      if (r.width === 0 && r.height === 0) continue;
      const cs = getComputedStyle(el);
      const ownT = own(el);
      let kind = null;
      if (el === root) kind = 'root';
      else if (MEDIA.has(tag)) kind = 'media';
      else if (ownT || (STRUCT.has(tag) && norm(el.textContent))) kind = 'text';
      else if (cs.backgroundImage && cs.backgroundImage !== 'none' && /url\(/.test(cs.backgroundImage)) kind = 'bg';
      else if (col(cs.backgroundColor) !== 'transparent' || border(cs) !== 'none' || cs.boxShadow !== 'none') kind = 'box';
      if (!kind) continue;
      let vis = 'visible';
      if (cs.visibility !== 'visible') vis = 'hidden';
      else if (el !== root && clipped(el, r, root)) vis = 'clipped';
      else if (effOpacity(el) === 0) vis = 'transparent';
      if (vis !== 'visible') { counts[vis]++; if (!opts.keepInvisible) continue; }
      const text = kind === 'media' ? '' : norm(el.innerText !== undefined && kind !== 'root' ? el.innerText : el.textContent).slice(0, 300);
      const rec = {
        i: idx, kind, tag: tag.toLowerCase(), id: el.id || '', cls: String(el.getAttribute('class') || '').trim().split(/\s+/).slice(0, 4).join('.'),
        text: kind === 'root' ? '' : text, own: ownT.slice(0, 300), vis,
        box: { x: r3(r.left - rr.left), y: r3(r.top - rr.top), w: r3(r.width), h: r3(r.height) },
        style: styleOf(el, cs, kind), lpBlock: el.getAttribute('data-lp-block') || undefined,
        interactive: el.matches(INTERACTIVE) || undefined,
      };
      if (kind === 'text') rec.lines = textLines(el);
      if (kind === 'media') {
        let src = '';
        if (tag === 'IMG') { src = el.currentSrc || el.src; rec.natural = [el.naturalWidth, el.naturalHeight]; rec.complete = el.complete; rec.alt = el.getAttribute('alt'); }
        else if (tag === 'VIDEO') { src = el.currentSrc || el.src || (el.querySelector('source') || {}).src || ''; rec.poster = srcKey(el.poster); rec.video = { paused: el.paused, t: r3(el.currentTime), ready: el.readyState, muted: el.muted, loop: el.loop, autoplay: el.autoplay }; }
        else if (tag === 'IFRAME') src = el.src;
        else if (tag === 'SVG') { const u = el.querySelector('use'); src = u ? (u.getAttribute('href') || u.getAttribute('xlink:href') || '') : ('svg:' + (el.getAttribute('viewBox') || '') + ':' + el.querySelectorAll('path,circle,rect,polygon,line,polyline,ellipse').length); }
        else if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') src = (el.type || tag) + ':' + (el.name || '') + ':' + (el.placeholder || '');
        rec.src = (src || '').slice(0, 300);
        rec.srcKey = tag === 'SVG' || tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' ? rec.src : srcKey(src);
      }
      if (kind === 'bg') rec.srcKey = (rec.style['background-image'] || '').slice(0, 200);
      if (opts.imageSelector) { try { rec.imgSel = el.matches(opts.imageSelector) || undefined; } catch (e) {} }
      el.setAttribute('data-lpp-i', String(idx));
      out.push(rec);
      idx++;
    }
    const ov = { top: 0, bottom: 0, left: 0, right: 0 };
    for (const e of out) { if (e.vis !== 'visible' || e.kind === 'root') continue; const b = e.box;
      ov.top = Math.max(ov.top, -b.y); ov.left = Math.max(ov.left, -b.x);
      ov.bottom = Math.max(ov.bottom, b.y + b.h - rr.height); ov.right = Math.max(ov.right, b.x + b.w - rr.width); }
    for (const k in ov) ov[k] = r3(ov[k]);
    return { root: { x: rr.left + scrollX, y: rr.top + scrollY, w: rr.width, h: rr.height }, elements: out, counts, scrollY, scrollX, overflow: ov };
  };
  lib.sections = () => {
    const out = [];
    for (const el of document.querySelectorAll('.shopify-section, [id^="shopify-section-"]')) {
      if (el.parentElement && el.parentElement.closest('.shopify-section, [id^="shopify-section-"]')) continue;
      const r = el.getBoundingClientRect();
      const id = el.id || '';
      const m = id.match(/__([^_].*)$/);
      const key = m ? m[1] : id.replace(/^shopify-section-/, '');
      const cs = getComputedStyle(el);
      out.push({ id, key, top: r3(r.top + scrollY), height: r3(r.height), left: r3(r.left), width: r3(r.width),
                 display: cs.display, rendered: el.getClientRects().length > 0 && r.height > 0,
                 text: norm(el.innerText || '').slice(0, 80) });
    }
    return out;
  };
  lib.shift = (px) => {
    const html = document.documentElement;
    if (html.dataset.lppBasePad === undefined) html.dataset.lppBasePad = String(parseFloat(getComputedStyle(html).paddingTop) || 0);
    html.style.paddingTop = (parseFloat(html.dataset.lppBasePad) + px) + 'px';
    return parseFloat(getComputedStyle(html).paddingTop);
  };
  window.__lpp = lib;
  return 'ok';
})()
"""

# Main-world snippets: they need the page's own JS objects.
JS_THEME = r"""(() => {
  const t = (window.Shopify && window.Shopify.theme) || null;
  const a = document.querySelector('link[href*="/cdn/shop/t/"], script[src*="/cdn/shop/t/"]');
  const u = a ? (a.href || a.src) : '';
  const m = u.match(/\/cdn\/shop\/t\/(\d+)\//);
  let status = null;
  try { const n = performance.getEntriesByType('navigation')[0]; status = n ? n.responseStatus : null; } catch (e) {}
  return { theme: t ? { id: String(t.id), name: t.name, role: t.role, schema: t.schema_name } : null,
           assetPath: m ? 't/' + m[1] : null, url: location.href, status, title: document.title };
})()"""

JS_UNVEIL = r"""(() => {
  let n = 0;
  try { if (window.lazySizes && lazySizes.loader) { document.querySelectorAll('.lazyload, .lazypreload').forEach((el) => { lazySizes.loader.unveil(el); n++; }); } } catch (e) {}
  return n;
})()"""

JS_FREEZE = r"""((reset) => {
  const out = { swiper: 0, swiperAutoplayStopped: 0, slick: 0, flickity: 0, splide: 0, videos: 0, videoPlayBlocked: false, errors: [] };
  for (const el of document.querySelectorAll('.swiper, .swiper-container, swiper-container, [class*="swiper"]')) {
    const s = el.swiper;
    if (!s || s.__lppFrozen) continue;
    s.__lppFrozen = true; out.swiper++;
    try { if (s.autoplay && (s.autoplay.running || (s.params && s.params.autoplay && s.params.autoplay.enabled))) { s.autoplay.stop(); out.swiperAutoplayStopped++; } } catch (e) { out.errors.push('swiper-autoplay ' + e); }
    if (reset) { try { if (s.params && s.params.loop && s.slideToLoop) s.slideToLoop(0, 0, false); else s.slideTo(0, 0, false); } catch (e) { out.errors.push('swiper-reset ' + e); } }
  }
  const $ = window.jQuery || window.$;
  if ($ && $.fn && $.fn.slick) {
    $('.slick-initialized').each(function () { try { $(this).slick('slickPause'); if (reset) $(this).slick('slickGoTo', 0, true); out.slick++; } catch (e) { out.errors.push('slick ' + e); } });
  }
  if (window.Flickity && Flickity.data) {
    for (const el of document.querySelectorAll('.flickity-enabled')) {
      const f = Flickity.data(el);
      if (!f) continue;
      try { if (f.player && f.player.stop) f.player.stop(); else if (f.stopPlayer) f.stopPlayer(); if (reset) f.select(0, false, true); out.flickity++; } catch (e) { out.errors.push('flickity ' + e); }
    }
  }
  if (window.Splide) {
    for (const el of document.querySelectorAll('.splide.is-initialized')) { try { const sp = el.splide; if (sp) { sp.Components.Autoplay && sp.Components.Autoplay.pause(); if (reset) sp.go(0); out.splide++; } } catch (e) {} }
  }
  for (const v of document.querySelectorAll('video')) {
    try { v.pause(); if (v.readyState >= 1 && v.currentTime !== 0) v.currentTime = 0; out.videos++; } catch (e) { out.errors.push('video ' + e); }
  }
  if (!HTMLMediaElement.prototype.__lppPlay) {
    HTMLMediaElement.prototype.__lppPlay = HTMLMediaElement.prototype.play;
    HTMLMediaElement.prototype.play = function () { return Promise.resolve(); };
    out.videoPlayBlocked = true;
  }
  return out;
})"""

JS_LIB2 = r"""
(() => {
  const lib = window.__lpp;
  const norm = (s) => (s || '').replace(/[​-‍﻿­]/g, '').replace(/ /g, ' ').replace(/\s+/g, ' ').trim();
  const r3 = (n) => Math.round(n * 1000) / 1000;
  const four = (a, b, c, d) => (a === b && b === c && c === d) ? a : [a, b, c, d].join(' ');
  const col = (c) => (c === 'rgba(0, 0, 0, 0)' ? 'transparent' : c);
  const INTER = 'a[href], button, summary, [role="button"], [role="tab"], [role="link"], input:not([type="hidden"]), select, textarea, label[for], [tabindex]:not([tabindex="-1"]), .swiper-button-next, .swiper-button-prev, .slick-arrow, .flickity-prev-next-button';
  const HPROPS = ['color', 'background-color', 'background-image', 'opacity', 'transform', 'box-shadow', 'text-decoration-line',
    'text-decoration-color', 'text-underline-offset', 'filter', 'width', 'height', 'outline-style', 'outline-width',
    'outline-color', 'outline-offset', 'fill', 'stroke', 'letter-spacing', 'font-weight', 'scale', 'translate'];
  const TPROPS = ['transition-property', 'transition-duration', 'transition-timing-function', 'transition-delay',
    'animation-name', 'animation-duration', 'animation-timing-function', 'animation-iteration-count', 'animation-delay'];
  const bord = (cs) => four(...['Top','Right','Bottom','Left'].map((s) => { const st = cs['border' + s + 'Style'], w = cs['border' + s + 'Width']; return (st === 'none' || parseFloat(w) === 0) ? 'none' : w + ' ' + st + ' ' + col(cs['border' + s + 'Color']); }));
  const hs = (el) => { const cs = getComputedStyle(el); const o = {}; for (const p of HPROPS) o[p] = col(cs.getPropertyValue(p)); o.border = bord(cs);
    // an outline or decoration that does not paint has no width/colour worth comparing
    if (o['outline-style'] === 'none') { o['outline-width'] = o['outline-color'] = o['outline-offset'] = '(no outline)'; }
    if (o['text-decoration-line'] === 'none') { o['text-decoration-color'] = o['text-underline-offset'] = '(no decoration)'; }
    return o; };
  const ts = (el) => { const cs = getComputedStyle(el); const o = {}; for (const p of TPROPS) o[p] = cs.getPropertyValue(p); return o; };
  const recOf = (el, rr, i) => { const r = el.getBoundingClientRect(); const t = norm(el.innerText || el.textContent || '');
    return { i, tag: el.tagName.toLowerCase(), cls: String(el.getAttribute('class') || '').trim().split(/\s+/).slice(0, 3).join('.'),
      text: t.slice(0, 200), own: t.slice(0, 200), aria: el.getAttribute('aria-label') || '', kind: t ? 'text' : 'media',
      srcKey: (el.getAttribute('aria-label') || el.getAttribute('title') || (String(el.className).match(/next|prev/) || [''])[0]),
      box: { x: r3(r.left - rr.left), y: r3(r.top - rr.top), w: r3(r.width), h: r3(r.height) } }; };
  lib.interactives = (sel) => {
    const root = document.querySelector(sel);
    if (!root) return { error: 'not-found' };
    const rr = root.getBoundingClientRect();
    const out = [];
    document.querySelectorAll('[data-lpp-h]').forEach((e) => e.removeAttribute('data-lpp-h'));
    let i = 0;
    for (const el of root.querySelectorAll(INTER)) {
      if (!el.getClientRects().length) continue;
      const r = el.getBoundingClientRect();
      if (r.width === 0 || r.height === 0 || getComputedStyle(el).visibility !== 'visible') continue;
      el.setAttribute('data-lpp-h', String(i));
      const rec = recOf(el, rr, i);
      rec.transition = ts(el);
      out.push(rec);
      i++;
    }
    return { elements: out };
  };
  lib.hread = (i, finish) => {
    const el = document.querySelector('[data-lpp-h="' + i + '"]');
    if (!el) return null;
    void document.body.offsetWidth; getComputedStyle(el).color;
    if (finish) for (const a of document.getAnimations()) { try { const t = a.effect && a.effect.getComputedTiming(); if (t && isFinite(t.endTime)) a.finish(); } catch (e) {} }
    const o = { self: hs(el) };
    const kids = Array.from(el.querySelectorAll('*')).filter((k) => k.getClientRects().length && !k.closest('svg *')).slice(0, 12);
    kids.forEach((k, j) => { o[k.tagName.toLowerCase() + '#' + j] = hs(k); });
    return o;
  };
  // motion
  const MP = (cs, el, rr, p) => {
    if (p === 'y') return r3(el.getBoundingClientRect().top - rr.top);
    if (p === 'x') return r3(el.getBoundingClientRect().left - rr.left);
    if (p === 'h') return r3(el.getBoundingClientRect().height);
    if (p === 'w') return r3(el.getBoundingClientRect().width);
    if (p === 'scrollLeft') return el.scrollLeft;
    if (p === 'scrollTop') return el.scrollTop;
    return cs.getPropertyValue(p);
  };
  lib.motionTargets = (sel, explicit) => {
    const root = document.querySelector(sel);
    if (!root) return { error: 'not-found' };
    const rr = root.getBoundingClientRect();
    document.querySelectorAll('[data-lpp-m]').forEach((e) => e.removeAttribute('data-lpp-m'));
    let els = [];
    if (explicit && explicit.length) { for (const s of explicit) { const e = root.querySelector(s) || document.querySelector(s); els.push(e); } }
    else {
      for (const el of [root, ...root.querySelectorAll('*')]) {
        if (el.closest('svg') && el.tagName.toLowerCase() !== 'svg') continue;
        const cs = getComputedStyle(el);
        const td = cs.transitionDuration.split(',').some((v) => parseFloat(v) > 0);
        const an = cs.animationName && cs.animationName !== 'none';
        if ((td || an) && el.getClientRects().length) els.push(el);
        if (els.length >= 40) break;
      }
    }
    const out = [];
    els.forEach((el, i) => { if (!el) { out.push(null); return; } el.setAttribute('data-lpp-m', String(i)); const rec = recOf(el, rr, i); rec.transition = ts(el); out.push(rec); });
    return { elements: out };
  };
  lib.sampleStart = (sel, props, intervalMs, durationMs) => {
    const root = document.querySelector(sel);
    const els = Array.from(document.querySelectorAll('[data-lpp-m]'));
    const S = { t0: performance.now(), samples: [], anims: [], done: false };
    window.__lppS = S;
    const seen = new WeakSet();
    let last = -1e9;
    const tick = () => {
      const now = performance.now();
      if (now - S.t0 > durationMs) { S.done = true; return; }
      for (const el of els) {
        for (const a of el.getAnimations()) {
          if (seen.has(a)) continue;
          seen.add(a);
          const t = a.effect ? a.effect.getComputedTiming() : {};
          S.anims.push({ target: el.getAttribute('data-lpp-m'), kind: a.constructor.name,
            what: a.transitionProperty || a.animationName || a.id || '', duration: t.duration, delay: t.delay,
            easing: t.easing, iterations: t.iterations, direction: t.direction, fill: t.fill, seenAt: r3(now - S.t0) });
        }
      }
      if (now - last >= intervalMs - 1) {
        last = now;
        const rr = (root || document.body).getBoundingClientRect();
        const row = { t: r3(now - S.t0), v: {} };
        for (const el of els) { const cs = getComputedStyle(el); const o = {}; for (const p of props) o[p] = MP(cs, el, rr, p); row.v[el.getAttribute('data-lpp-m')] = o; }
        S.samples.push(row);
      }
      requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
    return true;
  };
  lib.sampleRead = () => { const S = window.__lppS; return S ? { done: S.done, samples: S.samples, anims: S.anims } : null; };
  lib.keyframes = (sel) => {
    const root = document.querySelector(sel);
    const names = new Set();
    if (root) for (const el of [root, ...root.querySelectorAll('*')]) { const n = getComputedStyle(el).animationName; if (n && n !== 'none') n.split(',').forEach((x) => names.add(x.trim())); }
    const found = {}, blocked = [];
    const walk = (rules, href) => { for (const r of rules) { if (r.type === 7 && names.has(r.name)) found[r.name] = { css: r.cssText, sheet: href }; else if (r.cssRules) { try { walk(r.cssRules, href); } catch (e) {} } } };
    for (const sh of document.styleSheets) { try { walk(sh.cssRules, sh.href || 'inline'); } catch (e) { if (sh.href) blocked.push(sh.href); } }
    return { names: Array.from(names), found, blocked };
  };
  return 'ok2';
})()
"""

JS_VIDEOS_SETTLED = r"""(() => Array.from(document.querySelectorAll('video')).filter((v) => v.seeking).length)()"""


# ----------------------------------------------------------------------------------------------------------------
# One side (live or ours) = one Chrome.
# ----------------------------------------------------------------------------------------------------------------
class Side:
    def __init__(self, name, url, sel, expect, args):
        self.name, self.url, self.sel, self.expect, self.args = name, url, sel, expect, args
        self.browser = Browser(name)
        self._attach()
        self.loads = 0
        self.ctx = None
        self.width = self.height = None
        self.notes = []

    def close(self):
        self.browser.close()

    def _attach(self):
        self.cdp = self.browser.cdp
        self.cdp.call("Page.enable")
        self.cdp.call("Runtime.enable")
        self.cdp.call("Page.setLifecycleEventsEnabled", {"enabled": True})
        # the Alia promo popup mounts late and paints over whatever is captured: hide it from the first frame, both sides
        self.cdp.call("Page.addScriptToEvaluateOnNewDocument", {"source": (
            "(()=>{const st=document.createElement('style');st.textContent='[id^=\"alia-root\"]{display:none!important}';"
            "(document.head||document.documentElement).appendChild(st);})()")})

    def fresh(self):
        """Before every load after the first: blank document, no site cookies/storage, and Blink's memory cache
        purged (critical memory-pressure signal). Blink prefers a higher-density srcset candidate it already holds
        in memory, so without the purge a 390px render after a 1440px one shows the 1440px image (measured: 600w
        instead of 400w, 0.643% instead of 0.0%). The HTTP disk cache stays warm."""
        if self.loads:
            self.cdp.call("Page.navigate", {"url": "about:blank"})
            self.cdp.wait_event("Page.loadEventFired", timeout=10)
            u = urllib.parse.urlsplit(self.url)
            try:
                self.cdp.call("Storage.clearDataForOrigin", {"origin": f"{u.scheme}://{u.netloc}", "storageTypes":
                              "cookies,local_storage,session_storage,indexeddb,websql,service_workers,cache_storage"})
            except RuntimeError:
                pass
            self.cdp.call("Memory.simulatePressureNotification", {"level": "critical"})
            self.cdp.pump(0.3)
        self.loads += 1
        self.ctx = None

    # -- evaluation ----------------------------------------------------------------------------------------------
    def ev(self, expr, world="iso", timeout=60):
        params = {"expression": expr, "returnByValue": True}
        if world == "iso":
            if self.ctx is None:
                self._make_world()
            params["contextId"] = self.ctx
        r = self.cdp.call("Runtime.evaluate", params, timeout=timeout)
        if r.get("exceptionDetails"):
            d = r["exceptionDetails"]
            text = (d.get("exception") or {}).get("description") or d.get("text")
            if world == "iso" and "Cannot find context" in str(text):
                self.ctx = None
            raise RuntimeError(f"[{self.name}] page JS threw: {str(text)[:400]}")
        return r.get("result", {}).get("value")

    def lib(self, call, timeout=60):
        return self.ev(f"window.__lpp.{call}", "iso", timeout)

    def _make_world(self):
        tree = self.cdp.call("Page.getFrameTree")
        fid = tree["frameTree"]["frame"]["id"]
        w = self.cdp.call("Page.createIsolatedWorld", {"frameId": fid, "worldName": "lpp", "grantUniveralAccess": True})
        self.ctx = w["executionContextId"]
        for src in (JS_LIB, JS_LIB2):
            r = self.cdp.call("Runtime.evaluate", {"expression": src, "contextId": self.ctx, "returnByValue": True})
            if r.get("exceptionDetails"):
                raise Fatal(f"[{self.name}] could not install the page library: {r['exceptionDetails']}")

    # -- loading -------------------------------------------------------------------------------------------------
    def emulate(self, width, height):
        mobile = width < self.args.mobile_below
        scale = self.args.scale
        self.cdp.call("Emulation.setDeviceMetricsOverride", {
            "width": width, "height": height, "deviceScaleFactor": scale, "mobile": mobile,
            "screenWidth": width, "screenHeight": height})
        self.cdp.call("Emulation.setTouchEmulationEnabled", {"enabled": mobile, "maxTouchPoints": 5} if mobile
                      else {"enabled": False})
        meta = {"brands": [{"brand": "Chromium", "version": CHROME_MAJOR}, {"brand": "Google Chrome", "version": CHROME_MAJOR},
                           {"brand": "Not?A_Brand", "version": "99"}],
                "fullVersion": f"{CHROME_MAJOR}.0.0.0",
                "platform": "Android" if mobile else "macOS", "platformVersion": "10.0.0" if mobile else "10.15.7",
                "architecture": "" if mobile else "arm", "model": "K" if mobile else "", "mobile": mobile}
        self.cdp.call("Emulation.setUserAgentOverride", {"userAgent": UA_MOBILE if mobile else UA_DESKTOP,
                                                         "acceptLanguage": "en-US,en", "userAgentMetadata": meta})
        try:
            self.cdp.call("Emulation.setScrollbarsHidden", {"hidden": True})
        except RuntimeError:
            pass
        self.width, self.height, self.mobile = width, height, mobile

    def load(self, width, height, url=None, fresh=True):
        url = url or self.url
        if fresh:
            self.fresh()
        self.emulate(width, height)
        self.cdp.events.clear()
        self.ctx = None
        t0 = time.time()
        r = self.cdp.call("Page.navigate", {"url": url}, timeout=90)
        if r.get("errorText"):
            raise Fatal(f"[{self.name}] navigation to {url} failed: {r['errorText']}", EXIT_NAV)
        if self.cdp.wait_event("Page.loadEventFired", timeout=self.args.load_timeout) is None:
            self.notes.append(f"{width}: load event not fired within {self.args.load_timeout}s (continued)")
            log(f"[{self.name}] {width}px: load event not fired in {self.args.load_timeout}s; continuing")
        self.cdp.wait_event("Page.lifecycleEvent", timeout=8, pred=lambda p: p.get("name") == "networkAlmostIdle")
        info = self.ev(JS_THEME, "main")
        self.check_theme(info)
        self.load_ms = int((time.time() - t0) * 1000)
        return info

    def check_theme(self, info):
        st = info.get("status")
        if st and st >= 400:
            raise Fatal(f"[{self.name}] {info.get('url')} answered HTTP {st} (a 500 usually means a template references "
                        f"a section type that is missing on the theme)", EXIT_NAV)
        exp = self.expect
        th = info.get("theme")
        self.theme_info = info
        if exp == "any":
            return
        if not th:
            raise Fatal(f"[{self.name}] the page has no Shopify.theme — not a Shopify storefront render? url={info.get('url')}",
                        EXIT_THEME)
        if exp == "main":
            if th.get("role") != "main" or (DEV_THEME_ID not in (None, "any") and th.get("id") == str(DEV_THEME_ID)):
                raise Fatal(f"[{self.name}] expected the LIVE (published, role=main) theme but the page rendered "
                            f"{th} at {info.get('url')} — a preview cookie leaked or the URL has preview_theme_id", EXIT_THEME)
        elif th.get("id") != str(exp):
            raise Fatal(f"[{self.name}] expected theme {exp} but the page rendered {th.get('id')} ({th.get('name')}, "
                        f"role {th.get('role')}) at {info.get('url')}. Check the preview_theme_id in the URL.", EXIT_THEME)

    def check_viewport(self, where):
        vp = self.lib("viewport()")
        if vp["innerWidth"] != self.width or vp["clientWidth"] != self.width:
            raise WidthError(f"[{self.name}] asked for {self.width}px of layout, the page reports innerWidth "
                             f"{vp['innerWidth']} / clientWidth {vp['clientWidth']} (scrollWidth {vp['scrollWidth']}, "
                             f"scale {vp['scale']}) at {where}. Refusing to compare a render at the wrong width.",
                             EXIT_VIEWPORT)
        return vp

    # -- preparation ---------------------------------------------------------------------------------------------
    def scroll_to(self, y):
        return self.ev(f"window.scrollTo(0, {float(y)}); [window.scrollY, document.documentElement.scrollHeight]", "iso")

    def prepare(self, sel=None):
        """Lazy media, stepped scroll (driven from here, not from one async evaluate), fonts and images."""
        a = self.args
        eager = self.lib("eager()")
        unveil = self.ev(JS_UNVEIL, "main")
        step = max(200, int(self.height * 0.8))
        y, steps = 0, 0
        _, doc_h = self.scroll_to(0)
        while y < doc_h and steps < 400:
            y += step
            _, doc_h = self.scroll_to(y)
            self.cdp.pump(a.scroll_pause_ms / 1000.0)
            steps += 1
        self.cdp.pump(0.3)
        eager2 = self.lib("eager()")
        unveil2 = self.ev(JS_UNVEIL, "main")
        self.scroll_to(0)
        # images: the section's must all be complete; the page's must have pixels (carousel clones sit at
        # complete=false forever — see incidents/2026-09-16-lazy-images-render-as-blank-bands.md)
        end = time.time() + a.img_timeout
        img = None
        while time.time() < end:
            img = self.lib(f"images({json.dumps(sel)})" if sel else "images(null)")
            if img["pending"] == 0 and (not sel or img["partial"] == 0):
                break
            self.cdp.pump(0.3)
        end = time.time() + a.font_timeout
        fonts = None
        while time.time() < end:
            fonts = self.lib("fonts()")
            if fonts["status"] == "loaded":
                break
            self.cdp.pump(0.25)
        return {"eager": eager + eager2, "lazysizes_unveiled": (unveil or 0) + (unveil2 or 0), "scroll_steps": steps,
                "doc_height": doc_h, "images": img, "fonts_status": fonts and fonts["status"],
                "fonts_failed": [f for f in (fonts or {}).get("faces", []) if f["status"] == "error"]}

    def freeze(self):
        a = self.args
        rec = {"animations": None, "carousels": None}
        if not a.freeze:
            return rec
        rec["carousels"] = self.ev(f"{JS_FREEZE}({'true' if a.carousel_reset else 'false'})", "main")
        end = time.time() + 3
        while time.time() < end and (self.ev(JS_VIDEOS_SETTLED, "main") or 0) > 0:
            self.cdp.pump(0.1)
        self.cdp.pump(0.15)
        fin = self.lib("finishAnimations()")
        self.cdp.pump(0.1)
        fin2 = self.lib("finishAnimations()")
        rec["animations"] = {"finished": fin["finished"] + fin2["finished"], "paused_infinite": fin["paused"] + fin2["paused"],
                             "failed": fin["failed"] + fin2["failed"]}
        return rec

    def find(self, sel):
        f = self.lib(f"find({json.dumps(sel)})")
        if f.get("error") == "bad-selector":
            raise Fatal(f"[{self.name}] invalid CSS selector {sel!r}: {f.get('message')}", EXIT_SELECTOR)
        if f.get("error") == "not-found":
            near = [s for s in f.get("sections", [])]
            raise Fatal(f"[{self.name}] selector {sel!r} matches nothing on {self.theme_info.get('url')}.\n"
                        f"  top-level section ids on this page: {', '.join(near[:60]) or '(none)'}", EXIT_SELECTOR)
        return f

    def settle_section(self, sel):
        """Scroll the section to the top of the viewport, let reveals run, then freeze."""
        f = self.find(sel)
        target = max(0, f["y"] - self.args.scroll_margin)
        self.scroll_to(target)
        self.cdp.pump(self.args.settle_ms / 1000.0)
        if f["h"] > self.height:
            # tall section: walk through it so every reveal inside fires, then come back
            y = target
            while y < f["y"] + f["h"]:
                y += int(self.height * 0.7)
                self.scroll_to(y)
                self.cdp.pump(min(0.35, self.args.settle_ms / 1000.0))
            self.scroll_to(target)
            self.cdp.pump(self.args.settle_ms / 1000.0)
        frz = self.freeze()
        return f, frz

    # -- capture -------------------------------------------------------------------------------------------------
    def screenshot(self, x, y, w, h):
        """Capture a region in PAGE coordinates. Returns a PIL image at args.scale."""
        s = self.args.scale
        tiles = []
        # LP_TILE_SCROLL=1: scroll each tile into the viewport and capture without captureBeyondViewport — on our pages
        # (body overflow hidden) the beyond-viewport capture sometimes paints the top of the page into the clip
        tile_scroll = os.environ.get("LP_TILE_SCROLL") == "1"
        max_tile = min(800, int(self.height or 900)) if tile_scroll else 4000
        yy = y
        while yy < y + h:
            th = min(max_tile, y + h - yy)
            if tile_scroll:
                self.ev(f"window.scrollTo(0, {yy})", "main")
                self.cdp.pump(0.25)
            shot = self.cdp.call("Page.captureScreenshot", {
                "format": "png", "captureBeyondViewport": not tile_scroll, "fromSurface": True,
                "clip": {"x": x, "y": yy, "width": w, "height": th, "scale": 1}}, timeout=120)
            tiles.append(Image.open(io.BytesIO(base64.b64decode(shot["data"]))).convert("RGB"))
            yy += th
        if len(tiles) == 1:
            return tiles[0]
        out = Image.new("RGB", (tiles[0].width, sum(t.height for t in tiles)))
        oy = 0
        for t in tiles:
            out.paste(t, (0, oy))
            oy += t.height
        return out

    def point_of(self, sel, what="step"):
        """Scroll `sel` to the middle of the viewport and return its centre — refusing when something else would
        receive the pointer there (a transparent overlay, a sticky bar), because the state would never be entered."""
        pt = self.ev(f"(() => {{ const e = document.querySelector({json.dumps(sel)}); if (!e) return null; "
                     f"e.scrollIntoView({{block: 'center'}}); const r = e.getBoundingClientRect(); "
                     f"const x = r.left + r.width / 2, y = r.top + r.height / 2; const h = document.elementFromPoint(x, y); "
                     f"const d = (n) => n ? n.tagName.toLowerCase() + (n.id ? '#' + n.id : '') + (n.className && typeof n.className === 'string' ? '.' + n.className.trim().split(/\\s+/).slice(0, 2).join('.') : '') : 'nothing'; "
                     f"return [x, y, r.width, r.height, !!h && (h === e || e.contains(h)), d(h)]; }})()", "iso")
        if not pt:
            raise WidthError(f"[{self.name}] {what}: selector {sel!r} matches nothing")
        if pt[2] == 0 or pt[3] == 0:
            raise WidthError(f"[{self.name}] {what}: {sel!r} has no size (hidden at this width?)")
        if not pt[4]:
            raise WidthError(f"[{self.name}] {what}: the point under {sel!r} is covered by {pt[5]} — the pointer would land "
                             f"there, not on the target. Refusing a state that was never entered.")
        return pt[0], pt[1]

    def platform_fonts(self, n):
        """Which font actually painted each text element (catches fallback glyphs)."""
        out = {}
        try:
            self.cdp.call("DOM.enable")
            self.cdp.call("CSS.enable", timeout=60)
            doc = self.cdp.call("DOM.getDocument", {"depth": 0})
            ids = self.cdp.call("DOM.querySelectorAll", {"nodeId": doc["root"]["nodeId"], "selector": "[data-lpp-i]"})["nodeIds"]
            for nid in ids:
                attrs = self.cdp.call("DOM.getAttributes", {"nodeId": nid}).get("attributes", [])
                i = None
                for k in range(0, len(attrs) - 1, 2):
                    if attrs[k] == "data-lpp-i":
                        i = int(attrs[k + 1])
                if i is None or i not in n:
                    continue
                fonts = self.cdp.call("CSS.getPlatformFontsForNode", {"nodeId": nid}).get("fonts", [])
                out[i] = [f"{f['familyName']}{'' if f.get('isCustomFont') else ' (system)'}:{f['glyphCount']}" for f in fonts]
        except Exception as e:  # informative only
            out["error"] = str(e)[:200]
        finally:
            try:
                self.cdp.call("CSS.disable")
                self.cdp.call("DOM.disable")
            except Exception:
                pass
        return out


# ----------------------------------------------------------------------------------------------------------------
# Image helpers
# ----------------------------------------------------------------------------------------------------------------
def is_blank(im):
    w, h = im.size
    seen = set()
    for y in range(0, h, max(1, h // 60)):
        for x in range(0, w, max(1, w // 40)):
            seen.add(im.getpixel((x, y)))
            if len(seen) > 1:
                return False
    return True


def diff_mask(a, b, threshold):
    """Mismatch mask over the union of both sizes: a pixel counts when |dR|+|dG|+|dB| > threshold; the area
    only one image covers counts as mismatched. Returns (mask L-image, stats)."""
    W, H = max(a.width, b.width), max(a.height, b.height)
    ow, oh = min(a.width, b.width), min(a.height, b.height)
    full = Image.new("L", (W, H), 255)
    over = 0
    if ow > 0 and oh > 0:
        d = ImageChops.difference(a.crop((0, 0, ow, oh)), b.crop((0, 0, ow, oh)))
        r, g, bl = d.split()
        s = ImageChops.add(ImageChops.add(r, g), bl)  # clipping at 255 cannot change a "> 30" test
        m = s.point(lambda v: 255 if v > threshold else 0)
        over = m.histogram()[255]
        full.paste(m, (0, 0))
    total = W * H
    nonover = total - ow * oh
    return full, {
        "size_live": [a.width, a.height], "size_ours": [b.width, b.height],
        "mismatched_px": over + nonover, "total_px": total,
        "diff_pct": round(100.0 * (over + nonover) / total, 3) if total else 0.0,
        "overlap_diff_pct": round(100.0 * over / (ow * oh), 3) if ow * oh else None,
        "nonoverlap_px": nonover,
    }


def row_counts(mask):
    W, H = mask.size
    prof = mask.convert("F").resize((1, H), Image.BOX)
    data = prof.get_flattened_data() if hasattr(prof, "get_flattened_data") else prof.getdata()
    return [int(round(v * W / 255.0)) for v in data]


def bands(mask, scale=1, limit=8, gap=3):
    rows = row_counts(mask)
    W = mask.size[0]
    out, start, px, last = [], None, 0, None
    for y, c in enumerate(rows + [0] * (gap + 1)):
        if c > 0:
            if start is None:
                start, px = y, 0
            px += c
            last = y
        elif start is not None and y - last > gap:
            out.append({"y0": round(start / scale, 1), "y1": round((last + 1) / scale, 1), "px": px,
                        "pct_of_band": round(100.0 * px / (W * (last + 1 - start)), 2)})
            start = None
    out.sort(key=lambda b: b["px"], reverse=True)
    return out[:limit]


def heatmap(a, b, mask):
    W, H = mask.size
    base = Image.new("RGB", (W, H), (200, 200, 200))
    ga = a.convert("L").convert("RGB")
    gb = b.convert("L").convert("RGB")
    ow, oh = min(a.width, b.width), min(a.height, b.height)
    if ow and oh:
        bl = Image.blend(ga.crop((0, 0, ow, oh)), gb.crop((0, 0, ow, oh)), 0.5)
        bl = Image.eval(bl, lambda v: int(v * 0.55 + 90))
        base.paste(bl, (0, 0))
    red = Image.new("RGB", (W, H), (214, 48, 40))
    base.paste(red, mask=mask)
    return base


def side_by_side(images, labels):
    gap, top = 16, 30
    W = sum(im.width for im in images) + gap * (len(images) - 1)
    H = max(im.height for im in images) + top
    out = Image.new("RGB", (W, H), (238, 241, 244))
    d = ImageDraw.Draw(out)
    x = 0
    for im, lab in zip(images, labels):
        out.paste(im, (x, top))
        d.text((x + 6, 9), lab, fill=(23, 33, 43))
        x += im.width + gap
    return out


# ----------------------------------------------------------------------------------------------------------------
# Pairing live <-> ours
# ----------------------------------------------------------------------------------------------------------------
VISUAL_PROPS = ["font-family", "font-size", "line-height", "font-weight", "font-style", "letter-spacing", "color",
                "text-transform", "text-align", "text-decoration-line", "background-color", "background-image",
                "background-size", "background-position", "border", "border-radius", "opacity", "box-shadow",
                "object-fit", "object-position"]
LAYOUT_PROPS = ["padding", "margin", "gap", "display"]
# typography on a container is only inherited, never painted: compare it on text elements only
BOX_PROPS = ["background-color", "background-image", "background-size", "background-position", "border",
             "border-radius", "opacity", "box-shadow", "object-fit", "object-position"]


def el_label(e):
    t = e.get("text") or ""
    base = e["tag"] + (("." + e["cls"].split(".")[0]) if e.get("cls") else "")
    if e["kind"] == "root":
        return f"{base} (section root)"
    if e["kind"] == "media":
        return f"{base} [{e.get('srcKey') or e.get('src', '')[:50]}]"
    if e["kind"] in ("bg", "box") and not t:
        return f"{base} ({e['kind']})"
    return f"{base} \"{t[:48]}{'…' if len(t) > 48 else ''}\""


def pair_key(e, level):
    k = e["kind"]
    if k == "root":
        return "root"
    if k == "media":
        return f"media:{e['tag']}:{e.get('srcKey', '')}" if level == 0 else f"media:{e['tag']}"
    if k == "bg":
        return f"bg:{e.get('srcKey', '')}" if level == 0 else "bg"
    t = e.get("text") or ""
    if level == 0:
        return f"{k}:{t}"
    return f"{'text' if k == 'text' else k}:{re.sub(r'[^0-9a-z]+', '', t.lower())}"


def _cost(a, b):
    ba, bb = a["box"], b["box"]
    c = abs(ba["x"] - bb["x"]) + abs(ba["y"] - bb["y"]) + abs(ba["w"] - bb["w"]) + abs(ba["h"] - bb["h"])
    if a["tag"] != b["tag"]:
        c += 40
    if a["kind"] == "text" and b["kind"] == "text" and (a.get("own") or "") != (b.get("own") or ""):
        c += 20
    return c


def pair_elements(L, O):
    pairs = []
    free_l, free_o = list(L), list(O)
    for level in (0, 1):
        gl, go = collections.defaultdict(list), collections.defaultdict(list)
        for e in free_l:
            gl[pair_key(e, level)].append(e)
        for e in free_o:
            go[pair_key(e, level)].append(e)
        used_l, used_o = set(), set()
        for key in gl:
            if key not in go:
                continue
            a, b = gl[key], go[key]
            if len(a) == len(b) and level == 0:
                for x, y in zip(a, b):
                    pairs.append((x, y, "exact" if level == 0 else "loose"))
                    used_l.add(id(x))
                    used_o.add(id(y))
                continue
            cand = sorted(((_cost(x, y), i, j) for i, x in enumerate(a) for j, y in enumerate(b)))
            ua, ub = set(), set()
            for c, i, j in cand:
                if i in ua or j in ub:
                    continue
                ua.add(i)
                ub.add(j)
                pairs.append((a[i], b[j], "exact" if level == 0 else "loose"))
                used_l.add(id(a[i]))
                used_o.add(id(b[j]))
        free_l = [e for e in free_l if id(e) not in used_l]
        free_o = [e for e in free_o if id(e) not in used_o]
    # fuzzy text (copy differs by a word, an nbsp, a <br>)
    tl = [e for e in free_l if e["kind"] in ("text", "box") and e.get("text")]
    to = [e for e in free_o if e["kind"] in ("text", "box") and e.get("text")]
    cand = []
    for i, x in enumerate(tl):
        for j, y in enumerate(to):
            if x["kind"] != y["kind"]:
                continue
            r = difflib.SequenceMatcher(None, x["text"].lower(), y["text"].lower()).ratio()
            if r >= 0.8:
                cand.append((-r, _cost(x, y), i, j))
    cand.sort()
    ua, ub = set(), set()
    for _, _, i, j in cand:
        if i in ua or j in ub:
            continue
        ua.add(i)
        ub.add(j)
        pairs.append((tl[i], to[j], "fuzzy"))
    fl = {id(tl[i]) for i in ua}
    fo = {id(to[j]) for j in ub}
    free_l = [e for e in free_l if id(e) not in fl]
    free_o = [e for e in free_o if id(e) not in fo]
    pairs.sort(key=lambda p: p[0]["i"])
    return pairs, free_l, free_o


def src_candidate(u):
    """The width of the file actually downloaded: Shopify's `width=` parameter or a `_600x` suffix."""
    if not u:
        return None
    m = re.search(r"[?&]width=(\d+)", u) or re.search(r"_(\d+)x(?:\d+)?(?:_crop_\w+)?\.", u)
    return int(m.group(1)) if m else "original"


def nested_duplicate(e, side_list):
    """An unpaired element whose text and box equal another element on the same side (a wrapper span)."""
    for o in side_list:
        if o is e or o["kind"] == "root":
            continue
        if (o.get("text") == e.get("text") and all(abs(o["box"][k] - e["box"][k]) <= 1 for k in "xywh")):
            return True
    return False


def compare_elements(L, O, box_tol, fonts_l=None, fonts_o=None):
    pairs, ul, uo = pair_elements(L, O)
    rows = []
    n_box = n_vis = n_lay = 0
    for a, b, how in pairs:
        d = {}
        bd = {k: round(b["box"][k] - a["box"][k], 3) for k in "xywh"}
        if any(abs(v) > box_tol for v in bd.values()):
            d["box"] = bd
            n_box += 1
        props = VISUAL_PROPS if (a["kind"] == "text" or b["kind"] == "text") else BOX_PROPS
        vis = {p: [a["style"].get(p), b["style"].get(p)] for p in props
               if a["style"].get(p) != b["style"].get(p) and (a["style"].get(p) is not None or b["style"].get(p) is not None)}
        lay = {p: [a["style"].get(p), b["style"].get(p)] for p in LAYOUT_PROPS if a["style"].get(p) != b["style"].get(p)}
        if a.get("lines") is not None and b.get("lines") is not None and a["lines"] != b["lines"]:
            vis["text-lines"] = [a["lines"], b["lines"]]
        if a["kind"] == "media" and b["kind"] == "media" and a.get("srcKey") != b.get("srcKey"):
            vis["src"] = [a.get("srcKey"), b.get("srcKey")]
        elif a["tag"] == "img" and b["tag"] == "img" and src_candidate(a.get("src")) != src_candidate(b.get("src")):
            # same file, different srcset candidate: the same box resampled from a different download (check `sizes`)
            vis["srcset-candidate"] = [src_candidate(a.get("src")), src_candidate(b.get("src"))]
        if a.get("natural") and b.get("natural") and a["natural"] != b["natural"]:
            lay["natural-size"] = [a["natural"], b["natural"]]
        if fonts_l is not None and fonts_o is not None:
            fa, fb = fonts_l.get(a["i"]), fonts_o.get(b["i"])
            if fa is not None and fb is not None and [x.split(":")[0] for x in fa] != [x.split(":")[0] for x in fb]:
                vis["rendered-font"] = [fa, fb]
        if vis:
            d["style"] = vis
            n_vis += 1
        if lay:
            d["layout_style"] = lay
            n_lay += 1
        if d:
            d.update({"label": el_label(a), "ours_label": el_label(b), "pairing": how,
                      "live_box": a["box"], "ours_box": b["box"]})
            rows.append(d)
    true_ul = [e for e in ul if not nested_duplicate(e, L)]
    true_uo = [e for e in uo if not nested_duplicate(e, O)]
    fmt = lambda e: {"label": el_label(e), "box": e["box"], "kind": e["kind"]}
    return {
        "paired": len(pairs), "pairs_fuzzy": sum(1 for p in pairs if p[2] == "fuzzy"),
        "box_deltas": n_box, "style_deltas": n_vis, "layout_style_deltas": n_lay,
        "elements": rows,
        "unpaired_live": [fmt(e) for e in true_ul], "unpaired_ours": [fmt(e) for e in true_uo],
        "wrapper_duplicates": {"live": len(ul) - len(true_ul), "ours": len(uo) - len(true_uo)},
    }


# ----------------------------------------------------------------------------------------------------------------
# Section comparison at one width
# ----------------------------------------------------------------------------------------------------------------
def both(fn_live, fn_ours):
    """Live, then ours — never both at once (one page loading at a time keeps the shared laptop cool)."""
    return [fn_live(), fn_ours()]


def frac(v):
    return v - math.floor(v)


def section_at_width(live, ours, width, args, out_dir, steps=None):
    height = args.height
    rec = {"width": width, "height": height, "mobile_emulation": width < args.mobile_below}

    def prep(side, sel):
        info = side.load(width, height)
        vp = side.check_viewport("load")
        p = side.prepare(sel)
        side.find(sel)
        f, frz = side.settle_section(sel)
        if steps:
            # overlays first (a transparent fixed layer swallows clicks), then the steps — after the reset to slide 1,
            # so a "next" step is not undone — then settle what the steps started
            side.lib(f"hideOverlays({json.dumps(sel)}, {'true' if args.keep_fixed else 'false'})")
            p["steps"] = run_steps(side, steps, args)
            side.cdp.pump(args.settle_ms / 1000.0)
            if args.freeze:
                frz["after_steps"] = side.lib("finishAnimations()")
        hid = side.lib(f"hideOverlays({json.dumps(sel)}, {'true' if args.keep_fixed else 'false'})")
        if hid.get("bodyPosition") == "fixed":
            side.notes.append(f"{width}: body is position:fixed (a scroll lock from a popup?)")
        f = side.find(sel)
        return {"theme": info.get("theme"), "asset_path": info.get("assetPath"), "url": info.get("url"),
                "load_ms": side.load_ms, "viewport": vp, "prepare": p, "freeze": frz,
                "overlays_hidden": hid.get("count"), "overlays": hid.get("hidden")[:40], "section": f}

    pl, po = both(lambda: prep(live, args.live_sel), lambda: prep(ours, args.ours_sel))
    rec["live"], rec["ours"] = pl, po
    fl, fo = pl["section"], po["section"]
    if fl["count"] > 1 or fo["count"] > 1:
        rec["selector_warning"] = f"selector matched live {fl['count']} / ours {fo['count']} elements; the first was used"
    if not fl["rendered"] or not fo["rendered"]:
        rec["hidden"] = {"live": not fl["rendered"], "ours": not fo["rendered"]}
        if not fl["rendered"] and not fo["rendered"]:
            rec["status"] = "hidden-both"
            rec["diff_pct"] = 0.0
            return rec
        rec["status"] = "hidden-one-side"
        rec["diff_pct"] = 100.0
        return rec

    # sub-pixel alignment: give ours' section top the same fraction as live's
    shift = 0.0
    if args.align_fraction:
        shift = (frac(fl["y"]) - frac(fo["y"])) % 1.0
        if shift > 1e-6:
            ours.lib(f"shift({shift})")
            ours.cdp.pump(0.15)
            fo2 = ours.find(args.ours_sel)
            if abs(((frac(fo2["y"]) - frac(fl["y"])) + 0.5) % 1.0 - 0.5) > 0.01:
                rec["align_warning"] = (f"asked ours to move {shift:.4f}px; its top went {fo['y']:.4f} -> {fo2['y']:.4f} "
                                        f"(live {fl['y']:.4f})")
            fo = fo2
    rec["align_shift_px"] = round(shift, 4)
    rec["section_box"] = {
        "live": {k: round(fl[k], 3) for k in ("x", "y", "w", "h")},
        "ours": {k: round(fo[k] - (shift if k == "y" else 0), 3) for k in ("x", "y", "w", "h")},
    }
    rec["section_box"]["delta"] = {k: round(rec["section_box"]["ours"][k] - rec["section_box"]["live"][k], 3) for k in "xywh"}

    # one padding for both sides (the union of their overflow), so both crops start at the same offset
    shared_pad = {"top": 0, "bottom": 0, "left": 0, "right": 0}
    if args.include_overflow:
        ovs = [sd.lib(f"inventory({json.dumps(sl)}, {{}})")["overflow"] for sd, sl in ((live, args.live_sel), (ours, args.ours_sel))]
        shared_pad = {k: min(400, math.ceil(max(o[k] for o in ovs))) for k in shared_pad}
        if not args.allow_overflow_x:
            shared_pad["left"] = shared_pad["right"] = 0
    rec["capture_pad"] = shared_pad

    def measure_and_capture(side, sel):
        side.check_viewport("capture")
        inv = side.lib(f"inventory({json.dumps(sel)}, {json.dumps({'imageSelector': args.image_selector})})")
        root = inv["root"]
        pad = dict(shared_pad)
        inv["pad"] = pad
        x0, y0 = math.floor(root["x"]) - pad["left"], math.floor(root["y"]) - pad["top"]
        x1 = math.ceil(root["x"] + root["w"] - 1e-6) + pad["right"]
        y1 = math.ceil(root["y"] + root["h"] - 1e-6) + pad["bottom"]
        x0 = max(0, x0)
        x1 = min(x1, side.width) if not args.allow_overflow_x else x1
        img = side.screenshot(x0, y0, max(1, x1 - x0), max(1, y1 - y0))
        side.cdp.pump(args.stability_ms / 1000.0)
        img2 = side.screenshot(x0, y0, max(1, x1 - x0), max(1, y1 - y0)) if args.stability_ms > 0 else None
        # a capture that changes between two shots was taken mid-paint (cold cache): wait and take the pair again
        for _retry in range(3):
            if img2 is None or diff_mask(img, img2, args.threshold)[1]["diff_pct"] < 1.0:
                break
            side.cdp.pump(1.5)
            img = side.screenshot(x0, y0, max(1, x1 - x0), max(1, y1 - y0))
            side.cdp.pump(args.stability_ms / 1000.0)
            img2 = side.screenshot(x0, y0, max(1, x1 - x0), max(1, y1 - y0))
        # the rendered-font probe enables the CSS domain, which re-rasterises text: it must come after the captures
        fonts = None
        if args.fonts:
            text_idx = {e["i"] for e in inv["elements"] if e["kind"] == "text"}
            fonts = side.platform_fonts(text_idx)
        return inv, img, img2, (x0, y0), fonts

    (il, img_l, img_l2, org_l, fonts_l), (io_, img_o, img_o2, org_o, fonts_o) = both(
        lambda: measure_and_capture(live, args.live_sel), lambda: measure_and_capture(ours, args.ours_sel))

    for name, im in (("live", img_l), ("ours", img_o)):
        if is_blank(im) and not args.allow_blank:
            raise WidthError(f"[{name}] the {width}px capture is a single flat colour — the page had not painted, or "
                             f"the section is an empty band. Nothing written for this width (use --allow-blank if the "
                             f"band really is flat).", EXIT_BLANK)

    # stability: the same side captured twice
    stab = {}
    for name, a, b in (("live", img_l, img_l2), ("ours", img_o, img_o2)):
        if b is None:
            continue
        m, st = diff_mask(a, b, args.threshold)
        stab[name] = {"unstable_pct": st["diff_pct"], "bands": bands(m, args.scale, 4) if st["mismatched_px"] else []}
        if st["mismatched_px"]:
            pth = os.path.join(out_dir, f"{name}-{width}-unstable.png")
            side_by_side([a, b, heatmap(a, b, m)], [f"{name} capture 1", f"{name} capture 2 (+{args.stability_ms}ms)",
                                                   f"changed {st['diff_pct']}%"]).save(pth)
            stab[name]["file"] = pth
    rec["stability"] = stab

    mask, st = diff_mask(img_l, img_o, args.threshold)
    rec.update(st)
    rec["worst_bands"] = bands(mask, args.scale)
    rec["status"] = "compared"
    tag = f"{width}"
    paths = {
        "live": os.path.join(out_dir, f"live-{tag}.png"), "ours": os.path.join(out_dir, f"ours-{tag}.png"),
        "diff": os.path.join(out_dir, f"diff-{tag}.png"), "side_by_side": os.path.join(out_dir, f"side-by-side-{tag}.png"),
    }
    img_l.save(paths["live"])
    img_o.save(paths["ours"])
    heat = heatmap(img_l, img_o, mask)
    heat.save(paths["diff"])
    side_by_side([img_l, img_o, heat], [f"LIVE {width}px", f"OURS {width}px",
                                        f"diff {st['diff_pct']}% (|dR|+|dG|+|dB|>{args.threshold})"]).save(paths["side_by_side"])
    rec["files"] = paths

    # element inventory comparison
    ovl, ovo = il.get("overflow", {}), io_.get("overflow", {})
    if any(v > 0.5 for v in list(ovl.values()) + list(ovo.values())):
        rec.setdefault("notes", []).append(
            f"content paints outside the section box (px beyond top/bottom/left/right) — live {ovl}, ours {ovo}; "
            + ("captured with --include-overflow" if args.include_overflow else "not in the pixel diff: add --include-overflow"))
    rec["inventory"] = {"live": il["elements"], "ours": io_["elements"]}
    cmp = compare_elements(il["elements"], io_["elements"], args.box_tol,
                           fonts_l if fonts_l and "error" not in fonts_l else None,
                           fonts_o if fonts_o and "error" not in fonts_o else None)
    cmp["invisible"] = {"live": il["counts"], "ours": io_["counts"]}
    rec["elements"] = cmp
    if fonts_l and "error" in fonts_l:
        rec.setdefault("notes", []).append(f"live platform-font probe failed: {fonts_l['error']}")
    if fonts_o and "error" in fonts_o:
        rec.setdefault("notes", []).append(f"ours platform-font probe failed: {fonts_o['error']}")
    rec["fonts_used"] = {"live": summarise_fonts(fonts_l), "ours": summarise_fonts(fonts_o)}

    # per-image diffs
    if args.image_selector:
        imgs = []
        pairs, _, _ = pair_elements([e for e in il["elements"] if e.get("imgSel")], [e for e in io_["elements"] if e.get("imgSel")])
        for a, b, how in pairs:
            ca = crop_box(img_l, a["box"], il["root"], org_l, args.scale)
            cb = crop_box(img_o, b["box"], io_["root"], org_o, args.scale)
            if ca is None or cb is None:
                continue
            m, s2 = diff_mask(ca, cb, args.threshold)
            imgs.append({"label": el_label(a), "live_box": a["box"], "ours_box": b["box"], "diff_pct": s2["diff_pct"],
                         "src": [a.get("srcKey"), b.get("srcKey")],
                         "candidate": [src_candidate(a.get("src")), src_candidate(b.get("src"))],
                         "natural": [a.get("natural"), b.get("natural")]})
        rec["image_diffs"] = imgs
    return rec


def summarise_fonts(f):
    if not f or "error" in f:
        return None
    c = collections.Counter()
    for k, v in f.items():
        for x in v:
            c[x.split(":")[0]] += 1
    return dict(c.most_common(12))


def crop_box(img, box, root, origin, scale):
    ox = (root["x"] - origin[0]) + box["x"]
    oy = (root["y"] - origin[1]) + box["y"]
    x0, y0 = int(math.floor(ox * scale)), int(math.floor(oy * scale))
    x1, y1 = int(math.ceil((ox + box["w"]) * scale)), int(math.ceil((oy + box["h"]) * scale))
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(img.width, x1), min(img.height, y1)
    if x1 - x0 < 1 or y1 - y0 < 1:
        return None
    return img.crop((x0, y0, x1, y1))


# ----------------------------------------------------------------------------------------------------------------
# States (step replay)
# ----------------------------------------------------------------------------------------------------------------
def run_steps(side, steps, args):
    done = []
    for i, st in enumerate(steps):
        who = st.get("side", "both")
        if who not in ("both", side.name):
            continue
        do = st.get("do")
        sel = st.get(f"sel_{side.name}", st.get("sel"))
        try:
            if do == "wait":
                side.cdp.pump(st.get("ms", 300) / 1000.0)
            elif do == "scroll":
                if sel:
                    side.ev(f"(() => {{ const e = document.querySelector({json.dumps(sel)}); if (!e) throw new Error('no element {sel}'); "
                            f"e.scrollIntoView({{block: {json.dumps(st.get('block', 'center'))}}}); return scrollY; }})()", "iso")
                else:
                    side.scroll_to(st.get("y", 0))
                side.cdp.pump(st.get("ms", 300) / 1000.0)
            elif do in ("hover", "click", "tap"):
                x, y = side.point_of(sel, f"step {i} ({do})")
                side.cdp.pump(0.1)
                side.cdp.call("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": x, "y": y})
                if do == "tap":
                    side.cdp.call("Input.synthesizeTapGesture", {"x": x, "y": y, "duration": 60, "tapCount": 1,
                                                                 "gestureSourceType": "touch"})
                elif do == "click":
                    side.cdp.call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": x, "y": y, "button": "left", "clickCount": 1})
                    side.cdp.call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": x, "y": y, "button": "left", "clickCount": 1})
                side.cdp.pump(st.get("ms", 400) / 1000.0)
            elif do == "press":
                key = st.get("key", "Tab")
                kc = {"Tab": 9, "Enter": 13, "Escape": 27, "ArrowRight": 39, "ArrowLeft": 37, "ArrowDown": 40, "ArrowUp": 38, " ": 32}.get(key, 0)
                p = {"key": key, "code": ("Space" if key == " " else key) if (len(key) > 1 or key == " ") else f"Key{key.upper()}",
                     "windowsVirtualKeyCode": kc or (ord(key.upper()) if len(key) == 1 else 0)}
                text = "\r" if key == "Enter" else (key if len(key) == 1 else "")
                # as Puppeteer does: keys that type text send keyDown+text, the rest rawKeyDown
                side.cdp.call("Input.dispatchKeyEvent", dict(p, type="keyDown", text=text) if text else dict(p, type="rawKeyDown"))
                side.cdp.call("Input.dispatchKeyEvent", dict(p, type="keyUp"))
                side.cdp.pump(st.get("ms", 200) / 1000.0)
            elif do == "eval":
                side.ev(st["js"], st.get("world", "main"))
                side.cdp.pump(st.get("ms", 300) / 1000.0)
            elif do == "focus":
                side.ev(f"document.querySelector({json.dumps(sel)}).focus()", "iso")
                side.cdp.pump(st.get("ms", 200) / 1000.0)
            else:
                raise Fatal(f"unknown step {do!r} (use hover|click|tap|scroll|wait|press|focus|eval)", EXIT_USAGE)
        except RuntimeError as e:
            raise WidthError(f"[{side.name}] step {i} {st}: {e}")
        done.append({"i": i, "do": do, "sel": sel})
    return done


# ----------------------------------------------------------------------------------------------------------------
# Report writing
# ----------------------------------------------------------------------------------------------------------------
def md_escape(s):
    return str(s).replace("|", "\\|").replace("\n", " ")


def write_section_report(out_dir, meta, results, errors, cmd):
    rep = {"tool": "lp-parity.py", "command": cmd, "generated": datetime.datetime.now().isoformat(timespec="seconds"),
           "meta": meta, "widths": results, "errors": errors}
    with open(os.path.join(out_dir, "report.json"), "w") as f:
        json.dump(rep, f, indent=1, default=str)
    L = []
    L.append(f"# live-parity {meta['mode']} — {meta.get('title', '')}")
    L.append("")
    L.append(f"- live: `{meta['live_url']}` `{meta['live_sel']}` — theme {meta.get('live_theme')}")
    L.append(f"- ours: `{meta['ours_url']}` `{meta['ours_sel']}` — theme {meta.get('ours_theme')}")
    L.append(f"- threshold: a pixel counts when |dR|+|dG|+|dB| > {meta['threshold']}; box tolerance {meta['box_tol']}px; "
             f"scale {meta['scale']}; viewport height {meta['height']}; mobile emulation below {meta['mobile_below']}px")
    L.append(f"- freeze {meta['freeze']}, carousel reset {meta['carousel_reset']}, align-fraction {meta['align_fraction']}, "
             f"keep-fixed {meta['keep_fixed']}, settle {meta['settle_ms']}ms")
    L.append(f"- Chrome: {meta.get('chrome')}")
    L.append("")
    L.append("| width | status | diff % | live box (x,y,w,h) | ours box | Δh | boxes off | style Δ | unpaired L/O | unstable L/O | worst band (y0–y1 px) |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for r in results:
        if r.get("status") != "compared":
            L.append(f"| {r['width']} | {r.get('status')} | {r.get('diff_pct', '')} | | | | | | | | |")
            continue
        sb = r["section_box"]
        b = lambda d: f"{d['x']:.0f},{d['y']:.2f},{d['w']:.1f},{d['h']:.2f}"
        el = r["elements"]
        wb = r["worst_bands"][0] if r["worst_bands"] else None
        stl = r.get("stability", {})
        L.append(f"| {r['width']} | {r['status']} | **{r['diff_pct']}** | {b(sb['live'])} | {b(sb['ours'])} | "
                 f"{sb['delta']['h']:+.2f} | {el['box_deltas']} | {el['style_deltas']} | "
                 f"{len(el['unpaired_live'])}/{len(el['unpaired_ours'])} | "
                 f"{stl.get('live', {}).get('unstable_pct', '-')}/{stl.get('ours', {}).get('unstable_pct', '-')} | "
                 f"{(str(wb['y0']) + '–' + str(wb['y1']) + ' (' + str(wb['px']) + 'px)') if wb else '—'} |")
    for e in errors:
        L.append(f"| {e['width']} | ERROR | | | | | | | | | {md_escape(e['error'])[:160]} |")
    L.append("")
    for r in results:
        if r.get("status") != "compared":
            continue
        el = r["elements"]
        L.append(f"## {r['width']}px — {r['diff_pct']}% ({el['paired']} paired, {el['box_deltas']} boxes off, "
                 f"{el['style_deltas']} style deltas)")
        L.append("")
        L.append(f"![side by side]({os.path.basename(r['files']['side_by_side'])})")
        L.append("")
        notes = []
        if r.get("align_shift_px"):
            notes.append(f"ours shifted {r['align_shift_px']}px down to match live's sub-pixel section top")
        for nm in ("live", "ours"):
            s = r["stability"].get(nm)
            if s and s["unstable_pct"] > 0:
                notes.append(f"**{nm} is not stable**: {s['unstable_pct']}% of its own pixels changed between two captures "
                             f"{meta['stability_ms']}ms apart, bands {s['bands']} — motion the freeze did not stop")
            p = r[nm]["prepare"]
            if p["images"] and p["images"].get("broken"):
                notes.append(f"{nm}: images that never loaded: {p['images']['broken'][:5]}")
            if p["images"] and p["images"].get("pending"):
                notes.append(f"{nm}: images still loading at capture: {p['images']['pendingSrc'][:5]}")
            if p.get("fonts_status") != "loaded":
                notes.append(f"{nm}: document.fonts.status={p.get('fonts_status')}")
            if p.get("fonts_failed"):
                notes.append(f"{nm}: font faces that failed: {p['fonts_failed'][:4]}")
        if r.get("selector_warning"):
            notes.append(r["selector_warning"])
        if r.get("align_warning"):
            notes.append("alignment: " + r["align_warning"])
        for n in r.get("notes", []):
            notes.append(n)
        if r.get("fonts_used"):
            notes.append(f"fonts that painted the text — live {r['fonts_used'].get('live')} / ours {r['fonts_used'].get('ours')}")
        if el["wrapper_duplicates"]["live"] or el["wrapper_duplicates"]["ours"]:
            notes.append(f"unpaired wrapper duplicates (same text and box as a paired element, ignored): {el['wrapper_duplicates']}")
        if notes:
            for n in notes:
                L.append(f"- {md_escape(n)}")
            L.append("")
        if r["worst_bands"]:
            L.append("Worst bands (section-relative CSS px): " + ", ".join(
                f"{b['y0']}–{b['y1']} ({b['px']}px, {b['pct_of_band']}%)" for b in r["worst_bands"][:6]))
            L.append("")
        if el["elements"]:
            L.append("| element (live) | pairing | box Δ (x,y,w,h) | style Δ live → ours | layout-style Δ (informational) |")
            L.append("|---|---|---|---|---|")
            for d in el["elements"][:120]:
                bd = d.get("box")
                bds = f"{bd['x']:+.2f},{bd['y']:+.2f},{bd['w']:+.2f},{bd['h']:+.2f}" if bd else ""
                sd = "; ".join(f"{k}: {v[0]} → {v[1]}" for k, v in d.get("style", {}).items())
                ld = "; ".join(f"{k}: {v[0]} → {v[1]}" for k, v in d.get("layout_style", {}).items())
                L.append(f"| {md_escape(d['label'])} | {d['pairing']} | {bds} | {md_escape(sd)[:400]} | {md_escape(ld)[:200]} |")
            if len(el["elements"]) > 120:
                L.append(f"| … {len(el['elements']) - 120} more in report.json | | | | |")
            L.append("")
        if el["unpaired_live"] or el["unpaired_ours"]:
            L.append(f"Unpaired on live ({len(el['unpaired_live'])}): " + "; ".join(md_escape(u["label"]) for u in el["unpaired_live"][:30]))
            L.append("")
            L.append(f"Unpaired on ours ({len(el['unpaired_ours'])}): " + "; ".join(md_escape(u["label"]) for u in el["unpaired_ours"][:30]))
            L.append("")
        if r.get("image_diffs"):
            L.append("| image | diff % | live file (downloaded width) | ours file (downloaded width) |")
            L.append("|---|---|---|---|")
            for d in r["image_diffs"]:
                c = d.get("candidate") or [None, None]
                L.append(f"| {md_escape(d['label'])} | {d['diff_pct']} | {d['src'][0]} ({c[0]}) | {d['src'][1]} ({c[1]}) |")
            L.append("")
    if errors:
        L.append("## Errors")
        for e in errors:
            L.append(f"- {e['width']}: {md_escape(e['error'])}")
    with open(os.path.join(out_dir, "report.md"), "w") as f:
        f.write("\n".join(L) + "\n")


# ----------------------------------------------------------------------------------------------------------------
# Commands
# ----------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------
# page — every top-level section, both sides
# ----------------------------------------------------------------------------------------------------------------
def slug_of(url):
    path = urllib.parse.urlsplit(url).path.rstrip("/")
    return (path.split("/")[-1] or "home").replace(".", "-")


def page_capture(side, width, args, shots=True):
    info = side.load(width, args.height)
    vp = side.check_viewport("load")
    prep = side.prepare(None)
    side.scroll_to(0)
    side.cdp.pump(args.settle_ms / 1000.0)
    frz = side.freeze()
    hid = side.lib(f"hideOverlays(null, {'true' if args.keep_fixed else 'false'}, true)")
    side.scroll_to(0)
    side.cdp.pump(0.2)
    side.check_viewport("capture")
    secs = side.lib("sections()")
    doc_h = side.lib("viewport()")["docHeight"]
    img = side.screenshot(0, 0, width, doc_h) if shots else None
    if img is not None and is_blank(img) and not args.allow_blank:
        raise WidthError(f"[{side.name}] the {width}px full-page capture is blank", EXIT_BLANK)
    return {"theme": info.get("theme"), "asset_path": info.get("assetPath"), "url": info.get("url"), "viewport": vp,
            "prepare": prep, "freeze": frz, "overlays_hidden": hid.get("count"), "overlays": hid.get("hidden")[:40],
            "doc_height": doc_h, "sections": secs}, img


def match_sections(L, O, explicit=None):
    """By trailing key (and --map live=ours), then by order — but only between the same two key-matched neighbours
    and only where both sides have the same number of rendered sections there. Anything else stays unmatched: a
    guess that pairs two different sections because they happen to start at the same y is worse than no pair."""
    explicit = explicit or {}
    pairs, ul, uo = [], list(L), list(O)
    ko = collections.defaultdict(list)
    for s_ in O:
        ko[s_["key"]].append(s_)
    for s_ in L:
        want = explicit.get(s_["key"], s_["key"])
        if ko.get(want):
            o = ko[want].pop(0)
            pairs.append((s_, o, "key" if want == s_["key"] else "map"))
            ul.remove(s_)
            uo.remove(o)
    anchors = sorted(pairs, key=lambda p: p[0]["top"])
    bounds = [(-1e9, -1e9)] + [(a["top"], b["top"]) for a, b, _ in anchors] + [(1e12, 1e12)]
    for (la, oa), (lb, ob) in zip(bounds, bounds[1:]):
        gl = [x for x in ul if x["rendered"] and la < x["top"] < lb]
        go = [x for x in uo if x["rendered"] and oa < x["top"] < ob]
        if gl and len(gl) == len(go):
            for a, b in zip(sorted(gl, key=lambda x: x["top"]), sorted(go, key=lambda x: x["top"])):
                pairs.append((a, b, "order"))
                ul.remove(a)
                uo.remove(b)
    pairs.sort(key=lambda p: p[0]["top"])
    return pairs, ul, uo


def cmd_page(args):
    widths = parse_widths(args.widths)
    out_dir = ensure_out(args.out)
    snap_dir = ensure_out(os.path.join(out_dir, "live-snap")) if args.live_only else None
    urls = [u.strip() for u in (args.pages.split(",") if args.pages else [args.live_url]) if u and u.strip()]
    if not urls:
        raise Fatal("page needs --live-url (or --pages a,b,c with --live-only)", EXIT_USAGE)
    if not args.live_only and (not args.ours_url or len(urls) != 1):
        raise Fatal("page compares one --live-url with one --ours-url (or use --live-only [--pages])", EXIT_USAGE)
    results, errors = [], []
    with Slot():
        live = ours = None
        try:
            live = Side("live", urls[0], None, args.live_theme, args)
            if not args.live_only:
                ours = Side("ours", args.ours_url, None, args.ours_theme, args)
            for url in urls:
                live.url = url
                slug = args.slug or slug_of(url)
                for w in widths:
                    t0 = time.time()
                    try:
                        pl, il = page_capture(live, w, args)
                        rec = {"url": url, "slug": slug, "width": w, "live": pl}
                        if args.live_only:
                            png = os.path.join(snap_dir, f"{slug}-{w}.png")
                            il.save(png)
                            with open(os.path.join(snap_dir, f"{slug}-{w}.json"), "w") as f:
                                json.dump({"url": url, "width": w, "height": args.height, "doc_height": pl["doc_height"],
                                           "theme": pl["theme"], "captured": datetime.datetime.now().isoformat(timespec="seconds"),
                                           "sections": pl["sections"]}, f, indent=1)
                            rec["files"] = {"snap": png}
                            log(f"{slug} {w}px: {len(pl['sections'])} sections, doc {pl['doc_height']}px -> {png} ({time.time() - t0:.1f}s)")
                            results.append(rec)
                            continue
                        po, io_ = page_capture(ours, w, args)
                        rec["ours"] = po
                        pairs, ul, uo = match_sections(pl["sections"], po["sections"], dict(m.split("=", 1) for m in (args.map or [])))
                        rows, first_top, first_h = [], None, None
                        for a, b, how in pairs:
                            r = {"key": a["key"], "ours_key": b["key"], "match": how, "live_top": a["top"], "ours_top": b["top"],
                                 "d_top": round(b["top"] - a["top"], 3), "live_h": a["height"], "ours_h": b["height"],
                                 "d_h": round(b["height"] - a["height"], 3), "live_rendered": a["rendered"], "ours_rendered": b["rendered"]}
                            if a["rendered"] and b["rendered"] and a["height"] > 0:
                                ca = il.crop((0, int(a["top"] * args.scale), il.width, min(il.height, int((a["top"] + a["height"]) * args.scale))))
                                cb = io_.crop((0, int(b["top"] * args.scale), io_.width, min(io_.height, int((b["top"] + b["height"]) * args.scale))))
                                if ca.height > 0 and cb.height > 0:
                                    r["diff_pct"] = diff_mask(ca, cb, args.threshold)[1]["diff_pct"]
                            if first_top is None and abs(r["d_top"]) > args.box_tol and a["rendered"]:
                                first_top = r["key"]
                            if first_h is None and abs(r["d_h"]) > args.box_tol and a["rendered"]:
                                first_h = r["key"]
                            rows.append(r)
                        mask, st = diff_mask(il, io_, args.threshold)
                        rec.update(st)
                        rec["sections"] = rows
                        rec["first_top_divergence"] = first_top
                        rec["first_height_divergence"] = first_h
                        rec["unmatched_live"] = [s["key"] for s in ul]
                        rec["unmatched_ours"] = [s["key"] for s in uo]
                        rec["unmatched_rows"] = ([{"side": "live", "key": s["key"], "top": s["top"], "h": s["height"], "rendered": s["rendered"]} for s in ul]
                                                 + [{"side": "ours", "key": s["key"], "top": s["top"], "h": s["height"], "rendered": s["rendered"]} for s in uo])
                        tag = f"{slug}-{w}"
                        files = {"live": os.path.join(out_dir, f"page-live-{tag}.png"), "ours": os.path.join(out_dir, f"page-ours-{tag}.png"),
                                 "diff": os.path.join(out_dir, f"page-diff-{tag}.png"), "side_by_side": os.path.join(out_dir, f"page-side-by-side-{tag}.png")}
                        il.save(files["live"])
                        io_.save(files["ours"])
                        heat = heatmap(il, io_, mask)
                        heat.save(files["diff"])
                        k = min(1.0, 720.0 / w)
                        sm = [im.resize((max(1, int(im.width * k)), max(1, int(im.height * k)))) for im in (il, io_, heat)]
                        side_by_side(sm, [f"LIVE {w}", f"OURS {w}", f"diff {st['diff_pct']}%"]).save(files["side_by_side"])
                        rec["files"] = files
                        results.append(rec)
                        log(f"{slug} {w}px: page diff {st['diff_pct']}%  first top divergence: {first_top}  first height "
                            f"divergence: {first_h}  unmatched {len(ul)}/{len(uo)} ({time.time() - t0:.1f}s)")
                    except WidthError as e:
                        errors.append({"url": url, "width": w, "error": str(e), "code": e.code})
                        log(f"{slug} {w}px: REFUSED — {e}")
        finally:
            for sd in (live, ours):
                if sd:
                    sd.close()
    write_page_report(out_dir, args, results, errors)
    print(f"live-parity page: " + " ".join(f"{r['slug']}@{r['width']}:{r.get('diff_pct', 'snap')}" for r in results)
          + (f" errors:{len(errors)}" if errors else "") + f"  -> {os.path.join(out_dir, 'report.md')}")
    return EXIT_WIDTH_ERRORS if errors else EXIT_OK


def write_page_report(out_dir, args, results, errors):
    with open(os.path.join(out_dir, "report.json"), "w") as f:
        json.dump({"tool": "lp-parity.py page", "command": " ".join(sys.argv), "results": results, "errors": errors}, f, indent=1, default=str)
    L = [f"# live-parity page", ""]
    for r in results:
        L.append(f"## {r['slug']} @ {r['width']}px")
        L.append(f"- live theme {r['live']['theme']}, doc height {r['live']['doc_height']}px")
        if "ours" not in r:
            L.append(f"- snapshot: `{r['files']['snap']}`")
            L.append("")
            L.append("| # | section id | top | height | rendered |")
            L.append("|---|---|---|---|---|")
            for i, sct in enumerate(r["live"]["sections"]):
                L.append(f"| {i} | `{sct['id']}` | {sct['top']} | {sct['height']} | {sct['rendered']} |")
            L.append("")
            continue
        L.append(f"- ours theme {r['ours']['theme']}, doc height {r['ours']['doc_height']}px")
        L.append(f"- full-page diff **{r['diff_pct']}%**; first section whose TOP diverges: **{r['first_top_divergence']}**; "
                 f"first whose HEIGHT differs: **{r['first_height_divergence']}**")
        L.append(f"- unmatched live {r['unmatched_live']} / ours {r['unmatched_ours']}")
        L.append(f"- per-section diff is cropped from the full-page captures at each side's own top (no sub-pixel alignment): use `section` for exact numbers")
        L.append("")
        L.append(f"![side by side]({os.path.basename(r['files']['side_by_side'])})")
        L.append("")
        L.append("| live key | ours key | match | live top | ours top | Δtop | live h | ours h | Δh | diff % |")
        L.append("|---|---|---|---|---|---|---|---|---|---|")
        for x in r["sections"]:
            L.append(f"| {x['key']} | {x['ours_key']} | {x['match']} | {x['live_top']} | {x['ours_top']} | {x['d_top']:+} | "
                     f"{x['live_h']} | {x['ours_h']} | {x['d_h']:+} | {x.get('diff_pct', '')} |")
        for x in sorted(r.get("unmatched_rows", []), key=lambda z: z["top"]):
            if x["side"] == "live":
                L.append(f"| {x['key']} | — | unmatched | {x['top']} | | | {x['h']} | | | {'' if x['rendered'] else '(not rendered)'} |")
            else:
                L.append(f"| — | {x['key']} | unmatched | | {x['top']} | | | {x['h']} | | {'' if x['rendered'] else '(not rendered)'} |")
        L.append("")
    for e in errors:
        L.append(f"- ERROR {e.get('url')} {e['width']}: {md_escape(e['error'])}")
    with open(os.path.join(out_dir, "report.md"), "w") as f:
        f.write("\n".join(L) + "\n")


# ----------------------------------------------------------------------------------------------------------------
# hoverstyles — forced :hover / :focus-visible / :active computed-style deltas
# ----------------------------------------------------------------------------------------------------------------
STATE_SETS = {"hover": ["hover"], "focus-visible": ["focus", "focus-visible"], "active": ["active", "hover"]}


def hover_probe(side, sel, states):
    data = side.lib(f"interactives({json.dumps(sel)})")
    if data.get("error"):
        raise Fatal(f"[{side.name}] selector {sel!r} matches nothing", EXIT_SELECTOR)
    els = data["elements"]
    side.cdp.call("DOM.enable")
    side.cdp.call("CSS.enable", timeout=60)
    try:
        doc = side.cdp.call("DOM.getDocument", {"depth": 0})
        ids = side.cdp.call("DOM.querySelectorAll", {"nodeId": doc["root"]["nodeId"], "selector": "[data-lpp-h]"})["nodeIds"]
        idmap = {}
        for nid in ids:
            attrs = side.cdp.call("DOM.getAttributes", {"nodeId": nid}).get("attributes", [])
            for k in range(0, len(attrs) - 1, 2):
                if attrs[k] == "data-lpp-h":
                    idmap[int(attrs[k + 1])] = nid
        for e in els:
            nid = idmap.get(e["i"])
            if nid is None:
                continue
            base = side.lib(f"hread({e['i']}, true)")
            e["states"] = {}
            for st in states:
                side.cdp.call("CSS.forcePseudoState", {"nodeId": nid, "forcedPseudoClasses": STATE_SETS[st]})
                after = side.lib(f"hread({e['i']}, true)")
                side.cdp.call("CSS.forcePseudoState", {"nodeId": nid, "forcedPseudoClasses": []})
                side.lib(f"hread({e['i']}, true)")
                delta = {}
                for part, props in (after or {}).items():
                    b = (base or {}).get(part, {})
                    for k, v in props.items():
                        if b.get(k) != v:
                            delta[f"{part}:{k}" if part != "self" else k] = [b.get(k), v]
                e["states"][st] = delta
    finally:
        try:
            side.cdp.call("CSS.disable")
            side.cdp.call("DOM.disable")
        except Exception:
            pass
    return els


def cmd_hoverstyles(args):
    widths = parse_widths(args.widths)
    out_dir = ensure_out(args.out)
    states = [x.strip() for x in args.states.split(",") if x.strip()]
    bad = [x for x in states if x not in STATE_SETS]
    if bad:
        raise Fatal(f"unknown --states {bad}; use {list(STATE_SETS)}", EXIT_USAGE)
    results, errors = [], []
    with Slot():
        live = ours = None
        try:
            live = Side("live", args.live_url, args.live_sel, args.live_theme, args)
            ours = Side("ours", args.ours_url, args.ours_sel, args.ours_theme, args)
            for w in widths:
                try:
                    got = {}
                    for sd, sel in ((live, args.live_sel), (ours, args.ours_sel)):
                        sd.load(w, args.height)
                        sd.check_viewport("load")
                        sd.prepare(sel)
                        sd.settle_section(sel)
                        sd.lib(f"hideOverlays({json.dumps(sel)}, {'true' if args.keep_fixed else 'false'})")
                        got[sd.name] = hover_probe(sd, sel, states)
                    L, O = got["live"], got["ours"]
                    pairs, ul, uo = pair_elements(L, O)
                    rows = []
                    for a, b, how in pairs:
                        diffs = {}
                        for st in states:
                            da, db = a.get("states", {}).get(st, {}), b.get("states", {}).get(st, {})
                            keys = sorted(set(da) | set(db))
                            d = {}
                            for k in keys:
                                va, vb = da.get(k), db.get(k)
                                if va is None and vb is not None:
                                    d[k] = {"live": "no change", "ours": f"{vb[0]} → {vb[1]}"}
                                elif vb is None and va is not None:
                                    d[k] = {"live": f"{va[0]} → {va[1]}", "ours": "no change"}
                                elif va[1] != vb[1]:
                                    d[k] = {"live": f"{va[0]} → {va[1]}", "ours": f"{vb[0]} → {vb[1]}"}
                            if d:
                                diffs[st] = d
                        tdiff = {k: [a["transition"].get(k), b["transition"].get(k)] for k in a.get("transition", {})
                                 if a["transition"].get(k) != b.get("transition", {}).get(k)}
                        rows.append({"label": el_label(dict(a, kind=a["kind"], text=a["text"] or a.get("aria", ""))),
                                     "ours_label": el_label(dict(b, kind=b["kind"], text=b["text"] or b.get("aria", ""))),
                                     "pairing": how, "state_deltas_live": {st: a.get("states", {}).get(st, {}) for st in states},
                                     "state_deltas_ours": {st: b.get("states", {}).get(st, {}) for st in states},
                                     "differences": diffs, "transition_differences": tdiff})
                    res = {"width": w, "paired": len(pairs), "rows": rows,
                           "unpaired_live": [el_label(dict(e, text=e["text"] or e.get("aria", ""))) for e in ul],
                           "unpaired_ours": [el_label(dict(e, text=e["text"] or e.get("aria", ""))) for e in uo],
                           "mismatching": sum(1 for r in rows if r["differences"] or r["transition_differences"])}
                    results.append(res)
                    log(f"hoverstyles {w}px: {len(pairs)} interactive pairs, {res['mismatching']} differ, unpaired {len(ul)}/{len(uo)}")
                except WidthError as e:
                    errors.append({"width": w, "error": str(e), "code": e.code})
        finally:
            for sd in (live, ours):
                if sd:
                    sd.close()
    with open(os.path.join(out_dir, "report.json"), "w") as f:
        json.dump({"tool": "lp-parity.py hoverstyles", "command": " ".join(sys.argv), "states": states, "results": results,
                   "errors": errors}, f, indent=1, default=str)
    L = ["# live-parity hoverstyles", "", f"- live `{args.live_url}` `{args.live_sel}`", f"- ours `{args.ours_url}` `{args.ours_sel}`",
         f"- states forced with CSS.forcePseudoState: {states} (focus-visible also forces :focus; active also :hover); transitions "
         f"are finished before reading, so values are END states", ""]
    for r in results:
        L.append(f"## {r['width']}px — {r['paired']} interactive elements paired, {r['mismatching']} differ")
        L.append("")
        L.append("| element | state | property | live | ours |")
        L.append("|---|---|---|---|---|")
        for row in r["rows"]:
            for st, d in row["differences"].items():
                for k, v in d.items():
                    L.append(f"| {md_escape(row['label'])} | {st} | {k} | {md_escape(v['live'])} | {md_escape(v['ours'])} |")
            for k, v in row["transition_differences"].items():
                L.append(f"| {md_escape(row['label'])} | (base) | {k} | {md_escape(v[0])} | {md_escape(v[1])} |")
        L.append("")
        L.append("What live does on each state (for your behaviour table):")
        L.append("")
        for row in r["rows"]:
            eff = "; ".join(f"{st}: " + ", ".join(f"{k} {v[0]}→{v[1]}" for k, v in d.items()) for st, d in row["state_deltas_live"].items() if d)
            L.append(f"- {md_escape(row['label'])}: {md_escape(eff) or 'no change in any state'}")
        L.append("")
        if r["unpaired_live"] or r["unpaired_ours"]:
            L.append(f"Unpaired live: {r['unpaired_live']}  ")
            L.append(f"Unpaired ours: {r['unpaired_ours']}")
            L.append("")
    for e in errors:
        L.append(f"- ERROR {e['width']}: {md_escape(e['error'])}")
    with open(os.path.join(out_dir, "report.md"), "w") as f:
        f.write("\n".join(L) + "\n")
    print(f"live-parity hoverstyles: " + " ".join(f"{r['width']}:{r['mismatching']}/{r['paired']} differ" for r in results)
          + f"  -> {os.path.join(out_dir, 'report.md')}")
    return EXIT_WIDTH_ERRORS if errors else EXIT_OK


# ----------------------------------------------------------------------------------------------------------------
# motion — time series after a trigger
# ----------------------------------------------------------------------------------------------------------------
NUM_RE = re.compile(r"-?\d+(?:\.\d+)?(?:e-?\d+)?")


def to_vec(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return [float(v)]
    v = str(v)
    if v in ("none", "auto", "normal"):
        return [1, 0, 0, 1, 0, 0] if v == "none" else [0.0]
    return [float(x) for x in NUM_RE.findall(v)] or [0.0]


def analyse_series(ts, vals):
    """ts: times (ms); vals: raw values. Returns start/end/duration/end value and a progress curve."""
    vecs = [to_vec(v) for v in vals]
    if not vecs or vecs[0] is None:
        return None
    v0 = vecs[0]
    changed = [i for i, v in enumerate(vecs) if v != v0]
    if not changed:
        return {"moved": False, "start": None, "end": None, "duration": 0, "first": vals[0], "last": vals[-1]}
    s_i = changed[0]
    e_i = max(i for i in range(1, len(vecs)) if vecs[i] != vecs[i - 1])
    vend = vecs[-1]
    n = min(len(v0), len(vend))
    comp = max(range(n), key=lambda k: abs(vend[k] - v0[k])) if n else 0
    span = (vend[comp] - v0[comp]) if n else 0
    t_s, t_e = ts[max(0, s_i - 1)], ts[e_i]
    curve = []
    for t, v in zip(ts, vecs):
        if t < t_s or t > t_e or v is None or len(v) <= comp:
            continue
        p = (v[comp] - v0[comp]) / span if span else 0.0
        curve.append((t, p))
    return {"moved": True, "start": round(t_s, 1), "end": round(t_e, 1), "duration": round(t_e - t_s, 1),
            "first": vals[0], "last": vals[-1], "curve": curve}


def curve_dev(ca, cb):
    """Max |progress_a(u) - progress_b(u)| over normalised time u in [0,1]."""
    def at(c, u):
        if not c:
            return None
        t0, t1 = c[0][0], c[-1][0]
        t = t0 + u * (t1 - t0)
        for (ta, pa), (tb, pb) in zip(c, c[1:]):
            if ta <= t <= tb:
                return pa if tb == ta else pa + (pb - pa) * (t - ta) / (tb - ta)
        return c[-1][1]
    devs = []
    for k in range(21):
        u = k / 20.0
        a, b = at(ca, u), at(cb, u)
        if a is not None and b is not None:
            devs.append(abs(a - b))
    return round(max(devs), 3) if devs else None


def motion_probe(side, sel, args, trigger, explicit):
    side.load(args.widths_cur, args.height)
    side.check_viewport("load")
    # no stepped scroll here: it would fire every scroll reveal before we watch it
    side.lib("eager()")
    end = time.time() + args.font_timeout
    while time.time() < end and side.lib("fonts()")["status"] != "loaded":
        side.cdp.pump(0.25)
    side.find(sel)
    if trigger in ("load",):
        side.cdp.pump(0.1)
    tg = side.lib(f"motionTargets({json.dumps(sel)}, {json.dumps(explicit or [])})")
    if tg.get("error"):
        raise Fatal(f"[{side.name}] selector {sel!r} matches nothing", EXIT_SELECTOR)
    props = [x.strip() for x in args.props.split(",") if x.strip()]
    kind, _, tsel = trigger.partition(":")
    pt = None
    side.lib(f"hideOverlays({json.dumps(sel)}, {'true' if args.keep_fixed else 'false'})")
    if kind in ("click", "hover", "tap"):
        pt = side.point_of(tsel, "trigger")
        side.cdp.pump(args.settle_ms / 1000.0)
    side.lib(f"sampleStart({json.dumps(sel)}, {json.dumps(props)}, {args.interval_ms}, {args.duration_ms})")
    if kind == "scroll-into-view":
        side.ev(f"document.querySelector({json.dumps(sel)}).scrollIntoView({{block: {json.dumps(args.scroll_block)}}})", "iso")
    elif kind == "click":
        side.cdp.call("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": pt[0], "y": pt[1]})
        side.cdp.call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": pt[0], "y": pt[1], "button": "left", "clickCount": 1})
        side.cdp.call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": pt[0], "y": pt[1], "button": "left", "clickCount": 1})
    elif kind == "tap":
        side.cdp.call("Input.synthesizeTapGesture", {"x": pt[0], "y": pt[1], "duration": 60, "tapCount": 1, "gestureSourceType": "touch"})
    elif kind == "hover":
        side.cdp.call("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": pt[0], "y": pt[1]})
    elif kind != "load":
        raise Fatal(f"unknown --trigger {trigger!r} (scroll-into-view | load | click:SEL | tap:SEL | hover:SEL)", EXIT_USAGE)
    side.cdp.pump(args.duration_ms / 1000.0 + 0.3)
    data = side.lib("sampleRead()")
    kf = side.lib(f"keyframes({json.dumps(sel)})") if args.keyframes else None
    if kf and kf.get("blocked"):
        kf["fetched"] = fetch_keyframes(kf["blocked"], set(kf["names"]) - set(kf["found"]))
    return tg["elements"], data, props, kf


def fetch_keyframes(urls, names):
    out = {}
    for u in urls[:20]:
        try:
            req = urllib.request.Request(u, headers={"User-Agent": UA_DESKTOP})
            css = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", "replace")
        except Exception:
            continue
        for m in re.finditer(r"@(?:-webkit-)?keyframes\s+([\w-]+)\s*\{((?:[^{}]*\{[^{}]*\})*[^{}]*)\}", css):
            if m.group(1) in names:
                out[m.group(1)] = {"css": re.sub(r"\s+", " ", m.group(0)), "sheet": u}
    return out


def cmd_motion(args):
    widths = parse_widths(args.widths)
    out_dir = ensure_out(args.out)
    tl, to_ = args.trigger_live or args.trigger, args.trigger_ours or args.trigger
    el_l = args.el_live or args.el or []
    el_o = args.el_ours or args.el or []
    results, errors = [], []
    with Slot():
        live = ours = None
        try:
            live = Side("live", args.live_url, args.live_sel, args.live_theme, args)
            ours = Side("ours", args.ours_url, args.ours_sel, args.ours_theme, args)
            for w in widths:
                args.widths_cur = w
                try:
                    tgl, dl, props, kfl = motion_probe(live, args.live_sel, args, tl, el_l)
                    tgo, do_, _, kfo = motion_probe(ours, args.ours_sel, args, to_, el_o)
                    if explicit_pairs := (el_l and el_o):
                        pairs = [(a, b, "given") for a, b in zip(tgl, tgo) if a and b]
                        ul, uo = [], []
                    else:
                        pairs, ul, uo = pair_elements([t for t in tgl if t], [t for t in tgo if t])
                    rows = []
                    for a, b, how in pairs:
                        row = {"label": el_label(a), "ours_label": el_label(b), "pairing": how,
                               "transition": {"live": a.get("transition"), "ours": b.get("transition")}, "props": {}}
                        for p in props:
                            sa = [(r["t"], r["v"].get(str(a["i"]), {}).get(p)) for r in (dl or {}).get("samples", [])]
                            sb = [(r["t"], r["v"].get(str(b["i"]), {}).get(p)) for r in (do_ or {}).get("samples", [])]
                            ra = analyse_series([t for t, _ in sa], [v for _, v in sa]) if sa else None
                            rb = analyse_series([t for t, _ in sb], [v for _, v in sb]) if sb else None
                            if not ra or not rb:
                                continue
                            if not ra["moved"] and not rb["moved"]:
                                continue
                            d = {"live": {k: ra[k] for k in ("moved", "start", "duration", "first", "last")},
                                 "ours": {k: rb[k] for k in ("moved", "start", "duration", "first", "last")}}
                            if ra["moved"] and rb["moved"]:
                                d["duration_delta_ms"] = round(rb["duration"] - ra["duration"], 1)
                                d["start_delta_ms"] = round(rb["start"] - ra["start"], 1)
                                d["easing_max_dev"] = curve_dev(ra["curve"], rb["curve"])
                            d["end_equal"] = ra["last"] == rb["last"]
                            row["props"][p] = d
                        key = lambda x: (x["kind"], x["what"])
                        an_l = sorted([x for x in (dl or {}).get("anims", []) if x["target"] == str(a["i"])], key=key)
                        an_o = sorted([x for x in (do_ or {}).get("anims", []) if x["target"] == str(b["i"])], key=key)
                        if an_l or an_o:
                            row["animations"] = {"live": an_l, "ours": an_o}
                            fields = ("duration", "delay", "easing", "iterations", "direction", "fill")
                            dl_ = {key(x): x for x in an_l}
                            do2 = {key(x): x for x in an_o}
                            row["animation_differences"] = []
                            for k in sorted(set(dl_) | set(do2)):
                                x, y = dl_.get(k), do2.get(k)
                                if not x or not y:
                                    row["animation_differences"].append({"what": f"{k[0]} {k[1]}", "live": x and "present" or "absent",
                                                                          "ours": y and "present" or "absent"})
                                    continue
                                for fdn in fields:
                                    if x.get(fdn) != y.get(fdn):
                                        row["animation_differences"].append({"what": f"{k[0]} {k[1]} {fdn}", "live": x.get(fdn), "ours": y.get(fdn)})
                        if row["props"] or row.get("animations") or row["transition"]["live"] != row["transition"]["ours"]:
                            rows.append(row)
                    kfd = None
                    if args.keyframes:
                        fa = dict((kfl or {}).get("found", {}), **(kfl or {}).get("fetched", {}))
                        fb = dict((kfo or {}).get("found", {}), **(kfo or {}).get("fetched", {}))
                        kfd = {"live_names": (kfl or {}).get("names"), "ours_names": (kfo or {}).get("names"),
                               "live": fa, "ours": fb,
                               "same_name_different_body": [n for n in set(fa) & set(fb)
                                                            if re.sub(r"\s+", "", fa[n]["css"]) != re.sub(r"\s+", "", fb[n]["css"])]}
                    res = {"width": w, "trigger": {"live": tl, "ours": to_}, "props": props, "interval_ms": args.interval_ms,
                           "duration_ms": args.duration_ms, "samples": {"live": len((dl or {}).get("samples", [])),
                                                                        "ours": len((do_ or {}).get("samples", []))},
                           "targets": {"live": len([t for t in tgl if t]), "ours": len([t for t in tgo if t])},
                           "rows": rows, "unpaired_live": [el_label(e) for e in ul], "unpaired_ours": [el_label(e) for e in uo],
                           "keyframes": kfd}
                    if args.raw:
                        res["raw"] = {"live": dl, "ours": do_}
                    results.append(res)
                    log(f"motion {w}px: {len(pairs)} animated pairs, {len(rows)} with motion or transition differences; "
                        f"samples {res['samples']}")
                except WidthError as e:
                    errors.append({"width": w, "error": str(e), "code": e.code})
        finally:
            for sd in (live, ours):
                if sd:
                    sd.close()
    with open(os.path.join(out_dir, "report.json"), "w") as f:
        json.dump({"tool": "lp-parity.py motion", "command": " ".join(sys.argv), "results": results, "errors": errors}, f, indent=1, default=str)
    L = ["# live-parity motion", "", f"- live `{args.live_url}` `{args.live_sel}` trigger `{tl}`",
         f"- ours `{args.ours_url}` `{args.ours_sel}` trigger `{to_}`",
         f"- sampled with requestAnimationFrame every ≥{args.interval_ms}ms for {args.duration_ms}ms; times are ms after the trigger. "
         f"easing_max_dev = max |progress_live(u) − progress_ours(u)| over normalised time (0 = same curve, 1 = opposite).", ""]
    for r in results:
        L.append(f"## {r['width']}px — targets live {r['targets']['live']} / ours {r['targets']['ours']}, samples {r['samples']}")
        L.append("")
        L.append("| element | prop | live start / duration | ours start / duration | Δduration | easing dev | end live → ours |")
        L.append("|---|---|---|---|---|---|---|")
        for row in r["rows"]:
            for p, d in row["props"].items():
                lv, ov = d["live"], d["ours"]
                L.append(f"| {md_escape(row['label'])} | {p} | {lv['start']} / {lv['duration']} | {ov['start']} / {ov['duration']} | "
                         f"{d.get('duration_delta_ms', '')} | {d.get('easing_max_dev', '')} | "
                         f"{md_escape(str(lv['last'])[:60])} → {md_escape(str(ov['last'])[:60])}{'' if d['end_equal'] else ' **≠**'} |")
        L.append("")
        L.append("Web Animations seen on the targets during the window (exact declared timing — prefer these over the sampled curve):")
        L.append("")
        L.append("| element | animation | live duration / delay / easing | ours duration / delay / easing | differences |")
        L.append("|---|---|---|---|---|")
        for row in r["rows"]:
            al = {(x["kind"], x["what"]): x for x in row.get("animations", {}).get("live", [])}
            ao = {(x["kind"], x["what"]): x for x in row.get("animations", {}).get("ours", [])}
            for k in sorted(set(al) | set(ao)):
                x, y = al.get(k), ao.get(k)
                fmt = lambda z: f"{z['duration']}ms / {z['delay']}ms / {z['easing']}" + (f" ×{z['iterations']}" if z.get('iterations') not in (1, None) else "") if z else "—"
                dif = [d for d in row.get("animation_differences", []) if d["what"].startswith(f"{k[0]} {k[1]}")]
                L.append(f"| {md_escape(row['label'])} | {k[0]} {k[1]} | {fmt(x)} | {fmt(y)} | {md_escape('; '.join(str(d['what']).split(' ')[-1] + ': ' + str(d['live']) + ' → ' + str(d['ours']) for d in dif)) or 'same'} |")
        L.append("")
        L.append("Transitions declared (live → ours):")
        for row in r["rows"]:
            tl_, to2 = row["transition"]["live"] or {}, row["transition"]["ours"] or {}
            diff = {k: (tl_.get(k), to2.get(k)) for k in tl_ if tl_.get(k) != to2.get(k)}
            if diff:
                L.append(f"- {md_escape(row['label'])}: " + "; ".join(f"{k}: {a} → {b}" for k, (a, b) in diff.items()))
        L.append("")
        if r.get("keyframes"):
            k = r["keyframes"]
            L.append(f"Keyframes used — live {k['live_names']} / ours {k['ours_names']}; same name, different body: {k['same_name_different_body']}")
            for side_name in ("live", "ours"):
                for n, v in k[side_name].items():
                    L.append(f"- {side_name} `{n}`: `{md_escape(v['css'][:300])}`")
            L.append("")
        if r["unpaired_live"] or r["unpaired_ours"]:
            L.append(f"Unpaired animated elements — live: {r['unpaired_live']} / ours: {r['unpaired_ours']}")
            L.append("")
    for e in errors:
        L.append(f"- ERROR {e['width']}: {md_escape(e['error'])}")
    with open(os.path.join(out_dir, "report.md"), "w") as f:
        f.write("\n".join(L) + "\n")
    print(f"live-parity motion: " + " ".join(f"{r['width']}:{len(r['rows'])} rows" for r in results) + f"  -> {os.path.join(out_dir, 'report.md')}")
    return EXIT_WIDTH_ERRORS if errors else EXIT_OK


def parse_widths(s):
    try:
        ws = [int(x) for x in str(s).split(",") if x.strip()]
    except ValueError:
        raise Fatal(f"--widths must be comma-separated integers, got {s!r}", EXIT_USAGE)
    if not ws or any(w < 200 or w > 3840 for w in ws):
        raise Fatal(f"--widths out of range: {s!r}", EXIT_USAGE)
    return ws


def ensure_out(path):
    os.makedirs(path, exist_ok=True)
    return path


def cmd_section(args, mode="section"):
    widths = parse_widths(args.widths)
    out_dir = ensure_out(args.out)
    steps = None
    if mode == "states":
        steps = load_steps(args.steps)
    meta = {"mode": mode, "title": args.title or "", "live_url": args.live_url, "live_sel": args.live_sel,
            "ours_url": args.ours_url, "ours_sel": args.ours_sel, "threshold": args.threshold, "box_tol": args.box_tol,
            "scale": args.scale, "height": args.height, "mobile_below": args.mobile_below, "freeze": args.freeze,
            "carousel_reset": args.carousel_reset, "align_fraction": args.align_fraction, "keep_fixed": args.keep_fixed,
            "settle_ms": args.settle_ms, "stability_ms": args.stability_ms, "widths": widths, "steps": steps}
    results, errors = [], []
    cmdline = " ".join(sys.argv)
    with Slot():
        live = ours = None
        try:
            live = Side("live", args.live_url, args.live_sel, args.live_theme, args)
            ours = Side("ours", args.ours_url, args.ours_sel, args.ours_theme, args)
            meta["chrome"] = live.browser.version
            for w in widths:
                t0 = time.time()
                try:
                    r = section_at_width(live, ours, w, args, out_dir, steps)
                    meta["live_theme"] = r["live"]["theme"]
                    meta["ours_theme"] = r["ours"]["theme"]
                    results.append(r)
                    el = r.get("elements") or {}
                    log(f"{w}px: {r.get('status')} diff {r.get('diff_pct')}%  boxes-off {el.get('box_deltas', '-')}  "
                        f"style-deltas {el.get('style_deltas', '-')}  unpaired {len(el.get('unpaired_live', []))}/"
                        f"{len(el.get('unpaired_ours', []))}  Δh {r.get('section_box', {}).get('delta', {}).get('h', '-')}  "
                        f"({time.time() - t0:.1f}s)")
                except WidthError as e:
                    errors.append({"width": w, "error": str(e), "code": e.code})
                    log(f"{w}px: REFUSED — {e}")
                write_section_report(out_dir, meta, results, errors, cmdline)
        finally:
            for s in (live, ours):
                if s:
                    s.close()
    write_section_report(out_dir, meta, results, errors, cmdline)
    print(summary_line(out_dir, results, errors))
    if errors:
        return max(e["code"] for e in errors) if all(e["code"] != EXIT_WIDTH_ERRORS for e in errors) else EXIT_WIDTH_ERRORS
    if args.fail_on_diff and any((r.get("diff_pct") or 0) > args.fail_on_diff_above for r in results):
        return EXIT_DIFF
    return EXIT_OK


def summary_line(out_dir, results, errors):
    parts = []
    for r in results:
        parts.append(f"{r['width']}:{r.get('diff_pct')}%" + ("" if r.get("status") == "compared" else f"({r.get('status')})"))
    for e in errors:
        parts.append(f"{e['width']}:ERROR")
    return f"live-parity: {' '.join(parts)}  -> {os.path.join(out_dir, 'report.md')}"


def load_steps(spec):
    if not spec:
        raise Fatal("states needs --steps (a JSON list or @file.json)", EXIT_USAGE)
    try:
        if spec.startswith("@"):
            return json.load(open(spec[1:]))
        if os.path.exists(spec):
            return json.load(open(spec))
        return json.loads(spec)
    except (OSError, json.JSONDecodeError) as e:
        raise Fatal(f"--steps is not valid JSON: {e}", EXIT_USAGE)


def add_common(p, need_pair=True):
    p.add_argument("--live-url", required=need_pair, help="live page URL (the reference side)")
    p.add_argument("--ours-url", required=need_pair, help="our preview URL (…?preview_theme_id=THEME&view=zzt-x)")
    p.add_argument("--live-sel", help="CSS selector for live's section, e.g. '[id$=\"__slidersection_QrQG3X\"]'")
    p.add_argument("--ours-sel", help="CSS selector for our section, e.g. '[id$=\"slidersection_QrQG3X\"]'")
    p.add_argument("--key", help="live section key; sets --live-sel [id$=\"__KEY\"] and --ours-sel [id$=\"KEY\"]")
    p.add_argument("--widths", default=DEFAULT_WIDTHS)
    p.add_argument("--height", type=int, default=900, help="viewport height (both sides; affects vh units)")
    p.add_argument("--out", required=True, help="output directory")
    p.add_argument("--title", default="")
    p.add_argument("--threshold", type=int, default=30, help="pixel counts when |dR|+|dG|+|dB| > this")
    p.add_argument("--box-tol", type=float, default=0.5, help="box delta tolerance in CSS px")
    p.add_argument("--scale", type=int, default=1, help="deviceScaleFactor (1 = CSS px)")
    p.add_argument("--mobile-below", type=int, default=750, help="mobile emulation (touch, mobile UA) below this width")
    p.add_argument("--settle-ms", type=int, default=900, help="wait after scrolling the section into view")
    p.add_argument("--scroll-pause-ms", type=int, default=140, help="pause per step of the lazy-load scroll")
    p.add_argument("--scroll-margin", type=int, default=0, help="scroll the section to this many px below the top")
    p.add_argument("--stability-ms", type=int, default=500, help="second capture after N ms to detect motion (0=off)")
    p.add_argument("--img-timeout", type=float, default=25)
    p.add_argument("--font-timeout", type=float, default=10)
    p.add_argument("--load-timeout", type=float, default=60)
    p.add_argument("--image-selector", default=None, help="also diff each paired element matching this selector")
    p.add_argument("--keep-fixed", action="store_true", help="do not hide fixed/sticky elements (known overlays still hidden)")
    p.add_argument("--no-freeze", dest="freeze", action="store_false", help="leave animations/carousels/videos running")
    p.add_argument("--no-carousel-reset", dest="carousel_reset", action="store_false", help="freeze carousels where they are")
    p.add_argument("--no-align-fraction", dest="align_fraction", action="store_false")
    p.add_argument("--no-fonts", dest="fonts", action="store_false", help="skip the rendered-font probe")
    p.add_argument("--allow-blank", action="store_true")
    p.add_argument("--allow-overflow-x", action="store_true", help="capture beyond the viewport width")
    p.add_argument("--include-overflow", action="store_true", help="extend the capture over content painted outside the "
                                                                  "section box (up to 400px, top/bottom)")
    p.add_argument("--live-theme", default="main", help="expected theme on the live side: main | <id> | any")
    p.add_argument("--ours-theme", default=None, help="expected theme on our side: <id> | any "
                                                        "(default: the preview_theme_id in --ours-url, else any)")
    p.add_argument("--fail-on-diff", action="store_true", help="exit 1 when any width's diff exceeds --fail-on-diff-above")
    p.add_argument("--fail-on-diff-above", type=float, default=0.0)
    p.add_argument("--quiet", action="store_true")


def finalize_selectors(args):
    if getattr(args, "key", None):
        args.live_sel = args.live_sel or f'[id$="__{args.key}"]'
        args.ours_sel = args.ours_sel or f'[id$="{args.key}"]'
    if not args.live_sel or not args.ours_sel:
        raise Fatal("give --key KEY, or both --live-sel and --ours-sel", EXIT_USAGE)


def preview_id(url):
    if not url:
        return None
    q = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(url).query))
    return q.get("preview_theme_id") or None


def with_preview(url, theme_id):
    u = urllib.parse.urlsplit(url)
    q = [(k, v) for k, v in urllib.parse.parse_qsl(u.query, keep_blank_values=True) if k != "preview_theme_id"]
    if theme_id:
        q.insert(0, ("preview_theme_id", str(theme_id)))
    return urllib.parse.urlunsplit((u.scheme, u.netloc, u.path, urllib.parse.urlencode(q), u.fragment))


def main(argv):
    global QUIET
    import atexit
    import signal
    atexit.register(close_all_browsers)
    for sg in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        signal.signal(sg, _on_signal)
    ap = argparse.ArgumentParser(prog="live-parity.py", description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("section", help="compare one section live vs ours at many widths")
    add_common(p)
    p = sub.add_parser("regress", help="section, with the live side = QA-approved Main theme")
    add_common(p, need_pair=False)
    p.add_argument("--url", help="page URL without preview param; builds both sides (Main vs dev theme)")
    p.add_argument("--main-theme", default=None, help="the QA-approved main theme id (shopify theme list)")
    p = sub.add_parser("states", help="replay steps on both sides, then compare the section")
    add_common(p)
    p.add_argument("--steps", required=True, help='JSON list or @file: [{"do":"click","sel":"summary"},{"do":"wait","ms":400}]')
    p = sub.add_parser("page", help="every top-level section: top/height per side, first divergence, full-page diff")
    add_common(p, need_pair=False)
    p.add_argument("--live-only", action="store_true", help="only capture live: writes <out>/live-snap/<slug>-<width>.png/.json")
    p.add_argument("--pages", help="with --live-only: comma-separated live URLs, captured one after another in one browser")
    p.add_argument("--slug", help="file name stem (default: last URL path segment)")
    p.add_argument("--map", action="append", help="pair sections whose keys differ: LIVEKEY=OURSKEY (repeatable)")
    p.set_defaults(widths="1440,393")
    p = sub.add_parser("hoverstyles", help="forced :hover/:focus-visible/:active computed-style deltas, live vs ours")
    add_common(p)
    p.add_argument("--states", default="hover,focus-visible,active")
    p.set_defaults(widths="1440")
    p = sub.add_parser("motion", help="sample properties after a trigger on both sides; --keyframes")
    add_common(p)
    p.add_argument("--trigger", default="scroll-into-view", help="scroll-into-view | load | click:SEL | tap:SEL | hover:SEL")
    p.add_argument("--trigger-live")
    p.add_argument("--trigger-ours")
    p.add_argument("--el", action="append", help="element(s) to sample, both sides (default: every element in the section "
                                                 "with a transition or animation)")
    p.add_argument("--el-live", action="append")
    p.add_argument("--el-ours", action="append")
    p.add_argument("--props", default="opacity,transform,y,h")
    p.add_argument("--interval-ms", type=int, default=50)
    p.add_argument("--duration-ms", type=int, default=1500)
    p.add_argument("--scroll-block", default="center", help="scrollIntoView block for the scroll-into-view trigger")
    p.add_argument("--keyframes", action="store_true")
    p.add_argument("--raw", action="store_true", help="keep every sample in report.json")
    p.set_defaults(widths="1440")
    args = ap.parse_args(argv)
    QUIET = getattr(args, "quiet", False)
    global DEV_THEME_ID
    DEV_THEME_ID = args.ours_theme or preview_id(getattr(args, "ours_url", None)) or "any"
    args.ours_theme = DEV_THEME_ID
    if DEV_THEME_ID == "any" and getattr(args, "ours_url", None):
        log("note: no --ours-theme and no preview_theme_id in --ours-url — our side's theme is not asserted")
    try:
        if args.cmd == "regress":
            if not args.main_theme:
                raise Fatal("regress needs --main-theme <id> (the QA-approved theme, from `shopify theme list`)", EXIT_USAGE)
            if args.url:
                if DEV_THEME_ID == "any":
                    raise Fatal("regress --url needs --ours-theme <dev theme id> to build our side's preview URL", EXIT_USAGE)
                args.live_url = args.live_url or with_preview(args.url, args.main_theme)
                args.ours_url = args.ours_url or with_preview(args.url, DEV_THEME_ID)
            if not args.live_url or not args.ours_url:
                raise Fatal("regress needs --url, or --live-url (main-theme preview) and --ours-url", EXIT_USAGE)
            if "preview_theme_id" not in args.live_url:
                args.live_url = with_preview(args.live_url, args.main_theme)
            args.live_theme = args.main_theme if args.live_theme == "main" else args.live_theme
            finalize_selectors(args)
            return cmd_section(args, "regress")
        if args.cmd == "page":
            if args.live_only:
                args.ours_url = None
            return cmd_page(args)
        finalize_selectors(args)
        if args.cmd == "hoverstyles":
            return cmd_hoverstyles(args)
        if args.cmd == "motion":
            return cmd_motion(args)
        if args.cmd == "section":
            return cmd_section(args, "section")
        if args.cmd == "states":
            return cmd_section(args, "states")
    except Fatal as e:
        print(f"live-parity: ERROR: {e}", file=sys.stderr)
        return e.code
    except KeyboardInterrupt:
        return 130
    except Exception as e:
        traceback.print_exc()
        print(f"live-parity: INTERNAL ERROR: {e}", file=sys.stderr)
        return EXIT_INTERNAL
    return EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
