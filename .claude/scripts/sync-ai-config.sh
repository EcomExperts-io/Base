#!/bin/sh
# Keeps the Cursor, Codex and Claude Code copies of our AI configuration identical.
#
# Usage: sh .claude/scripts/sync-ai-config.sh [--check] [--force]
#   --check  exit 1 if anything is out of sync, write nothing (for the hook)
#   --force  overwrite even a hand-edited .mdc (discards it — last resort)
#
# Canonical source is .claude/ — edit there, never in .cursor/.
#   Rules:     .claude/rules/*.md        -> .cursor/rules/*.mdc  (frontmatter converted)
#   Examples:  .claude/rules/examples/** -> .cursor/rules/examples/**  (verbatim)
#   Skills:    .claude/skills/**         -> .cursor/skills/**          (verbatim)
#   Agents:    .claude/agents/**         -> .cursor/agents/**          (verbatim)
#   Workflows: .claude/workflows/**      -> .cursor/workflows/**       (verbatim)
#   References:.claude/references/**     -> .cursor/references/**      (verbatim)
#   Hooks:     .claude/hooks/**          -> .cursor/hooks/**           (verbatim)
#
# Codex reads a different layout:
#   Skills:    .claude/skills/**         -> .agents/skills/**          (verbatim, tree replaced)
#   Hooks:     .claude/hooks/**          -> .codex/hooks/**            (verbatim, tree replaced)
#   Agents:    .claude/agents/*.md       -> .codex/agents/*.toml       (frontmatter + body as TOML)
#   CLAUDE.md                            -> AGENTS.md                  (banner + checksum; paths kept,
#                                                                       the files really are under .claude/)
# .codex/config.toml (MCP servers) and .codex/hooks.json (the hook wiring, the
# Codex equivalent of .claude/settings.json) are hand-maintained and tracked.
#
# Notes:
#   * Hooks are mirrored so a Cursor user has the gate scripts to wire into
#     Cursor's own hooks configuration; the wiring (.claude/settings.json) has
#     no Cursor equivalent. Cursor does not auto-load agents or workflows the
#     way it loads rules; the mirrored copies are for a human to open.
#   * Generated .mdc files carry a checksum of their own content. If it no
#     longer matches, the file was edited by hand and the script REFUSES to
#     overwrite it.
#   * Skills and the other verbatim trees carry no checksum, so a hand-edit
#     there cannot be told from a source change and is overwritten.

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

  # Conflict markers in a generated file are not a hand edit: two branches that
  # each regenerated the same .mdc collide on the checksum line, and the
  # resolution is always to regenerate from .claude/.
  if [ -f "$dest" ] && grep -q '^<<<<<<< \|^>>>>>>> ' "$dest"; then
    mv "$tmp" "$dest"
    echo "resolved $dest (merge conflict in a generated file — regenerated)"
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
# still loads.
for dest in .cursor/rules/*.mdc; do
  [ -f "$dest" ] || continue
  name=$(basename "$dest" .mdc)
  if [ ! -f ".claude/rules/${name}.md" ]; then
    echo "ORPHAN: $dest has no source at .claude/rules/${name}.md"
    STALE=1
  fi
done

# --- verbatim trees ----------------------------------------------------------
# Everything below is a straight copy — no format conversion, and so no banner
# and no checksum. A hand-edit under .cursor/ in these trees cannot be told
# apart from a source change and WILL be overwritten. Edit .claude/ only.
mirror_tree() {
  src="$1"
  dest="$2"
  [ -d "$src" ] || return 0
  if [ "$CHECK" -eq 1 ]; then
    if ! diff -rq "$src" "$dest" >/dev/null 2>&1; then
      echo "OUT OF SYNC: $dest (source: $src)"
      STALE=1
    fi
  else
    # Replace the tree rather than layer onto it: `cp -a` alone never removes a
    # destination file whose source was deleted or renamed. The guard keeps a
    # bad argument from ever expanding to `rm -rf` of anything outside .cursor/.
    case "$dest" in
      .cursor/*|.agents/*|.codex/hooks*) rm -rf "$dest" ;;
      *) echo "refusing to replace '$dest': not a generated tree"; exit 1 ;;
    esac
    mkdir -p "$dest"
    cp -a "$src". "$dest"/
    echo "synced  ${dest%/}/"
  fi
}

# The skills tree is replaced as a whole, so a renamed skill leaves no
# orphan behind.
mirror_skills() {
  root="$1"
  if [ "$CHECK" -eq 1 ]; then
    if ! diff -rq .claude/skills "$root" >/dev/null 2>&1; then
      echo "OUT OF SYNC: $root/ (source: .claude/skills/)"
      STALE=1
    fi
    return 0
  fi
  case "$root" in
    .cursor/skills|.agents/skills) rm -rf "$root" ;;
    *) echo "refusing to replace '$root': not a generated tree"; exit 1 ;;
  esac
  for src in .claude/skills/*/; do
    [ -d "$src" ] || continue
    mirror_tree "$src" "$root/$(basename "$src")"
  done
}
mirror_skills .cursor/skills
mirror_skills .agents/skills

