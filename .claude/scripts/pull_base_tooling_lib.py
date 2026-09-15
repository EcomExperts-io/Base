"""Shared pieces of pull-base-tooling.py and check-tooling-drift.py.

Kept in one place so the two scripts cannot disagree about what "tooling" is
or how Base's files are read. A hyphenated script name cannot be imported, so
the importable half lives here; pull-base-tooling.py re-exports nothing and
imports this too.
"""

import json
import subprocess

STAMP = ".base-version"

TOOLING_PREFIXES = (".claude/", ".githooks/", "docs/ai-workflow/", "docs/base-theme-standards/")
TOOLING_FILES = {".mcp.json", ".theme-check.yml", "CLAUDE.md", ".github/workflows/theme-review.yml"}
EXCLUDE_PREFIXES = (".claude/settings.local.json", ".claude/agent-memory-local/", ".claude/.cache/",
                    ".claude/verify/", "docs/ai-workflow/incidents/")


def sh(*args, cwd=None, check=True):
    r = subprocess.run(args, capture_output=True, text=True, cwd=cwd)
    if check and r.returncode != 0:
        raise RuntimeError(f"{' '.join(args)}\n{r.stderr.strip()}")
    return r.stdout


def is_tooling(path):
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
