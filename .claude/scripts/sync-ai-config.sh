#!/bin/sh
# Keeps the Cursor and Claude Code copies of our AI configuration identical.
#
# Why this exists: on the Bites Vitamins build the conventions lived only in
# .cursor/rules/. Claude Code does not read that path, so for the first 18 days
# of the build the agent had no access to them and ~30 sections shipped without
# the section schema contract or translation keys. Two hand-maintained copies is
# how that happened; this script makes drift impossible instead of discouraged.
#
# Canonical source is .claude/ — edit there, never in .cursor/.
#   Rules:  .claude/rules/*.md  -> .cursor/rules/*.mdc  (frontmatter converted)
#   Skills: .claude/skills/**   -> .cursor/skills/**    (verbatim copy)
#
# Generated .mdc files carry a checksum of their own content. Before overwriting
# one, the script recomputes it: if it no longer matches, the file was edited by
# hand and the script REFUSES rather than silently discarding that work. Without
# this, the hook told a Cursor user their .cursor copy had diverged and the fix
# command then destroyed the change they had just made.
#
# Note the weaker guarantee for skills: they are byte-identical copies with no
# banner to carry a checksum, so a hand-edit there cannot be distinguished from
# a source change and will be overwritten. Never edit .cursor/skills/ directly.
#
# Usage: sh .claude/scripts/sync-ai-config.sh [--check] [--force]
#   --check  exit 1 if anything is out of sync, write nothing (for the hook)
#   --force  overwrite even a hand-edited .mdc (discards it — last resort)

set -e
cd "$(git rev-parse --show-toplevel)"

CHECK=0
FORCE=0
for arg in "$@"; do
  [ "$arg" = "--check" ] && CHECK=1
  [ "$arg" = "--force" ] && FORCE=1
done
STALE=0
CLOBBER=0

# Checksum of a file with its own checksum line removed, so the recorded value
# never feeds into itself. cksum is POSIX and sufficient for tamper detection.
content_sum() {
  grep -v '^<!-- checksum: ' "$1" | cksum | awk '{print $1}'
}

# --- rules: .md -> .mdc -------------------------------------------------------
# A .claude rule carries a `paths:` glob (or nothing, meaning always-apply).
# Cursor wants `globs:` plus an explicit `alwaysApply:` boolean.
for src in .claude/rules/*.md; do
  [ -f "$src" ] || continue
  name=$(basename "$src" .md)
  dest=".cursor/rules/${name}.mdc"

  desc=$(sed -n 's/^description:[[:space:]]*//p' "$src" | head -1)

  # `paths:` may be inline (`paths: "a,b"`) or a YAML list of indented `- "glob"`
  # lines. Cursor wants one comma-separated `globs:` value, so flatten either form.
  # List items must be indented, which is what keeps the closing `---` fence from
  # being read as an item. Every action ends in `next` because sub() rewrites $0
  # and a later rule would otherwise match the rewritten line.
  paths=$(awk '
    /^paths:[[:space:]]*$/ { inlist=1; next }
    /^paths:[[:space:]]*[^[:space:]]/ {
      sub(/^paths:[[:space:]]*/,""); gsub(/"/,""); print; found=1; exit
    }
    inlist && /^[[:space:]]+-[[:space:]]*/ {
      sub(/^[[:space:]]+-[[:space:]]*/,""); gsub(/"/,"")
      printf "%s%s", sep, $0; sep=","; next
    }
    inlist { exit }
    END { if (sep != "") printf "\n" }
  ' "$src")

  # No paths glob means the rule is unscoped, which Cursor expresses as alwaysApply.
  if [ -n "$paths" ]; then
    always=false
  else
    always=true
  fi

  body=$(awk 'BEGIN{n=0} /^---[[:space:]]*$/{n++; next} n>=2{print}' "$src")

  tmp=$(mktemp)
  {
    echo "---"
    echo "description: ${desc}"
    echo "globs: ${paths}"
    echo "alwaysApply: ${always}"
    echo "---"
    echo ""
    echo "<!-- GENERATED from ${src} by .claude/scripts/sync-ai-config.sh — do not edit here. -->"
    echo ""
    printf '%s\n' "$body"
  } > "$tmp"

  # Stamp the generated content with its own checksum.
  sum=$(content_sum "$tmp")
  tmp2=$(mktemp)
  awk -v s="$sum" '
    /^<!-- GENERATED from /{ print; print "<!-- checksum: " s " -->"; next }
    { print }
  ' "$tmp" > "$tmp2"
  mv "$tmp2" "$tmp"

  if [ -f "$dest" ] && cmp -s "$tmp" "$dest"; then
    rm -f "$tmp"
    continue
  fi

  if [ "$CHECK" -eq 1 ]; then
    echo "OUT OF SYNC: $dest (source: $src)"
    STALE=1
    rm -f "$tmp"
    continue
  fi

  # Would this overwrite hand-written work? Only if the destination's recorded
  # checksum disagrees with its actual content.
  if [ -f "$dest" ] && [ "$FORCE" -eq 0 ]; then
    recorded=$(sed -n 's/^<!-- checksum: \([0-9]*\) -->$/\1/p' "$dest" | head -1)
    actual=$(content_sum "$dest")
    if [ -n "$recorded" ] && [ "$recorded" != "$actual" ]; then
      echo "REFUSING to overwrite $dest — it has been edited by hand."
      echo "    Move your changes into ${src}, then run this script again."
      echo "    (.cursor/rules is generated; edits there are lost on every sync.)"
      CLOBBER=1
      rm -f "$tmp"
      continue
    fi
  fi

  mkdir -p .cursor/rules
  mv "$tmp" "$dest"
  echo "synced  $dest"
done

# --- orphan check ------------------------------------------------------------
# A .mdc with no matching .claude/rules/*.md source is a leftover that Cursor
# still loads. That is how a stale duplicate of rules-of-engagement survived
# under a misspelled filename.
for dest in .cursor/rules/*.mdc; do
  [ -f "$dest" ] || continue
  name=$(basename "$dest" .mdc)
  if [ ! -f ".claude/rules/${name}.md" ]; then
    echo "ORPHAN: $dest has no source at .claude/rules/${name}.md"
    STALE=1
  fi
done

# --- skills: verbatim --------------------------------------------------------
for src in .claude/skills/*/; do
  [ -d "$src" ] || continue
  name=$(basename "$src")
  dest=".cursor/skills/${name}"
  if [ "$CHECK" -eq 1 ]; then
    if ! diff -rq "$src" "$dest" >/dev/null 2>&1; then
      echo "OUT OF SYNC: $dest (source: $src)"
      STALE=1
    fi
  else
    mkdir -p "$dest"
    # -a keeps it a straight copy; skills need no format conversion.
    cp -a "$src". "$dest"/
    echo "synced  $dest/"
  fi
done

if [ "$CLOBBER" -eq 1 ]; then
  echo ""
  echo "Nothing was overwritten. Move the hand edits above into .claude/rules/,"
  echo "or re-run with --force to discard them."
  exit 1
fi

if [ "$CHECK" -eq 1 ] && [ "$STALE" -eq 1 ]; then
  echo ""
  echo "Run: sh .claude/scripts/sync-ai-config.sh"
  exit 1
fi

[ "$CHECK" -eq 1 ] && echo "AI config in sync." || echo "Done."
