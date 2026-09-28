#!/usr/bin/env python3
"""Is this machine ready to run the Base AI workflow? One command answers.

Why this exists
---------------
The audit of 14 Sep 2026 found the onboarding path was "sit next to Naish".
Nothing in the repo said which MCP servers a build needs, whether the Shopify
CLI could start on the installed Node, or whether the commit gate was even
wired up in this checkout. Each of those failures is silent: a CLI that cannot
start is reported by the hook as *skipped*, a missing hook path means the gate
never runs, an unconfigured MCP server means the skill fails on its first call.

This prints the state of every dependency the workflow has, with the fix
beside each one that is off. The SessionStart hook runs the fast subset so a
session opens knowing what is missing, instead of discovering it at 5pm.

Usage
-----
  python3 .claude/scripts/doctor.py            full report
  python3 .claude/scripts/doctor.py --brief    one line, fast checks only (for hooks)
  python3 .claude/scripts/doctor.py --context  brief line + compliance + incidents (SessionStart)
  python3 .claude/scripts/doctor.py --strict   exit 1 if any check FAILS

OK    ready.   WARN  degraded — part of the workflow will not work.   FAIL  the gate is off.
"""

import glob
import json
import os
import re
import shutil
import subprocess
import sys
import time

ROOT = None


def run(cmd, timeout=20, env=None):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except (OSError, subprocess.TimeoutExpired) as e:
        return 127, str(e)


def node_major():
    rc, out = run(["node", "--version"])
    m = re.match(r"v(\d+)", out.strip())
    return int(m.group(1)) if rc == 0 and m else 0


def best_nvm_node():
    """Newest Node >= 22 under ~/.nvm, or None. check-theme-staged.py uses the same rule."""
    cands = []
    for d in glob.glob(os.path.expanduser("~/.nvm/versions/node/v*")):
        m = re.match(r"v(\d+)\.(\d+)\.(\d+)", os.path.basename(d))
        if m and int(m.group(1)) >= 22:
            cands.append((tuple(int(x) for x in m.groups()), d))
    return sorted(cands)[-1][1] if cands else None


def load_json(path):
    try:
        return json.load(open(os.path.join(ROOT, path)))
    except (OSError, json.JSONDecodeError):
        return {}


# ---------------------------------------------------------------------------
# checks — each returns (status, label, detail, fix)
# ---------------------------------------------------------------------------
def check_hooks_wired():
    rc, out = run(["git", "config", "core.hooksPath"])
    hooks_path = out.strip()
    husky = os.path.join(ROOT, ".husky", "pre-commit")
    if hooks_path == ".githooks":
        return ("OK", "commit gate", "core.hooksPath = .githooks", "")
    if os.path.exists(husky) and ".githooks/pre-commit" in open(husky, errors="replace").read():
        return ("OK", "commit gate", "husky pre-commit calls .githooks/pre-commit", "")
    return ("FAIL", "commit gate",
            f"core.hooksPath = {hooks_path or '(unset)'} and husky does not call Base's hook",
            "sh .claude/scripts/setup.sh   (npm run setup where package.json has the script)")


def check_theme_check_config():
    """A Theme Check config that enables nothing makes three gates vacuous.

    .theme-check.yml is tooling, so pull-base-tooling.py carries it — but a fork
    that already had one keeps its own, and the org's older repo template starts
    with `extends: :nothing` (the Ruby-era form) and lists a dozen checks by
    their old names. The current CLI runs that as almost nothing: on the first
    v2 pilot it reported one warning over the whole theme where Base's config
    found fourteen errors. check-theme-staged.py blocks on errors only, so the
    Stop hook, the commit gate and CI all passed — a gate that cannot fail,
    which is the failure this workflow exists to remove. The doctor is the one
    place that looks at the config itself.
    """
    path = os.path.join(ROOT, ".theme-check.yml")
    if not os.path.exists(path):
        return ("WARN", "theme check",
                "no .theme-check.yml — the CLI's defaults run; Base's exclusions (docs/, .claude/, .base-tooling/) are missing",
                "python3 .claude/scripts/pull-base-tooling.py")
    lines = open(path, errors="replace").read().split("\n")
    values = []
    for i, ln in enumerate(lines):
        m = re.match(r"^extends:\s*(.*)$", ln)
        if not m:
            continue
        head = m.group(1).strip()
        if head:
            values.append(head)
        for follow in lines[i + 1:]:
            fm = re.match(r"^\s+-\s*(.+)$", follow)
            if not fm:
                break
            values.append(fm.group(1).strip())
        break
    shown = ", ".join(v.strip("'\"[]") for v in values) or "(default: theme-check:recommended)"
    enables_something = any("theme-check:" in v for v in values) or not values
    if not enables_something and all(v.strip("'\"[]") in ("nothing", ":nothing", "") for v in values):
        return ("FAIL", "theme check",
                f"extends: {shown} — Theme Check runs only the checks this file lists, so the Stop hook, "
                "the commit gate and CI pass without looking",
                "extend theme-check:recommended — Base's .theme-check.yml is the model; a tooling pull saves it under .claude/.cache/base-new/")
    return ("OK", "theme check", f".theme-check.yml extends {shown}", "")


