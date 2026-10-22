#!/bin/bash
# push-dev-theme.sh — push theme files to THIS developer's development theme, safely, from several agents at once.
#
# Why this exists
# ---------------
# On a landing-page batch five agents push to one shared development theme.
# Pique's first batch hand-rolled this and learned four things the hard way:
#   * a push to the wrong theme id is the one mistake nobody can take back —
#     the live theme and the GitHub-synced QA theme are read-only, always;
#   * two pushes at once interleave and one of them loses;
#   * a brand-new section file needs ~25 s to register before a template may
#     reference it, or every route on the theme returns 500;
#   * `shopify theme push` exits 0 when Shopify rejects a file — the error is
#     in the output, and a script that trusts the exit code pushes on blind.
#
# Usage:  sh .claude/scripts/push-dev-theme.sh [--theme <id>] [--fragments <dir>] <path> [<path> ...]
#   paths are relative to the repo root (assets/, blocks/, config/, layout/, locales/, sections/, snippets/, templates/)
#
# The theme id comes from --theme or from .claude/.cache/dev-theme-id (write it once:
# `shopify theme push --unpublished --theme "<repo>/<branch>" --json` prints it). It is refused when
# it appears in .claude/protected-themes.txt (one id per line: the live theme, the QA theme), and
# when `shopify theme list --json` says its role is not development or unpublished.
#
# With --fragments, locales/en.default.json and en.default.schema.json are rebuilt from HEAD plus
# every fragment in that directory before the push (merge-locale-fragments.py), so an agent's keys
# are never lost and the locale files are never edited by hand.

set -u
ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || { echo "not a git repository" >&2; exit 2; }
cd "$ROOT" || exit 2
CACHE=".claude/.cache"
mkdir -p "$CACHE"

THEME_ID=""; FRAGMENTS=""; PATHS=()
while [ $# -gt 0 ]; do
  case "$1" in
    --theme) THEME_ID="$2"; shift 2 ;;
    --fragments) FRAGMENTS="$2"; shift 2 ;;
    -h|--help) sed -n '2,30p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    --*) echo "unknown flag $1" >&2; exit 2 ;;
    *) PATHS+=("$1"); shift ;;
  esac
done
[ ${#PATHS[@]} -gt 0 ] || { echo "usage: push-dev-theme.sh [--theme <id>] [--fragments <dir>] <path> [<path> ...]" >&2; exit 2; }
[ -n "$THEME_ID" ] || THEME_ID="$(cat "$CACHE/dev-theme-id" 2>/dev/null || true)"
[ -n "$THEME_ID" ] || { echo "no theme id: pass --theme <id> or write it to $CACHE/dev-theme-id" >&2; exit 3; }

# --- the guard: never the live theme, never a protected one, never a role we did not expect -------
if [ -f .claude/protected-themes.txt ] && grep -qx "$THEME_ID" .claude/protected-themes.txt; then
  echo "refusing: theme $THEME_ID is listed in .claude/protected-themes.txt (live or QA): nothing is ever pushed there" >&2
  exit 9
fi
ROLE="$(shopify theme list --json 2>/dev/null | python3 -c '
import json, sys
tid = sys.argv[1]
try:
    themes = json.load(sys.stdin)
except Exception:
    print("unknown"); sys.exit(0)
for t in themes if isinstance(themes, list) else themes.get("themes", []):
    if str(t.get("id")) == tid:
        print(t.get("role", "unknown")); sys.exit(0)
print("missing")' "$THEME_ID")"
case "$ROLE" in
  development|unpublished) ;;
  main|live) echo "refusing: theme $THEME_ID is the LIVE theme (role $ROLE)" >&2; exit 9 ;;
  missing) echo "refusing: theme $THEME_ID is not on this store (shopify theme list)" >&2; exit 9 ;;
  *) echo "warning: could not read the theme's role from shopify theme list (got '$ROLE'); pushing to $THEME_ID anyway" >&2 ;;
esac

for f in "${PATHS[@]}"; do
  case "$f" in
    assets/*|blocks/*|config/*|layout/*|locales/*|sections/*|snippets/*|templates/*) ;;
    *) echo "refusing '$f': not a theme path" >&2; exit 5 ;;
  esac
  [ -f "$f" ] || { echo "missing file: $f" >&2; exit 6; }
done

# --- one push at a time --------------------------------------------------------------------------
LOCK="$CACHE/push.lock"
tries=0
until mkdir "$LOCK" 2>/dev/null; do
  tries=$((tries+1))
  [ $tries -le 180 ] || { echo "could not get the push lock after 6 minutes; if nothing else is pushing, rmdir $LOCK" >&2; exit 7; }
  sleep 2
done
trap 'rmdir "$LOCK" 2>/dev/null' EXIT

if [ -n "$FRAGMENTS" ]; then
  git checkout -q HEAD -- locales/en.default.json locales/en.default.schema.json 2>/dev/null
  if ls "$FRAGMENTS"/*.json >/dev/null 2>&1; then
    python3 .claude/scripts/merge-locale-fragments.py "$FRAGMENTS" || echo "WARNING: locale merge reported problems (see above)" >&2
  fi
  python3 .claude/scripts/check-json.py locales/en.default.json locales/en.default.schema.json || { echo "refusing: the locale files fail check-json.py (over the key cap or invalid)" >&2; exit 8; }
fi

phase1=(); phase2=(); new_section=0
for f in "${PATHS[@]}"; do
  case "$f" in
    templates/*.json|sections/*.json) phase2+=("$f") ;;
    *) phase1+=("$f")
       case "$f" in sections/*.liquid) grep -qxF "$f" "$CACHE/pushed.list" 2>/dev/null || new_section=1 ;; esac ;;
  esac
done

push() {
  args=(theme push --theme "$THEME_ID" --nodelete)
  for f in "$@"; do args+=(--only "$f"); done
  out="$(shopify "${args[@]}" 2>&1)"
  rc=$?
  printf '%s\n' "$out" | grep -vE '^\s*$' | tail -25
  # Shopify prints a rejection and exits 0. Treat the words as the verdict.
  if printf '%s' "$out" | grep -qiE 'error|rejected|failed|invalid schema|too many translation keys'; then
    return 1
  fi
  return $rc
}

rc=0
if [ -n "$FRAGMENTS" ]; then
  phase1=(locales/en.default.json locales/en.default.schema.json "${phase1[@]}")
fi
if [ ${#phase1[@]} -gt 0 ]; then
  push "${phase1[@]}" || rc=1
  for f in "${phase1[@]}"; do echo "$f" >> "$CACHE/pushed.list"; done
fi
if [ ${#phase2[@]} -gt 0 ] && [ $rc -eq 0 ]; then
  if [ $new_section -eq 1 ]; then echo "a new section file went up; waiting 25 s for Shopify to register it before the templates…"; sleep 25; fi
  push "${phase2[@]}" || rc=1
fi
if [ $rc -ne 0 ]; then
  echo "push-dev-theme: Shopify rejected something above (theme $THEME_ID) — fix it; the theme may now serve the previous file or a 500" >&2
  exit 1
fi
echo "push-dev-theme: done (theme $THEME_ID). Preview: https://<store>/<path>?preview_theme_id=$THEME_ID"
exit 0
