# Development Workflow

How to set up, run, format, and ship changes to the Base theme and its documentation site.

Commands below are derived from the real `package.json` files and config in the repo. Where the
repo does not pin a value (e.g. the dev store name), this page says **confirm with the team**
rather than guessing.

---

## Prerequisites

- **Node.js** — the docs CI uses **Node 20** (`.github/workflows/deploy-docs.yml`). Use Node 20
  locally for parity.
- **Shopify CLI 3.x** — the README and docs describe this theme as built with Shopify CLI 3.0 and
  Online Store 2.0. Install per Shopify's current instructions.
- **A Shopify development store** with theme access. The store handle is **not** committed (the
  `.shopify/` directory is git-ignored) — **confirm with the team** which dev store to use.
- Accounts/permissions for the dev store and (for docs deploys) the GitHub repo — **confirm with
  the team**.

---

## Two `package.json` files — know the difference

This repo has two separate Node projects:

| Location | Purpose | Scripts |
|----------|---------|---------|
| `package.json` (root) | Theme dev tooling (linters/formatters) | only a placeholder `test` script; **no `dev` script** |
| `docs/package.json` | The VitePress documentation site | `dev`, `build`, `preview` |

So **`npm run dev` only exists inside `docs/`** and runs the VitePress docs site — it does **not**
run the Shopify theme. Running the theme is done with the Shopify CLI (below). This distinction
matters: `npm run dev` at the repo root will fail; you almost certainly mean one of the two
workflows below.

---

## Running the theme locally (Shopify CLI)

Use the Shopify CLI from the repo root:

```bash
shopify theme dev --store=<your-dev-store>
```

- Replace `<your-dev-store>` with the team dev store handle (**confirm with the team** — not
  committed).
- `shopify theme dev` hot-reloads Liquid/CSS/JS against the dev store and serves a local preview.
- `.shopifyignore` controls which files the CLI pushes/pulls (currently only documentation
  examples; review it before a `push`/`pull`).

Other common CLI commands (confirm exact flags against your CLI version):

```bash
shopify theme pull --store=<your-dev-store>     # pull current theme files
shopify theme push --store=<your-dev-store>     # push local changes (use a dev/unpublished theme)
shopify theme list --store=<your-dev-store>     # see theme IDs/roles
```

> There is **no `schemas/` folder and no `npm run build:schemas`** step in this repo. Schemas are
> written inline in each section/block `.liquid` file inside a `{% schema %}` tag. Do not create a
> `schemas/` directory.

---

## Running the documentation site locally (VitePress)

```bash
cd docs
npm install        # first time (CI uses `npm ci` against docs/package-lock.json)
npm run dev        # local VitePress dev server
npm run build      # production build → docs/.vitepress/dist
npm run preview    # preview the production build
```

The docs project is fully separate from the theme — it only needs `docs/` and Node.

---

## Formatting & linting

Dev dependencies in the root `package.json`:

- `prettier` + `@shopify/prettier-plugin-liquid`
- `eslint` + `@shopify/eslint-plugin`

**Prettier** is configured in `.prettierrc.json`:

- `printWidth: 140`, `singleQuote: true`
- Override: `*.liquid` files use `singleQuote: false`
- Liquid formatting via `@shopify/prettier-plugin-liquid`

There are **no `lint`/`format` npm scripts** defined, so run the tools directly, e.g.:

```bash
npx prettier --write .            # format using .prettierrc.json
npx eslint assets/                # lint JS in assets/
```

> **ESLint config:** no `.eslintrc*` / flat config file is committed at the repo root. The
> `@shopify/eslint-plugin` dependency is present but its activation/config is unconfirmed — **confirm
> with the team** how ESLint is expected to be run (or add a committed config + `lint` script).

Editor format-on-save is encouraged (see `rules-of-engagement.mdc`); match the existing file style
where no formatter is configured.

---

## Git branching & releases

- **`development`** is the integration branch. **Docs deploy only on pushes to `development`** (see
  below).
- **`main`** is the release branch (**confirm the exact release process with the team** — not
  encoded in the repo).
- **Feature branches** branch off `development`; open PRs back into `development`. Run
  `/pr-review` (see `ai-tooling.md`) before requesting merge.

### Docs deployment

`.github/workflows/deploy-docs.yml` deploys the VitePress site to GitHub Pages and is gated to:

```yaml
on:
  push:
    branches: [development]
    paths:
      - 'docs/**'
```

Implications:

- The site only rebuilds/deploys when commits land on **`development`** and touch **`docs/**`**.
- **On a feature branch, your docs changes will not deploy.** Preview them locally with
  `cd docs && npm run dev` (or `npm run build && npm run preview`). They go live once merged to
  `development`.
- The published site base path is `/Base/` and the live URL is
  https://ecomexperts-io.github.io/Base/ (see `docs/.vitepress/config.mts`).

---

## Single-language note

This theme currently ships **English only**. `locales/` contains `en.default.json` (storefront
strings) and `en.default.schema.json` (editor/schema strings) — there are no `es.json`/`fr.json`/
`de.json`. Add new keys to `en.default.json` (and schema keys to `en.default.schema.json`); other
languages are added later if the store goes multilingual.
