---
description: Section coding standards, including the required merchant settings contract every section must expose
paths:
  - "sections/**/*.liquid"
---

# Section Development Standards

## The Merchant Settings Contract — required

**Every section must expose these settings.** This is not a style
preference; it is the contract that makes a section usable in the theme editor.
Base implements the desktop pair in 37 of its 48 sections; the mobile pair
joined the contract on 2026-09-21 and applies to new work (see the ruling
below the worked example).

| Setting | Required | Notes |
|---|---|---|
| `padding_top` | **Always. No exceptions.** | Desktop. `range`, 0–100, step 4, default 40 |
| `padding_bottom` | **Always. No exceptions.** | Desktop. `range`, 0–100, step 4, default 40 |
| `padding_top_mobile` | **Always. No exceptions.** | `range`, 0–100, step 4, default 40 |
| `padding_bottom_mobile` | **Always. No exceptions.** | `range`, 0–100, step 4, default 40 |
| `color_scheme` | Exposed by default | May be omitted **only** with a Liquid comment stating why (see below) |

Plus a `presets` entry, so a merchant can actually add the section.

### Why this rule exists

On the Bites Vitamins build, 30 of 31 new sections shipped without any of
this — spacing and colour were hardcoded into the CSS instead. The cause is
worth understanding, because it will recur: **a Figma frame specifies exactly
one spacing value and one background colour.** An agent building to match a
design has no reason to invent a merchant control, because the control is not
in the design. Visual fidelity was good; the merchant-facing contract was
near-zero. They are different success criteria and this one has to be applied
deliberately.

### The colour-scheme exception

Some designs fix a section's surface on purpose. When that is genuinely the
case, hardcode it and say so in one line:

```liquid
{%- comment -%}
  No color_scheme setting: this section's mint background is a fixed brand
  surface in the design (Figma node 1234:5678). Merchant-switchable schemes
  would break the illustration overlap.
{%- endcomment -%}
```

No comment means it was forgotten, not decided. The four padding settings have
no equivalent exception — there is no design reason for a merchant not to
adjust vertical rhythm, on either breakpoint.

## Section Structure

This is Base's actual pattern, verified against `sections/promo-banner.liquid`
and 36 other sections. **Load CSS with `stylesheet_tag`** (Base: 62 uses vs 4
for `{% stylesheet %}`) and **load JS as `type="module"`** (Base: 40 uses, zero
`defer`).

```liquid
{{ 'section-example-name.css' | asset_url | stylesheet_tag }}

{%- style -%}
  .section-{{ section.id }}-padding {
    padding-top: {{ section.settings.padding_top_mobile }}px;
    padding-bottom: {{ section.settings.padding_bottom_mobile }}px;
  }

  @media screen and (min-width: 750px) {
    .section-{{ section.id }}-padding {
      padding-top: {{ section.settings.padding_top }}px;
      padding-bottom: {{ section.settings.padding_bottom }}px;
    }
  }
{%- endstyle -%}

<div class="color-{{ section.settings.color_scheme }} section-{{ section.id }}-padding">
  <div class="page-width">
    {%- if section.settings.heading != blank -%}
      <h2 class="example-name__heading">{{ section.settings.heading | escape }}</h2>
    {%- endif -%}

    {%- for block in section.blocks -%}
      <div class="example-name__item" {{ block.shopify_attributes }}>
        {{ block.settings.text | escape }}
      </div>
    {%- endfor -%}
  </div>
</div>

{% schema %}
{
  "name": "t:names.example_name",
  "tag": "section",
  "settings": [
    {
      "type": "color_scheme",
      "id": "color_scheme",
      "label": "t:sections.all.colors.label",
      "default": "scheme-1"
    },
    {
      "type": "header",
      "content": "t:sections.all.padding.section_padding_heading"
    },
    {
      "type": "range",
      "id": "padding_top",
      "label": "t:sections.all.padding.padding_top",
      "min": 0, "max": 100, "step": 4, "unit": "px", "default": 40
    },
    {
      "type": "range",
      "id": "padding_bottom",
      "label": "t:sections.all.padding.padding_bottom",
      "min": 0, "max": 100, "step": 4, "unit": "px", "default": 40
    },
    {
      "type": "range",
      "id": "padding_top_mobile",
      "label": "t:sections.all.padding.padding_top_mobile",
      "min": 0, "max": 100, "step": 4, "unit": "px", "default": 40
    },
    {
      "type": "range",
      "id": "padding_bottom_mobile",
      "label": "t:sections.all.padding.padding_bottom_mobile",
      "min": 0, "max": 100, "step": 4, "unit": "px", "default": 40
    }
  ],
  "presets": [
    { "name": "t:names.example_name" }
  ]
}
{% endschema %}
```

> **The `750px` above is the padding boilerplate's breakpoint, not the theme's
> layout breakpoint.** Keep it — it is inherited from Dawn and 31 sections here
> already use it, so changing it in one section desynchronises that section's mobile
> padding from every other. Below it the mobile pair applies; at it and above,
> the desktop pair. Your own component CSS is a separate decision: Base's
> `section-*.css` is split evenly between `750px` and `769px`, so **in a client theme
> forked from Base, grep `assets/` and match whatever that theme settled on** rather
> than copying a number out of this file. Two numbers, two jobs — don't unify them.