def check_runtime_hooks():
    hooks = load_json(".claude/settings.json").get("hooks", {})
    have = [k for k in ("PostToolUse", "Stop", "SessionStart") if k in hooks]
    if len(have) == 3:
        return ("OK", "runtime hooks", "PostToolUse, Stop, SessionStart configured in .claude/settings.json", "")
    if have:
        return ("WARN", "runtime hooks", f"only {', '.join(have)} configured", "pull the latest Base tooling")
    return ("FAIL", "runtime hooks", "no hooks in .claude/settings.json — edits and turn-ends are ungated",
            "sh .claude/scripts/pull-base-tooling.sh")


def check_node():
    major = node_major()
    if major >= 22:
        return ("OK", "node", f"v{major} on PATH", "")
    alt = best_nvm_node()
    if alt:
        return ("WARN", "node",
                (f"v{major or '?'} on PATH is too old for the Shopify CLI; "
                 f"{os.path.basename(alt)} found in ~/.nvm and is used by the gate automatically"),
                f"nvm alias default {os.path.basename(alt)}")
    return ("FAIL", "node",
            f"v{major or '?'} — the Shopify CLI needs Node 22+, so Theme Check silently skips",
            "nvm install 24 && nvm alias default 24")


def check_python():
    v = sys.version_info
    ok = (v.major, v.minor) >= (3, 9)
    return (("OK" if ok else "FAIL"), "python3", f"{v.major}.{v.minor}", "" if ok else "install Python 3.9+")


def check_shopify_cli():
    if shutil.which("shopify") is None:
        return ("FAIL", "shopify cli", "not on PATH", "npm install -g @shopify/cli")
    env = dict(os.environ)
    alt = best_nvm_node()
    if node_major() < 22 and alt:
        env["PATH"] = os.path.join(alt, "bin") + os.pathsep + env["PATH"]
    rc, out = run(["shopify", "version"], timeout=40, env=env)
    m = re.search(r"\b(\d+\.\d+\.\d+)\b", out)
    if rc == 0 and m:
        return ("OK", "shopify cli", f"v{m.group(1)}", "")
    return ("FAIL", "shopify cli", "installed but cannot start (Node too old?)",
            "nvm install 24 && nvm alias default 24")


def check_mcp_config():
    path = os.path.join(ROOT, ".mcp.json")
    if not os.path.exists(path):
        return ("FAIL", "mcp servers", ".mcp.json missing", "sh .claude/scripts/pull-base-tooling.sh")
    try:
        servers = sorted(json.load(open(path)).get("mcpServers", {}))
    except json.JSONDecodeError:
        return ("FAIL", "mcp servers", ".mcp.json is not valid JSON", "fix the file")
    return ("OK", "mcp servers",
            f"{', '.join(servers)} declared — approve once when Claude Code asks, then /mcp to sign in", "")


def check_figma_plugin():
    if shutil.which("claude") is None:
        return ("WARN", "figma plugin", "claude CLI not on PATH, cannot check",
                "claude plugin install figma@claude-plugins-official")
    rc, out = run(["claude", "plugin", "list"], timeout=30)
    if rc == 0 and "figma" in out.lower():
        return ("OK", "figma plugin", "installed (provides the Figma MCP and the design-to-code skill)", "")
    return ("WARN", "figma plugin", "not installed — no Figma MCP, no /figma-design-to-code skill",
            "claude plugin install figma@claude-plugins-official")


def check_store():
    store = os.environ.get("SHOPIFY_FLAG_STORE") or \
        load_json(".claude/settings.local.json").get("env", {}).get("SHOPIFY_FLAG_STORE")
    if store:
        return ("OK", "store handle", f"{store} (SHOPIFY_FLAG_STORE)", "")
    return ("WARN", "store handle",
            "no SHOPIFY_FLAG_STORE — `shopify theme dev` and the verify skill will ask every time",
            'echo \'{"env":{"SHOPIFY_FLAG_STORE":"<handle>"}}\' > .claude/settings.local.json')


def check_pillow():
    try:
        import PIL  # noqa: F401
        return ("OK", "pillow", "available (verify-against-figma pixel diff)", "")
    except ImportError:
        return ("WARN", "pillow", "missing — verify-against-figma cannot compute a pixel diff",
                "python3 -m pip install --user pillow")


