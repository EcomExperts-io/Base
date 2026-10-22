---
name: figma-readiness
description: Score a Figma frame's structure before building from it — default layer names, hidden leftovers, width in the frame name, components, text as text, tokens, behaviour notes — and write the message to send the designer if it is not ready. Use before the first get_design_context call of any build, and whenever asked whether a frame is buildable or why a build keeps needing re-prompts.
argument-hint: <fileKey> <nodeId>[@<width>] [<nodeId>@<width>]
---

# figma-readiness

Check the frame before spending a day on it.

Every re-prompt cycle traces back to a structural fact a script can see:
default layer names, hidden old versions, no width in the frame name, no
components, text flattened to vectors. This finds them before the build, all
at once, with the layers named.

**Invocation:** `/figma-readiness <fileKey> <nodeId>[@<width>] [<nodeId>@<width>]`
— runs as Step 1½ of `/build-page-from-figma`; also on its own.

## Steps — per frame

1. **Metadata.** Call the Figma `get_metadata` tool with the file key and node
   id. Save the XML it returns to `.claude/verify/readiness/<nodeId>.xml`
   (write the response body as-is).

2. **Score.**

   ```bash
   python3 .claude/scripts/figma-readiness-score.py .claude/verify/readiness/<nodeId>.xml --width <width>
   ```

   It prints a verdict per check — `pass`, `warn`, `ask`, `send back` — the
   largest default-named layers to rename first, and any hidden layers.

3. **The two things metadata cannot show.**
   - **Auto layout.** Call `get_design_context` on the frame (invoke the Figma
     design-to-code skill first, as the build skill requires). If the returned
     layout is dominated by absolute positioning rather than flex/grid, that
     is a `send back` on practice 6, whatever the score said.
   - **Tokens.** Call `get_variable_defs`. Empty means colours, spacing and
     type will be reverse-engineered from raw values — a `warn` to state in the
     report and to the designer.
   - **Behaviour.** For any interactive component (menu, drawer, accordion,
     filter, carousel) look for text layers or comments beside the frame that
     describe states. None → `ask` before building the behaviour.

4. **Second breakpoint.** If only one node id was given, ask for the other.
   Two frames with the width in each name is practice 3; a single frame means
   the other breakpoint will be invented.

## Verdict

- **pass / warn** — build. Put the warnings in the build report so the
  designer sees them once.
- **ask** — build what is unambiguous; ask the specific question before the
  ambiguous part.
- **send back** — do not build yet. Write the designer a short message: the
  verdict lines, the layers to rename (ids and names), the hidden layers to
  remove, the missing width or breakpoint, in plain language and under twenty
  lines. Hand it to the developer to forward. Then stop — a developer can
  override with "build anyway", and the report records that they did.

## What to record

Copy the scorer's output into the build report under "Frame readiness". A
frame that scored `send back` and was built anyway is a fact the reviewer
should know; a frame that scored `pass` and still needed three re-prompts is
an incident for this skill (`/record-incident` with `should_have_caught`
pointing here).
