---
name: figma-readiness
description: Score a Figma frame's structure before building from it — default layer names, hidden leftovers, width in the frame name, components, text as text, tokens, behaviour notes — and write the message to send the designer if it is not ready. Use before the first get_design_context call of any build, and whenever asked whether a frame is buildable or why a build keeps needing re-prompts.
argument-hint: <fileKey> <nodeId>[@<width>] [<nodeId>@<width>]
---

# figma-readiness

Every re-prompt cycle traces back to a structural fact a script can see.
Find them before the build.

**Invocation:** `/figma-readiness <fileKey> <nodeId>[@<width>] [<nodeId>@<width>]`
— Step 1½ of `/build-page-from-figma`; also on its own.

## Steps — per frame

1. **Metadata.** Call the Figma `get_metadata` tool with the file key and node
   id. Save the XML as-is to `.claude/verify/readiness/<nodeId>.xml`.

2. **Score.**

   ```bash
   python3 .claude/scripts/figma-readiness-score.py .claude/verify/readiness/<nodeId>.xml --width <width>
   ```

   It prints a verdict per check — `pass`, `warn`, `ask`, `send back` — the
   largest default-named layers to rename first, and any hidden layers.

3. **What metadata cannot show.**
   - **Auto layout.** Call `get_design_context` (after the Figma
     design-to-code skill). Layout dominated by absolute positioning rather
     than flex/grid is a `send back` on practice 6, whatever the score said.
   - **Tokens.** Call `get_variable_defs`. Empty means values will be
     reverse-engineered from raw numbers — a `warn` for report and designer.
   - **Behaviour.** For any interactive component (menu, drawer, accordion,
     filter, carousel) look for text layers or comments beside the frame
     describing states. None → `ask` before building the behaviour.

4. **Second breakpoint.** One node id given: ask for the other (practice 3).

## Verdict

- **pass / warn** — build; put the warnings in the build report.
- **ask** — build what is unambiguous; ask before the ambiguous part.
- **send back** — do not build. Write the designer a message under twenty
  lines: the verdict lines, the layers to rename (ids and names), the hidden
  layers to remove, the missing width or breakpoint. Hand it to the
  developer to forward and stop; "build anyway" overrides, and the report
  records that it did.

## What to record

Copy the scorer's output into the build report under "Frame readiness". A
`pass` that still needed three re-prompts is `/record-incident` pointing here.
