---
name: scaffold-snippet
description: Generate a complete, standards-compliant component snippet. Use when the user asks to scaffold, create, or add a new snippet/component in snippets/.
---

# scaffold-snippet

**Purpose:** Generate a complete, standards-compliant component snippet.

**Invocation:** `/scaffold-snippet <name> [description]`
Example: `/scaffold-snippet video-player "Renders a responsive video player with poster"`

## Steps

1. Create `snippets/component-<name>.liquid` with a mandatory `{% doc %}` block including a
   `@param` entry for every parameter and an `@example` usage.
2. Add a parameter validation block using a `{% liquid %}` tag with
   `assign param = param | default: value` for every parameter; add an early `break` guard for any
   required parameter that is blank.
3. Create `assets/component-<name>.css` with a BEM class structure.
4. If JS is needed: create `assets/component-<name>.js` with the `customElements.define` guard
   (`if (!customElements.get(...))`), `connectedCallback`, and `disconnectedCallback`.
5. Load the JS in the Liquid file with `type="module"` (not `defer`).
6. Create `docs/snippets/component-<name>.md` with the standard VitePress structure.
7. Confirm there are **no hardcoded hex colors**; use `var(--color-*)` tokens.

## Notes

- Snippet file naming must match across `.liquid`, `.css`, and `.js`:
  `component-<name>.{liquid,css,js}`.
- Every `component-` snippet must ship LiquidDoc (`{% doc %}`) — this is non-negotiable.
