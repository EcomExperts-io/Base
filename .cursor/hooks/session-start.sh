#!/bin/sh
# SessionStart hook — prints the state of this checkout as session context.
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
if [ -f .claude/scripts/where-are-we.py ]; then
  python3 .claude/scripts/where-are-we.py 2>/dev/null
fi
echo "Most-missed rules: (1) every merchant-addable section exposes padding_top, padding_bottom, padding_top_mobile, padding_bottom_mobile, color_scheme and a preset — mobile padding is its own setting, not 0.75x desktop; (2) every string is a translation key — schema labels, aria-label, alt, and brand-new files most of all; (3) name by function, never by page; a class on a custom-element tag needs an explicit display."
echo "Skills: /build-page-from-figma  /verify-against-reference  /scaffold-section  /recon-theme  /record-incident  /harvest  — details: python3 .claude/scripts/doctor.py"
exit 0
