---
name: pr-review
description: Run a standards checklist against changed files in a PR before merge and emit a structured pass/fail report. Use when the user asks to review a PR or a git diff against theme standards.
---

# pr-review

**Purpose:** Run a standards checklist against any set of changed files in a PR before merge.

**Invocation:** `/pr-review` (run against the current git diff, or against a named PR)

## Steps

1. Identify all changed files (Liquid, CSS, JS).
2. Run each check in the checklist below and emit a structured pass/fail report.
3. For any failure, cite the file, line number, and the specific standard violated.
4. Do **not** auto-fix — report only. The developer decides whether to fix before merge.

## Checklist

| # | Check | Standard | Bucket 1 Finding |
|---|-------|----------|-----------------|
| P-01 | No new `sections/` files with capital letters in name | `naming-conventions.mdc` | Faq.liquid anomaly |
| P-02 | No new `sections/` files with `main-` prefix | `naming-conventions.mdc` | Pre-existing rule |
| P-03 | All new/modified snippets have a `{% doc %}` block | `snippets.mdc` | 13 missing LiquidDoc |
| P-04 | All `<script src>` tags for section/component JS use `type="module"` not `defer` | `javascript-standards.mdc` | `shop-by-category` `defer` anomaly |
| P-05 | No new `customElements.define` without a `customElements.get` guard | `javascript-standards.mdc` | Pre-existing rule |
| P-06 | No ID selectors in new/modified CSS | `css-standards.mdc` | `cart.css` ID selectors |
| P-07 | No new `!important` declarations without an explanatory comment on the same line | `css-standards.mdc` | 41 undocumented `!important` |
| P-08 | No hardcoded hex color values in new/modified CSS or Liquid | `css-standards.mdc` | ~50 hardcoded hex values |
| P-09 | All schema labels in new/modified sections use `t:` key format | `schemas.mdc` / `localization.mdc` | i18n drift in multiple sections |
| P-10 | All user-facing strings in Liquid output pass through `\| t` | `localization.mdc` | `"Quantity"` hardcoded string |
| P-11 | If section uses Swiper, verify `theme.liquid` template whitelist covers the template where the section appears | `theme.liquid` pattern | Swiper conditional load gap |
| P-12 | No `DOMContentLoaded` event listeners in new JS | `rules-of-engagement.mdc` | Pre-existing rule |
| P-13 | No jQuery usage | `rules-of-engagement.mdc` | Pre-existing rule |
| P-14 | `theme.liquid` remains ≤ 300 lines | `rules-of-engagement.mdc` | Pre-existing rule |
| P-15 | New snippet parameters have default values assigned via `\| default:` | `snippets.mdc` | Parameter validation gap |
