# Workflow — building a page's sections with parallel agents

Build one page of a Figma design by giving each section to its own agent,
running them concurrently, then assembling and verifying the page yourself.
A human starts this. **Use it** for a page of 5+ independent content
sections, each with its own Figma frame; **not** when sections share a
stylesheet or JS module, or one's markup depends on another's.

---

## Part 1 — Orchestrator (you)

### 1. Establish the section list before spawning anything

Enumerate the page's sections from the desktop frame, top to bottom, with the
**desktop node id and the mobile node id** for each. One agent per row. Then
**check what already exists**: a section another page ships is a
`templates/*.json` entry, not a build. Grep `sections/` and open both; a name match is not enough.

### 2. Fill in the agent brief

Copy Part 2 into the scratchpad, fill the placeholders, and hand every agent
the same file: divergent briefs produce divergent conventions.

### 3. Spawn, then stay out of the way

One agent per section, all in a single message so they run concurrently,
each with only its own two node ids and file ownership list.

### 4. Assemble

- Merge the locale fragments: `python3 .claude/scripts/merge-locale-fragments.py <fragment-dir>`.
  It refuses to overwrite an existing key and reports every conflict.
- Build `templates/<page>.json` from the section presets, in frame order.
- **Strip `t:` values.** Shopify resolves `t:` in a schema `default`, not in
  a template value; one left in renders the key path to the customer.
- A brand-new block type needs roughly 25 seconds to register with Shopify
  before a template may reference it; too early and every route returns 500.

### 5. Verify — before you report anything

Agents report their own fidelity, often from a static harness; a section can
measure 614px against a 615px frame and share nothing else with it. With the
template assembled and the theme running (`/run-theme`), run
`/verify-against-reference` per band with its desktop and mobile node ids and
a `--section` selector; it writes `.claude/verify/<band>/report.json`. Agents
cannot run it — their section is not on a page yet — which is why step 10 of
their brief asks for the raw values. No usable screenshot means "unverified".

### 6. Gate

`shopify-pr-reviewer` over the whole diff before it goes to a human.

---

## Part 2 — Agent brief template

Fill in `{{REPO}}`, `{{BRANCH}}`, `{{FIGMA_FILE_KEY}}`, `{{FRAGMENT_DIR}}`,
`{{PREVIEW_URL}}`, then give this to every agent verbatim.

---

Repo: `{{REPO}}`
Branch: `{{BRANCH}}` (already checked out — do not switch branches)

You are building **one section** of a page from Figma; other agents build
the others in parallel. Stay strictly inside the files you own.

### 1. Read these before writing any code

- `CLAUDE.md` and `.claude/rules/` — they apply in full
- `.claude/skills/scaffold-section/SKILL.md` — follow its steps and its self-check
- `.claude/skills/scaffold-section/reference-section.liquid` — the structural template

Do **not** use `.claude/rules/examples/section-example.liquid`. It predates the standard.

### 2. Get the design — two frames, separately

Invoke the Figma design-to-code skill **before** your first
`get_design_context` call. Then call it twice, once per frame:

```
get_design_context
  fileKey: {{FIGMA_FILE_KEY}}
  nodeId: <your DESKTOP node>
  clientLanguages: liquid,html,css
  clientFrameworks: shopify-liquid
```

- Desktop frames are designed at **1440**, mobile at **393**: two designs,
  not one responsive artifact.
- Read real values — spacing, type, line height, colour, radii — off the
  design; never by eye. The returned React + Tailwind is **reference only**.
- Icons and images come back as asset URLs. Never hand-author SVG path data;
  download into `assets/` (flat directory, unique filename).

**Figma is design-only.** Prices, review counts, ratings, stock and product
copy come from Shopify. **Never invent a fallback value**; name what has no
source and say what you wired it to. Placeholder copy is reported, not shipped.

### 3. Design tokens

Use the theme's token layer. A token that does not exist is a component-scoped
custom property in your own CSS, reported — **never an edit to the shared token file**.

### 4. House conventions

`.claude/rules/` carries them. Grep rather than trust: the breakpoint this
theme's component CSS uses (the majority in `assets/`), the LiquidDoc
`@param` form, and any number or behaviour a comment states about this codebase.

### 5. The merchant settings contract — the most-missed rule here

`sections.md` states it; the scaffold skill's self-check lists it. The six
`t:` label keys exist; reuse them. A Figma frame shows one spacing value
because it can only show one — expose the controls anyway, plus everything a
merchant would reasonably change, and repeating items as blocks. A `range`
needs **at least 3 steps**; a 2-step range passes Theme Check and then fails
the whole theme upload — every route 500.

### 6. Locale keys — write a fragment, never edit the locale files

`locales/*.json` are shared by every agent; concurrent edits corrupt them.
Write your keys to `{{FRAGMENT_DIR}}/<your-section>.json`:

```json
{
  "schema":     { "sections": { "your_section": { "name": "...", "settings": { "heading": { "label": "..." } } } } },
  "storefront": { "sections": { "your_section": { "empty": "No items yet" } } }
}
```

`schema` merges into `en.default.schema.json` (`t:`), `storefront` into
`en.default.json` (`| t`); write your code as though the keys resolve. Shopify
resolves `t:` only in `label` / `content` / `info` / `name` / `default`; a
preset that seeds blocks **cannot** localise their per-block text.

### 7. Liquid traps that take the whole theme down

Not caught by Theme Check; each 500s every route:

- An **output tag inside a string literal** — `'{{amount}}'` — is a parse
  error. Use `{% capture %}` with `{% raw %}`.
- A **filter chain wrapped inside `{% liquid %}`** parses as an unknown tag.
  Prettier reformats code into this shape; re-check after formatting.
- **`{% raw %}` inside `{% comment %}`** unbalances the comment.

### 8. Hard boundaries

Do not touch the page's main section, `templates/*.json`, `locales/**`, the
shared token or font snippets, `config/**`, `.husky/**`, or `.claude/**`. No
`git add`, `commit`, `push`, `checkout` or `stash`. A file outside your list: **stop and report it**.

### 9. Verification you can actually do

Your section is not on the preview page yet. So:

- Confirm your Liquid parses:
  `shopify theme check --config=.theme-check.yml 2>&1 | grep -A3 "<your file>"`
  A CLI that crashes on startup is the Node version — prepend a Node 22+ bin
  directory to `PATH` (`ls ~/.nvm/versions/node`); a crashed CLI proves nothing.
- Run Prettier: `npx prettier --config .prettierrc.json --write sections/<name>.liquid`
- Grep your own output for bare English:
  `grep -nE '"(label|content|info|name)": "[A-Z]' sections/<name>.liquid` and
  `grep -nE 'aria-label="[A-Za-z]|alt="[A-Za-z]|title="[A-Za-z]' sections/<name>.liquid`
- Confirm every `t:` and `| t` key you referenced exists in your fragment.

### 10. What to report back

1. Files created or changed, with line counts.
2. **A fidelity table**: property → Figma value → your CSS value (container
   widths, gaps, type sizes, colours, radii), desktop and mobile.
3. The schema settings and blocks you exposed, and why those.
4. Anything in the design you could **not** implement, and why.
5. Any real data the design implies that has no Shopify source — name it,
   say what you wired it to.
6. The `scaffold-section` self-check, item by item, with actual results.
7. **Anything you did not verify**, said as "unverified".
