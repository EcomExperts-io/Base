# Workflow — building a page's sections with parallel agents

Build one page of a Figma design by giving each section to its own agent, running
them concurrently, then assembling and verifying the page yourself.

Used on the BPN PDP: 9 sections, ~1.5 hours wall-clock, reviewed by the team lead as
"could be more than 60%" saved against a 40-hour estimate. This file is what made
that repeatable rather than lucky. It is not a skill — skills only run when invoked,
and this is a procedure a human chooses to start.

**When to use it.** A page of 5+ independent content sections, each traceable to its
own Figma frame. **When not to:** anything where the sections share a stylesheet or a
JS module, or where section B's markup depends on section A's. Concurrency buys
nothing there and costs you a merge.

---

## Part 1 — Orchestrator (you)

### 1. Establish the section list before spawning anything

Enumerate the page's sections from the desktop frame, top to bottom, and for each one
record the **desktop node id and the mobile node id**. One agent per row.

Then — and this is the step that is skipped and always costs the most — **check what
already exists.** A section that another page already ships is a `templates/*.json`
entry, not a build. Grep `sections/`, and read whatever estimate or scope doc the
lead has written. On BPN, seven of the PDP's sections had already been delivered by
the homepage build.

Do not trust a name match. "Collections strip → Shop By Goal cards" looked like the
same component in a scope doc and was not remotely the same component. Open both and
look.

### 2. Fill in the agent brief

Copy Part 2 below into the scratchpad, fill the four placeholders at the top, and
hand every agent the same file. One brief, N agents — divergent briefs produce
divergent conventions, which you then pay for at assembly.

### 3. Spawn, then stay out of the way

One agent per section, all in a single message so they run concurrently. Give each
one only its own two node ids and its own file ownership list.

### 4. Assemble

- Merge the locale fragments: `python3 .claude/scripts/merge-locale-fragments.py <fragment-dir>`
  It refuses to overwrite an existing key and reports every conflict, which is the
  whole reason agents write fragments instead of touching `locales/` directly.
- Build `templates/<page>.json` from the section presets, in frame order.
- **Strip `t:` values.** Shopify resolves `t:` keys in a schema `default`, but *not*
  in values stored in a template. A `t:` left in a template renders the key path to
  the customer.
- A brand-new block type needs roughly 25 seconds to register with Shopify before a
  template may reference it. Reference it too early and every route on the theme
  returns 500.

### 5. Verify — and read this before you report anything

Agents report their own fidelity. Two of three "X is broken" reports on the BPN build
were false, both from agents measuring inside their own static harness rather than in
the theme. Re-verify anything load-bearing yourself.

**Matching heights is not matching the design.** The single worst failure of this
workflow to date: a section was reported as built because it measured 614px against
the frame's 615px, and a scope doc independently agreed. It shared nothing else with
the design. A FAQ layout was reported as matching at 728 vs 727 while its media
column was rendering completely empty.

So: **screenshot both breakpoints and look at them, against the Figma frame.** A
measurement is a check on a screenshot, never a substitute for one. If you could not
get a usable screenshot, the honest report is "unverified" — not the number you did
manage to measure.

### 6. Gate

Run `shopify-standards-coach` for the advisory pass and `shopify-pr-reviewer` over the
whole diff before it goes to a human.

---

## Part 2 — Agent brief template

Fill in `{{REPO}}`, `{{BRANCH}}`, `{{FIGMA_FILE_KEY}}`, `{{FRAGMENT_DIR}}`,
`{{PREVIEW_URL}}`, then give this to every agent verbatim.

---

Repo: `{{REPO}}`
Branch: `{{BRANCH}}` (already checked out — do not switch branches)

You are building **one section** of a page from Figma. Other agents are building the
other sections in parallel. Stay strictly inside the files you own.

### 1. Read these before writing any code

