#!/usr/bin/env python3
"""Does the installed agentic-os plugin still say what Base's skills rely on?

Base points at the plugin's skills by name and repeats a few of their facts
(build-page-from-figma Step 5, close-qa-loop). This reads the installed
plugin's SKILL.md files and names every skill or phrase that is gone, so the
Base text is corrected rather than left contradicting the plugin.

Usage
-----
  python3 .claude/scripts/check-plugin-contract.py                 full report
  python3 .claude/scripts/check-plugin-contract.py --brief         one line (doctor.py)
  python3 .claude/scripts/check-plugin-contract.py --plugin-dir D  check the plugin at D

Exit 0 when the plugin matches or is not installed (the fallback applies), 1 on drift.
"""

import glob
import json
import os
import re
import sys

PLUGIN = "agentic-os"
WRITTEN_AGAINST = "1.0.1"

# skill -> (phrase the plugin must still contain, what in Base depends on it)
CONTRACT = {
    "handoff": [
        ("_Dev checks_", "build-page-from-figma Step 5 hands the proof to _Dev checks_"),
        ("_Known gaps_", "build-page-from-figma Step 5 hands assumptions to _Known gaps_"),
        ("_Steps to QA_", "the fallback's numbered steps to QA copy this section"),
        ("Expect:", "the fallback's steps end with `Expect:`"),
        ("Never edit the card's body or status", "Step 5 says /handoff never changes the card's status"),
        ("_Fixed this round_", "close-qa-loop's re-hand-off carries a fixed-this-round line per bug"),
    ],
    "fix-issues": [
        ("Never set a bug to", "close-qa-loop says the QI, not the developer, marks a bug done"),
        ("never change the card's status", "close-qa-loop says the card's status is left alone"),
    ],
    "qa-precheck": [
        ("_Dev checks_", "build-page-from-figma Step 4 feeds the reports into its one-line result"),
    ],
    "kickoff": [
        ("<ClientID>.<ProjectID>/Project-<Title>", "multi-session-rebuild.md §5 gives the same branch-name pattern"),
    ],
}


def version_key(v):
    return tuple(int(x) for x in re.findall(r"\d+", v))


def find_plugin():
    """(dir, version) of the installed plugin, or (None, None)."""
    home = os.path.expanduser("~/.claude/plugins")
    try:
        data = json.load(open(os.path.join(home, "installed_plugins.json")))
        for key, installs in (data.get("plugins") or data).items():
            if key.split("@")[0] == PLUGIN and installs:
                best = sorted(installs, key=lambda i: version_key(str(i.get("version", "0"))))[-1]
                if os.path.isdir(best.get("installPath", "")):
                    return best["installPath"], str(best.get("version", "?"))
    except (OSError, ValueError, AttributeError):
        pass
    dirs = [d for d in glob.glob(os.path.join(home, "cache", "*", PLUGIN, "*")) if os.path.isdir(os.path.join(d, "skills"))]
    if dirs:
        best = sorted(dirs, key=lambda d: version_key(os.path.basename(d)))[-1]
        return best, os.path.basename(best)
    return None, None


def check(plugin_dir):
    """A list of (skill, problem, what in Base depends on it)."""
    drift = []
    for skill, phrases in CONTRACT.items():
        path = os.path.join(plugin_dir, "skills", skill, "SKILL.md")
        try:
            text = open(path, encoding="utf-8").read()
        except OSError:
            drift.append((skill, "skill not found", "Base names /%s" % skill))
            continue
        for phrase, why in phrases:
            if phrase not in text:
                drift.append((skill, "no longer says `%s`" % phrase, why))
    return drift


def main(argv):
    brief = "--brief" in argv
    if "--plugin-dir" in argv:
        plugin_dir = argv[argv.index("--plugin-dir") + 1]
        version = "?"
        try:
            version = str(json.load(open(os.path.join(plugin_dir, ".claude-plugin", "plugin.json"))).get("version", "?"))
        except (OSError, ValueError):
            pass
    else:
        plugin_dir, version = find_plugin()
    if not plugin_dir:
        print("plugin contract: %s not installed — the fallback in build-page-from-figma Step 5 applies" % PLUGIN)
        return 0
    drift = check(plugin_dir)
    if not drift:
        print("plugin contract: %s %s matches what Base relies on (written against %s)" % (PLUGIN, version, WRITTEN_AGAINST))
        return 0
    if brief:
        print("plugin contract: %s %s differs from Base's text in %d place(s) — python3 .claude/scripts/check-plugin-contract.py"
              % (PLUGIN, version, len(drift)))
        return 1
    print("plugin contract: %s %s differs from what Base relies on (written against %s)\n" % (PLUGIN, version, WRITTEN_AGAINST))
    for skill, problem, why in drift:
        print("  /%s: %s\n      %s" % (skill, problem, why))
    print("\n  Read the plugin's skill, correct the Base text to match, then update CONTRACT and")
    print("  WRITTEN_AGAINST in this script. In a client fork, /record-incident it for Base.")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
