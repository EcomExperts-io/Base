#!/bin/sh
# SessionStart hook — every session opens knowing where the theme stands.
#
# Why this exists
# ---------------
# The rules run to 3,700 lines and CLAUDE.md is loaded every session, but
# neither can say what is true of THIS checkout right now: whether the gate is
# wired, how far the tooling has drifted from Base, how many sections meet the
# contract, how many incidents are waiting to be harvested. Those numbers
# change daily and were only ever known to the one person who ran the scripts.
# Ten lines here, under a second, and the session starts from facts.
#
# Plain stdout from a SessionStart hook is injected as context. Keep it short.

ROOT="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null)}"
[ -n "$ROOT" ] || exit 0
cd "$ROOT" || exit 0
[ -f .claude/scripts/doctor.py ] || exit 0

echo "Base AI workflow — session context"
python3 .claude/scripts/doctor.py --context 2>/dev/null
if [ -f .claude/scripts/check-tooling-drift.py ]; then
  python3 .claude/scripts/check-tooling-drift.py --brief 2>/dev/null
fi
echo "Most-missed rules: (1) every merchant-addable section exposes padding_top, padding_bottom, color_scheme and a preset; (2) every string is a translation key — schema labels, aria-label, alt, and brand-new files most of all; (3) name by function, never by page; a class on a custom-element tag needs an explicit display."
echo "Skills: /build-page-from-figma  /verify-against-figma  /scaffold-section  /recon-theme  /record-incident  /harvest  — details: python3 .claude/scripts/doctor.py"
exit 0