- `CLAUDE.md`
- `.claude/rules/sections.md` — the merchant settings contract
- `.claude/rules/schemas.md`, `css-standards.md`, `localization.md`,
  `naming-conventions.md`, `html-standards.md`, `liquid.md`
- `.claude/skills/scaffold-section/SKILL.md` — follow its steps and its self-check
- `.claude/skills/scaffold-section/reference-section.liquid` — the structural template

Do **not** use `.cursor/rules/examples/section-example.liquid`. It predates the standard.

### 2. Get the design — two frames, separately

Invoke the Figma design-to-code skill **before** your first `get_design_context` call.
Then call it twice, once per frame:

```
get_design_context
  fileKey: {{FIGMA_FILE_KEY}}
  nodeId: <your DESKTOP node>
  clientLanguages: liquid,html,css
  clientFrameworks: shopify-liquid
```

- Desktop frames are designed at **1440**, mobile at **393**.
- These are two designs, not one responsive artifact. Mobile frequently uses a
  different layout and sometimes a different component entirely.
- Read real values — spacing, type size, line height, colour, radii — off the design.
  Do not approximate by eye.
- The returned code is React + Tailwind. **Reference only.** Convert it.
- Icons and images come back as asset URLs. Never hand-author SVG path data. Download
  what you need into `assets/` (flat directory, unique filename).

**Figma is design-only.** It never supplies real data. Prices, review counts, ratings,
stock, product copy, ingredient values all come from Shopify objects, settings or
metafields. A mock reading "4.9 (127 reviews)" is a picture of a number, not the number.
**Never invent a fallback value.** Name what has no source and say what you wired it to.

Some frames legitimately contain placeholder copy. If yours does, say so rather than
shipping lorem ipsum as though it were content.

### 3. Design tokens

Use the theme's existing token layer. **Never write a raw hex.** If your design needs
a token that does not exist, **do not edit the shared token file** — define a
component-scoped custom property in your own CSS and report it.

### 4. House conventions

- **px**, not rem.
- **Mobile-first, `min-width` only**, never `max-width`. Every query includes `screen`.
  Use the breakpoint this theme's component CSS actually uses — grep `assets/` and
  match the majority rather than copying a number out of a rule file.
- **BEM**, and namespace component custom properties: `--<block>-<thing>`.
- **Logical properties**: `padding-block`, `padding-inline`, `inline-size`, `inset`.
- **Max selector specificity 0 4 0.**
- CSS via `{{ 'section-<name>.css' | asset_url | stylesheet_tag }}`; JS, only if
  genuinely needed, as `type="module"`.
- **LiquidDoc form is `@param {type} name - description`** — match the codebase, and
  grep to confirm before trusting any example.
- `| escape` on every merchant string, in attributes *and* text nodes.
- Validate snippet params: early `break` when a required one is blank.
- Interactive JS only as a custom element behind `if (!customElements.get('x'))`,
  wiring in `connectedCallback` and **removing every listener** in
  `disconnectedCallback`. No `DOMContentLoaded`, no jQuery. Alpine and Swiper are
  already loaded globally — Alpine for ephemeral UI state, Swiper for carousels.
  Prefer native HTML first: `<details>`, `<dialog>`, `popover`.
- No commented-out code. No `!important` without a comment saying why.
- Add nothing that has no reader — no unused tokens, data attributes, or classes.
- If a comment states a number or a behaviour about this codebase, grep to confirm it
  before you write it.

**A custom element carrying section styling needs an explicit `display`.** Custom
elements default to `display: inline`, which paints no background around block children
and ignores vertical padding — while `getComputedStyle()` still reports both. This looks
correct in a DOM check and wrong on screen.

### 5. The merchant settings contract — the most-missed rule here

Every section exposes, in this order: `color_scheme`, a padding `header`,
`padding_top` and `padding_bottom` (`range` 0–100 step 4 default 40), plus a `presets`
array. Those four `t:` label keys already exist — reuse them.

