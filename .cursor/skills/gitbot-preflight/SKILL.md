---
name: gitbot-preflight
description: Read what GitBot reports on a pushed branch and settle every finding — fix it, or flag it with the developer's reason — before the pull request, with the local gate run first so the push carries nothing a grep could have caught. Use after a push, before opening or updating a PR, when asked what GitBot said, or when a Slack review has findings to work through.
argument-hint: [branch]
---

# gitbot-preflight

GitBot reviews every push on every branch of every client repository against
Base's rules, and posts in the client's Slack channel. On one rebuild nothing
in the build read those posts: 532 of 1,363 commits were fixes, and the review
that would have named most of them was sitting in Slack a minute after each
push. This skill closes that gap from inside the session.

**Base itself is not in GitBot's repository list.** This skill is for client
forks. In Base, the local gate is the whole preflight.

GitBot reviews **what is pushed**, so there is no reviewing before a push.
The order is: local gate → push → read GitBot → fix or flag → push again.
A second review of the same branch is a follow-up; it judges the open
findings fixed or open.

## Step 1 — The local gate first

The gate greps for what GitBot reports most often: hardcoded px/rem
outside custom properties, physical properties, hex anywhere, CSS `order`,
`white-space: nowrap`, `outline: none` on focus, spinners with no
reduced-motion override, a click handler on a div, an `<img>` with no `alt`,
a metafield unescaped in an attribute. Run it and fix what it finds, so the
push carries nothing a grep could have caught:

```bash
python3 .claude/scripts/check-conventions.py --changed
```

```bash
python3 .claude/scripts/check-theme-staged.py --files <changed liquid and json>
```

Theme Check's recommended set covers Liquid correctness — an unknown filter
such as `remove_last` fails it locally. Do not push with it failing.

## Step 2 — Push, then read the review

Push the branch (not the PR — a pushed branch is enough). Then, with the
GitBot connector in the session:

1. `review` with `repo` from `git remote get-url origin` and `branch` from
   `git branch --show-current`. Never ask the developer for either. It posts
   in the repo's Slack channel and takes one to two minutes.
2. `get_findings` with the same repo and branch. It waits for the running
   review and lists the findings, numbered, newest review first.

Without the connector, read the Slack post, or `get_fix_prompt` for the same
text as the Slack button. GitBot's review of a push that already has an open
pull request is the pull request's review; read it by `pr` number.

## Step 3 — Settle every finding

Work through the numbered list. Each one is **fixed** or **flagged**; none is
left for the lead to find on the PR.

- **Fix** when the finding is right. Severity follows GitBot's own:
  Critical and Major are errors, Minor is a warning, and all three get fixed
  before the PR unless the developer says why not.
- **Flag** when it does not apply here — with `flag`, the finding numbers,
  and a note **in the developer's words**. Ask for the note; never invent
  one. The note is kept and shown to the lead. A flag on an accessibility
  finding lifts the merge block for that finding, so it is a decision, not a
  shortcut: flagging every open accessibility finding to unblock a PR is the
  thing the lead reads first.
- **Record** when a finding is something the local gate should have caught
  — a greppable pattern, a platform limit, a Liquid trap — with
  `/record-incident`, naming `check-conventions.py` or the rule. That is
  how the gate learns; the ten checks in Step 1 are one rebuild's most
  frequent findings written down.

Then push again and re-run Step 2. The follow-up review reports each earlier
finding fixed or still open; stop when nothing is open.

## Step 4 — Leave the record

```bash
python3 .claude/scripts/preflight-status.py --record <open> <fixed> <flagged>
```

It stamps the branch's HEAD. The Stop hook reads it: on a client branch with
commits GitBot has not been read for, it says so, once per turn, until this
runs. The handoff (`build-page-from-figma` Step 6) quotes the three numbers.

## What not to do

- Do not open the pull request with findings unread. GitBot updates the
  PR's check either way; the difference is whether the lead or the developer
  reads it first.
- Do not flag with a note you wrote. The note is the developer's reason and
  the lead reads it as such.
- Do not call `review` on Base. It is not configured; the call fails and
  nothing is lost, but the local gate was the answer.
