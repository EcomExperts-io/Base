---
name: run-theme
description: Start or reuse the Shopify theme dev server for this checkout so the theme can be opened, screenshotted and verified. Use when the theme needs to be running — before verify-against-reference, before /run, or when asked to preview, launch or open the theme.
argument-hint: [--verify]
---

# run-theme

`shopify theme dev` uploads the working tree to a **development theme** on the
store (created on first run, never the live theme), serves it at
`http://127.0.0.1:9292`, and re-uploads files as they change.

## Recipe

1. **Store handle.** `SHOPIFY_FLAG_STORE` in `settings.local.json` inside
   `.claude/` (per machine, gitignored):

   ```json
   { "env": { "SHOPIFY_FLAG_STORE": "<store-handle>" } }
   ```

   If it is not set, ask for the handle — never guess a store.

2. **Node 22+.** The CLI dies at startup on older Node. If `node --version`
   is below 22:

   ```bash
   export PATH="$HOME/.nvm/versions/node/$(ls ~/.nvm/versions/node | sort -V | tail -1)/bin:$PATH"
   ```

3. **Already running?** `curl -sI http://127.0.0.1:9292 | head -1`. If it
   answers, reuse it.

4. **Start it**, in the background:

   ```bash
   shopify theme dev --port 9292 --live-reload hot-reload
   ```

   The Browser pane can start it from `.claude/launch.json` (`theme-dev`).
   A first run asks the developer to log in — hand that to them.

5. **Wait for readiness**: poll `curl -sI http://127.0.0.1:9292` until it
   returns 200 (10–30 s, longer on a first upload).

6. **Open a page** by path: `/`, `/products/<handle>`,
   `/collections/<handle>`, `/pages/<handle>`. A page template 404s until a
   page with that handle and template exists in admin; not a code defect.

## Stopping

`pgrep -f "theme dev"`; stop it when done, or leave it if the developer started it.

## Notes

- `--theme <id>` attaches to an existing development theme (`shopify theme list`).
- Output is noisy; read it for "Serving" and for upload errors.
- The dev server renders the working tree; verify after the gate passes.
- **Verification renders against a second server.** Hot reload keeps a stream
  open, so a headless render that waits for the network never returns.
  `.claude/launch.json` has `theme-verify` on port 9293 for
  `/verify-against-reference`: `shopify theme dev --port 9293 --live-reload off`.
- With live reload off, an upload error latches: the server keeps serving the
  failed state (a 500 on every route) after the fix. Restart it.
- **A theme-wide 500 whose body names a file you were not editing is an
  invalid schema elsewhere.** One rejected upload fails every route; read the
  filename in the error, and restart once to tell a real failure from a latched one.
- **An upload rejection is silent from the agent's side.** After writing a
  schema or a template with dynamic sources, `curl -s <url> | grep -c "Upload Errors"`.
- **A change that adds a setting and sets it in a template needs a restart**;
  the watcher may sync the template first and Shopify drops the key (`templates.md`).
- **Do not verify against a server another session started.**