def check_chrome():
    for c in ("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
              shutil.which("google-chrome") or "", shutil.which("chromium") or "",
              os.environ.get("CHROME_BIN", "")):
        if c and os.path.exists(c):
            return ("OK", "chrome", "found (headless screenshots for verify-against-figma)", "")
    return ("WARN", "chrome", "no Chrome/Chromium binary — the verify skill falls back to the browser tool",
            "install Google Chrome or set CHROME_BIN")


def check_gh():
    if shutil.which("gh") is None:
        return ("WARN", "gh", "not installed — /harvest cannot open Base PRs", "brew install gh && gh auth login")
    rc, out = run(["gh", "auth", "status"], timeout=20)
    if rc == 0:
        return ("OK", "gh", "authenticated", "")
    return ("WARN", "gh", "not authenticated", "gh auth login")


def check_base_link():
    rc, out = run(["git", "remote", "get-url", "origin"])
    if "EcomExperts-io/Base" in out:
        return ("OK", "base link", "this is Base itself", "")
    rc2, _ = run(["git", "remote", "get-url", "base"])
    stamp = load_json(".base-version")
    if stamp and rc2 == 0:
        return ("OK", "base link",
                f"tooling stamped at Base {str(stamp.get('sha', '?'))[:9]} ({stamp.get('date', '?')})", "")
    if rc2 != 0:
        return ("WARN", "base link", "no `base` remote — cannot pull tooling or harvest",
                "sh .claude/scripts/base-link.sh")
    return ("WARN", "base link", "base remote present but no .base-version stamp",
            "sh .claude/scripts/pull-base-tooling.sh")


def check_hook_latency():
    sample = sorted(glob.glob(os.path.join(ROOT, "sections", "*.liquid")))
    if not sample:
        return ("OK", "hook latency", "no sections to time", "")
    rel = os.path.relpath(sample[0], ROOT)
    t = time.time()
    run([sys.executable, ".claude/scripts/check-conventions.py", "--files", rel, "--quiet"])
    run([sys.executable, ".claude/scripts/check-section-contract.py", "--files", rel, "--quiet"])
    ms = int((time.time() - t) * 1000)
    if ms < 2000:
        return ("OK", "hook latency", f"{ms} ms for the per-edit gate", "")
    return ("WARN", "hook latency", f"{ms} ms per edit — over the 2 s budget; developers will disable hooks",
            "profile check-conventions.py")


def compliance_line():
    rc, out = run([sys.executable, ".claude/scripts/report-compliance.py", "--json"], timeout=30)
    try:
        d = json.loads(out)
        return f"compliance: {d.get('compliant', '?')}/{d.get('in_scope', '?')} sections meet the settings contract"
    except (json.JSONDecodeError, AttributeError):
        return "compliance: report unavailable"


def incidents_line():
    files = [f for f in glob.glob(os.path.join(ROOT, "docs", "ai-workflow", "incidents", "*.md"))
             if open(f, errors="replace").read(64).startswith("---")]
    open_ = [f for f in files
             if not re.search(r"^status:\s*(harvested|client-only)", open(f, errors="replace").read(), re.M)]
    return f"incidents: {len(open_)} open of {len(files)} recorded"


FAST = [check_hooks_wired, check_runtime_hooks, check_theme_check_config, check_node, check_python,
        check_mcp_config, check_store, check_pillow, check_chrome, check_base_link]
SLOW = [check_shopify_cli, check_figma_plugin, check_gh, check_hook_latency]


def main(argv):
    global ROOT
    rc, out = run(["git", "rev-parse", "--show-toplevel"])
    ROOT = out.strip() if rc == 0 else os.getcwd()
    os.chdir(ROOT)
    context = "--context" in argv
    brief = "--brief" in argv or context
    strict = "--strict" in argv

    results = [c() for c in FAST] + ([] if brief else [c() for c in SLOW])
    counts = {s: sum(1 for r in results if r[0] == s) for s in ("OK", "WARN", "FAIL")}

    if brief:
        off = [f"{r[1]}: {r[3] or r[2]}" for r in results if r[0] != "OK"]
        line = f"doctor: {counts['OK']} ok, {counts['WARN']} warn, {counts['FAIL']} fail"
        if off:
            line += " — " + "; ".join(off[:3])
            if len(off) > 3:
                line += f"; +{len(off) - 3} more (python3 .claude/scripts/doctor.py)"
        print(line)
        if context:
            print(compliance_line())
            print(incidents_line())
        return 1 if (strict and counts["FAIL"]) else 0

    print()
    print("  Base AI workflow — doctor")
    print("  " + "-" * 70)
    for status, label, detail, fix in results:
        print(f"  {status:<5} {label:<14} {detail}")
        if fix and status != "OK":
            print(f"        fix: {fix}")
    print("  " + "-" * 70)
    print(f"  {compliance_line()}")
    print(f"  {incidents_line()}")
    print(f"  {counts['OK']} ok · {counts['WARN']} warn · {counts['FAIL']} fail")
    print()
    return 1 if (strict and counts["FAIL"]) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
