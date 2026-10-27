---
description: What the platform already handles, so it is not built into or reported against the theme
---

# Storefront infrastructure

What runs outside the theme, and therefore what a theme must not build or
report as missing.

## Bot protection, rate limiting and abuse mitigation

Every storefront in this organisation runs these **at the platform layer,
outside the theme**.

- Do not add CAPTCHA, request throttling, client-side rate limiting or bot
  scoring to a theme; it duplicates a control in the one layer a client can bypass.
- Do not report the absence of any of them as a defect.

Bot-detection code that **is** in the theme — scoring, thresholds, blocking
logic — is reviewed like any other code. The rule is about absence, not exemption.

## What this does not cover

Form validation, honeypots on a custom form, and anything protecting merchant
data inside the theme are ordinary theme concerns and are reviewed normally.
