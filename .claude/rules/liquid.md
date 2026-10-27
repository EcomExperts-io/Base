---
description: Liquid syntax standards
paths:
  - "**/*.liquid"
---

# Liquid Syntax Standards

## Syntax Rules

- `{% liquid %}` for multiline logic; `{% # comment %}` for inline comments
- Never invent filters, tags or objects; Shopify's reference is the whole list
- Close tags in reverse order of opening
- Dot notation: `product.title`, not `product['title']`
- `{% render %}` for snippets; `{% section %}` for a static section
- Escape anything printed into an attribute: `{{ value | escape }}`

## Traps

### A literal `{{ }}` cannot be passed as a filter argument

Shopify's tokenizer cuts an output tag at the **first** `}` it meets, so a
string literal holding a brace fails the whole file with "Variable … was not
properly terminated" — every route 500s. Build the string with `capture` first:

```liquid
{% comment %} BROKEN — the tag closes at the inner brace {% endcomment %}
{{ 'products.price_each' | t: price: '{{price}}' }}

{% comment %} Correct — a translated string handed to JavaScript as a template {% endcomment %}
{%- capture price_token %}{% raw %}{{price}}{% endraw %}{% endcapture -%}
{{ 'products.price_each' | t: price: price_token }}

{% comment %} Correct — JSON for a data attribute {% endcomment %}
{%- capture props -%}{"_supply_length":"{{ days }}-day"}{%- endcapture -%}
data-properties="{{ props | escape }}"
```

### Filters are not applied to `{% render %}` arguments

The filter is silently ignored and the snippet receives the raw value. Assign
first — the one standing exception to the inline-variables pattern below.
Theme Check reports it as `UnsupportedFilterArguments`.

```liquid
{% comment %} BROKEN — the snippet gets the raw drop {% endcomment %}
{% render 'component-answer', answer: item.answer | metafield_tag %}

{% comment %} Correct {% endcomment %}
{%- assign answer_html = item.answer | metafield_tag -%}
{% render 'component-answer', answer: answer_html %}
```

### A rich text metafield does not print as HTML

`rich_text_field` stores a JSON AST; `metafield_tag` is the filter that
produces markup, and it brings its own wrapper element. A schema `richtext`
**setting** is already HTML and needs no filter.

```liquid
{{ item.answer }}                     {% comment %} {"type":"root",…} on the page {% endcomment %}
{{ item.answer.value }}               {% comment %} same tree, as an object {% endcomment %}
{{ item.answer | metafield_tag }}     {% comment %} <div class="metafield-rich_text_field"><p>…</p></div> {% endcomment %}
```

### Array filters cannot reach a nested property on a metaobject

`sort`, `sort_natural`, `map` and `where` all fail quietly on a dotted path
such as `system.id`: the sort is a no-op, `map` returns empties, `where`
matches nothing.

Sort on a field the merchant controls — an explicit `order` or `date` field on
the definition. `metaobject.system` exposes only `handle`, `id`, `type` and
`url`; there is no `created_at`, and id order is not documented. If you must
fall back to `system.id`, build the key by hand (append `key:handle` pairs,
`split`, `sort`, match back; zero-pad a numeric key) and say so in a Liquid
comment and in the handoff.

### `.first` does not work on `shop.metaobjects.<type>.values`

It iterates in a `for` loop but `.first` returns blank. Use `for … limit: 1`.
`shop.metaobjects` is documented as replaced by `metaobjects`, and the
paginated form (`{% paginate … by 250 %}`) and the bare form differ once a type
holds more than one page of entries.

### Count a `*_list` setting with `.count`, not `.size`

`.size` on an `article_list` or `product_list` setting is blank, so
`pool.size > 0` renders the empty state with every post picked. `blog.articles`
is a real array where `.size` works, which hides the bug until the setting branch runs.

### A typed metafield's `.value` is a drop, and its numbers are strings

`product.metafields.reviews.rating.value` prints `4.8` and `| times: 100.0`
gives `0.0`. The number is `.value.rating`, as a JSON string, so coerce with
`| times: 1.0` before comparing. `money`, `dimension` and `volume` have the same shape.

### Multi-tag collection URLs are alphabetical

Shopify canonicalises `/collections/all/<tag>+<tag>` to alphabetical order and
301s any other order with no `Location` header, so a section fetch gets nothing
to follow. Sort before building the path:
`assign next_tags = next_tags | split: '+' | sort | join: '+'`.

### Date arithmetic: `date: '%s'` returns a string

Add seconds to a coerced timestamp; `%e` is space-padded, so strip it first.

```liquid
assign stamp = 'now' | date: '%s' | plus: 0
assign stamp = days | times: 86400 | plus: stamp
assign day   = stamp | date: '%e' | strip | plus: 0
assign month = stamp | date: '%b'
```

Ordinals need the teens exception (`day | modulo: 100` in 11–13 is "th"), as
translation keys. `'now'` is UTC and the page cache can hold it across midnight.

### Nil is not an error

A missing value renders empty, `contains` against nil is false, a filter on nil
returns nil. Nothing raises.

```liquid
{{ product.metafields.custom.missing }}
{% if product.tags contains undefined_variable %}{% endif %}
{{ nil_value | upcase | strip }}
```

Report a nil as the content bug it is — a silent blank, or a whole `{% if %}`
block that renders nothing — never as a runtime error.

### `with` before a named argument still parses

```liquid
{% render 'component-list' with items: collection.products %}
{% render 'component-list', items: collection.products %}
```

Both pass `items`; prefer the comma form. An undocumented spelling is not a
syntax error, and reporting working markup as broken sends a developer
rewriting something that already renders.

## Inline Variables Pattern

Inline straightforward values rather than assigning them first, so what is
applied where reads in one place.

**✅ Do this:**

```liquid
<div
  class='component component--{{ settings.style_modifier }}'
  style='
    color: {{ settings.text_color }};
    {% if settings.show_border %}
      border: 1px solid {{ settings.border_color }};
    {% endif %}
  '
>
  <h2>{{ 'sections.component.title' | t }}</h2>
  {{ content | truncate: settings.max_length | default: 200 }}
</div>
```

**❌ Not this:**

```liquid
{% liquid
  assign component_class = 'component component--' | append: settings.style_modifier
  assign text_color = settings.text_color
  assign truncate_length = settings.max_length | default: 200
%}

{% capture component_style %}
  color: {{ text_color }};
  {% if settings.show_border %}
    border: 1px solid {{ settings.border_color }};
  {% endif %}
{% endcapture %}

<div class='{{ component_class }}' style='{{ component_style }}'>
  <h2>{{ 'sections.component.title' | t }}</h2>
  {{ content | truncate: truncate_length }}
</div>
```

Assign first when a filtered value goes to `render`, when the same calculation
is used more than once, or when a string is built incrementally.
