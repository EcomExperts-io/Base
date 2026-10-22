#!/usr/bin/env python3
"""Have GitBot's findings for this branch been read since its last commit?

GitBot reviews every push of a client branch and posts in Slack. Nothing in
the session reads Slack, so the review is found on the pull request, by the
lead. `/gitbot-preflight` reads it from inside the session and records that
it did, here; the Stop hook asks this script whether that record is current.

It never blocks. In Base (origin EcomExperts-io/Base) and on a trunk branch
it prints nothing: GitBot does not review Base, and a trunk is reviewed as
pull requests land on it.

Usage:
  preflight-status.py --changed                 one advisory line, or nothing
  preflight-status.py --record <open> <fixed> <flagged>   stamp HEAD as read
"""

import json
import os
import subprocess
import sys
import time

RECORD = ".claude/.cache/gitbot-preflight.json"
TRUNKS = ("main", "master", "develop", "development", "staging")


def git(*args):
    r = subprocess.run(["git", *args], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def main(argv):
    root = git("rev-parse", "--show-toplevel")
    if not root:
        return 0
    os.chdir(root)
    head = git("rev-parse", "HEAD")
    branch = git("branch", "--show-current")

    if "--record" in argv:
        nums = [a for a in argv[argv.index("--record") + 1:] if a.isdigit()]
        open_, fixed, flagged = (nums + ["0", "0", "0"])[:3]
        os.makedirs(os.path.dirname(RECORD), exist_ok=True)
        json.dump({"branch": branch, "head": head, "time": int(time.time()),
                   "open": int(open_), "fixed": int(fixed), "flagged": int(flagged)}, open(RECORD, "w"))
        print(f"GitBot preflight recorded for {branch}@{head[:9]}: {open_} open, {fixed} fixed, {flagged} flagged.")
        return 0

    origin = git("remote", "get-url", "origin")
    if not origin or "EcomExperts-io/Base" in origin or branch.lower() in TRUNKS or not branch:
        return 0
    try:
        rec = json.load(open(RECORD))
    except (OSError, json.JSONDecodeError):
        rec = None
    if rec and rec.get("head") == head and rec.get("branch") == branch:
        if rec.get("open"):
            print(f"gitbot: {rec['open']} GitBot finding(s) on {branch} still open since the last preflight — "
                  "fix or flag them before the pull request (/gitbot-preflight).")
        return 0
    upstream = git("rev-parse", "--abbrev-ref", "@{upstream}")
    unpushed = git("rev-list", "--count", f"{upstream}..HEAD") if upstream else ""
    state = (f"{unpushed} commit(s) not yet pushed" if unpushed and unpushed != "0"
             else "pushed" if upstream else "no upstream yet")
    print(f"gitbot: {branch} is at {head[:9]} ({state}) and GitBot's findings for it have not been read "
          "from this session. After the push, /gitbot-preflight reads them and settles each one — "
          "fix or flag — before the pull request. GitBot reviews every push either way.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
