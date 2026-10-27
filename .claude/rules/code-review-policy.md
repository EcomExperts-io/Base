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
