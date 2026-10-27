#!/usr/bin/env python3
"""Which of the three situations is this session in — A fresh rebuild, B joining midway, C correcting after QA?

Usage
-----
  where-are-we.py                               one line for the session (default)
  where-are-we.py --json                        the signals and the verdict
  where-are-we.py --close-stage <n> "<name>"    record a stage closed, on this branch, today
  where-are-we.py --qa-round <open-issues>      record a QA round picked up (open issue count)

Notes:
- Reads only local files: the origin remote (Base itself is none of the three), state-of-the-theme.md, the reference map,
  verify reports, docs/ai-workflow/progress.json (written by --close-stage and --qa-round), the branch name and [FIX] commits.
- The verdict is a reading, not a ruling: it says "looks like", gives the evidence and names the next step.
"""

import datetime
import glob
import json
import os
import re
import subprocess
import sys

PROGRESS = "docs/ai-workflow/progress.json"
STATE = "docs/ai-workflow/state-of-the-theme.md"
MAPS = ("docs/ai-workflow/reference-map.md", "docs/ai-workflow/figma-frame-map.md")
QA_BRANCH = re.compile(r"(qa|qi|fix|issue|bug|hotfix|reopen|correction)", re.I)
TRUNKS = {"main", "master", "develop", "development", "staging"}


