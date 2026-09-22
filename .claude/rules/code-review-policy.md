---
description: How code is reviewed here — what to report, what to leave alone, and how to write it up
---

# Code review policy

Applies to a human reviewing a pull request, to an agent asked to review a
branch, and to GitBot, which reads this file directly.

## What to look for, in priority order

1. **Correctness bugs that change behaviour** — off-by-one, inverted conditions,
   unanchored matches, wrong variable, null and empty handling, regressions.
2. **Security and data issues** — leaking customer data, unsafe output,
   injection, exposed tokens.
3. **Brittle edges** — markets, currencies, empty carts, out of stock,
   logged-out users.
4. **Performance and accessibility regressions.**
5. **Minor issues and nits** — naming, dead code, style. Still worth reporting.

## Classify by consequence, not by how it feels

Name what a defect actually harms; severity follows from that. Wrong text or the
wrong product shown to a shopper is a content defect even when embarrassing. A
control that misbehaves but still lets the shopper through is a broken experience
even when it looks severe. Something that stops a shopper buying is a purchase
blocker even when the fix is one line.

## Report what you find, invent nothing

Do not self-filter for importance — coverage matters. Do not pad a review to look
thorough either: a clean change reported as clean is a useful review.

## Do not assert what you cannot see

Do not claim something is missing, undefined, unused, never called or duplicated
unless you have the **full current content** of the file. A diff shows a slice;
the definition may sit elsewhere in it. If the point depends on the rest of the
file and you only have the diff, leave it out or raise it as a question to check.

The same caution applies to limits and to syntax. Only assert a platform limit
you can name and point at — the ones we have documented live with their topic, in
`schemas.md` and `liquid.md`. Only call something a parse failure if you can show
it breaks; an undocumented spelling is not automatically invalid, and reporting
working code as broken sends a developer rewriting something that already runs.

## Respect documented intent

Where an author has written a comment explaining why something is deliberate or
safe, do not report it as a bug unless the code shows their reasoning is wrong.

## Writing it up

Every finding names the exact failure, the mechanism, and one specific fix — the
one you would apply, not a menu.

Be brief. A finding read in ten seconds gets fixed; a paragraph gets skimmed.
About forty words of prose. Keep the file, the line, the mechanism and the
consequence; drop the explanation of how Liquid or CSS work in general and the
second way of fixing it.

Write the summary for a busy lead skimming the pull request: what the change
does, and its single biggest risk.

## Confidence

Where a review states a confidence score it rates **the review**, not the change:
how much should a lead trust what was just written? Five means everything needed
was available and the findings stand; three means reasoning partly from a diff
without surrounding context; one means largely guessing.

Finding a serious bug does not lower it — a confidently reported blocker is a
five. Risk in the change is carried by severity, never by lowering confidence.

## The CHANGELOG entry

Not the review summary. It goes in the store's public-facing CHANGELOG: one
past-tense line a non-technical account manager would understand, describing what
the change does for the storefront. No file names, no severities, no mention of
the review. **Added** for new capability, **Fixed** for repaired behaviour,
**Changed** for the rest. For example: *Improved keyboard accessibility and focus
treatment for product option selectors on product pages.*
