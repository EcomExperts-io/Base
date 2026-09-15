# Your first build

One page, one hour, and at the end a section that passes the gate, verified
against its frame, on a branch you can open a pull request from. This is how
the workflow is learned; nobody sits next to you.

**Why this page exists.** Until v2 the way to learn the workflow was to watch
the one person who had built it. Nothing in the repo said which tools a build
needed or how to tell whether the gate was wired. The acceptance test for v2 is
that a developer who has never used it finishes this page alone — every place
you stall is a defect in the tooling, not in you, so note it and
`/record-incident` it at the end.

## 0. What you need

- A Mac or Linux machine with **Node 22+** (`nvm install 24 && nvm alias default 24`), `python3`,
  Google Chrome, and [`gh`](https://cli.github.com/) signed in.
- Claude Code, signed in.
- Access to the client store you will build in (a staff account) and to its
  Figma file. Your lead gives you **one known-good frame** — a desktop node id
  and a mobile node id for a single section, plus the file key. Until the
  company owns a Figma template file, that frame comes from the current
  client file.

## 1. Get the repo ready

```bash
git clone <client-repo-url> && cd <repo>
npm install
npm run setup
```

`setup` wires the commit gate (under `.githooks/` or through husky, whichever
the repo has), regenerates the Cursor mirror, and runs the doctor. Read the
doctor's output: every line that is not `OK` has the fix beside it. Fix them.

If the repo has no `.claude/` directory yet, or `doctor` says the tooling is
missing:

```bash
sh .claude/scripts/base-link.sh || git clone https://github.com/EcomExperts-io/Base.git ../Base && sh ../Base/.claude/scripts/base-link.sh
python3 .claude/scripts/pull-base-tooling.py
```

## 2. Connect the tools, once per machine

```bash
claude plugin install figma@claude-plugins-official
claude
```

On first launch Claude Code asks to approve the project's MCP servers
(`notion`, `shopify-dev-mcp`) — approve. Then `/mcp` and sign in to Notion and
Figma in the browser. Set the store handle so the dev server and the verifier
know where to look:

```bash
echo '{"env":{"SHOPIFY_FLAG_STORE":"<store-handle>"}}' > .claude/settings.local.json
```

Run `python3 .claude/scripts/doctor.py` again. It should be all `OK` apart from
lines about your machine's Node if you skipped step 0.

## 3. Open a session and read what it tells you

Start `claude` in the repo. The first lines of the session are the theme's
state: doctor status, how far the tooling is from Base, the compliance number,
open incidents, and the three most-missed rules. If those lines are missing,
the SessionStart hook is not firing — that is a stall; note it.

## 4. Build the section

Paste this, with your frame's values:

```text
Build the <section name> section from Figma using our Base Theme standards.
File key: <fileKey>. Desktop: <nodeId>@1440. Mobile: <nodeId>@390.
Run /figma-readiness first and stop if it says send back.
Set a /goal so a fresh evaluator decides when it is done.
```

What you should see happen, in order:

1. **Readiness** — a score for the frame and, if it is not green, a message
   to forward to the designer instead of a build.
2. **Scaffold** — the section created from the reference shape with
   `padding_top`, `padding_bottom`, `color_scheme` and a preset already in the
   schema, every string a translation key.
3. **The per-edit gate** — after each file Claude writes, a short block of
   findings appears in the conversation if anything is off. It is normal to
   see one or two on the first pass; it is not normal to see "missing
   padding_top" survive to the end.
4. **Verification** — `/run-theme` starts the dev server, `/verify-against-figma`
   renders the section at 1440 and 390, diffs it against the frame, and writes
   `.claude/verify/<slug>/report.md`. Open the side-by-side preview it names
   and look at it yourself.
5. **The turn ends only when the gate passes** — if Claude tries to finish
   with a new file failing the contract, the Stop hook refuses and it fixes
   it. You will see this in the transcript as an extra turn.

## 5. Prove it

```bash
python3 .claude/scripts/report-compliance.py | head -12
```

The compliant count is one higher than the session's opening line said. Then:

```bash
git add -A && git commit -m "[FEATURE]: Add the <section name> section"
```

The commit runs the gate again. It passes, and it has regenerated and staged
`.cursor/` for you. Do not open a pull request from this exercise unless your
lead asks; the point was the loop, not the section.

## 6. Say what stalled

Anything that made you stop and ask a person — a command that did not exist, a
hook that did not fire, a message you did not understand — is a defect in this
workflow. Record each one:

```text
/record-incident
```

with `should_have_caught` set to `docs/ai-workflow/first-build.md`. That queue
is how this page gets shorter for the next developer.

## What "done" looks like

- `doctor.py` all `OK` (Node aside).
- One new section, compliant, verified, with a report on disk.
- One commit that went through the gate.
- Zero questions asked to a human — or one incident per question you did ask.
