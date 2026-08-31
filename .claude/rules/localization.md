---
description: Localization standards — applies to every string in every file, including brand-new sections with no existing translation calls nearby
paths:
  - "**/*.liquid"
  - "schemas/**"
---

# Localization Standards

## Scope — read this first

This rule applies to **every string you write**, in every file, regardless of
what the surrounding code looks like.

That sounds obvious enough not to need saying. It needs saying because of how it
actually failed. On the Bites Vitamins build, localisation was applied
diligently wherever the agent was *editing an existing Base file* — those files
were already dense with `| t` calls, so it matched them. In **brand-new
sections**, where there was no surrounding `| t` to copy, it was skipped almost
entirely: 5 uses of `| t` across 31 new sections, against 221 across Base's
sections, and zero `t:` schema keys against Base's 136.

The failure mode is pattern-matching on nearby code instead of applying a
standard. So, explicitly:

- A brand-new section with no translation calls anywhere in it is **not**
  evidence that translations don't apply here.
- An empty file is not a licence to hardcode English.
- Copy in a Figma frame is English because the designer wrote it in English.
  That is a design artifact, not an instruction to hardcode it.

## What counts as a string

All four of these need translating. The last two are the ones that get missed:

| Where | Example |
|---|---|
| Visible text | `<h2>{{ 'sections.faq.title' \| t }}</h2>` |
| Schema labels and preset names | `"label": "t:sections.all.colors.label"` |
| **Accessibility attributes** | `aria-label`, `alt`, `title` |
| **Screen-reader-only text** | `.visually-hidden` spans |

Concrete misses from the Bites build, all hardcoded English in shipped
`aria-label` attributes: `"Products"`, `"Contact methods"`,
`"Comparison columns"`, `"Filter reviews"`, `"Filter articles"`.

Schema labels use the `t:` prefix and live in
`locales/en.default.schema.json`. User-facing strings use `| t` and live in
`locales/en.default.json`. Two different files — check you are adding to the
right one.

### What does *not* need `| t`

**Merchant-entered text from a setting.** `{{ section.settings.heading | escape }}`
is content the merchant typed in the theme editor; it is already localised by
whoever typed it, and wrapping it in `| t` would be wrong. Most visible copy in
a content section is this.

`| t` is for **theme-provided** strings — text the theme itself supplies, which
the merchant never sees a field for:

| Needs `| t` | Does not |
|---|---|
| `"Add to cart"`, `"Read more"`, `"No results"` | `{{ section.settings.heading }}` |
| Empty-state and error copy | `{{ product.title }}` |
| `aria-label`, `alt`, `title` you authored | `{{ block.settings.text }}` |
| Schema labels (`t:` form) | Merchant-uploaded image alt text |

So a section whose visible copy all comes from settings can legitimately contain
very few `| t` calls. That is not the failure. The failure is the theme-authored
strings — accessibility attributes and schema labels above all — which have no
setting behind them and get hardcoded because nobody notices they are strings at
all.

## Translation Requirements

- **Every user-facing text** must use translation filters
- **Update `locales/en.default.json`** with all new keys
- **Use descriptive, hierarchical keys** for organization
- **Only add English text** - translators handle other languages

## Translation Filter Usage

**Use `{{ 'key' | t }}` for all text:**

```liquid
<!-- Good -->
<h2>{{ 'sections.featured_collection.title' | t }}</h2>
<p>{{ 'sections.featured_collection.description' | t }}</p>
<button>{{ 'products.add_to_cart' | t }}</button>

<!-- Bad -->
<h2>Featured Collection</h2>
<p>Check out our best products</p>
<button>Add to cart</button>
```

## Never chain `| escape` onto `| t`

`t` already HTML-escapes the values it interpolates. Adding `| escape` after it
encodes the output a second time, and the entity itself becomes visible: a
product called **Salt & Pepper** renders as `Salt &amp; Pepper` on the page.

```liquid
<!-- Bad — double-encoded -->
{{ 'blogs.article.back_to_blog' | t: title: blog.title | escape }}

<!-- Good -->
{{ 'blogs.article.back_to_blog' | t: title: blog.title }}
```

It is easy to misread the bad form as escaping the *argument*. It does not —
Liquid parses the filter arguments up to the next `|`, so `escape` receives the
finished output of `t`.

The escaping is keyed off the **key name**, which is the convention this theme
already relies on: a key ending in `_html` is left unescaped so it can carry
markup, and every other key has its interpolations escaped. This theme has eleven
`_html` keys (`paragraph_html`, `date_html`, `shipping_policy_html` …), which
is what proves the rule is in force here.

So:

| Key | `t` escapes interpolations? | Add `\| escape`? |
|---|---|---|
| `products.foo` | yes | never |
| `products.foo_html` | no, by design | no — the key opted out on purpose |

`| escape` is still correct on a **bare object** in its own output tag —
`{{ product.title | escape }}` — because nothing has escaped it yet. The rule
is only about chaining it onto `t`.

## Translation with Variables

**Use variables for interpolation:**

```liquid
<!-- Liquid template -->
<p>{{ 'products.price_range' | t: min: product.price_min | money, max: product.price_max | money }}</p>
<p>{{ 'general.pagination.page' | t: page: paginate.current_page, pages: paginate.pages }}</p>
```

**Corresponding keys in Locale files:**

```json
{
  "products": {
    "price_range": "From {{ min }} to {{ max }}"
  },
  "general": {
    "pagination": {
      "page": "Page {{ page }} of {{ pages }}"
    }
  }
}
```

## Best Practices

**Content Guidelines:**
- Write clear, concise text
- Use sentence case for UI elements
- Be consistent with terminology
- Consider character limits for UI elements

**Before you finish a file:**
- Grep your own output for bare English in `aria-label`, `alt`, and `"label"`.
  It is faster than waiting for review to catch it.
- Confirm every new key actually exists in the locale file. A `| t` pointing at
  a missing key renders the key path as visible text.

**Variable Usage:**
- Use interpolation rather than appending strings together
- Naming should be prioritize clarity over brevity
- Escape variables whenever they aren't expected to output HTML: `{{ variable | escape }}`
