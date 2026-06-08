# Base Theme — Claude Configuration

See `AGENTS.md` for full project context and standards.

## Claude-Specific Notes

- Skills are in `.claude/skills/` (same content as `.cursor/skills/`).
- When asked to scaffold a section, block, or snippet, follow `AGENTS.md` §Core Standards exactly.
- Run the `/pr-review` equivalent steps before suggesting any merge-ready code.
- **This repo has no `schemas/` folder** — do not introduce `schemas/` references or a
  `npm run build:schemas` step. Schemas are written inline in each `.liquid` file's `{% schema %}` tag.
