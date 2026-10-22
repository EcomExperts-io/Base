# Your first build

One page, one hour: a section that passes the gate, verified against its frame,
on a branch. Every place you stall is a tooling defect, not yours: `/record-incident` it.

## 0. What you need

- A Mac or Linux machine with **Node 22+** (`nvm install 24 && nvm alias default 24`), `python3`,
  Google Chrome, [`gh`](https://cli.github.com/) signed in, and Claude Code signed in.
- A staff account on the client store, and access to its Figma file.
- **One known-good frame**: desktop and mobile node ids for one section, plus the file key.

## 1. Get the repo ready

```bash
git clone <client-repo-url> && cd <repo>
npm install
npm run setup
```

`setup` wires the commit gate (`.githooks/` or husky), regenerates the Cursor
mirror and runs the doctor; `sh .claude/scripts/setup.sh` is the same thing if
npm has no such script. Every doctor line that is not `OK` has the fix beside
it. Fix them. If there is no `.claude/` yet, or `doctor` says the tooling is missing:

```bash
sh .claude/scripts/base-link.sh || git clone https://github.com/EcomExperts-io/Base.git ../Base && sh ../Base/.claude/scripts/base-link.sh
python3 .claude/scripts/pull-base-tooling.py
```

## 2. Connect the tools, once per machine

```bash
claude plugin install figma@claude-plugins-official
claude
```

On first launch approve the project's MCP servers (`notion`, `shopify-dev-mcp`),
then `/mcp` and sign in to Notion and Figma. Set the store handle for the dev
server and the verifier:

```bash
echo '{"env":{"SHOPIFY_FLAG_STORE":"<store-handle>"}}' > .claude/settings.local.json
```

`python3 .claude/scripts/doctor.py` again: all `OK`, Node aside.

## 3. Build the section

Start `claude` in the repo. The first lines are the theme's state — doctor
status, tooling drift, compliance number, open incidents, most-missed rules; if
they are missing the SessionStart hook is not firing: a stall. Then paste this,
with your frame's values, and expect the following in order:

```text
Build the <section name> section from Figma using our Base Theme standards.
File key: <fileKey>. Desktop: <nodeId>@1440. Mobile: <nodeId>@390.
Run /figma-readiness first and stop if it says send back.
Set a /goal so a fresh evaluator decides when it is done.
```

1. **Readiness** — a frame score; if not green, a designer message instead of a build.
2. **Scaffold** — four padding settings, `color_scheme` and a preset in the schema; every string a key.
3. **The per-edit gate** — findings after each file Claude writes. One or two
   on a first pass is normal; "missing padding_top" surviving to the end is not.
4. **Verification** — `/run-theme`, then `/verify-against-reference` renders at
   1440 and 390, diffs against the frame, writes `.claude/verify/<slug>/report.md`.
   Open the side-by-side it names and look.
5. **The turn ends only when the gate passes** — the Stop hook refuses a failing new file; Claude fixes it.

## 4. Prove it

```bash
python3 .claude/scripts/report-compliance.py | head -12
```

The compliant count is one higher than the session's opening line said. Then:

```bash
git add -A && git commit -m "[FEATURE]: Add the <section name> section"
```

The commit runs the gate again and stages the regenerated `.cursor/`. No pull
request from this exercise unless asked.

## 5. Say what stalled

Anything that made you stop and ask a person — a missing command, a hook that
did not fire, a message you did not understand — is a defect in this workflow.
`/record-incident` each one with `should_have_caught` = `docs/ai-workflow/first-build.md`.

## What "done" looks like

- `doctor.py` all `OK` (Node aside).
- One new section, compliant, verified, with a report on disk; one commit through the gate.
- Zero questions asked to a human — or one incident per question you did ask.