`padding_top`/`padding_bottom` have **no exceptions**. `color_scheme` may be omitted
only with a Liquid comment naming the Figma node and saying why the surface is fixed.

A Figma frame shows one spacing value because a frame can only show one. That is not a
reason to omit the control. Expose everything a merchant would reasonably want to
change — headings, copy, images, links — and the repeating items as blocks.

A `range` needs **at least 3 steps** between min and max. A 2-step range is accepted by
Theme Check and then fails the whole theme upload — every route 500, not just the page.

### 6. Locale keys — write a fragment, never edit the locale files

`locales/en.default.json` and `en.default.schema.json` are shared by every agent.
Editing them concurrently corrupts them. Write your keys to
`{{FRAGMENT_DIR}}/<your-section>.json`:

```json
{
  "schema":     { "sections": { "your_section": { "name": "...", "settings": { "heading": { "label": "..." } } } } },
  "storefront": { "sections": { "your_section": { "empty": "No items yet" } } }
}
```

`schema` merges into `en.default.schema.json` (referenced as `t:`), `storefront` into
`en.default.json` (referenced as `| t`). Write your code as though the keys resolve.

Note: Shopify resolves `t:` only in `label` / `content` / `info` / `name` / `default`.
A preset that seeds blocks **cannot** localise their per-block text.

### 7. Liquid traps that take the whole theme down

These are not caught by Theme Check and each one 500s every route:

- An **output tag inside a string literal** — `'{{amount}}'` — is a parse error. Use
  `{% capture %}` with `{% raw %}`.
- A **filter chain wrapped inside `{% liquid %}`** parses as an unknown tag. Prettier
  will reformat code into this shape, so re-check after formatting.
- **`{% raw %}` inside `{% comment %}`** unbalances the comment.

### 8. Hard boundaries

Do not touch the page's main section, `templates/*.json`, `locales/**`, the shared
token or font snippets, `config/**`, `.husky/**`, or `.claude/**`. Do not `git add`,
`commit`, `push`, `checkout`, or `stash` — leave every change unstaged; the developer
reviews and commits. If you need a file outside your ownership list, **stop and report
it** rather than expanding scope.

### 9. Verification you can actually do

Your section will not be on the preview page yet — the orchestrator assembles the
template at the end. So:

- Confirm your Liquid parses:
  `shopify theme check --config=.theme-check.yml 2>&1 | grep -A3 "<your file>"`
  If the CLI crashes on startup it is the Node version, not your code — prepend a
  Node 24+ bin directory to `PATH` (`ls ~/.nvm/versions/node`). A crashed CLI is
  reported by the pre-commit hook as *skipped*, so it silently proves nothing.
- Run Prettier: `npx prettier --config .prettierrc.json --write sections/<name>.liquid`
- Grep your own output for bare English:
  `grep -nE '"(label|content|info|name)": "[A-Z]' sections/<name>.liquid` and
  `grep -nE 'aria-label="[A-Za-z]|alt="[A-Za-z]|title="[A-Za-z]' sections/<name>.liquid`
- Confirm every `t:` and `| t` key you referenced exists in your fragment.

### 10. What to report back

1. Files created or changed, with line counts.
2. **A fidelity table**: property → Figma value → your CSS value, for the things that
   matter (container widths, gaps, type sizes, colours, radii), desktop and mobile.
3. The schema settings and blocks you exposed, and why those and not others.
4. Anything in the design you could **not** implement, and why. Be specific.
5. Any real data the design implies that has no Shopify source — name it, say what you
   wired it to (setting? metafield? left blank?). Never invent a fallback.
6. The `scaffold-section` self-check, item by item, with actual results — not an
   assertion that you complied.
7. **Anything you did not verify.** Say "unverified" rather than reporting the one
   number you could measure as though it settled the question.

Honesty is worth more than a clean report. If something is half-done, say so.
