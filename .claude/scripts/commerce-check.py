#!/usr/bin/env python3
"""commerce-check.py — walk the purchase path on OUR theme and prove each step with the engine's own event.

Usage
-----
  python3 .claude/scripts/commerce-check.py --url <product page URL> [--widths 393,768,1024,1440]
      [--discount-code CODE] [--market CC] [--out .claude/verify/commerce] [--allow-live] [--no-mutate]
  --no-mutate checks the engine only, adds nothing. Exit 0 every step passed, 1 any failed, 2 usage, 3+ as live-parity.py.

Notes:
- Steps per width: engine (window.Cart, #cart-data), add, change (properties kept), discount, remove, market; the cart
  is emptied at the end. Not covered, and the report says so: a logged-in customer, Safari, checkout.
- Each result is read from the engine's `cart:change` event, never after a sleep: a stale DOM looks exactly like a broken cart.
- The rendered theme is asserted from Shopify.theme: a leaked preview cookie makes "ours" the live theme (refused unless --allow-live).
- Analytics hosts are blocked so test adds fire no pixels; one Chrome, one run slot, closed on exit (via live-parity.py).
"""

import datetime
import importlib.util
import json
import os
import sys
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("live_parity", os.path.join(HERE, "live-parity.py"))
lp = importlib.util.module_from_spec(spec)
sys.modules["live_parity"] = lp
spec.loader.exec_module(lp)

BLOCKED = ["*google-analytics.com*", "*analytics.google.com*", "*googletagmanager.com*", "*googleadservices.com*",
           "*doubleclick.net*", "*facebook.com/tr*", "*connect.facebook.net*", "*analytics.tiktok.com*",
           "*ct.pinterest.com*", "*klaviyo.com/client*", "*kmail-lists.com*", "*hotjar.com*", "*clarity.ms*",
           "*northbeam*", "*triplewhale*", "*elevar*", "*attn.tv*", "*postscript.io*", "*/checkouts/*", "*/checkout*"]

WAIT_CHANGE = """
new Promise((res, rej) => {
  const t = setTimeout(() => { document.removeEventListener('cart:change', h); rej(new Error('no cart:change within %dms')); }, %d);
  function h(e) { clearTimeout(t); document.removeEventListener('cart:change', h);
    setTimeout(() => res({ action: e.detail.action, count: e.detail.cart && e.detail.cart.item_count,
      items: (e.detail.cart && e.detail.cart.items || []).map(i => ({ key: i.key, q: i.quantity, props: i.properties || {}, plan: i.selling_plan_allocation ? i.selling_plan_allocation.selling_plan.id : null })) }), 200); }
  document.addEventListener('cart:change', h);
  try { %s } catch (e) { clearTimeout(t); document.removeEventListener('cart:change', h); rej(e); }
})
"""


def ev(c, js, timeout=40):
    r = c.call("Runtime.evaluate", {"expression": js, "returnByValue": True, "awaitPromise": True}, timeout=timeout)
    if r.get("exceptionDetails"):
        d = r["exceptionDetails"]
        raise RuntimeError(str((d.get("exception") or {}).get("description") or d.get("text"))[:300])
    return r.get("result", {}).get("value")


def wait_change(c, trigger_js, ms=20000):
    return ev(c, WAIT_CHANGE % (ms, ms, trigger_js), timeout=ms / 1000 + 10)


def load(c, url, width):
    mobile = width < 750
    c.call("Emulation.setDeviceMetricsOverride", {"width": width, "height": 900, "deviceScaleFactor": 1, "mobile": mobile,
                                                  "screenWidth": width, "screenHeight": 900})
    c.call("Emulation.setTouchEmulationEnabled", {"enabled": mobile, "maxTouchPoints": 5} if mobile else {"enabled": False})
    c.call("Page.navigate", {"url": url})
    c.wait_event("Page.loadEventFired", timeout=60)
    c.pump(2.5)
    return ev(c, "({ theme: (window.Shopify && window.Shopify.theme) || null, width: document.documentElement.clientWidth,"
                 " country: window.Shopify && window.Shopify.country, currency: window.Shopify && window.Shopify.currency && window.Shopify.currency.active })")


