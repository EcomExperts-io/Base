---
description: How code is reviewed here — what to report, what to leave alone, and how to write it up
---

# Code review policy

Applies to a human reviewing a pull request, to an agent asked to review a
branch, and to GitBot, which reads this file directly.

## What to look for, in priority order

1. **Correctness bugs that change behaviour** — off-by-one, inverted conditions,
   unanchored matches, wrong variable, null and empty handling, regressions.
2. **Security and data issues** — leaking customer data, unsafe or unescaped
   output, injection, an exposed key or token. Classified as security, never
   as something softer.
3. **Brittle edges** — markets, currencies, empty carts, out of stock,
   logged-out users.
4. **Performance and accessibility regressions.**
5. **Minor issues and nits** — naming, dead code, style. Reported when the
   budget below has room for them.

## Classify by consequence, not by how it feels

Name what a defect actually harms; severity follows. The wrong product shown
to a shopper is a content defect even when embarrassing; a control that
misbehaves but lets the shopper through is a broken experience even when it
looks severe; what stops a shopper buying is a purchase blocker even when the
fix is one line.

## Report what matters, once

A review has a budget: **at most eight findings**, ordered by consequence. One
problem that occurs on several lines of a file is **one finding** — anchored to
the first line, the other lines named in the body. Five untranslated labels in
a schema are one localization finding, not five. Minor issues go in only when
fewer than three findings sit above them.

Invent nothing, and do not pad a review to look thorough: a clean change
reported as clean is a useful review.

Accessibility is its own pass with its own standard (`accessibility.md`) and
it is the one that blocks a merge. Untranslated text is localization and
unescaped output is security; neither is an accessibility finding.

## Do not assert what you cannot see

Do not claim something is missing, undefined, unused, never called or duplicated
unless you have the **full current content** of the file; a diff shows a slice.
If the point depends on the rest of the file, raise it as a question to check.

Only assert a platform limit you can name and point at (`schemas.md`,
`liquid.md`). Only call something a parse failure if you can show it breaks;
an undocumented spelling is not automatically invalid.

## Review this change, on this theme

**Only what the change introduced.** A line that is the same as on the base
branch, code moved from one file to another unchanged, or code that came in
by merging the base branch into this one is not this change's finding. If it
is wrong, it was wrong before; say so in the summary at most.

**The rules describe Base; a fork may predate them.** Where a rule names a
Base mechanism — `window.Cart` in `assets/cart.js`, colour schemes, the
section padding settings — it applies to a theme that has that mechanism.
On a theme without it, do not ask for it: the change follows what the theme
already uses. Check the file list or the full content before asserting the
mechanism exists.

**Match the file for style.** A style-level rule (media-query direction, the
`screen` media type, hardcoded colours in a file with no colour scheme, an
inline `<style>` in a family of sections that all use one) is not reported
on a line that follows the convention the rest of the same file already
uses. Mixing two conventions in one file is worse than either. Converting a
file is a separate task, not a finding on the line that matched it.

**Code that is not ours is not reviewed.** A file an app installs and owns —
an app's loader snippet (Shoplift's A/B testing loader), an app's own
section (Rivo's loyalty sections), anything whose header says an app
generated it —
is not changed by us and not reported on. Mention it in the summary if it
matters to the release.

## Respect documented intent

Where an author has written a comment explaining why something is deliberate or
safe, do not report it as a bug unless the code shows their reasoning is wrong.

## Writing it up

Every finding names the exact failure, the mechanism, and one specific fix —
the one you would apply, not a menu — in about forty words: the file, the
line, the mechanism and the consequence, with no general explanation of how
Liquid or CSS work.

Write the summary for a busy lead skimming the pull request: what the change
does, and its single biggest risk.

## Confidence

A confidence score rates **the review**, not the change. Five: everything
needed was available and the findings stand; three: reasoning partly from a
diff without context; one: largely guessing. A confidently reported blocker is
a five — risk in the change is carried by severity, never by confidence.

## The CHANGELOG entry

One past-tense line for the store's public CHANGELOG that a non-technical
account manager would understand: no file names, severities or mention of the
review. **Added** for new capability, **Fixed** for repaired behaviour,
**Changed** for the rest. For example: *Improved keyboard accessibility and
focus treatment for product option selectors on product pages.*