mirror_tree ".claude/rules/examples/" ".cursor/rules/examples/"
mirror_tree ".claude/agents/"         ".cursor/agents/"
mirror_tree ".claude/workflows/"      ".cursor/workflows/"
mirror_tree ".claude/references/"     ".cursor/references/"
mirror_tree ".claude/hooks/"          ".cursor/hooks/"
mirror_tree ".claude/hooks/"          ".codex/hooks/"

# --- Codex agents: .claude/agents/*.md -> .codex/agents/*.toml ----------------
# Frontmatter name and description become TOML keys; the body becomes
# developer_instructions. Python does the escaping (a backslash or a triple
# quote in a body would otherwise break the TOML string).
gen_agents() {
  python3 - "$CHECK" <<'PY'
import glob, os, re, sys
check = sys.argv[1] == "1"
stale = False
os.makedirs(".codex/agents", exist_ok=True)
expected = set()
for src in sorted(glob.glob(".claude/agents/*.md")):
    text = open(src, encoding="utf-8").read()
    m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    fm, body = (m.group(1), m.group(2)) if m else ("", text)
    def field(k):
        mm = re.search(r"^%s:\s*(.*)$" % k, fm, re.M)
        return mm.group(1).strip() if mm else ""
    name = field("name") or os.path.basename(src)[:-3]
    desc = field("description").replace("\\", "\\\\").replace('"', '\\"')
    esc = body.replace("\\", "\\\\").replace('"""', '""\\"')
    out = ("# GENERATED from %s by .claude/scripts/sync-ai-config.sh - do not edit here.\n"
           'name = "%s"\ndescription = "%s"\ndeveloper_instructions = """\n%s"""\n' % (src, name, desc, esc))
    dest = ".codex/agents/%s.toml" % name
    expected.add(dest)
    cur = open(dest, encoding="utf-8").read() if os.path.exists(dest) else None
    if cur == out:
        continue
    if check:
        print("OUT OF SYNC: %s (source: %s)" % (dest, src)); stale = True
    else:
        open(dest, "w", encoding="utf-8").write(out); print("synced  " + dest)
for dest in glob.glob(".codex/agents/*.toml"):
    if dest not in expected:
        if check:
            print("ORPHAN: %s has no source under .claude/agents/" % dest); stale = True
        else:
            os.remove(dest); print("removed " + dest)
sys.exit(1 if stale else 0)
PY
}
if ! gen_agents; then STALE=1; fi

# --- AGENTS.md from CLAUDE.md -------------------------------------------------
# Same content, same paths (they are real), a banner and a checksum so a hand
# edit is refused rather than discarded, as for the .mdc files.
gen_agents_md() {
  src="CLAUDE.md"
  dest="AGENTS.md"
  [ -f "$src" ] || return 0
  tmp=$(mktemp)
  awk 'NR==1 && /^# CLAUDE\.md/ { print "# AGENTS.md"; next }
       { sub(/^Guidance for Claude Code \(and any AI coding tool\)/, "Guidance for Codex (and any AI coding tool)"); print }' "$src" > "$tmp"
  tmp2=$(mktemp)
  awk 'NR==1 { print; print ""; print "<!-- GENERATED from CLAUDE.md by .claude/scripts/sync-ai-config.sh - do not edit here. The files it names live under .claude/; .codex/ holds the Codex wiring and the generated hooks and agents. -->"; next } { print }' "$tmp" > "$tmp2"
  mv "$tmp2" "$tmp"
  sum=$(content_sum "$tmp")
  awk -v s="$sum" '/^<!-- GENERATED from CLAUDE\.md /{ print; print "<!-- checksum: " s " -->"; next } { print }' "$tmp" > "$tmp2"
  mv "$tmp2" "$tmp"
  if [ -f "$dest" ] && cmp -s "$tmp" "$dest"; then rm -f "$tmp"; return 0; fi
  if [ "$CHECK" -eq 1 ]; then echo "OUT OF SYNC: $dest (source: $src)"; STALE=1; rm -f "$tmp"; return 0; fi
  if [ -f "$dest" ] && grep -q '^<<<<<<< \|^>>>>>>> ' "$dest"; then mv "$tmp" "$dest"; echo "resolved $dest (merge conflict in a generated file - regenerated)"; return 0; fi
  if [ -f "$dest" ] && [ "$FORCE" -eq 0 ]; then
    recorded=$(sed -n 's/^<!-- checksum: \([0-9]*\) -->$/\1/p' "$dest" | head -1)
    actual=$(content_sum "$dest")
    if [ -n "$recorded" ] && [ "$recorded" != "$actual" ]; then
      echo "REFUSING to overwrite $dest - it has been edited by hand. Move the change into CLAUDE.md."
      CLOBBER=1; rm -f "$tmp"; return 0
    fi
  fi
  mv "$tmp" "$dest"
  echo "synced  $dest"
}
gen_agents_md

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
