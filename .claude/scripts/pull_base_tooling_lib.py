"""Shared pieces of pull-base-tooling.py and check-tooling-drift.py.

Kept in one place so the two scripts cannot disagree about what "tooling" is
or how Base's files are read. A hyphenated script name cannot be imported, so
the importable half lives here; pull-base-tooling.py re-exports nothing and
imports this too.
"""

import json
import subprocess
import sys

STAMP = ".base-version"


def check_flags(argv, known, usage):
    """Refuse to run on an argument the script does not know.

    Returns an exit code to return at once, or None to carry on. `known` maps
    each flag to whether it takes a value. This runs before anything is read or
    written: a stray `--help` once ran a real overlay and re-stamped a fork to
    the wrong Base commit, because the script only looked for the flags it
    recognised and silently ignored the rest (Pique incident
    2026-09-15-pull-script-runs-on-unknown-flag).
    """
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("-h", "--help"):
            print(usage.strip())
            return 0
        if a not in known:
            print(f"unknown argument: {a} — nothing was read or written.\n\n{usage.strip()}", file=sys.stderr)
            return 2
        if known[a]:
            if i + 1 >= len(argv) or argv[i + 1].startswith("-"):
                print(f"{a} needs a value.\n\n{usage.strip()}", file=sys.stderr)
                return 2
            i += 1
        i += 1
    return None

TOOLING_PREFIXES = (".claude/", ".githooks/", "docs/ai-workflow/", "docs/base-theme-standards/")
TOOLING_FILES = {".mcp.json", ".theme-check.yml", "CLAUDE.md", ".github/workflows/theme-review.yml"}
EXCLUDE_PREFIXES = (".claude/settings.local.json", ".claude/agent-memory-local/", ".claude/.cache/",
                    ".claude/verify/", "docs/ai-workflow/incidents/")
# The one file under the excluded incidents directory that does travel. Incidents
# belong to the repo that recorded them, but the directory itself must exist in
# a fork on arrival: rules and skills link to it, check-rule-links.py resolves
# those links, and git cannot carry an empty directory — so the pilot fork's
# very first commit of the tooling was blocked by three links to a folder only
# Base had (Pique incident 2026-09-15-dangling-paths-block-first-fork-commit).
INCIDENTS_README = "docs/ai-workflow/incidents/README.md"


def sh(*args, cwd=None, check=True):
    r = subprocess.run(args, capture_output=True, text=True, cwd=cwd)
    if check and r.returncode != 0:
        raise RuntimeError(f"{' '.join(args)}\n{r.stderr.strip()}")
    return r.stdout


def is_tooling(path):
    if path == INCIDENTS_README:
        return True
    if path.startswith(EXCLUDE_PREFIXES) or "__pycache__" in path or path.endswith(".pyc"):
        return False
    return path in TOOLING_FILES or path.startswith(TOOLING_PREFIXES)


def load_stamp():
    try:
        return json.load(open(STAMP))
    except (OSError, json.JSONDecodeError):
        return None


class Source:
    """Base's files at a ref, read from the `base` remote or from a local Base checkout."""

    def __init__(self, ref=None, base_path=None):
        self.base_path = base_path
        if base_path:
            self.git_dir = base_path
            self.sha = sh("git", "rev-parse", "HEAD", cwd=base_path).strip()
            self.ref = f"{base_path}@HEAD"
        else:
            self.git_dir = None
            self.ref = ref
            self.sha = sh("git", "rev-parse", ref).strip()

    def files(self):
        if self.base_path:
            out = sh("git", "ls-files", cwd=self.base_path)
        else:
            out = sh("git", "ls-tree", "-r", "--name-only", self.sha)
        return sorted(p for p in out.split("\n") if p and is_tooling(p))

    def read(self, path, sha=None):
        sha = sha or self.sha
        r = subprocess.run(["git", "show", f"{sha}:{path}"], capture_output=True, cwd=self.git_dir)
        return r.stdout if r.returncode == 0 else None
