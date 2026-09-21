---
name: run-theme
description: Start or reuse the Shopify theme dev server for this checkout so the theme can be opened, screenshotted and verified. Use when the theme needs to be running — before verify-against-figma, before /verify or /run, or when asked to preview, launch or open the theme.
---

# run-theme

The recorded recipe for getting this theme running, so every skill that needs
a rendered page starts it the same way instead of rediscovering how.

## What `shopify theme dev` does

It uploads the working tree to a **development theme** on the store (created on
first run, never the live theme), serves it at `http://127.0.0.1:9292`, and
re-uploads files as they change. Nothing here touches the published theme.

## Recipe

1. **Store handle.** The CLI reads `SHOPIFY_FLAG_STORE`. It lives in
   `settings.local.json` inside `.claude/` — per machine, gitignored, so it is
   never in a checkout until the developer writes it:

   ```json
   { "env": { "SHOPIFY_FLAG_STORE": "<store-handle>" } }
   ```

   If it is not set, ask for the handle — do not guess a store.

2. **Node 22+.** The CLI dies at startup on older Node, and this team's default
   is often 20 with a newer one under nvm. If `node --version` is below 22:

   ```bash
   export PATH="$HOME/.nvm/versions/node/$(ls ~/.nvm/versions/node | sort -V | tail -1)/bin:$PATH"
   ```

3. **Already running?** `curl -sI http://127.0.0.1:9292 | head -1`. If it
   answers, reuse it.

4. **Start it**, in the background so the session keeps working:

   ```bash
   shopify theme dev --port 9292 --live-reload hot-reload
   ```

   In the desktop app the Browser pane can start it from `.claude/launch.json`
   (`theme-dev`), which runs the same command. First run on a store asks the
   developer to log in in the browser — hand that to them; never type
   credentials.

5. **Wait for readiness**: poll `curl -sI http://127.0.0.1:9292` until it
   returns 200 (typically 10–30 s, longer on the first upload of a theme).

6. **Open a page** by path: `/`, `/products/<handle>`,
   `/collections/<handle>`, `/pages/<handle>`. A page template renders nothing
   until a page with that handle and template exists in admin — four pages
   404'd on a client build for that reason alone, which is not a code defect.

## Stopping

Find the process (`pgrep -f "theme dev"`) and stop it when the session is done
with it, or leave it for the developer if they started it.

## Notes

- `--theme <id>` attaches to an existing development theme instead of creating
  another; `shopify theme list` shows them.
- Output is noisy; read it for "Serving" and for upload errors, not in full.
- The dev server renders the working tree, so the Stop gate and this skill see
  the same files — verify after the gate passes, not before.
- **Verification renders against a second server, not this one.** Hot reload
  keeps a stream open, so a headless render that waits for the network to
  settle never returns. `.claude/launch.json` has a `theme-verify`
  configuration on port 9293 with `--live-reload off` for
  `/verify-against-figma`; day-to-day work stays on 9292. Same command
  otherwise: `shopify theme dev --port 9293 --live-reload off`.
- With live reload off, an upload error latches: after the offending file is
  fixed the server keeps serving the failed state (a 500 on every route),
  because nothing re-uploads it. Restart that server; the next request is 200.
