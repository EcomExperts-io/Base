#!/bin/sh
# One command to make a checkout ready for the Base AI workflow.
#
# Why this exists
# ---------------
# Before this, activating the workflow meant knowing four unrelated things: that
# hooks live in .githooks/ and need core.hooksPath (or a husky shim in a client
# fork), that .cursor/ is generated and must be regenerated, which MCP servers
# the skills expect, and how to tell whether any of it worked. Nothing in the
# repo said so. `npm run setup` says so, and doctor.py proves it.
#
# Safe to re-run at any time. Writes nothing outside this repo except the
# git config for this checkout.

set -e
cd "$(git rev-parse --show-toplevel)"

echo "==> commit gate"
if [ -d .husky ]; then
  # A client fork on husky keeps husky. Base's checks run from inside it.
  HOOK=.husky/pre-commit
  LINE='sh "$(git rev-parse --show-toplevel)/.githooks/pre-commit"'
  if [ ! -f "$HOOK" ]; then
    printf '%s\n' "$LINE" > "$HOOK"
    chmod +x "$HOOK"
    echo "    created $HOOK calling .githooks/pre-commit"
  elif ! grep -Fq '.githooks/pre-commit' "$HOOK"; then
    printf '\n%s\n' "$LINE" >> "$HOOK"
    echo "    appended Base's pre-commit to $HOOK"
  else
    echo "    $HOOK already calls .githooks/pre-commit"
  fi
  git config core.hooksPath .husky
else
  git config core.hooksPath .githooks
  echo "    core.hooksPath = .githooks"
fi
chmod +x .githooks/pre-commit .claude/hooks/*.sh 2>/dev/null || true

echo "==> cursor mirror"
sh .claude/scripts/sync-ai-config.sh | tail -1

echo "==> cache directories"
mkdir -p .claude/.cache .claude/verify

echo "==> doctor"
python3 .claude/scripts/doctor.py

cat <<'NEXT'
  Next, once, on this machine:

    1. claude plugin install figma@claude-plugins-official
         The Figma MCP and the design-to-code skill the build workflow calls.
    2. claude                       then approve the project MCP servers when asked,
       /mcp                         and sign in to notion.
    3. Store handle for `shopify theme dev` and the verify skill:
         echo '{"env":{"SHOPIFY_FLAG_STORE":"<store-handle>"}}' > .claude/settings.local.json
    4. Read docs/ai-workflow/first-build.md and do the build it describes.

NEXT
