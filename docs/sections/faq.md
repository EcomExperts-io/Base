# FAQ Section (`sections/Faq.liquid`)

`sections/Faq.liquid` renders an FAQ accordion with a configurable heading and multiple Q&A items (blocks). Each FAQ item can be expanded/collapsed, with the open state managed by Alpine.js (`x-data`, `x-show`, `x-transition`). The section supports color schemes and responsive padding.

---

## Dependencies & Assets

| Type | Files / Components |
|------|-------------------|
| CSS  | `section-faq.css`, inline `{%- style -%}` block for responsive padding |
| JS   | Uses Alpine.js directives in markup (no section-specific JS file) |
| Blocks | `faq_item` block type |
| Icons | `icon-plus.svg`, `icon-minus.svg` (inline via `inline_asset_content`) |
| Data | Relies on `section.settings` and `section.blocks` |

Notes:

- This section assumes Alpine.js is available globally in the theme (since it uses `x-data`, `x-show`, `x-transition`, `x-cloak`).

---

## Dynamic Styles

The section uses responsive padding set via a `{%- style -%}` block:

```liquid
{%- style -%}
  .section-{{ section.id }}-padding {
    padding-top: {{ section.settings.padding_top | times: 0.75 | round: 0 }}px;
    padding-bottom: {{ section.settings.padding_bottom | times: 0.75 | round: 0 }}px;
  }

  @media screen and (min-width: 750px) {
    .section-{{ section.id }}-padding {
      padding-top: {{ section.settings.padding_top }}px;
      padding-bottom: {{ section.settings.padding_bottom }}px;
    }
  }
{%- endstyle -%}
```

- **Responsive padding**: Mobile padding is 75% of desktop value; full padding applies at 750px+.

---

## Markup Structure

```liquid
<div class="color-{{ section.settings.color_scheme }} faq-section section-{{ section.id }}-padding">
  <div class="page-width">
    <!-- Optional heading -->
    <div class="faq__container" x-data="{ openBlock: null }">
      {%- for block in section.blocks -%}
        <!-- Accordion item -->
      {%- endfor -%}
    </div>
  </div>
</div>
```

### Heading

```liquid
{%- if section.settings.title != blank -%}
  <h2 class="faq__heading">{{ section.settings.title | escape }}</h2>
{%- endif -%}
```

### Accordion item (question + icon)

```liquid
<button
  @click="openBlock = openBlock === {{ forloop.index0 }} ? null : {{ forloop.index0 }}"
  class="faq__header"
  :aria-expanded="openBlock === {{ forloop.index0 }}"
  type="button"
>
  <h3 class="faq__title">{{ block.settings.question | default: 'Question' }}</h3>

  <span class="faq__icon" x-show="openBlock !== {{ forloop.index0 }}">
    {{ 'icon-plus.svg' | inline_asset_content }}
  </span>
  <span class="faq__icon" x-show="openBlock === {{ forloop.index0 }}" x-cloak>
    {{ 'icon-minus.svg' | inline_asset_content }}
  </span>
</button>
```

### Accordion content (answer)

```liquid
<div
  x-show="openBlock === {{ forloop.index0 }}"
  x-transition
  class="faq__content"
  x-cloak
>
  <div class="faq__content-wrapper">
    {%- if block.settings.answer != blank -%}
      <div class="faq__answer">
        {{ block.settings.answer }}
      </div>
    {%- else -%}
      <div class="faq__answer">
        <p>Add your answer here.</p>
      </div>
    {%- endif -%}
  </div>
</div>
```

- `answer` is a richtext setting and is output unescaped (expected HTML from the editor).

---

## Behavior

- **Accordion UI**: Implemented with Alpine.js state (`openBlock`) and transitions.
- **Initial state**: All items start collapsed (`openBlock: null`).
- **Icons**: Plus/minus icons swap based on open state; the open-state icon uses `x-cloak` to avoid flicker before Alpine initializes.

---

## Schema

```json
{
  "name": "FAQ",
  "tag": "section",
  "class": "faq",
  "settings": [
    { "type": "text", "id": "title", "label": "Heading", "default": "FREQUENTLY ASKED QUESTIONS" },
    { "type": "color_scheme", "id": "color_scheme", "label": "t:sections.all.colors.label", "default": "scheme-1" },
    { "type": "range", "id": "padding_top", "label": "Padding Top", "min": 0, "max": 100, "step": 4, "unit": "px", "default": 40 },
    { "type": "range", "id": "padding_bottom", "label": "Padding Bottom", "min": 0, "max": 100, "step": 4, "unit": "px", "default": 40 }
  ],
  "blocks": [
    {
      "type": "faq_item",
      "name": "FAQ Item",
      "settings": [
        { "type": "text", "id": "question", "label": "Question", "default": "Add Question here" },
        { "type": "richtext", "id": "answer", "label": "Answer", "default": "<p>Add your answer here.</p>" }
      ]
    }
  ],
  "presets": [{ "name": "FAQ" }]
}
```

---

## Implementation Notes

1. **Alpine dependency**: Without Alpine.js, content may stay hidden due to `x-cloak`, and the accordion won’t toggle.
2. **Accessibility**: Uses `:aria-expanded` bound to the open state; icons are purely visual.
3. **Richtext output**: `block.settings.answer` is rendered as HTML (expected for richtext).
4. **VitePress mustache safety**: If referencing Liquid mustaches in prose/inline code, escape them like `\{\{ ... \}\}` to avoid blank pages. [[memory:13638067]]