> **`.page-width` is correct in Base and may not be in the theme you are working in.**
> Base uses it in all 32 of its sections. A client theme often introduces its own
> container with a different max-width, and the two are frequently **identical at
> 1440** — so a section built and measured only at 1440 passes review and then reads
> as broken on a large screen. This happened on a client build and was caught by the
> lead, not by the developer. Check which container class that theme's finished,
> QI-passed pages use, and measure at 1920 and 393 as well as at the width the Figma
> frame was drawn at.

> **Mobile padding is its own merchant setting, not a multiple of the desktop
> one.** Ruled 2026-09-17 on the Pique rebuild and adopted here 2026-09-21; it
> replaces the `padding_top | times: 0.75` boilerplate inherited from Dawn.
>
> The multiplier was measured wrong three ways on one build. Seven homepage
> bands at 393 wanted roughly *half* the desktop padding, so a `padding_top` of
> 80 needed 40 and the boilerplate gave 60 — every band's first row sat 19 to
> 21px low. A footer wanted 80/20 on desktop against 34/34 on mobile, ratios of
> 0.43 and 1.70 on the two edges of one section. And a header measured 9 on
> desktop against 15 on mobile — a ratio of 1.67, desktop the *tighter* band,
> because its tallest child was a 46px search field in a 64px bar while mobile
> fitted a 26px logo in 56px. A constant cannot express a ratio that crosses
> 1.0, so `0.75` was never a number to tune; it was the wrong shape.
>
> The tempting middle ("add the mobile pair only when the measured ratio is not
> about 0.75") was rejected. It leaves a judgment call at the moment a developer
> is least able to make it — before the section has been measured against its
> frames — and it is how four sections on one build ended up with three
> spellings between them. **Four settings always, no condition to evaluate.**
>
> **Existing sections are not retrofitted as part of unrelated work.** None of
> Base's 48 carries the mobile pair yet; a section still on the multiplier is
> legacy, not a bug to fix while passing through — the same standing rule as
> the 750/769 breakpoint split above. The retrofit is an open ruling in the
> decisions log. New sections carry all four.

The six `t:` keys above all resolve in `locales/en.default.schema.json` today —
use them rather than inventing new ones.

## Section Requirements

- `{% schema %}` with valid JSON, and a `presets` entry
- The settings above — four padding ranges and `color_scheme`
- Semantic HTML; a `page-width` wrapper unless the section is deliberately full-bleed
- CSS scoped to the section, in `assets/section-[name].css`
- **Translation keys for every string** — schema labels and user-facing text
  alike. See `localization.md`; it applies to brand-new sections exactly as
  much as to edits.
- `{{ block.shopify_attributes }}` on every block-rendered element

## Declaring a section exempt

A section a merchant cannot place is out of scope for the contract — but it has
to **say so**, in a Liquid comment mentioning `presets`:

```liquid
{%- comment -%}
  No `presets`: main section for the `product` template. A merchant places it
  by choosing the template, not by adding it in the theme editor.
{%- endcomment -%}
```

Three cases qualify, and nothing else does:

| Case | Example |
|---|---|
| Template main section | `product`, `cart`, `search`, `customers/*` |
| Section-group member | `header` |
| Render target, requested by other code | `pickup-availability`, `predictive-results` |

A separate comment mentioning `color_scheme` exempts that one setting on a
section that is otherwise in scope, for a design that fixes the surface on
purpose. **Padding has no exemption at all.**

The check only runs on sections **added** in a commit, so this is about new
work. Base's existing sections predate the contract and are not annotated: 17
have no `presets` (most of them legitimately, being template mains), 7 are
missing padding or `color_scheme`, and 20 carry bare English schema labels.
Do not copy an existing section and assume its schema is compliant — measure
against the list above, or start from
`.claude/skills/scaffold-section/reference-section.liquid`, which is.

## Naming

Name sections by **function**, not by the page they first appear on. `hero`,
`faq`, `selling-points` — not `home-hero` or `about-values`. A page-prefixed
name stops being descriptive the first time the section is reused, and on the
Bites build that happened immediately.

`main-` is reserved for template main sections. Do not use it for new sections.

## Do Not

- **Do not** use `{% stylesheet %}` or `{% content_for 'blocks' %}` in a new
  section. Both appear in older scaffolding examples, but Base uses
  `stylesheet_tag` and a `section.blocks` loop almost everywhere. `content_for`
  appears in exactly one Base section (`custom-section.liquid`) and is not the
  general pattern.
- **Do not** reach for container queries. Zero uses in Base; use the
  `min-width` media queries the rest of the theme uses.
- **Do not** follow `.claude/rules/examples/section-example.liquid`. It predates
  this rule, teaches the two patterns above, and exposes none of the required
  settings. The worked example in this file is the current one.

## Performance

- `{% liquid %}` for multi-line logic
- `loading="lazy"` on below-fold images
- Scope CSS custom properties to the section via `style="--foo: {{ setting }};"`
  rather than generating per-instance classes