def git(*args):
    r = subprocess.run(["git", *args], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def read(path):
    try:
        return open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return None


def load_progress():
    try:
        d = json.load(open(PROGRESS))
        return d if isinstance(d, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def save_progress(d):
    os.makedirs(os.path.dirname(PROGRESS), exist_ok=True)
    with open(PROGRESS, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2)
        f.write("\n")


def map_rows(text):
    """Table rows with a band name, excluding the header, the rule and the template row."""
    rows = 0
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 4 or set(cells[0]) <= set("-: ") or cells[0].lower() in ("page", "band", "reference", ""):
            continue
        if "figma / live / both" in line:
            continue
        rows += 1
    return rows


def signals():
    s = {"today": datetime.date.today().isoformat()}
    origin = git("remote", "get-url", "origin")
    s["origin"] = origin
    s["is_base"] = "EcomExperts-io/Base" in origin
    s["branch"] = git("branch", "--show-current")
    state = read(STATE)
    s["state_doc"] = state is not None
    s["state_age_days"] = None
    if state:
        m = re.search(r"on (\d{4}-\d{2}-\d{2})", state)
        if m:
            try:
                d = datetime.date.fromisoformat(m.group(1))
                s["state_age_days"] = (datetime.date.today() - d).days
            except ValueError:
                pass
    s["map_rows"] = 0
    s["map_file"] = None
    for p in MAPS:
        t = read(p)
        if t is not None:
            s["map_file"] = p
            s["map_rows"] = map_rows(t)
            break
    s["verify_reports"] = len(glob.glob("docs/ai-workflow/verify/*/report.md")) + len(glob.glob(".claude/verify/*/report.json"))
    prog = load_progress()
    stages = prog.get("stages", []) if isinstance(prog.get("stages"), list) else []
    s["stages_closed"] = [x for x in stages if isinstance(x, dict)]
    s["last_stage"] = max((int(x.get("stage", 0)) for x in s["stages_closed"] if str(x.get("stage", "")).isdigit()), default=None)
    rounds = prog.get("qa_rounds", []) if isinstance(prog.get("qa_rounds"), list) else []
    s["qa_rounds"] = [x for x in rounds if isinstance(x, dict)]
    s["last_qa_round"] = s["qa_rounds"][-1] if s["qa_rounds"] else None
    subjects = [l for l in git("log", "--no-merges", "--format=%s", "-15").splitlines() if l.strip()]
    s["recent_commits"] = len(subjects)
    s["recent_fix"] = sum(1 for l in subjects if re.match(r"\s*\[FIX\]", l, re.I) or re.search(r"\bfix(es|ed)?\b", l, re.I))
    s["history"] = int(git("rev-list", "--count", "HEAD") or 0)
    s["branch_qa"] = bool(QA_BRANCH.search(s["branch"] or "")) and (s["branch"] or "").lower() not in TRUNKS
    return s


def verdict(s):
    if s["is_base"]:
        return "base", "this is Base itself, not a client rebuild", "tooling work: the rules, checks and skills; `/record-incident` and `/harvest` land here"
    fix_ratio = s["recent_fix"] / s["recent_commits"] if s["recent_commits"] else 0
    built = s["verify_reports"]
    rows = s["map_rows"]
    because = []
    # C — correcting after QA: the branch or the recent history says so, or a QA round was recorded
    if s["last_qa_round"] and (s["last_stage"] is None or True):
        because.append(f"a QA round was recorded on {s['last_qa_round'].get('date', '?')} with {s['last_qa_round'].get('open', '?')} open issue(s)")
    if s["branch_qa"]:
        because.append(f"the branch is named {s['branch']}")
    if s["recent_commits"] >= 6 and fix_ratio >= 0.6:
        because.append(f"{s['recent_fix']} of the last {s['recent_commits']} commits are fixes")
    if s["last_stage"] is not None and s["last_stage"] >= 7:
        because.append("the last stage closed is 7, the long tail")
    if because and (s["last_qa_round"] or s["branch_qa"] or fix_ratio >= 0.6 or (s["last_stage"] or 0) >= 7):
        return "C", "; ".join(because), "`/close-qa-loop` picks the issues up; the fix is proved against its reference, the other pages stay at 0.0%, GitBot's follow-up says closed"
    # A — fresh: nothing measured yet and little history, or a state doc from this week with nothing built
    if not s["state_doc"]:
        if s["history"] <= 40 and built == 0:
            return "A", f"no state document, {s['history']} commit(s) of history, nothing verified yet", "`/recon-theme --live-url` and `/store-recon` first; then name the reference per band in `docs/ai-workflow/reference-map.md`"
        return "B", f"no state document, but {s['history']} commits of history and {built} verify report(s): a rebuild nobody measured", "`sh .claude/scripts/base-link.sh`, `python3 .claude/scripts/pull-base-tooling.py`, then `/recon-theme --live-url` for the carry verdict"
    age = s["state_age_days"]
    recent = age is not None and age <= 7
    if recent and built <= 2 and (s["last_stage"] is None or s["last_stage"] <= 1):
        return "A", f"the state document is {age} day(s) old, {built} verify report(s), " + (f"last stage closed {s['last_stage']}" if s['last_stage'] is not None else "no stage closed yet"), "stage " + str((s['last_stage'] or 0) + 1) + " of `rebuild-playbook.md`; commerce is stage 2"
    # B — midway
    parts = [f"the state document is {age} day(s) old" if age is not None else "the state document has no date"]
    parts.append(f"{built} verify report(s)" + (f" for {rows} band(s) in the reference map" if rows else ""))
    if s["last_stage"] is not None:
        parts.append(f"last stage closed {s['last_stage']}")
    return "B", ", ".join(parts), "re-read `state-of-the-theme.md` (re-run `/recon-theme` if it is older than a week); the missing list, sorted by stage, is the build order; `landing-batch.md` for a card of pages"


NAMES = {"A": "a fresh rebuild", "B": "joining a rebuild midway", "C": "correcting after QA", "base": "Base itself"}


def main(argv):
    root = git("rev-parse", "--show-toplevel")
    if not root:
        return 0
    os.chdir(root)
    if "--close-stage" in argv:
        i = argv.index("--close-stage")
        try:
            n = int(argv[i + 1])
        except (IndexError, ValueError):
            print("usage: where-are-we.py --close-stage <n> \"<name>\"", file=sys.stderr)
            return 2
        name = argv[i + 2] if i + 2 < len(argv) and not argv[i + 2].startswith("--") else ""
        d = load_progress()
        d.setdefault("stages", []).append({"stage": n, "name": name, "date": datetime.date.today().isoformat(), "branch": git("branch", "--show-current"), "head": git("rev-parse", "--short", "HEAD")})
        save_progress(d)
        print(f"recorded: stage {n} {name} closed on {git('branch', '--show-current')} — commit {PROGRESS} with the stage's work")
        return 0
    if "--qa-round" in argv:
        i = argv.index("--qa-round")
        try:
            n = int(argv[i + 1])
        except (IndexError, ValueError):
            print("usage: where-are-we.py --qa-round <open-issues>", file=sys.stderr)
            return 2
        d = load_progress()
        d.setdefault("qa_rounds", []).append({"open": n, "date": datetime.date.today().isoformat(), "branch": git("branch", "--show-current")})
        save_progress(d)
        print(f"recorded: QA round with {n} open issue(s) — commit {PROGRESS} with the round's fixes")
        return 0
    s = signals()
    code, because, nxt = verdict(s)
    if "--json" in argv:
        print(json.dumps({"verdict": code, "name": NAMES[code], "because": because, "next": nxt, "signals": s}, indent=2, default=str))
        return 0
    if code == "base":
        print(f"where-are-we: {NAMES[code]} — {because}. Next: {nxt}.")
    else:
        print(f"where-are-we: looks like {code}, {NAMES[code]} — {because}. Next: {nxt}. (A reading, not a ruling: run what fits if you know better.)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
