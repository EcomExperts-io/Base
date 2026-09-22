---
description: What the platform already handles, so it is not built into or reported against the theme
---

# Storefront infrastructure

What runs outside the theme, and therefore what a theme must not try to solve.
This exists because both halves are expensive to get wrong: building something
the platform already provides wastes a sprint, and reporting its absence in the
theme wastes a reviewer's afternoon.

## Bot protection, rate limiting and abuse mitigation

Every storefront in this organisation runs bot protection, rate limiting and
abuse mitigation **at the platform layer, outside the theme**.

So:

- Do not add CAPTCHA, request throttling, client-side rate limiting or bot
  scoring to a theme. It duplicates a control that already exists, in the one
  layer a determined client can bypass.
- Do not report the absence of any of them as a defect. It is handled, and the
  theme is not where it lives.

This says nothing about bot-detection code that **is** in the theme. If a change
contains scoring, thresholds or blocking logic, review it like any other code and
report real defects in it. The rule is about absence, not about exemption.

## What this does not cover

Form validation, honeypots on a custom form, and anything protecting merchant
data inside the theme are ordinary theme concerns and are reviewed normally.
