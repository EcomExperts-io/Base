---
name: gitbot-preflight
description: Read what GitBot reports on a pushed branch and settle every finding — fix it, or flag it with the developer's reason — before the pull request, with the local gate run first so the push carries nothing a grep could have caught. Use after a push, before opening or updating a PR, when asked what GitBot said, or when a Slack review has findings to work through.
argument-hint: [branch]
---

# gitbot-preflight

GitBot reviews every push on every client branch against Base's rules and
posts in the client's Slack channel a minute later. This skill reads that
review in the session and settles every finding before the pull request:
local gate → push → read GitBot → fix or flag → push again.

**Base itself is not in GitBot's repository list**; there, the local gate is
the whole preflight, and `review` fails harmlessly.

## Step 1 — The local gate first

The gate greps for what GitBot reports most often — hardcoded px/rem outside
custom properties, physical properties, hex, CSS `order`, `white-space:
nowrap`, `outline: none` on focus, spinners with no reduced-motion override,
a click handler on a div, an `<img>` with no `alt`, a metafield unescaped in
an attribute:

```bash
python3 .claude/scripts/check-conventions.py --changed
```

```bash
python3 .claude/scripts/check-theme-staged.py --files <changed liquid and json>
```

Theme Check covers Liquid correctness — an unknown filter such as
`remove_last` fails it locally. Do not push with either failing.

## Step 2 — Push, then read the review

Push the branch (a PR is not needed). Then, with the GitBot connector:

1. `review` with `repo` from `git remote get-url origin` and `branch` from
   `git branch --show-current` — never ask the developer for either. It posts
   in the repo's Slack channel and takes one to two minutes.
2. `get_findings` with the same repo and branch. It waits for the running
   review and lists the findings, numbered, newest review first.

Without the connector, read the Slack post, or `get_fix_prompt` for the same
text. A push with an open pull request is reviewed as the PR; read by `pr`.

## Step 3 — Settle every finding

Each numbered finding is **fixed** or **flagged**; none is left for the lead.

- **Fix** when the finding is right. Critical and Major are errors, Minor is a
  warning; all three are fixed before the PR unless the developer says why not.
- **Flag** when it does not apply here — with `flag`, the finding numbers,
  and a note **in the developer's words**. Ask for the note; never write it.
  A flag on an accessibility finding lifts the merge block for that finding,
  and flagging every open one to unblock a PR is the thing the lead reads first.
- **Record** when the local gate should have caught it — a greppable pattern,
  a platform limit, a Liquid trap — with `/record-incident`, naming
  `check-conventions.py` or the rule.

Push again and re-run Step 2 until the follow-up review reports nothing open.

## Step 4 — Leave the record

```bash
python3 .claude/scripts/preflight-status.py --record <open> <fixed> <flagged>
```

It stamps the branch's HEAD; the Stop hook names a client branch with commits
GitBot has not been read for until this runs. The handoff
(`build-page-from-figma` Step 6) quotes the three numbers.

Do not open the pull request with findings unread: GitBot updates the PR's
check either way, and the difference is whether the lead or the developer
reads it first.