def main(argv):
    args = {"--widths": "393,768,1024,1440", "--out": ".claude/verify/commerce", "--discount-code": None, "--market": None, "--url": None}
    flags = {"--allow-live": False, "--no-mutate": False}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in flags:
            flags[a] = True
        elif a in args and i + 1 < len(argv):
            args[a] = argv[i + 1]
            i += 1
        elif a in ("-h", "--help"):
            print(__doc__)
            return 0
        else:
            print(f"commerce-check: unknown argument {a!r}\n{__doc__}", file=sys.stderr)
            return 2
        i += 1
    if not args["--url"]:
        print("commerce-check: --url <product page URL> is required\n" + __doc__, file=sys.stderr)
        return 2
    url = args["--url"]
    try:
        widths = [int(w) for w in args["--widths"].split(",") if w.strip()]
    except ValueError:
        print("commerce-check: --widths must be comma-separated integers", file=sys.stderr)
        return 2
    expect_theme = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query).get("preview_theme_id", [None])[0]
    os.makedirs(args["--out"], exist_ok=True)

    results, failed = [], False

    def row(width, step, ok, evidence):
        nonlocal failed
        results.append({"width": width, "step": step, "ok": ok, "evidence": evidence})
        failed = failed or ok is False
        lp.log(f"{width:>5} {step:<9} {'ok  ' if ok else 'SKIP' if ok is None else 'FAIL'}  {evidence}")

    with lp.Slot():
        b = lp.Browser("commerce")
        c = b.cdp
        try:
            c.call("Page.enable"); c.call("Runtime.enable"); c.call("Network.enable")
            c.call("Network.setBlockedURLs", {"urls": BLOCKED})
            for width in widths:
                info = load(c, url, width)
                if info["width"] != width:
                    row(width, "viewport", False, f"page laid out at {info['width']}px, not {width}")
                    continue
                th = info.get("theme") or {}
                if not th:
                    row(width, "theme", False, "no Shopify.theme on the page — not a storefront render?")
                    continue
                if th.get("role") == "main" and not flags["--allow-live"]:
                    row(width, "theme", False, f"the page rendered the LIVE theme {th.get('id')} ({th.get('name')}); pass the dev "
                                               "theme's preview URL, or --allow-live to walk the published theme")
                    break
                if expect_theme and str(th.get("id")) != str(expect_theme):
                    row(width, "theme", False, f"expected theme {expect_theme}, page rendered {th.get('id')} ({th.get('name')})")
                    break
                row(width, "theme", True, f"{th.get('id')} {th.get('name')} role={th.get('role')}")

                engine = ev(c, "({ cart: typeof window.Cart === 'object' && ['add','change','update','refresh'].every(k => typeof window.Cart[k] === 'function'),"
                               " seeded: !!(window.Cart && window.Cart.state && typeof window.Cart.state.item_count === 'number'),"
                               " form: !!document.querySelector('form[action*=\"/cart/add\"]'),"
                               " drawer: !!document.querySelector('cart-drawer'), page: !!document.querySelector('cart-page'),"
                               " discount: !!document.querySelector('cart-discount-form'), localization: !!document.querySelector('localization-form') })")
                row(width, "engine", engine["cart"] and engine["seeded"], json.dumps(engine))
                if not (engine["cart"] and engine["form"]) or flags["--no-mutate"]:
                    if flags["--no-mutate"]:
                        row(width, "add", None, "--no-mutate")
                    continue

                # make sure the cart starts empty so counts are absolute
                ev(c, "fetch('/cart/clear.js', {method: 'POST'}).then(r => r.json()).then(() => window.Cart.refresh())", timeout=40)
                c.pump(0.5)
                try:
                    r = wait_change(c, "document.querySelector('form[action*=\"/cart/add\"]').requestSubmit();")
                    opened = ev(c, "(() => { const d = document.querySelector('cart-drawer'); if (!d) return 'no drawer';"
                                   " return d.classList.contains('cart-open') || d.hasAttribute('open') || d.matches('[aria-hidden=\"false\"]') ? 'open' : 'closed'; })()")
                    count_el = ev(c, "(document.querySelector('[data-cart-count]') || {}).textContent")
                    ok = r["action"] == "add" and r["count"] == 1 and opened != "closed" and str(count_el).strip() == "1"
                    row(width, "add", ok, f"action={r['action']} item_count={r['count']} drawer={opened} count-el={str(count_el).strip()!r}")
                except RuntimeError as e:
                    row(width, "add", False, str(e))
                    continue
                before = r["items"][0] if r["items"] else {}

                try:
                    r = wait_change(c, "(() => { const a = document.querySelector('.cart-quantity a[href*=\"/cart/change\"][href*=\"quantity=2\"], a[href*=\"/cart/change\"][href*=\"quantity=2\"]);"
                                        " if (!a) throw new Error('no quantity-2 stepper link in the rendered cart'); a.click(); })();", ms=25000)
                    after = r["items"][0] if r["items"] else {}
                    ok = r["action"] == "change" and after.get("q") == 2 and after.get("props") == before.get("props") and after.get("plan") == before.get("plan")
                    row(width, "change", ok, f"quantity={after.get('q')} properties kept={after.get('props') == before.get('props')} plan kept={after.get('plan') == before.get('plan')}")
                except RuntimeError as e:
                    row(width, "change", False, str(e))

                if args["--discount-code"]:
                    code = args["--discount-code"]
                    try:
                        has_form = ev(c, "!!document.querySelector('cart-discount-form input, form[action*=\"/discount\"] input')")
                        if not has_form:
                            row(width, "discount", False, "no discount input rendered in the cart")
                        else:
                            r = wait_change(c, "(() => { const i = document.querySelector('cart-discount-form input, form[action*=\"/discount\"] input');"
                                               " i.value = %s; i.dispatchEvent(new Event('input', {bubbles: true}));"
                                               " const f = i.closest('form'); if (f) f.requestSubmit(); else i.dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter', bubbles: true})); })();" % json.dumps(code), ms=25000)
                            codes = ev(c, "fetch('/cart.js').then(r => r.json()).then(c => (c.discount_codes || []).map(d => d.code + ':' + d.applicable))", timeout=40)
                            ok = any(x.lower().startswith(code.lower() + ":true") for x in codes)
                            row(width, "discount", ok, f"/cart.js discount_codes={codes} after action={r['action']}")
                    except RuntimeError as e:
                        row(width, "discount", False, str(e))

                try:
                    r = wait_change(c, "(() => { const a = document.querySelector('.cart-item__remove a[href*=\"/cart/change\"], a[href*=\"/cart/change\"][href*=\"quantity=0\"]);"
                                        " if (!a) throw new Error('no remove link in the rendered cart'); a.click(); })();", ms=25000)
                    empty = ev(c, "(() => { const d = document.querySelector('cart-drawer, cart-page'); if (!d) return null;"
                                  " const t = (d.innerText || '').toLowerCase(); return /empty|nothing in your cart|no items/.test(t) || !d.querySelector('.cart-item'); })()")
                    row(width, "remove", r["count"] == 0 and bool(empty), f"item_count={r['count']} empty-state={empty}")
                except RuntimeError as e:
                    row(width, "remove", False, str(e))

                if args["--market"]:
                    cc = args["--market"].upper()
                    try:
                        before_c = (info.get("country"), info.get("currency"))
                        switched = ev(c, "(() => { const f = document.querySelector('localization-form form'); if (!f) return 'no form';"
                                         " const sel = f.querySelector('select[name=\"country_code\"], input[name=\"country_code\"]'); if (!sel) return 'no country field';"
                                         " if (sel.tagName === 'SELECT') { if (![...sel.options].some(o => o.value === %s)) return 'country not offered'; sel.value = %s; }"
                                         " else sel.value = %s; f.submit(); return 'submitted'; })()" % ((json.dumps(cc),) * 3))
                        if switched != "submitted":
                            row(width, "market", False, switched)
                        else:
                            c.wait_event("Page.loadEventFired", timeout=60); c.pump(2)
                            now = ev(c, "({ country: window.Shopify && window.Shopify.country, currency: window.Shopify && window.Shopify.currency && window.Shopify.currency.active,"
                                        " price: (document.querySelector('.price, [class*=price]') || {}).textContent })")
                            ok = now["country"] == cc
                            row(width, "market", ok, f"{before_c} -> ({now['country']}, {now['currency']}) price={str(now.get('price') or '').strip()[:30]!r}")
                            if before_c[0]:
                                ev(c, "(() => { const f = document.querySelector('localization-form form'); const s = f && f.querySelector('[name=\"country_code\"]');"
                                      " if (s) { s.value = %s; f.submit(); } })()" % json.dumps(before_c[0]))
                                try:
                                    c.wait_event("Page.loadEventFired", timeout=60)
                                except Exception:
                                    pass
                    except RuntimeError as e:
                        row(width, "market", False, str(e))
                row(width, "logged-in", None, "not automated — log in once in the browser pane and walk add/change/remove by hand")
            try:
                ev(c, "fetch('/cart/clear.js', {method: 'POST'})", timeout=30)
            except Exception:
                pass
        finally:
            b.close()

    report = {"url": url, "generated": datetime.datetime.now().isoformat(timespec="seconds"), "widths": widths,
              "discount_code": bool(args["--discount-code"]), "market": args["--market"], "mutated": not flags["--no-mutate"],
              "steps": results, "passed": sum(1 for r in results if r["ok"]), "failed": sum(1 for r in results if r["ok"] is False),
              "skipped": sum(1 for r in results if r["ok"] is None), "not_automated": ["logged-in", "safari", "checkout"]}
    with open(os.path.join(args["--out"], "report.json"), "w") as f:
        json.dump(report, f, indent=2)
    lines = [f"# Commerce check — {url}", "", f"Generated {report['generated']}; {report['passed']} passed, {report['failed']} failed, {report['skipped']} skipped.", "",
             "| width | step | result | evidence |", "|---|---|---|---|"]
    for r in results:
        lines.append(f"| {r['width']} | {r['step']} | {'ok' if r['ok'] else 'skip' if r['ok'] is None else '**FAIL**'} | {r['evidence'].replace('|', '\\\\|')} |")
    lines += ["", "Not automated, walked by a person: logged in (add, change, remove), Safari on iPhone and Mac, checkout handoff.", ""]
    with open(os.path.join(args["--out"], "report.md"), "w") as f:
        f.write("\n".join(lines))
    print(f"commerce-check: {report['passed']} passed, {report['failed']} failed, {report['skipped']} skipped -> {os.path.join(args['--out'], 'report.md')}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
